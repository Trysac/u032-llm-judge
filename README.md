# llm-judge

[![PyPI version](https://img.shields.io/pypi/v/trysac-llm-judge)](https://pypi.org/project/trysac-llm-judge/)
[![License: MIT](https://img.shields.io/pypi/l/trysac-llm-judge)](LICENSE)
[![CI](https://github.com/Trysac/u032-llm-judge/actions/workflows/ci.yml/badge.svg)](https://github.com/Trysac/u032-llm-judge/actions/workflows/ci.yml)

LLM-as-judge with versioned rubrics, strict per-criterion score parsing with one bounded re-ask, and quadratic weighted kappa calibration

## Problem

LLM judge prompts written ad hoc drift between runs, return text that cannot be parsed, can be steered by instructions planted in the graded answer, and are rarely compared with human ratings. This library keeps rubrics as hashed, immutable data, parses judge replies strictly, places the candidate and reference inside escaped data tags, and measures agreement between judge scores and human scores with exact agreement, within-one agreement and quadratic weighted Cohen kappa.

## Install

```sh
pip install trysac-llm-judge
# or
uv add trysac-llm-judge
```

Requires Python 3.10 or newer. No runtime dependencies. The import name is `llm_judge`.

## Usage

```python
from llm_judge import Criterion, RecordedLLM, Rubric, judge

rubric = Rubric("qa", "1", (Criterion("clarity", "Is it clear?"),))
llm = RecordedLLM(['{"scores": {"clarity": 4}, "rationale": "Clear."}'])
result = judge(llm, rubric, "Paris is the capital of France.")
print(result.scores["clarity"], result.total, result.attempts)  # 4 4.0 1
print(rubric.version_hash)
```

## Public API

- `Criterion(name, description, scale_min=1, scale_max=5, weight=1.0)`: frozen dataclass. The weight must be finite and greater than 0.
- `Rubric(name, version, criteria)`: frozen dataclass. `Rubric.from_dict(data)` builds one from plain data. `version_hash` is the first 12 hex characters of the SHA-256 of the canonical JSON form, so criterion order matters.
- `judge(llm, rubric, candidate, reference=None, *, max_repairs=1, max_tokens=1024, max_candidate_chars=50_000, on_event=None) -> Judgement`. Returns `Judgement(scores, total, rationale, rubric_hash, attempts)`. `total` is the weighted mean of the scores.
- `calibrate(pairs, rubric) -> CalibrationReport`. Each pair is `(judgement, human_scores)`. The report holds an `Agreement(exact, within_one, kappa, n)` per criterion. `kappa` is `None` when the expected disagreement is 0.
- `LLMPort` (protocol with `complete(messages, *, max_tokens) -> str`), `Message`, `RecordedLLM` (replays recorded replies in order and raises `RecordingExhaustedError` when they run out) and `FakeLLM` (computes each reply with a function) from `llm_judge` or `llm_judge.ports`.
- `JudgeEvent(attempt, ok, error_paths)`: observability payload. It never contains candidate, reference or reply text.

### Errors

`JudgeError` has a `code`, a `message` of at most 200 characters and a `raw` field. Codes:

- `rubric_invalid`: the rubric data or a `Rubric` is invalid.
- `parse_failed`: no attempt produced a valid reply. `raw` holds the last reply cut to 200 characters.
- `candidate_too_large`: the candidate or reference exceeds `max_candidate_chars`. This is checked before any port call.
- `calibration_invalid`: empty or oversized pairs, mismatched criteria, or an invalid human score.

Invalid numeric arguments of `judge()` raise `ValueError`, and non-string candidate or reference raise `TypeError`.

### Limits

- `max_repairs` is at most 10, `max_tokens` at most 1,000,000 and `max_candidate_chars` at most 10,000,000.
- A reply longer than 100,000 characters is invalid. At most 100 `{` positions are tried when searching for a JSON object.
- The rationale is cut to 2000 characters. At most 20 validation problems are reported.
- `calibrate()` accepts at most 100,000 pairs.
- Exceptions raised by the port propagate unchanged and do not count as attempts. Exceptions raised by `on_event` are logged and ignored.

## Security

See [docs/SECURITY.md](docs/SECURITY.md) for the threat model, including what this library does not defend against.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Testing](docs/TESTING.md) and [security](docs/SECURITY.md)
- [Project record](docs/PROJECT.md) and [stack](docs/STACK.md)

## License

[MIT](LICENSE) (c) 2026 Miguel Gomez
