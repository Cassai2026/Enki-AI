"""Central assistant orchestrator — wires together provider, memory, plugins."""
from __future__ import annotations

import json
import logging
from typing import AsyncIterator

from enki.core.config import Settings, settings as default_settings
from enki.core.memory import ConversationMemory
from enki.plugins.base import Plugin, PluginResult
from enki.providers.base import BaseProvider

logger = logging.getLogger(__name__)


class Assistant:
    """
    The main entry-point for Enki AI.

    Usage::

        assistant = Assistant()
        response = await assistant.chat("What is the speed of light?")
        print(response)
    """

    def __init__(
        self,
        provider: BaseProvider | None = None,
        plugins: list[Plugin] | None = None,
        cfg: Settings | None = None,
    ) -> None:
        self._cfg = cfg or default_settings
        self._provider = provider or self._build_provider()
        self._memory = ConversationMemory(window=self._cfg.memory_window)
        self._memory.set_system(self._cfg.system_prompt)
        self._plugins: dict[str, Plugin] = {}
        for p in plugins or []:
            self.register_plugin(p)

    # ------------------------------------------------------------------
    # Plugin management
    # ------------------------------------------------------------------

    def register_plugin(self, plugin: Plugin) -> None:
        self._plugins[plugin.name] = plugin
        logger.debug("Registered plugin: %s", plugin.name)

    @property
    def plugins(self) -> list[Plugin]:
        return list(self._plugins.values())

    # ------------------------------------------------------------------
    # Chat
    # ------------------------------------------------------------------

    async def chat(self, user_input: str) -> str:
        """Send a user message and return the assistant reply."""
        self._memory.add("user", user_input)

        tool_schemas = [p.schema() for p in self._plugins.values()]

        response = await self._provider.complete(
            messages=self._memory.as_dicts(),
            tools=tool_schemas if tool_schemas else None,
            max_tokens=self._cfg.max_tokens,
            temperature=self._cfg.temperature,
        )

        # If the provider wants to call a tool, handle it.
        while response.tool_calls:
            for tc in response.tool_calls:
                result = await self._dispatch_tool(tc.name, tc.arguments)
                self._memory.add(
                    "tool",
                    json.dumps(result.output),
                    name=tc.name,
                )

            # Ask the provider again with the tool results included.
            response = await self._provider.complete(
                messages=self._memory.as_dicts(),
                tools=tool_schemas if tool_schemas else None,
                max_tokens=self._cfg.max_tokens,
                temperature=self._cfg.temperature,
            )

        self._memory.add("assistant", response.content)
        return response.content

    async def stream(self, user_input: str) -> AsyncIterator[str]:
        """Stream the assistant reply token by token."""
        self._memory.add("user", user_input)

        full_content = []
        async for chunk in self._provider.stream(
            messages=self._memory.as_dicts(),
            max_tokens=self._cfg.max_tokens,
            temperature=self._cfg.temperature,
        ):
            full_content.append(chunk)
            yield chunk

        self._memory.add("assistant", "".join(full_content))

    def reset(self) -> None:
        """Clear conversation history."""
        self._memory.clear()

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    async def _dispatch_tool(self, name: str, arguments: dict) -> PluginResult:
        plugin = self._plugins.get(name)
        if plugin is None:
            return PluginResult(success=False, output={"error": f"Unknown tool: {name}"})
        try:
            return await plugin.run(**arguments)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Plugin %s raised an error", name)
            return PluginResult(success=False, output={"error": str(exc)})

    def _build_provider(self) -> BaseProvider:
        if self._cfg.provider == "openai":
            from enki.providers.openai_provider import OpenAIProvider

            return OpenAIProvider(self._cfg)
        if self._cfg.provider == "anthropic":
            from enki.providers.anthropic_provider import AnthropicProvider

            return AnthropicProvider(self._cfg)
        raise ValueError(f"Unknown provider: {self._cfg.provider!r}")
