"""OpenAI provider (chat completions + tool calling)."""
from __future__ import annotations

import json
import logging
from typing import AsyncIterator

from openai import AsyncOpenAI

from enki.core.config import Settings
from enki.providers.base import BaseProvider, CompletionResponse, ToolCall

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseProvider):
    def __init__(self, cfg: Settings) -> None:
        self._cfg = cfg
        self._client = AsyncOpenAI(api_key=cfg.openai_api_key or None)

    async def complete(
        self,
        messages: list[dict],
        *,
        tools: list[dict] | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> CompletionResponse:
        kwargs: dict = {
            "model": self._cfg.openai_model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if tools:
            kwargs["tools"] = [{"type": "function", "function": t} for t in tools]
            kwargs["tool_choice"] = "auto"

        response = await self._client.chat.completions.create(**kwargs)
        choice = response.choices[0]
        msg = choice.message

        tool_calls: list[ToolCall] = []
        if msg.tool_calls:
            for tc in msg.tool_calls:
                tool_calls.append(
                    ToolCall(
                        name=tc.function.name,
                        arguments=json.loads(tc.function.arguments),
                    )
                )

        return CompletionResponse(
            content=msg.content or "",
            tool_calls=tool_calls,
            input_tokens=response.usage.prompt_tokens if response.usage else 0,
            output_tokens=response.usage.completion_tokens if response.usage else 0,
        )

    async def stream(
        self,
        messages: list[dict],
        *,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        stream = await self._client.chat.completions.create(
            model=self._cfg.openai_model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
