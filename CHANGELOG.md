# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
- CI pipeline with Ruff, mypy, and coverage reporting
- Published on [PyPI](https://pypi.org/project/cognigy-api-client/) as `cognigy-api-client`

[0.1.0]: https://github.com/TheHenkelmann/cognigy-api-client/releases/tag/v0.1.0
