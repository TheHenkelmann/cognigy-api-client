# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2026-06-25

### Added

- CI pipeline with Ruff lint/format, mypy, pytest, and coverage reporting across Python 3.9–3.13
- Pre-commit hooks, `CONTRIBUTING.md`, and `CHANGELOG.md`
- README badges (PyPI, CI, Codecov, mypy, Ruff) and feature summary
- GitHub Actions workflow for PyPI Trusted Publishing on version tags
- Codecov integration for coverage tracking

### Changed

- Applied Ruff formatting and import sorting across the codebase
- Improved PyPI project description and repository metadata

### Fixed

- Python 3.9 compatibility via `eval_type_backport` and deferred annotations in all modules

### Removed

- Redundant `requirements.txt` (use `pyproject.toml` and `uv.lock` instead)

## [0.1.0] - 2026-03-25

### Added

- Initial public release of the unofficial Cognigy.AI Python SDK
- Synchronous (`CognigyClient`) and asynchronous (`AsyncCognigyClient`) clients
- Pydantic v2 models with camelCase API serialization and `_id` → `id` mapping
- Resource modules for projects, flows, nodes, AI agents, analytics, conversations,
  knowledge stores/sources/chunks/connectors, locales, logs, tasks, search, snapshots,
  connections, extensions, functions, and LLMs
- Pagination helpers, validation utilities, and structured exception types
- Test suite with pytest across Python 3.9–3.13
- Published on [PyPI](https://pypi.org/project/cognigy-api-client/) as `cognigy-api-client`

[0.1.1]: https://github.com/TheHenkelmann/cognigy-api-client/releases/tag/v0.1.1
[0.1.0]: https://github.com/TheHenkelmann/cognigy-api-client/releases/tag/v0.1.0
