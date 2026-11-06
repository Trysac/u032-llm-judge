"""Result and event value objects."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

__all__ = ["JudgeEvent", "Judgement"]


@dataclass(frozen=True)
class Judgement:
    """A validated judgement.

    Attributes:
        scores: Integer score per criterion name, in rubric order.
        total: Weighted mean of the scores.
        rationale: Judge rationale cut to 2000 characters.
        rubric_hash: ``Rubric.version_hash`` of the rubric used.
        attempts: Number of port calls that were needed (1 means no re-ask).
    """

    scores: Mapping[str, int]
    total: float
    rationale: str
    rubric_hash: str
    attempts: int


@dataclass(frozen=True)
class JudgeEvent:
    """Observability event emitted after every attempt.

    It never carries candidate, reference or reply text, only error paths.
    """

    attempt: int
    ok: bool
    error_paths: tuple[str, ...]
