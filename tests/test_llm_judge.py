"""Smoke tests for the public package surface."""

import llm_judge


def test_version_has_three_parts() -> None:
    assert llm_judge.__version__.count(".") == 2


def test_all_exports_resolve() -> None:
    for name in llm_judge.__all__:
        assert hasattr(llm_judge, name)
