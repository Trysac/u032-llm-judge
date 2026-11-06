# Project record

## Objective

Provide a dependency-free Python library for LLM-as-judge evaluation that keeps rubrics as hashed data, parses judge replies strictly with one bounded re-ask, isolates candidate and reference text in data tags, and measures agreement with human labels using exact, within-one and quadratic weighted kappa statistics.

## Scope

- In scope: `Criterion`, `Rubric` with `from_dict` and `version_hash`, `judge()`, `calibrate()`, the `LLMPort` protocol with `RecordedLLM` and `FakeLLM` test doubles, `JudgeEvent`, and `JudgeError` with its four codes.
- Out of scope: provider clients for any LLM service, pairwise judging, ensembles of judges, and storage or retrieval of rubrics.

## Timeline

| Date | Event |
|---|---|
| 2026 | Repository created from the factory utility template. |

## Effort metrics

Measured values only; a value that has not been measured stays "pending measurement".

| Metric | Value |
|---|---|
| Tokens (input / output) | 544058 / 81708 |
| Hours (human) | pending measurement |
| Cost (USD) | 0.7661 |

## Factory run u032 (measured from API usage)

| Phase | Model | Batch | Input | Output | Cache write | Cache read | Cost (USD) |
|---|---|---|---|---|---|---|---|
| generation | claude-sonnet-5-5 | yes | 2798 | 64684 | 0 | 4246 | 0.3266 |
| fix-1 | claude-sonnet-5-5 | no | 4 | 881 | 7174 | 25148 | 0.0293 |
| fix-2 | claude-sonnet-5-5 | no | 4 | 327 | 6078 | 24772 | 0.0210 |
| fix-3 | claude-sonnet-5-5 | no | 4 | 276 | 5993 | 24768 | 0.0202 |
| fix-4 | claude-sonnet-5-5 | no | 8 | 1608 | 9820 | 58690 | 0.0465 |
| fix-1 | claude-sonnet-5-5 | no | 4 | 311 | 6053 | 24936 | 0.0207 |
| fix-2 | claude-sonnet-5-5 | no | 12 | 1628 | 8638 | 91269 | 0.0470 |
| audit | claude-sonnet-5-5 | no | 12 | 3573 | 37125 | 129661 | 0.1415 |
| fix-3 | claude-sonnet-5-5 | no | 6 | 1307 | 7997 | 41312 | 0.0372 |
| docs | claude-haiku-5-5 | no | 116404 | 7113 | 0 | 0 | 0.0760 |

Total: $0.7661. Prices: Anthropic list prices.
