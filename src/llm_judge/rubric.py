"""Versioned rubrics expressed as hashable data."""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from typing import Any

from .errors import JudgeError

__all__ = [
    "MAX_CRITERIA",
    "MAX_DESCRIPTION_CHARS",
    "MAX_NAME_CHARS",
    "MAX_SCALE_SPAN",
    "Criterion",
    "Rubric",
]

MAX_CRITERIA = 50
MAX_NAME_CHARS = 100
MAX_DESCRIPTION_CHARS = 2000
MAX_SCALE_SPAN = 100

_CRITERION_KEYS = frozenset({"name", "description", "scale_min", "scale_max", "weight"})
_RUBRIC_KEYS = frozenset({"name", "version", "criteria"})


def _invalid(message: str) -> JudgeError:
    return JudgeError("rubric_invalid", message)


def _check_label(what: str, value: object) -> None:
    if (
        not isinstance(value, str)
        or not value.strip()
        or len(value) > MAX_NAME_CHARS
        or not value.isprintable()
    ):
        raise _invalid(f"{what} must be a printable string of 1-{MAX_NAME_CHARS} characters")


@dataclass(frozen=True)
class Criterion:
    """One scored dimension of a rubric.

    ``weight`` must be finite and greater than 0; it is stored as a float so equal
    content always hashes equally.
    """

    name: str
    description: str
    scale_min: int = 1
    scale_max: int = 5
    weight: float = 1.0

    def __post_init__(self) -> None:
        _check_label("criterion name", self.name)
        description = self.description
        if (
            not isinstance(description, str)
            or not description.strip()
            or len(description) > MAX_DESCRIPTION_CHARS
        ):
            raise _invalid(f"criterion description must be 1-{MAX_DESCRIPTION_CHARS} characters")
        if type(self.scale_min) is not int or type(self.scale_max) is not int:
            raise _invalid("scale_min and scale_max must be integers")
        if self.scale_min >= self.scale_max:
            raise _invalid("scale_min must be less than scale_max")
        if self.scale_max - self.scale_min > MAX_SCALE_SPAN:
            raise _invalid(f"scale must span at most {MAX_SCALE_SPAN} steps")
        weight = self.weight
        if isinstance(weight, bool) or not isinstance(weight, int | float):
            raise _invalid("weight must be a number")
        try:
            value = float(weight)
        except OverflowError:
            raise _invalid("weight must be a finite number") from None
        if not math.isfinite(value) or value <= 0:
            raise _invalid("weight must be finite and greater than 0")
        object.__setattr__(self, "weight", value)


@dataclass(frozen=True)
class Rubric:
    """A named, versioned list of criteria."""

    name: str
    version: str
    criteria: tuple[Criterion, ...]

    def __post_init__(self) -> None:
        _check_label("rubric name", self.name)
        _check_label("rubric version", self.version)
        criteria = self.criteria
        if isinstance(criteria, list):
            criteria = tuple(criteria)
            object.__setattr__(self, "criteria", criteria)
        if not isinstance(criteria, tuple) or not criteria:
            raise _invalid("criteria must be a non-empty sequence")
        if len(criteria) > MAX_CRITERIA:
            raise _invalid(f"a rubric has at most {MAX_CRITERIA} criteria")
        names: set[str] = set()
        for criterion in criteria:
            if not isinstance(criterion, Criterion):
                raise _invalid("criteria must contain Criterion objects")
            if criterion.name in names:
                raise _invalid("criterion names must be unique")
            names.add(criterion.name)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Rubric:
        """Build a rubric from plain data, raising ``rubric_invalid`` on any problem."""
        if not isinstance(data, Mapping):
            raise _invalid("rubric data must be a mapping")
        if set(data) - _RUBRIC_KEYS:
            raise _invalid("unexpected rubric field")
        if _RUBRIC_KEYS - set(data):
            raise _invalid("rubric needs name, version and criteria")
        raw = data["criteria"]
        if not isinstance(raw, list | tuple):
            raise _invalid("criteria must be a list")
        if len(raw) > MAX_CRITERIA:
            raise _invalid(f"a rubric has at most {MAX_CRITERIA} criteria")
        criteria: list[Criterion] = []
        for item in raw:
            if not isinstance(item, Mapping):
                raise _invalid("each criterion must be a mapping")
            if set(item) - _CRITERION_KEYS:
                raise _invalid("unexpected criterion field")
            if not {"name", "description"} <= set(item):
                raise _invalid("criterion needs name and description")
            criteria.append(Criterion(**item))
        return cls(name=data["name"], version=data["version"], criteria=tuple(criteria))

    @property
    def version_hash(self) -> str:
        """First 12 hex characters of the SHA-256 of the canonical JSON form."""
        canonical = json.dumps(
            asdict(self),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        return hashlib.sha256(canonical.encode("utf-8", "surrogatepass")).hexdigest()[:12]
