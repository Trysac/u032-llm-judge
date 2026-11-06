# Architecture

## Purpose

`trysac-llm-judge` is a small, dependency-free Python library (import name `llm_judge`) for LLM-as-judge scoring with versioned rubrics, strict per-criterion score parsing with one bounded re-ask, and quadratic weighted kappa calibration against human scores.

## Shape

```text
caller code --> llm_judge (public API in __init__.py)
                    |
                    +-- rubric.py      Criterion, Rubric, version_hash
                    +-- judging.py     prompt building, judge() loop
                    +-- parsing.py     strict JSON decoding and validation (internal)
                    +-- calibration.py calibrate(), agreement and kappa
                    +-- ports.py       LLMPort protocol, RecordedLLM, FakeLLM
                    +-- models.py      Judgement, JudgeEvent
                    +-- errors.py      JudgeError and error codes
```

- **Public API**: the names listed in `__all__` of `src/llm_judge/__init__.py`. Anything else is internal.
- **Provider access**: none. The caller supplies an object that implements `LLMPort.complete`.
- **Errors**: domain failures raise `JudgeError` with a stable code. Argument type and range problems in `judge()` raise `TypeError` or `ValueError`.
- **Side effects**: the only one is a `logging` debug and warning record through the `llm_judge` logger, which has a `NullHandler`. The library does not print and does not touch the file system or network.

## Judge flow

1. Validate the rubric, the argument types and the numeric limits. Reject oversized candidate or reference text before calling the port.
2. Build a system message listing the criteria and a user message with the escaped candidate and optional reference.
3. Call the port. Parse the reply: decode the first JSON object that is valid, reject duplicate keys, and validate every criterion.
4. On an invalid reply, if repairs remain, append the assistant reply and a re-ask message that lists the problems, then call the port again.
5. Return a `Judgement`, or raise `JudgeError` with code `parse_failed`.

## Calibration flow

`calibrate()` checks every pair, then computes exact agreement, agreement within one point and quadratic weighted kappa per criterion, in rubric order.

## Decisions

No ADR directory is part of the supplied source tree. Design choices are recorded in the code docstrings and in this document.