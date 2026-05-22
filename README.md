# SpeechSense

A speech processing pipeline.

## Prerequisites

- Python 3.10+
- [Poetry](https://python-poetry.org/docs/#installation)

## Setup

1. Install Poetry (if not already installed):

```bash
pip install poetry
```

2. Install the project dependencies and pre-commit hooks:

```bash
make install
```

This runs `poetry install` and sets up pre-commit hooks for automatic linting/formatting on commit.

## Development

### Running Tests

```bash
make test
```

Runs `pytest` with coverage reporting. To run a specific test:

```bash
poetry run pytest tests/test_foo.py -v
```

### Linting and Formatting

```bash
make check
```

This runs all code quality checks in sequence:

1. **Poetry lock check** — verifies `poetry.lock` is consistent with `pyproject.toml`
2. **Pre-commit hooks** — runs ruff (linting + formatting), trailing whitespace fixes, YAML/TOML validation
3. **mypy** — static type checking with strict settings
4. **deptry** — checks for unused/missing/transitive dependencies

To auto-format code manually:

```bash
poetry run ruff format src/ tests/
```

To auto-fix lint issues:

```bash
poetry run ruff check --fix src/ tests/
```

### Type Checking

Type checking is included in `make check`, but to run it standalone:

```bash
poetry run mypy
```

The project enforces strict typing rules — all functions must have type annotations.

### Documentation

Build and serve docs locally:

```bash
make docs
```

### All Available Make Commands

```bash
make help
```

## Project Structure

```
SpeechSense/
├── src/
│   └── speechsense/      # Main package source code
├── tests/                 # Test files
├── docs/                  # MkDocs documentation
├── pyproject.toml         # Project config, dependencies, tool settings
├── Makefile               # Development workflow commands
└── tox.ini                # Multi-version test config
```
