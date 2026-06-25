# Contributing

Thanks for your interest in contributing to **cognigy-api-client**.

## Development setup

```bash
git clone https://github.com/TheHenkelmann/cognigy-api-client.git
cd cognigy-api-client
pip install -e ".[dev]"
pre-commit install
```

## Running checks locally

```bash
ruff check src tests
ruff format --check src tests
mkdir -p .mypy_stubs && ln -sfn ../src .mypy_stubs/cognigy
MYPYPATH=.mypy_stubs mypy -p cognigy
pytest --cov=cognigy
```

Or run all hooks:

```bash
pre-commit run --all-files
```

## Pull request guidelines

- Keep changes focused and well-scoped
- Add or update tests when changing behavior
- Ensure `ruff`, `mypy`, and `pytest` pass locally before opening a PR
- Update [CHANGELOG.md](CHANGELOG.md) for user-visible changes
- Use clear commit messages (e.g. `feat:`, `fix:`, `docs:`, `chore:`)

## Release process

1. Update version in `pyproject.toml` and add a changelog entry
2. Tag the release (`vX.Y.Z`) and push the tag
3. GitHub Actions publishes to PyPI via Trusted Publishing (when configured)

## Code of conduct

Be respectful and constructive. This is a community-maintained project and is not
affiliated with Cognigy GmbH.
