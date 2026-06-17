# SpeechSense

A speech processing pipeline for recording, transcribing, correcting, enriching, and analysing meeting speech.

## Prerequisites

- Python 3.10+
- [Poetry](https://python-poetry.org/docs/#installation)
- [Ollama](https://ollama.com/download) running locally with `gemma3` pulled (see [Setting up Ollama](#setting-up-ollama))

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

## Setting up Ollama

Ollama runs a local AI server on your machine. The project uses it for transcript correction.

1. **Install** — download from [ollama.com/download](https://ollama.com/download) and open the app.

2. **Download the model**:

   ```bash
   ollama pull gemma3
   ```

   If your computer is slow or has limited memory, use the smaller model instead:

   ```bash
   ollama pull gemma3:1b
   ```

   Then set `--ollama-model gemma3:1b` when running commands below.

3. **Verify the server is running**:
   ```bash
   curl http://localhost:11434/api/generate \
     -d '{"model": "gemma3", "prompt": "Correct this: helo team", "stream": false}'
   ```
   A JSON response means it is working. If you see a connection error, open the Ollama app and try again.

## Usage

### Correct transcripts with AI (Stage 2)

Read a CSV with `raw_text_vosk`, correct each transcript via AI in parallel, and write an enriched CSV with a `text` column.

```bash
correct-transcripts --input raw.csv --output corrected.csv
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

| Option           | Default                               | Description                                  |
| ---------------- | ------------------------------------- | -------------------------------------------- |
| `--input`        | _(required)_                          | Path to input CSV                            |
| `--output`       | _(required)_                          | Path to output CSV                           |
| `--provider`     | `ollama`                              | AI provider (`ollama`)                       |
| `--workers`      | `4`                                   | Number of parallel threads for AI correction |
| `--ollama-model` | `gemma3`                              | Ollama model name                            |
| `--ollama-url`   | `http://localhost:11434/api/generate` | Ollama server URL                            |

Rows are read one-by-one with `csv.DictReader` and corrected in parallel using a thread pool (I/O-bound API calls). Results are written in input order. Use `--workers` to tune concurrency — Ollama may not scale linearly with more threads.

## connecting to MongoDB

- create your .env file at the root
  - `cd SpeechSense/`
  - `touch .env`
- inside the file add the connection string
  - `MONGODB_URI= "mongodb+srv://SpeechSenseAdmin:<PASSWORD>@speechsense.kkxnwfq.mongodb.net/?appName=SpeechSense"`

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
│       ├── correction.py              # AI correction via Ollama
│       ├── correction_pipeline.py     # CSV load → correct → save pipeline
│       └── data/
│           ├── base_mongo.py
│           ├── processed_db.py
│           └── transcript_db.py
├── tests/
│   ├── test_foo.py
│   └── test_correction.py             # Tests for correction module + pipeline
│   └── data/
│       └── base_mongo_test.py
├── data/
│   ├── README.md                      # Project brief
│   ├── requirements.txt
│   └── examples/                      # Starter example scripts
├── docs/                  # MkDocs documentation
├── pyproject.toml         # Project config, dependencies, tool settings
├── Makefile               # Development workflow commands
└── tox.ini                # Multi-version test config
```
