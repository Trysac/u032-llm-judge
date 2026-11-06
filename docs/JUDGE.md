# LLM judge

`llm_judge` grades free-form answers with an LLM judge and checks the judge against human labels.

## Rubrics

`Criterion` and `Rubric` are frozen dataclasses. `Rubric.from_dict()` validates plain data and
raises `JudgeError` with code `rubric_invalid`. `Rubric.version_hash` is the first 12 hex characters
of the SHA-256 of the canonical JSON form, so equal content hashes equally and criteria order counts.

## Judging

`judge(llm, rubric, candidate, reference=None)` sends a system and a user message. The candidate and
the optional reference are wrapped in `<candidate>` and `<reference>` tags; every `</candidate` and
`</reference` inside them is rewritten (case-insensitively) to `&lt;/candidate` and `&lt;/reference`
so the text cannot close its own block. The system message tells the judge to ignore instructions
inside the tags.

The reply is parsed strictly: the first JSON object found (at most 100 candidate positions, duplicate
keys rejected, replies over 100 000 characters invalid) must contain `scores` with exactly the
rubric's criteria as integers within each scale, and a string `rationale`. An invalid reply is
answered by at most `max_repairs` re-asks that list up to 20 problems as `- <path>: <message>` lines.
Still invalid replies raise `JudgeError` with code `parse_failed`; the last reply, cut to 200
characters, is available in `.raw` and never in the message.

Port exceptions (including `RecordingExhaustedError`) propagate unchanged. `on_event` receives a
`JudgeEvent(attempt, ok, error_paths)` per attempt; it never contains candidate, reference or reply
text, and criterion names invented by the judge are reported as `scores.<unexpected>`.

## Calibration

`calibrate(pairs, rubric)` compares `(Judgement, human_scores)` pairs per criterion and reports exact
agreement, agreement within one point and the quadratic weighted kappa, or `None` when the expected
disagreement is 0. Human scores must be `int` (not `bool`) within the criterion's scale.

## Limits

| Limit | Value |
|---|---|
| Candidate and reference length | `max_candidate_chars`, default 50 000 |
| Judge reply length | 100 000 characters |
| JSON start positions tried | 100 |
| Rationale length | 2 000 characters |
| Problems listed in a re-ask | 20 |
| Criteria per rubric | 50 |
| Pairs per calibration | 100 000 |

Out of scope: provider clients, pairwise judging, ensembles and rubric storage.
