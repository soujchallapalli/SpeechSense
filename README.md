# SpeechSense

A speech processing pipeline for recording, transcribing, correcting, enriching, and analysing meeting speech.

## Prerequisites

- Python 3.10+
- [Poetry](https://python-poetry.org/docs/#installation)
- For Gemini: a [Gemini API key](https://aistudio.google.com/apikey)
- For Ollama: [Ollama](https://ollama.com/download) running locally with `gemma3` pulled

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

## Usage

### Correct transcripts with AI (Stage 2)

Read a CSV with `raw_text_vosk`, correct each transcript via AI in parallel, and write an enriched CSV with a `text` column.

**With Gemini (default):**

```bash
export GEMINI_API_KEY="your_key_here"
correct-transcripts --input raw.csv --output corrected.csv
```

**With Ollama (local):**

```bash
correct-transcripts --input raw.csv --output corrected.csv --provider ollama
```

**Input CSV format:**

| timestamp             | name    | raw_text_vosk                                  | time_taken_sec |
| --------------------- | ------- | ---------------------------------------------- | -------------- |
| `2026-04-28T10:00:05` | Stelios | `helo team today we discuss mobile app growth` | `6.2`          |

**Output CSV format:** same columns plus a `text` column with the AI-corrected transcript.

### Available commands

| Command               | Description                          |
| --------------------- | ------------------------------------ |
| `correct-transcripts` | Correct raw Vosk transcripts with AI |

All commands accept `--help` for full usage.

### CLI reference

```
correct-transcripts --input INPUT --output OUTPUT [options]
```

| Option             | Default                               | Description                                  |
| ------------------ | ------------------------------------- | -------------------------------------------- |
| `--input`          | _(required)_                          | Path to input CSV                            |
| `--output`         | _(required)_                          | Path to output CSV                           |
| `--provider`       | `gemini`                              | AI provider (`gemini` or `ollama`)           |
| `--workers`        | `4`                                   | Number of parallel threads for AI correction |
| `--gemini-api-key` | `GEMINI_API_KEY` env var              | Gemini API key                               |
| `--gemini-model`   | `gemini-2.5-flash`                    | Gemini model name                            |
| `--ollama-model`   | `gemma3`                              | Ollama model name                            |
| `--ollama-url`     | `http://localhost:11434/api/generate` | Ollama server URL                            |

Rows are read one-by-one with `csv.DictReader` and corrected in parallel using a thread pool (I/O-bound API calls). Results are written in input order. Use `--workers` to tune concurrency — Gemini may throttle bursts and Ollama may not scale linearly with more threads.

## Development

### Running Tests

```bash
make test
```

Runs `pytest` with coverage reporting. To run a specific test:

```bash
poetry run pytest tests/test_correction.py -v
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
│   └── speechsense/
│       ├── __init__.py
│       ├── main.py
│       ├── correction.py              # AI correction providers (Gemini, Ollama)
│       └── correction_pipeline.py     # CSV load → correct → save pipeline
├── tests/
│   ├── test_foo.py
│   └── test_correction.py             # Tests for correction module + pipeline
├── data/
│   ├── README.md                      # Project brief
│   ├── requirements.txt
│   └── examples/                      # Starter example scripts
├── docs/                  # MkDocs documentation
├── pyproject.toml         # Project config, dependencies, tool settings
├── Makefile               # Development workflow commands
└── tox.ini                # Multi-version test config
```
