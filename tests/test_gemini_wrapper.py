"""
Tests for the Sovereign Fallback Gemini wrapper
(enki_ai.agents.gemini_wrapper).

These tests run without any external dependencies (Gemini API key, Ollama,
or aiohttp) — the wrapper's fallback chain is exercised via coroutine mocks.
"""
from __future__ import annotations

import asyncio
import pytest

from enki_ai.agents.gemini_wrapper import (
    _LRUCache,
    _extract_http_status,
    _extract_text,
    _sovereign_fallback,
    generate,
    TIMEOUT_MS,
)


# ---------------------------------------------------------------------------
# LRU cache
# ---------------------------------------------------------------------------

class TestLRUCache:
    def test_miss_returns_none(self):
        cache = _LRUCache(maxsize=4)
        assert cache.get("hello") is None

    def test_put_and_get(self):
        cache = _LRUCache(maxsize=4)
        cache.put("hello world", "response A")
        assert cache.get("hello world") == "response A"

    def test_key_truncated_to_128_chars(self):
        cache = _LRUCache(maxsize=4)
        long_prompt = "x" * 200
        cache.put(long_prompt, "val")
        # A prompt with the same first 128 chars should hit.
        assert cache.get("x" * 200) == "val"
        assert cache.get("x" * 128) == "val"

    def test_eviction_on_overflow(self):
        cache = _LRUCache(maxsize=2)
        cache.put("a", "1")
        cache.put("b", "2")
        cache.put("c", "3")  # should evict "a"
        assert cache.get("a") is None
        assert cache.get("b") == "2"
        assert cache.get("c") == "3"

    def test_lru_order_updated_on_get(self):
        cache = _LRUCache(maxsize=2)
        cache.put("a", "1")
        cache.put("b", "2")
        cache.get("a")         # access "a" → "b" becomes LRU
        cache.put("c", "3")   # should evict "b" not "a"
        assert cache.get("a") == "1"
        assert cache.get("b") is None


# ---------------------------------------------------------------------------
# _extract_text
# ---------------------------------------------------------------------------

class TestExtractText:
    def test_plain_string_passthrough(self):
        assert _extract_text("hello") == "hello"

    def test_object_with_text_attr(self):
        class FakeResponse:
            text = "generated text"
        assert _extract_text(FakeResponse()) == "generated text"

    def test_object_without_text_attr(self):
        class Unknown:
            def __str__(self):
                return "str-repr"
        assert _extract_text(Unknown()) == "str-repr"


# ---------------------------------------------------------------------------
# _extract_http_status
# ---------------------------------------------------------------------------

class TestExtractHttpStatus:
    def test_status_attr(self):
        class Exc(Exception):
            status = 503
        assert _extract_http_status(Exc()) == 503

    def test_status_code_attr(self):
        class Exc(Exception):
            status_code = 500
        assert _extract_http_status(Exc()) == 500

    def test_nested_response_attr(self):
        class Resp:
            status = 502
        class Exc(Exception):
            response = Resp()
        assert _extract_http_status(Exc()) == 502

    def test_no_status_returns_none(self):
        assert _extract_http_status(ValueError("plain error")) is None


# ---------------------------------------------------------------------------
# generate() — fallback paths
# ---------------------------------------------------------------------------

class TestGenerate:
    @pytest.mark.asyncio
    async def test_no_coroutine_triggers_fallback(self):
        """When no coroutine is provided the fallback sentinel is returned."""
        result = await generate("test prompt", gemini_coroutine=None)
        # Should return some non-empty string (cached, Ollama, or sentinel).
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_successful_coroutine_returns_text(self):
        """A coroutine that succeeds returns its text and caches it."""
        async def _ok():
            return "gemini reply"

        result = await generate("my prompt", gemini_coroutine=_ok())
        assert result == "gemini reply"

    @pytest.mark.asyncio
    async def test_timeout_triggers_fallback(self, monkeypatch):
        """A coroutine that takes too long triggers Sovereign Fallback."""
        import enki_ai.agents.gemini_wrapper as gw

        # Temporarily lower the timeout so the test runs fast.
        monkeypatch.setattr(gw, "TIMEOUT_MS", 50)
        monkeypatch.setattr(gw, "FALLBACK_ENABLED", True)

        async def _slow():
            await asyncio.sleep(10)
            return "never reached"

        result = await gw.generate("slow prompt", gemini_coroutine=_slow())
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_5xx_triggers_fallback(self, monkeypatch):
        """A 5xx exception triggers Sovereign Fallback instead of propagating."""
        import enki_ai.agents.gemini_wrapper as gw
        monkeypatch.setattr(gw, "FALLBACK_ENABLED", True)

        class ServerError(Exception):
            status = 503

        async def _5xx():
            raise ServerError("service unavailable")

        result = await gw.generate("5xx prompt", gemini_coroutine=_5xx())
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_non_5xx_exception_propagates(self, monkeypatch):
        """A non-5xx exception (e.g. auth error) is NOT swallowed."""
        import enki_ai.agents.gemini_wrapper as gw
        monkeypatch.setattr(gw, "FALLBACK_ENABLED", True)

        class AuthError(Exception):
            status = 401

        async def _auth_err():
            raise AuthError("invalid key")

        with pytest.raises(AuthError):
            await gw.generate("auth prompt", gemini_coroutine=_auth_err())

    @pytest.mark.asyncio
    async def test_cache_populated_after_success(self):
        """After a successful call the response is stored in the LRU cache."""
        from enki_ai.agents.gemini_wrapper import _cache

        prompt = "cache-test-prompt-unique-9182"
        async def _ok():
            return "cached-answer"

        await generate(prompt, gemini_coroutine=_ok())
        assert _cache.get(prompt) == "cached-answer"

    @pytest.mark.asyncio
    async def test_cached_response_served_on_fallback(self, monkeypatch):
        """When fallback is triggered an existing cache entry is returned."""
        import enki_ai.agents.gemini_wrapper as gw
        monkeypatch.setattr(gw, "FALLBACK_ENABLED", True)
        monkeypatch.setattr(gw, "TIMEOUT_MS", 50)

        prompt = "cached-fallback-prompt-unique-5541"
        gw._cache.put(prompt, "prior-good-answer")

        async def _slow():
            await asyncio.sleep(10)
            return "never"

        result = await gw.generate(prompt, gemini_coroutine=_slow())
        assert "prior-good-answer" in result


# ---------------------------------------------------------------------------
# _sovereign_fallback (unit-level)
# ---------------------------------------------------------------------------

class TestSovereignFallback:
    @pytest.mark.asyncio
    async def test_returns_string(self):
        result = await _sovereign_fallback("any prompt", "test reason")
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_cache_hit_prefixed(self):
        from enki_ai.agents.gemini_wrapper import _cache
        _cache.put("special-prompt-99", "remembered answer")
        result = await _sovereign_fallback("special-prompt-99", "timeout")
        assert "remembered answer" in result
