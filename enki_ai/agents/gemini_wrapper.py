"""
Sovereign Fallback Gemini Wrapper — enki_ai.agents.gemini_wrapper

Wraps outbound calls to the Google Gemini API with:

* **5xx circuit-breaker** — any HTTP 5xx response code triggers immediate
  fallback so the Node remains stable.
* **Latency guard** — if a call exceeds ``TIMEOUT_MS`` (default 2 000 ms)
  the wrapper cancels the pending coroutine and activates fallback.
* **Fallback hierarchy**
  1. In-memory LRU response cache (most recently seen Gemini reply keyed by
     the first 128 chars of the prompt).
  2. Local Ollama endpoint (``http://localhost:11434``) running TinyLlama or
     any model configured via ``SOVEREIGN_OLLAMA_MODEL``.
  3. Hard-coded "Node Stability" sentinel reply so the caller always gets a
     response.

The wrapper exposes a single coroutine ``generate(prompt, **kwargs)`` that
mirrors the minimal interface used by the rest of the Enki AI kernel.

Environment variables
---------------------
``SOVEREIGN_FALLBACK_ENABLED``  – set to ``"0"`` to disable fallback entirely
                                   (useful for local dev; defaults to enabled).
``SOVEREIGN_TIMEOUT_MS``        – per-call timeout in milliseconds (default 2000).
``SOVEREIGN_CACHE_SIZE``        – max LRU cache entries (default 64).
``SOVEREIGN_OLLAMA_MODEL``      – Ollama model slug (default ``"tinyllama"``).
``SOVEREIGN_OLLAMA_URL``        – Ollama base URL (default ``"http://localhost:11434"``).
"""

from __future__ import annotations

import asyncio
import collections
import logging
import os
import time

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

FALLBACK_ENABLED: bool = os.getenv("SOVEREIGN_FALLBACK_ENABLED", "1") != "0"
TIMEOUT_MS: int = int(os.getenv("SOVEREIGN_TIMEOUT_MS", "2000"))
CACHE_SIZE: int = int(os.getenv("SOVEREIGN_CACHE_SIZE", "64"))
OLLAMA_MODEL: str = os.getenv("SOVEREIGN_OLLAMA_MODEL", "tinyllama")
OLLAMA_URL: str = os.getenv("SOVEREIGN_OLLAMA_URL", "http://localhost:11434")

# Sentinel returned when both cache and Ollama are unavailable.
_STABILITY_SENTINEL = (
    "[NODE STABILITY] Gemini is temporarily unreachable. "
    "Enki AI is operating in Sovereign Fallback mode. "
    "Please try again shortly."
)


# ---------------------------------------------------------------------------
# LRU response cache
# ---------------------------------------------------------------------------

class _LRUCache:
    """Simple thread-safe LRU cache backed by an OrderedDict."""

    def __init__(self, maxsize: int = 64) -> None:
        self._maxsize = maxsize
        self._store: collections.OrderedDict[str, str] = collections.OrderedDict()

    @staticmethod
    def _key(prompt: str) -> str:
        return prompt[:128]

    def get(self, prompt: str) -> str | None:
        key = self._key(prompt)
        if key in self._store:
            self._store.move_to_end(key)
            return self._store[key]
        return None

    def put(self, prompt: str, response: str) -> None:
        key = self._key(prompt)
        self._store[key] = response
        self._store.move_to_end(key)
        if len(self._store) > self._maxsize:
            self._store.popitem(last=False)


_cache = _LRUCache(maxsize=CACHE_SIZE)


# ---------------------------------------------------------------------------
# Ollama fallback
# ---------------------------------------------------------------------------

async def _call_ollama(prompt: str) -> str | None:
    """
    Send *prompt* to a local Ollama instance and return the generated text,
    or ``None`` if Ollama is unavailable or returns an error.
    """
    try:
        import aiohttp  # already in requirements.txt
    except ImportError:
        log.warning("[SOVEREIGN] aiohttp not available — Ollama fallback disabled.")
        return None

    url = f"{OLLAMA_URL}/api/generate"
    payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("response", "").strip() or None
                log.warning("[SOVEREIGN] Ollama returned HTTP %d.", resp.status)
    except Exception as exc:
        log.warning("[SOVEREIGN] Ollama unavailable: %s", exc)
    return None


