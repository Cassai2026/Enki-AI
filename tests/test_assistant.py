"""Unit tests for the Assistant orchestrator (provider mocked)."""
from __future__ import annotations

import pytest

from enki.core.assistant import Assistant
from enki.providers.base import BaseProvider, CompletionResponse, ToolCall
from enki.plugins.calculator import CalculatorPlugin


class _FakeProvider(BaseProvider):
    """A deterministic provider stub for testing."""

    def __init__(self, reply: str = "Hello!", tool_calls: list[ToolCall] | None = None) -> None:
        self._reply = reply
        self._tool_calls = tool_calls or []
        self._call_count = 0

    async def complete(self, messages, *, tools=None, max_tokens=4096, temperature=0.7):
        self._call_count += 1
        # Only return tool calls on the first turn; subsequent turns return text.
        tc = self._tool_calls if self._call_count == 1 else []
        return CompletionResponse(content=self._reply, tool_calls=tc)

    async def stream(self, messages, *, max_tokens=4096, temperature=0.7):
        for word in self._reply.split():
            yield word + " "


@pytest.mark.asyncio
async def test_simple_chat():
    provider = _FakeProvider(reply="42")
    assistant = Assistant(provider=provider)
    reply = await assistant.chat("What is 6 * 7?")
    assert reply == "42"


@pytest.mark.asyncio
async def test_memory_grows_with_turns():
    provider = _FakeProvider(reply="OK")
    assistant = Assistant(provider=provider)
    await assistant.chat("First message")
    await assistant.chat("Second message")
    # system + 2 user + 2 assistant = 4 non-system turns
    assert len(assistant._memory) == 4


@pytest.mark.asyncio
async def test_reset_clears_memory():
    provider = _FakeProvider(reply="OK")
    assistant = Assistant(provider=provider)
    await assistant.chat("Hi")
    assistant.reset()
    assert len(assistant._memory) == 0


@pytest.mark.asyncio
async def test_streaming():
    provider = _FakeProvider(reply="hello world foo")
    assistant = Assistant(provider=provider)
    chunks = []
    async for chunk in assistant.stream("test"):
        chunks.append(chunk)
    assert "".join(chunks).strip() == "hello world foo"


@pytest.mark.asyncio
async def test_plugin_dispatch():
    """Assistant should call the calculator plugin and return its result."""
    tool_call = ToolCall(name="calculator", arguments={"expression": "6 * 7"})
    provider = _FakeProvider(reply="The answer is 42", tool_calls=[tool_call])
    assistant = Assistant(provider=provider, plugins=[CalculatorPlugin()])
    reply = await assistant.chat("What is 6 * 7?")
    assert reply == "The answer is 42"
    # Memory should include a tool turn.
    roles = [m.role for m in assistant._memory.messages()]
    assert "tool" in roles


@pytest.mark.asyncio
async def test_unknown_plugin_graceful_error():
    tool_call = ToolCall(name="nonexistent_tool", arguments={})
    provider = _FakeProvider(reply="fallback", tool_calls=[tool_call])
    assistant = Assistant(provider=provider)
    # Should not raise, should return the fallback reply.
    reply = await assistant.chat("trigger unknown tool")
    assert reply == "fallback"


def test_register_plugin():
    assistant = Assistant(provider=_FakeProvider())
    calc = CalculatorPlugin()
    assistant.register_plugin(calc)
    assert any(p.name == "calculator" for p in assistant.plugins)
