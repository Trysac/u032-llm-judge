"""The LLM port and deterministic test doubles."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Literal, Protocol, TypedDict

__all__ = ["FakeLLM", "LLMPort", "Message", "RecordedLLM", "RecordingExhaustedError"]


class Message(TypedDict):
    """One chat message."""

    role: Literal["system", "user", "assistant"]
    content: str


class LLMPort(Protocol):
    """Minimal chat-completion port; provider clients live outside this library."""

    def complete(self, messages: Sequence[Message], *, max_tokens: int) -> str:
        """Return the assistant reply for ``messages``."""
        ...


class RecordingExhaustedError(Exception):
    """Raised by :class:`RecordedLLM` when all recorded replies were served."""


class RecordedLLM:
    """Port that returns pre-recorded replies in order and remembers every call."""

    def __init__(self, replies: Sequence[str]) -> None:
        self._replies = tuple(replies)
        self.calls: list[list[Message]] = []

    def complete(self, messages: Sequence[Message], *, max_tokens: int) -> str:
        """Return the next recorded reply or raise :class:`RecordingExhaustedError`."""
        index = len(self.calls)
        if index >= len(self._replies):
            raise RecordingExhaustedError("no recorded replies left")
        self.calls.append([Message(role=m["role"], content=m["content"]) for m in messages])
        return self._replies[index]


class FakeLLM:
    """Port whose reply is computed by a function of the messages."""

    def __init__(self, fn: Callable[[Sequence[Message]], str]) -> None:
        self._fn = fn
        self.call_count = 0

    def complete(self, messages: Sequence[Message], *, max_tokens: int) -> str:
        """Return ``fn(messages)``."""
        self.call_count += 1
        return self._fn(messages)
