# Strict reply parsing with a bounded re-ask and tag-isolated candidates

Status: accepted (generated, pending human review)

## Context

Ad-hoc judge prompts drift, return unparseable text and can be steered by instructions planted in the graded answer. Teams also rarely measure how well the judge agrees with people.

## Decision

Rubrics are hashed immutable data. The candidate and reference are placed in escaped data tags, replies are decoded by scanning for the first JSON object with duplicate-key rejection and size and position limits, validated per criterion and re-asked at most max_repairs times with a deterministic problem list. Events carry only redacted error paths. Calibration uses exact, within-one and quadratic weighted kappa computed with integer arithmetic. The port is a small Protocol so provider clients stay outside the library.

## Consequences

Judge behaviour is reproducible and testable without a network, and failures surface as one typed JudgeError with stable codes. Strictness (integers only, no extra criteria, first JSON object wins) means some lenient replies are rejected and cost a re-ask. Escaping only neutralises closing tags; it reduces but cannot eliminate prompt injection, which the calibration step helps to detect.
