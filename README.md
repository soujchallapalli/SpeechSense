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

# Vosk and PyAnnote Setup Guide

This project uses **Vosk** for offline speech-to-text transcription and **PyAnnote** for speaker diarization.

---

# Vosk Model Setup

## Model: `vosk-model-en-us-0.42-gigaspeech`

The recommended English Vosk model for this project is:

```text
vosk-model-en-us-0.42-gigaspeech
```

This is one of the larger and more accurate English models provided by Vosk and is designed for offline speech recognition.

### Download

Official Vosk model repository:

https://alphacephei.com/vosk/models

Download the model from the **English Models** section and extract it into your project directory.

---

# Hugging Face Token Setup (Required for PyAnnote)

PyAnnote models are hosted on Hugging Face and require authentication before they can be downloaded.

## 1. Create a Hugging Face Account

Sign up or log in:

- Login: https://huggingface.co/login
- Sign Up: https://huggingface.co/join

---

## 2. Create an Access Token

Navigate to:

https://huggingface.co/settings/tokens

### Steps

1. Click **Create new token**
2. Enter a name, for example:

```text
SpeechSense
```

3. Select **Read** permissions
4. Click **Create token**

---

## 3. Copy and Save Your Token

You will receive a token similar to:

```text
hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

> **Important:** Copy and store the token securely. Hugging Face will not display the full token again.

---

## 4. Accept PyAnnote Model Terms

Before using PyAnnote, you must accept the license terms for the required models.

Visit and accept access for:

### Speaker Diarization Model

https://huggingface.co/pyannote/speaker-diarization-3.1

### Segmentation Model

https://huggingface.co/pyannote/segmentation

Click:

```text
Access repository
```

or

```text
Agree and access repository
```

on each page.

---

## 5. Authenticate Using Your Token

### Option A: Using the CLI

```bash
huggingface-cli login
```

Paste your token when prompted.

### Option B: Using Python

```python
from huggingface_hub import login

login("hf_your_token_here")
```

---

## 6. Verify Authentication

Run:

```bash
huggingface-cli whoami
```

If authentication is successful, your Hugging Face username will be displayed.

## 7. System Prerequisites: FFmpeg

FFmpeg is a core system dependency for PyAnnote.

Run:

```bash
brew install ffmpeg (for Mac)

winget install Gyan.FFmpeg (for Windows)
```

# Model Caching

When PyAnnote downloads the models for the first time:

- Models are cached locally
- Subsequent runs load from the cache
- Internet access is no longer required
- The Hugging Face token is not needed again unless the cache is cleared

---

# Useful Links

| Resource                     | Link                                                    |
| ---------------------------- | ------------------------------------------------------- |
| Vosk Models                  | https://alphacephei.com/vosk/models                     |
| Hugging Face                 | https://huggingface.co                                  |
| Access Tokens                | https://huggingface.co/settings/tokens                  |
| PyAnnote Speaker Diarization | https://huggingface.co/pyannote/speaker-diarization-3.1 |
| PyAnnote Segmentation        | https://huggingface.co/pyannote/segmentation            |
