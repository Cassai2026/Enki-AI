"""Anthropic (Claude) provider."""
from __future__ import annotations

import logging
from typing import AsyncIterator

import anthropic

from enki.core.config import Settings
from enki.providers.base import BaseProvider, CompletionResponse, ToolCall

logger = logging.getLogger(__name__)

_TOOL_USE = "tool_use"


class AnthropicProvider(BaseProvider):
    def __init__(self, cfg: Settings) -> None:
        self._cfg = cfg
        self._client = anthropic.AsyncAnthropic(
            api_key=cfg.anthropic_api_key or None
        )

    async def complete(
        self,
        messages: list[dict],
        *,
        tools: list[dict] | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> CompletionResponse:
        # Anthropic separates the system prompt from the messages array.
        system_content = ""
        filtered: list[dict] = []
        for m in messages:
            if m["role"] == "system":
                system_content = m["content"]
            else:
                filtered.append(m)

        kwargs: dict = {
            "model": self._cfg.anthropic_model,
            "max_tokens": max_tokens,
            "messages": filtered,
        }
        if system_content:
            kwargs["system"] = system_content

        # Anthropic tool schema is identical to OpenAI's function schema.
        if tools:
            kwargs["tools"] = tools

        response = await self._client.messages.create(**kwargs)

        text_parts: list[str] = []
        tool_calls: list[ToolCall] = []
        for block in response.content:
            if block.type == "text":
                text_parts.append(block.text)
            elif block.type == _TOOL_USE:
                tool_calls.append(ToolCall(name=block.name, arguments=block.input))

        return CompletionResponse(
            content="".join(text_parts),
            tool_calls=tool_calls,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )

    async def stream(
        self,
        messages: list[dict],
        *,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        system_content = ""
        filtered: list[dict] = []
        for m in messages:
            if m["role"] == "system":
                system_content = m["content"]
            else:
                filtered.append(m)

        kwargs: dict = {
            "model": self._cfg.anthropic_model,
            "max_tokens": max_tokens,
            "messages": filtered,
        }
        if system_content:
            kwargs["system"] = system_content

        async with self._client.messages.stream(**kwargs) as stream:
            async for text in stream.text_stream:
                yield text
