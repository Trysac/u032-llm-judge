"""Strict parsing and validation of judge replies (internal module)."""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from .rubric import Rubric

MAX_REPLY_CHARS = 100_000
MAX_JSON_POSITIONS = 100
MAX_RATIONALE_CHARS = 2000
MAX_PROBLEMS = 20
_MAX_KEY_CHARS = 50
_UNEXPECTED_EVENT_PATH = "scores.<unexpected>"


class _DuplicateKeyError(ValueError):
    """Raised by the JSON object hook when an object repeats a key."""


def _reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKeyError("duplicate key")
        result[key] = value
    return result


_DECODER = json.JSONDecoder(object_pairs_hook=_reject_duplicates)


@dataclass(frozen=True)
class Problem:
    """One validation problem.

    ``path`` is shown to the judge; ``event_path`` is the redacted variant used in events.
    """

    path: str
    message: str
    event_path: str


@dataclass(frozen=True)
class Parsed:
    """A validated reply."""

    scores: dict[str, int]
    rationale: str


def _problem(path: str, message: str) -> Problem:
    return Problem(path, message, path)


def _safe_key(key: str) -> str:
    clipped = key[:_MAX_KEY_CHARS]
    return "".join(ch if ch.isprintable() else "?" for ch in clipped)


def _decode_at(reply: str, position: int) -> tuple[dict[str, Any] | None, bool]:
    try:
        value, _ = _DECODER.raw_decode(reply, position)
    except _DuplicateKeyError:
        return None, True
    except (ValueError, RecursionError):
        return None, False
    return (value if isinstance(value, dict) else None), False


def _decode_first_object(reply: str) -> tuple[dict[str, Any] | None, bool]:
    duplicate_seen = False
    position = reply.find("{")
    tried = 0
    while position != -1 and tried < MAX_JSON_POSITIONS:
        tried += 1
        obj, duplicate = _decode_at(reply, position)
        duplicate_seen = duplicate_seen or duplicate
        if obj is not None:
            return obj, duplicate_seen
        position = reply.find("{", position + 1)
    return None, duplicate_seen


def _check_scores(raw: dict[str, Any], rubric: Rubric) -> tuple[dict[str, int], list[Problem]]:
    scores: dict[str, int] = {}
    problems: list[Problem] = []
    for criterion in rubric.criteria:
        path = f"scores.{criterion.name}"
        if criterion.name not in raw:
            problems.append(_problem(path, "missing"))
            continue
        value = raw[criterion.name]
        low, high = criterion.scale_min, criterion.scale_max
        if type(value) is not int:
            problems.append(_problem(path, "must be an integer"))
        elif not low <= value <= high:
            problems.append(_problem(path, f"must be between {low} and {high}"))
        else:
            scores[criterion.name] = value
    known = {criterion.name for criterion in rubric.criteria}
    for key in raw:
        if key not in known:
            path = f"scores.{_safe_key(key)}"
            problems.append(Problem(path, "unexpected criterion", _UNEXPECTED_EVENT_PATH))
    return scores, problems


def _ordered(problems: list[Problem]) -> list[Problem]:
    return sorted(problems, key=lambda p: (p.path, p.message))[:MAX_PROBLEMS]


def validate(obj: dict[str, Any], rubric: Rubric) -> tuple[Parsed | None, list[Problem]]:
    """Validate a decoded object against ``rubric``."""
    problems: list[Problem] = []
    scores: dict[str, int] = {}
    if "scores" not in obj:
        problems.append(_problem("scores", "missing"))
    elif not isinstance(obj["scores"], dict):
        problems.append(_problem("scores", "must be an object"))
    else:
        scores, found = _check_scores(obj["scores"], rubric)
        problems.extend(found)
    rationale = ""
    if "rationale" not in obj:
        problems.append(_problem("rationale", "missing"))
    elif not isinstance(obj["rationale"], str):
        problems.append(_problem("rationale", "must be a string"))
    else:
        rationale = obj["rationale"][:MAX_RATIONALE_CHARS]
    if problems:
        return None, _ordered(problems)
    return Parsed(scores, rationale), []


def parse_reply(reply: str, rubric: Rubric) -> tuple[Parsed | None, list[Problem]]:
    """Parse and validate a raw judge reply.

    Returns the parsed result, or ``None`` with up to 20 problems sorted by path.
    """
    if len(reply) > MAX_REPLY_CHARS:
        return None, [_problem("$", "missing")]
    obj, duplicate_seen = _decode_first_object(reply)
    if obj is None:
        return None, [_problem("$", "duplicate key" if duplicate_seen else "missing")]
    return validate(obj, rubric)


def format_reask(problems: Sequence[Problem]) -> str:
    """Build the user message that asks the judge to repair its reply."""
    lines = "\n".join(f"- {p.path}: {p.message}" for p in problems)
    return "Your previous reply was invalid:\n" + lines
