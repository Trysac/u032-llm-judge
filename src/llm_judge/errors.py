"""Typed errors for the LLM judge library."""

from __future__ import annotations

from typing import Literal

__all__ = ["ErrorCode", "JudgeError"]

ErrorCode = Literal[
    "rubric_invalid",
    "parse_failed",
    "candidate_too_large",
    "calibration_invalid",
]

_MAX_TEXT_CHARS = 200


class JudgeError(Exception):
    """Base error of the library.

    Attributes:
        code: Stable machine-readable error code.
        message: Human-readable message, at most 200 characters, never containing a reply.
        raw: For ``parse_failed`` the last judge reply cut to 200 characters, else empty.
    """

    def __init__(self, code: ErrorCode, message: str, *, raw: str = "") -> None:
        text = message[:_MAX_TEXT_CHARS]
        super().__init__(text)
        self.code: ErrorCode = code
        self.message = text
        self.raw = raw[:_MAX_TEXT_CHARS]