# ---------------------------------------------------------------------------
# Main fallback entry-point
# ---------------------------------------------------------------------------

async def _sovereign_fallback(prompt: str, reason: str) -> str:
    """
    Activate Sovereign Fallback mode.  Priority order:
    1. LRU cache hit.
    2. Local Ollama/TinyLlama.
    3. Stability sentinel.
    """
    log.warning("[SOVEREIGN] Fallback activated — reason: %s", reason)

    cached = _cache.get(prompt)
    if cached:
        log.info("[SOVEREIGN] Cache hit — serving cached response.")
        return f"[CACHED] {cached}"

    ollama_reply = await _call_ollama(prompt)
    if ollama_reply:
        log.info("[SOVEREIGN] Served by local Ollama (%s).", OLLAMA_MODEL)
        return ollama_reply

    log.warning("[SOVEREIGN] All fallback sources exhausted — returning stability sentinel.")
    return _STABILITY_SENTINEL


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def generate(prompt: str, gemini_coroutine=None, **kwargs) -> str:
    """
    Generate a response for *prompt*.

    Parameters
    ----------
    prompt:
        The user prompt or instruction.
    gemini_coroutine:
        An awaitable produced by the Gemini client (e.g.
        ``client.aio.models.generate_content(...)``).  When ``None`` the
        wrapper skips the primary call and goes straight to fallback — useful
        for unit-testing the fallback logic in isolation.
    **kwargs:
        Passed through to *gemini_coroutine* if it is a callable factory.

    Returns
    -------
    str
        The generated text.  Never raises; always returns a string.
    """
    if not FALLBACK_ENABLED or gemini_coroutine is None:
        if gemini_coroutine is None:
            return await _sovereign_fallback(prompt, "no Gemini coroutine provided")
        # Fallback disabled — call Gemini directly without timeout guard.
        try:
            result = await gemini_coroutine
            text = _extract_text(result)
            _cache.put(prompt, text)
            return text
        except Exception as exc:
            log.error("[SOVEREIGN] Gemini call failed (fallback disabled): %s", exc)
            raise

    # ------------------------------------------------------------------
    # Primary path: Gemini with timeout + 5xx detection
    # ------------------------------------------------------------------
    start_ns = time.monotonic_ns()
    timeout_s = TIMEOUT_MS / 1000.0

    try:
        result = await asyncio.wait_for(gemini_coroutine, timeout=timeout_s)
    except asyncio.TimeoutError:
        elapsed_ms = (time.monotonic_ns() - start_ns) // 1_000_000
        return await _sovereign_fallback(
            prompt, f"latency exceeded {elapsed_ms} ms (limit {TIMEOUT_MS} ms)"
        )
    except Exception as exc:
        # Detect HTTP 5xx codes surfaced via exception message or attributes.
        status_code = _extract_http_status(exc)
        if status_code is not None and 500 <= status_code < 600:
            return await _sovereign_fallback(
                prompt, f"Gemini returned HTTP {status_code}"
            )
        log.error("[SOVEREIGN] Gemini call raised unexpected error: %s", exc)
        raise

    text = _extract_text(result)
    _cache.put(prompt, text)
    return text


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_text(result) -> str:
    """
    Pull the text content out of a Gemini response object.

    Handles both ``google.genai`` and plain string responses so the wrapper
    can be used in tests without the SDK installed.
    """
    if isinstance(result, str):
        return result
    # google.genai GenerateContentResponse
    try:
        return result.text or ""
    except AttributeError:
        pass
    # Fallback: stringify
    return str(result)


def _extract_http_status(exc: Exception) -> int | None:
    """
    Attempt to extract an HTTP status code from an exception.

    Checks common attributes used by aiohttp, httpx, requests, and the
    google-genai SDK.
    """
    for attr in ("status", "status_code", "code"):
        val = getattr(exc, attr, None)
        if isinstance(val, int):
            return val
    # Some SDKs embed the code inside a nested response object.
    response = getattr(exc, "response", None)
    if response is not None:
        for attr in ("status", "status_code"):
            val = getattr(response, attr, None)
            if isinstance(val, int):
                return val
    return None
