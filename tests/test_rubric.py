"""Tests for Criterion and Rubric."""

import copy
import hashlib
import json
from dataclasses import asdict

import pytest

from llm_judge import Criterion, JudgeError, Rubric


def _data() -> dict:
    return {
        "name": "qa",
        "version": "1",
        "criteria": [
            {"name": "clarity", "description": "Is it clear?"},
            {"name": "accuracy", "description": "Is it correct?", "weight": 3.0},
        ],
    }


def _assert_invalid(data: object) -> None:
    with pytest.raises(JudgeError) as info:
        Rubric.from_dict(data)  # type: ignore[arg-type]
    assert info.value.code == "rubric_invalid"


def test_from_dict_builds_rubric() -> None:
    rubric = Rubric.from_dict(_data())
    assert rubric.name == "qa"
    assert [c.name for c in rubric.criteria] == ["clarity", "accuracy"]
    assert rubric.criteria[0].scale_min == 1
    assert rubric.criteria[0].scale_max == 5
    assert rubric.criteria[1].weight == 3.0


def test_empty_criteria() -> None:
    data = _data()
    data["criteria"] = []
    _assert_invalid(data)


def test_duplicate_names() -> None:
    data = _data()
    data["criteria"][1]["name"] = "clarity"
    _assert_invalid(data)


@pytest.mark.parametrize("scale", [(5, 5), (6, 5), (1, 1)])
def test_scale_min_must_be_below_scale_max(scale: tuple[int, int]) -> None:
    data = _data()
    data["criteria"][0]["scale_min"] = scale[0]
    data["criteria"][0]["scale_max"] = scale[1]
    _assert_invalid(data)


@pytest.mark.parametrize("weight", [0, -1.0, float("nan"), float("inf")])
def test_weight_must_be_finite_and_positive(weight: float) -> None:
    data = _data()
    data["criteria"][0]["weight"] = weight
    _assert_invalid(data)


@pytest.mark.parametrize("weight", [True, "2", None, 10**400])
def test_weight_must_be_a_number(weight: object) -> None:
    data = _data()
    data["criteria"][0]["weight"] = weight
    _assert_invalid(data)


def test_integer_weight_is_stored_as_float() -> None:
    criterion = Criterion("a", "d", weight=1)
    assert isinstance(criterion.weight, float)
    left = Rubric("r", "1", (criterion,))
    right = Rubric("r", "1", (Criterion("a", "d", weight=1.0),))
    assert left.version_hash == right.version_hash


def test_version_hash_equal_for_equal_content() -> None:
    assert Rubric.from_dict(_data()).version_hash == Rubric.from_dict(_data()).version_hash


def test_version_hash_matches_canonical_form() -> None:
    rubric = Rubric.from_dict(_data())
    canonical = json.dumps(
        asdict(rubric), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    expected = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12]
    assert rubric.version_hash == expected
    assert len(expected) == 12


def test_version_hash_changes_with_any_field() -> None:
    mutators = [
        lambda d: d.update(name="other"),
        lambda d: d.update(version="2"),
        lambda d: d["criteria"][0].update(name="clarity2"),
        lambda d: d["criteria"][0].update(description="Another text"),
        lambda d: d["criteria"][0].update(scale_min=0),
        lambda d: d["criteria"][0].update(scale_max=10),
        lambda d: d["criteria"][0].update(weight=2.0),
        lambda d: d["criteria"].reverse(),
    ]
    base = Rubric.from_dict(_data()).version_hash
    hashes = set()
    for mutate in mutators:
        data = copy.deepcopy(_data())
        mutate(data)
        hashes.add(Rubric.from_dict(data).version_hash)
    assert base not in hashes
    assert len(hashes) == len(mutators)


def test_non_ascii_names_hash() -> None:
    rubric = Rubric("r", "1", (Criterion("cl\u00e4rit\u00e9", "d"),))
    assert len(rubric.version_hash) == 12


def test_list_criteria_become_tuple() -> None:
    rubric = Rubric("r", "1", [Criterion("a", "d")])  # type: ignore[arg-type]
    assert isinstance(rubric.criteria, tuple)


@pytest.mark.parametrize(
    "data",
    [
        "not a mapping",
        {"name": "qa", "version": "1"},
        {"name": "qa", "version": "1", "criteria": "abc"},
        {"name": "qa", "version": "1", "criteria": ["abc"]},
        {"name": "qa", "version": "1", "criteria": [{"name": "a"}]},
        {"name": "qa", "version": "1", "criteria": [{"name": "a", "description": "d", "x": 1}]},
        {"name": "qa", "version": "1", "criteria": [{"name": "a", "description": "d"}], "x": 1},
        {"name": "", "version": "1", "criteria": [{"name": "a", "description": "d"}]},
        {"name": "qa", "version": 1, "criteria": [{"name": "a", "description": "d"}]},
    ],
)
def test_malformed_data(data: object) -> None:
    _assert_invalid(data)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"name": ""},
        {"name": "   "},
        {"name": "a\nb"},
        {"name": "x" * 101},
        {"name": 5},
        {"description": ""},
        {"description": "d" * 2001},
        {"description": 5},
        {"scale_min": True},
        {"scale_max": 5.0},
        {"scale_min": 0, "scale_max": 101},
    ],
)
def test_invalid_criterion_fields(kwargs: dict) -> None:
    fields = {"name": "a", "description": "d"}
    fields.update(kwargs)
    with pytest.raises(JudgeError) as info:
        Criterion(**fields)
    assert info.value.code == "rubric_invalid"


def test_scale_span_limit_is_inclusive() -> None:
    assert Criterion("a", "d", scale_min=0, scale_max=100).scale_max == 100


def test_too_many_criteria() -> None:
    criteria = [{"name": f"c{i}", "description": "d"} for i in range(51)]
    _assert_invalid({"name": "qa", "version": "1", "criteria": criteria})
    with pytest.raises(JudgeError):
        Rubric("qa", "1", tuple(Criterion(f"c{i}", "d") for i in range(51)))


def test_rubric_rejects_non_criterion_items() -> None:
    with pytest.raises(JudgeError):
        Rubric("qa", "1", ("x",))  # type: ignore[arg-type]
    with pytest.raises(JudgeError):
        Rubric("qa", "1", "x")  # type: ignore[arg-type]


def test_error_message_is_short() -> None:
    with pytest.raises(JudgeError) as info:
        Criterion("x" * 5000, "d")
    assert len(info.value.message) <= 200
    assert "x" * 300 not in str(info.value)
