"""Tests for the port test doubles."""

import pytest

from llm_judge import FakeLLM, RecordedLLM, RecordingExhaustedError

MESSAGES = [{"role": "user", "content": "hi"}]


def test_recorded_returns_replies_in_order_and_records_calls() -> None:
    llm = RecordedLLM(["a", "b"])
    assert llm.complete(MESSAGES, max_tokens=10) == "a"
    assert llm.complete(MESSAGES, max_tokens=10) == "b"
    assert llm.calls == [MESSAGES, MESSAGES]


def test_recorded_raises_when_exhausted() -> None:
    llm = RecordedLLM(["a"])
    llm.complete(MESSAGES, max_tokens=10)
    with pytest.raises(RecordingExhaustedError):
        llm.complete(MESSAGES, max_tokens=10)
    assert len(llm.calls) == 1


def test_recorded_copies_messages() -> None:
    messages = [{"role": "user", "content": "hi"}]
    llm = RecordedLLM(["a"])
    llm.complete(messages, max_tokens=10)
    messages[0]["content"] = "changed"
    assert llm.calls[0][0]["content"] == "hi"


def test_fake_computes_each_reply() -> None:
    llm = FakeLLM(lambda messages: str(len(messages)))
    assert llm.complete(MESSAGES, max_tokens=1) == "1"
    assert llm.complete(MESSAGES * 2, max_tokens=1) == "2"
    assert llm.call_count == 2
