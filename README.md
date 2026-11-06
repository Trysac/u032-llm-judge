# llm-judge

[![PyPI version](https://img.shields.io/pypi/v/trysac-llm-judge)](https://pypi.org/project/trysac-llm-judge/)
[![License: MIT](https://img.shields.io/pypi/l/trysac-llm-judge)](LICENSE)
[![CI](https://github.com/Trysac/u032-llm-judge/actions/workflows/ci.yml/badge.svg)](https://github.com/Trysac/u032-llm-judge/actions/workflows/ci.yml)

LLM-as-judge with versioned rubrics, strict per-criterion score parsing with one bounded re-ask, and quadratic weighted kappa calibration

## Problem

Describe in two or three sentences the concrete problem this utility solves, who hits it, and what
they do today without it. Replace this paragraph when the first real feature lands.

## Install

```sh
pip install trysac-llm-judge
# or
uv add trysac-llm-judge
```

Requires Python 3.10 or newer. No runtime dependencies.

## Usage

```python
import llm_judge

# normalize() trims surrounding whitespace and lower-cases the text.
print(llm_judge.normalize("  Hello World "))  # -> "hello world"

# Blank input is rejected explicitly instead of returning an empty string.
try:
    llm_judge.normalize("   ")
except ValueError as exc:
    print(f"rejected: {exc}")
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md) and [decisions](docs/decisions/)
- [Testing](docs/TESTING.md) and [security](docs/SECURITY.md)
- [Project record](docs/PROJECT.md) and [stack](docs/STACK.md)
- [Changelog](CHANGELOG.md) and [contributing guide](CONTRIBUTING.md)

## License

[MIT](LICENSE) (c) 2026 Miguel Gomez
