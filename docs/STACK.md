# Stack

## Used

| Tool | Why |
|---|---|
| Python >= 3.10 | Minimum version declared by the package; the code uses `X | Y` union types in `isinstance`. |
| hatchling | Build backend declared for the package. |
| pytest + pytest-cov | Test runner and branch coverage, as described in TESTING.md. |
| mypy | The package ships `py.typed`, so type annotations are part of the public contract. |
| ruff | Lint and format, as used by the quality gates. |
| gitleaks | Secret scanning in the local gates and CI. |
| GitHub Actions + Dependabot | CI workflow and dependency updates. |

Runtime dependencies: none. The library only uses the Python standard library (`json`, `hashlib`, `re`, `logging`, `collections`, `dataclasses`, `math`, `types`, `typing`).

## Discarded

No discarded tools are recorded in the supplied material.