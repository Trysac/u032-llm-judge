"""Agreement between judge scores and human scores."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType

from .errors import JudgeError
from .models import Judgement
from .rubric import Rubric

__all__ = ["MAX_PAIRS", "Agreement", "CalibrationReport", "calibrate"]

MAX_PAIRS = 100_000


def _invalid(message: str) -> JudgeError:
    return JudgeError("calibration_invalid", message)


@dataclass(frozen=True)
class Agreement:
    """Agreement statistics for one criterion.

    ``kappa`` is the quadratic weighted Cohen kappa, or ``None`` when the expected
    disagreement is 0 (for example when every score is the same value).
    """

    exact: float
    within_one: float
    kappa: float | None
    n: int


@dataclass(frozen=True)
class CalibrationReport:
    """Per-criterion agreement, in rubric order."""

    per_criterion: Mapping[str, Agreement]


def _check_scores(index: int, label: str, scores: object, rubric: Rubric) -> None:
    if not isinstance(scores, Mapping):
        raise _invalid(f"pair {index}: {label} scores must be a mapping")
    if set(scores) != {criterion.name for criterion in rubric.criteria}:
        raise _invalid(f"pair {index}: {label} scores do not match the rubric criteria")
    for criterion in rubric.criteria:
        value = scores[criterion.name]
        if type(value) is not int or not criterion.scale_min <= value <= criterion.scale_max:
            low, high = criterion.scale_min, criterion.scale_max
            raise _invalid(
                f"pair {index}: {label} score for {criterion.name!r} "
                f"must be an integer between {low} and {high}"
            )


def _quadratic_weighted_kappa(judged: Sequence[int], human: Sequence[int]) -> float | None:
    """Return 1 - sum(w*O)/sum(w*E) with w_ij = (i-j)^2/(k-1)^2.

    The ``(k-1)^2`` factor cancels in the ratio, so integer arithmetic is used. With
    ``n`` pairs, ``sum(w*O)`` is proportional to ``sum(d^2)/n`` and ``sum(w*E)`` to
    ``sum((i-j)^2 * a_i * b_j)/n^2`` where ``a`` and ``b`` are the marginal counts.
    """
    n = len(judged)
    judged_counts = Counter(judged)
    human_counts = Counter(human)
    expected = 0
    for i, x in judged_counts.items():
        for j, y in human_counts.items():
            expected += (i - j) ** 2 * x * y
    if expected == 0:
        return None
    observed = sum((a - b) ** 2 for a, b in zip(judged, human, strict=True))
    return 1.0 - n * observed / expected


def _agreement(judged: Sequence[int], human: Sequence[int]) -> Agreement:
    n = len(judged)
    pairs = list(zip(judged, human, strict=True))
    exact = sum(1 for a, b in pairs if a == b) / n
    within_one = sum(1 for a, b in pairs if abs(a - b) <= 1) / n
    return Agreement(
        exact=exact,
        within_one=within_one,
        kappa=_quadratic_weighted_kappa(judged, human),
        n=n,
    )


def calibrate(
    pairs: Sequence[tuple[Judgement, Mapping[str, int]]],
    rubric: Rubric,
) -> CalibrationReport:
    """Compare judgements with human scores per criterion.

    Each pair is ``(judgement, human_scores)``. Human scores must be ints (not bools)
    within the criterion's scale and cover exactly the rubric's criteria.

    Raises:
        JudgeError: code ``calibration_invalid`` for empty or oversized input, mismatched
            criteria or an invalid score.
    """
    if not isinstance(rubric, Rubric):
        raise _invalid("rubric must be a Rubric")
    if not isinstance(pairs, Sequence) or isinstance(pairs, str | bytes):
        raise _invalid("pairs must be a sequence")
    if len(pairs) == 0:
        raise _invalid("pairs must not be empty")
    if len(pairs) > MAX_PAIRS:
        raise _invalid(f"pairs exceed the limit of {MAX_PAIRS}")
    judged: dict[str, list[int]] = {c.name: [] for c in rubric.criteria}
    humans: dict[str, list[int]] = {c.name: [] for c in rubric.criteria}
    for index, pair in enumerate(pairs):
        if not isinstance(pair, tuple) or len(pair) != 2:
            raise _invalid(f"pair {index} must be a (judgement, human scores) tuple")
        judgement, human = pair
        if not isinstance(judgement, Judgement):
            raise _invalid(f"pair {index}: first item must be a Judgement")
        _check_scores(index, "judge", judgement.scores, rubric)
        _check_scores(index, "human", human, rubric)
        for name in judged:
            judged[name].append(judgement.scores[name])
            humans[name].append(human[name])
    report = {name: _agreement(judged[name], humans[name]) for name in judged}
    return CalibrationReport(per_criterion=MappingProxyType(report))
