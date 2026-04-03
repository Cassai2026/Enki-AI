"""Base plugin interface."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PluginResult:
    success: bool
    output: Any


class Plugin(ABC):
    """A capability that the assistant can invoke as a tool."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique snake_case identifier used as the tool name."""

    @property
    @abstractmethod
    def description(self) -> str:
        """One-sentence description exposed to the LLM."""

    @abstractmethod
    def parameters(self) -> dict:
        """JSON Schema 'properties' dict describing the tool's parameters."""

    @property
    def required_parameters(self) -> list[str]:
        """Names of required parameters (default: all)."""
        return list(self.parameters().keys())

    def schema(self) -> dict:
        """Full OpenAI-compatible function schema."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": self.parameters(),
                "required": self.required_parameters,
            },
        }

    @abstractmethod
    async def run(self, **kwargs: Any) -> PluginResult:
        """Execute the plugin and return a result."""
