# Testing

## Running

```sh
uv run pytest --cov=llm_judge   # tests with coverage report
uv run python scripts/check.py  # every gate, as CI runs it
```

`scripts/check.py` and the `tests/` directory are referenced by the project configuration, but they were not part of the source tree supplied for this documentation. The test files are therefore not listed here, and this document does not claim any specific test file exists.

## Policy

- Branch coverage of `src/llm_judge` must stay at or above 80 %, as the project gate requires.
- Tests should exercise the public API (`import llm_judge`) and check return values, raised exceptions and their codes and messages.
- Tests should be deterministic: no network, no wall clock, no dependence on test order. `RecordedLLM` and `FakeLLM` are the intended doubles for the port.

## Acceptance checks defined by the specification

These are the behaviours the implementation is meant to satisfy and that tests should cover:

- `Rubric.from_dict()` rejects empty criteria, duplicate names, `scale_min >= scale_max` and weights that are 0, negative, NaN or infinite.
- `judge()` returns the expected total and attempt count for a valid reply, also when the JSON is inside a code fence or after prose.
- A re-ask after an invalid reply carries the exact problem lines.
- Replies that stay invalid raise `parse_failed`, including duplicate keys, boolean or float scores, extra criteria and deeply nested input.
- Candidate and reference closing tags are escaped case-insensitively.
- `calibrate()` produces the expected exact, within-one and kappa values, returns `None` kappa when expected disagreement is 0, and rejects invalid pairs.
- Oversized candidates raise `candidate_too_large` before any port call, and port exceptions propagate unchanged.

## Layout

The intended layout is `tests/test_<module>.py` mirroring each module, with shared fixtures in `tests/conftest.py`. The supplied tree does not include these files.