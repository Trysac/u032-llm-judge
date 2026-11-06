# Security notes

## Threat model

`trysac-llm-judge` performs no I/O and has no runtime dependencies. The risks it addresses and the limits it has are listed below.

### Defended

- **Prompt injection through the candidate or reference**: both texts are wrapped in `<candidate>` and `<reference>` tags. Every case-insensitive occurrence of `</candidate` and `</reference` is replaced by `&lt;` followed by the rest of the match, so the text cannot close its own data block. The system message states that text inside those tags is data and that instructions inside them must be ignored.
- **Malformed or hostile judge replies**: replies longer than 100,000 characters are rejected. JSON is decoded with a hook that rejects duplicate keys, at most 100 `{` positions are tried, and `ValueError` and `RecursionError` are caught and reported as invalid replies. Scores must be exact `int` values within the criterion scale; booleans and floats are rejected.
- **Oversized input**: candidate and reference longer than `max_candidate_chars` are rejected before the port is called. `max_repairs`, `max_tokens` and `max_candidate_chars` have upper bounds.
- **Leakage through observability**: `JudgeEvent` carries only attempt number, success flag and error paths. Extra criterion names are reported as `scores.<unexpected>` in events. Error messages and `JudgeError.raw` are truncated to 200 characters, and `raw` is set only for `parse_failed`.
- **Unsafe deserialization**: the library never uses `eval`, `exec` or pickle.

### Not defended

- **Semantic manipulation of the judge model**: escaping and the system instruction reduce, but do not eliminate, the chance that a judge model follows instructions inside the candidate. Scores can still be biased or wrong.
- **Opening tags and other delimiters**: only closing tags matching `</candidate` and `</reference` are escaped. Other text in the candidate is passed through unchanged.
- **Port behaviour**: the library sets no timeout and no retry budget beyond `max_repairs`. A slow or hanging port blocks the caller. Exceptions raised by the port propagate unchanged.
- **Credentials and providers**: the library holds no API keys and implements no provider client. Securing the provider connection is the caller's responsibility.
- **Event handler failures**: exceptions raised by `on_event` are logged and ignored, so a faulty observer cannot stop judging, but it also cannot be detected by the caller.

## Supply chain

No runtime dependencies. Dependency updates and CI actions are managed as described in the project configuration.

## Publishing

Releases are intended to be published to PyPI with trusted publishing (OIDC) when available, not with a long-lived token stored in the repository.

To report a vulnerability, see [SECURITY.md](../SECURITY.md).