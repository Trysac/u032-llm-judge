"""Tests for calibrate()."""

import pytest

from llm_judge import Criterion, JudgeError, Judgement, Rubric, calibrate
from llm_judge.calibration import MAX_PAIRS

RUBRIC = Rubric("qa", "1", (Criterion("quality", "Overall quality"),))


def _judgement(score: int) -> Judgement:
    return Judgement({"quality": score}, float(score), "r", RUBRIC.version_hash, 1)


def _pairs(judged: list[int], human: list[int]) -> list:
    return [(_judgement(a), {"quality": b}) for a, b in zip(judged, human, strict=True)]


def _assert_invalid(pairs: object, rubric: object = RUBRIC) -> None:
    with pytest.raises(JudgeError) as info:
        calibrate(pairs, rubric)  # type: ignore[arg-type]
    assert info.value.code == "calibration_invalid"
    assert len(info.value.message) <= 200


def test_reference_example() -> None:
    report = calibrate(_pairs([1, 2, 3, 4, 5, 3, 2, 4], [1, 2, 4, 4, 5, 2, 2, 3]), RUBRIC)
    agreement = report.per_criterion["quality"]
    assert agreement.exact == 0.625
    assert agreement.within_one == 1.0
    assert agreement.kappa is not None
    assert abs(agreement.kappa - 0.88) < 1e-9
    assert agreement.n == 8


def test_perfect_agreement_has_kappa_one() -> None:
    agreement = calibrate(_pairs([1, 2, 3], [1, 2, 3]), RUBRIC).per_criterion["quality"]
    assert agreement.kappa == 1.0
    assert agreement.exact == 1.0


def test_chance_level_kappa_is_zero() -> None:
    agreement = calibrate(_pairs([3, 3, 3, 3], [1, 3, 5, 3]), RUBRIC).per_criterion["quality"]
    assert agreement.kappa == pytest.approx(0.0)
    assert agreement.within_one == 0.5


def test_opposite_scores_give_negative_kappa() -> None:
    agreement = calibrate(_pairs([1, 5], [5, 1]), RUBRIC).per_criterion["quality"]
    assert agreement.kappa is not None
    assert agreement.kappa < 0
    assert agreement.exact == 0.0
    assert agreement.within_one == 0.0


def test_kappa_none_when_every_score_is_the_same() -> None:
    agreement = calibrate(_pairs([3, 3, 3], [3, 3, 3]), RUBRIC).per_criterion["quality"]
    assert agreement.kappa is None
    assert agreement.exact == 1.0


def test_report_follows_rubric_order_with_two_criteria() -> None:
    rubric = Rubric("qa", "1", (Criterion("b", "d"), Criterion("a", "d")))
    judgement = Judgement({"b": 1, "a": 5}, 3.0, "r", rubric.version_hash, 1)
    report = calibrate([(judgement, {"a": 5, "b": 2})], rubric)
    assert list(report.per_criterion) == ["b", "a"]
    assert report.per_criterion["b"].within_one == 1.0
    assert report.per_criterion["a"].exact == 1.0


def test_empty_pairs() -> None:
    _assert_invalid([])


def test_too_many_pairs() -> None:
    _assert_invalid([(_judgement(1), {"quality": 1})] * (MAX_PAIRS + 1))


def test_mismatched_criteria() -> None:
    _assert_invalid([(_judgement(3), {"other": 3})])
    _assert_invalid([(_judgement(3), {"quality": 3, "extra": 1})])
    judgement = Judgement({"other": 3}, 3.0, "r", "h", 1)
    _assert_invalid([(judgement, {"quality": 3})])


@pytest.mark.parametrize("bad", [6, 0, 3.0, True, "3", None])
def test_invalid_human_score(bad: object) -> None:
    _assert_invalid([(_judgement(3), {"quality": bad})])


def test_invalid_judge_score() -> None:
    judgement = Judgement({"quality": 9}, 9.0, "r", "h", 1)
    _assert_invalid([(judgement, {"quality": 3})])


def test_malformed_pairs() -> None:
    _assert_invalid(["not a pair"])
    _assert_invalid([(_judgement(3),)])
    _assert_invalid([("judgement", {"quality": 3})])
    _assert_invalid([(_judgement(3), [3])])
    _assert_invalid([(Judgement([3], 3.0, "r", "h", 1), {"quality": 3})])  # type: ignore[arg-type]
    _assert_invalid("abc")
    _assert_invalid(iter([(_judgement(3), {"quality": 3})]))


def test_rubric_must_be_a_rubric() -> None:
    _assert_invalid(_pairs([1], [1]), rubric="rubric")
