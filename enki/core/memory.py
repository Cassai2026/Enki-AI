"""Conversation memory with optional sliding-window truncation."""
from __future__ import annotations

from collections import deque
from typing import Deque, Iterator, Literal

from pydantic import BaseModel


Role = Literal["system", "user", "assistant", "tool"]


class Message(BaseModel):
    role: Role
    content: str
    name: str | None = None  # used for tool/function roles


class ConversationMemory:
    """Stores conversation turns and enforces a sliding window."""

    def __init__(self, window: int = 20) -> None:
        """
        Args:
            window: Maximum number of *non-system* messages to keep.
                    0 means unlimited.
        """
        self._window = window
        self._system: Message | None = None
        self._turns: Deque[Message] = deque()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_system(self, content: str) -> None:
        self._system = Message(role="system", content=content)

    def add(self, role: Role, content: str, name: str | None = None) -> None:
        self._turns.append(Message(role=role, content=content, name=name))
        self._maybe_trim()

    def messages(self) -> list[Message]:
        """Return the full message list (system + turns)."""
        msgs: list[Message] = []
        if self._system:
            msgs.append(self._system)
        msgs.extend(self._turns)
        return msgs

    def as_dicts(self) -> list[dict]:
        """Return messages as plain dicts suitable for LLM APIs."""
        result = []
        for m in self.messages():
            d: dict = {"role": m.role, "content": m.content}
            if m.name:
                d["name"] = m.name
            result.append(d)
        return result

    def clear(self) -> None:
        self._turns.clear()

    def __len__(self) -> int:
        return len(self._turns)

    def __iter__(self) -> Iterator[Message]:
        return iter(self.messages())

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _maybe_trim(self) -> None:
        if self._window > 0:
            while len(self._turns) > self._window:
                self._turns.popleft()
