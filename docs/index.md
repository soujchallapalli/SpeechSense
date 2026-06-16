# SpeechSense

A speech processing pipeline for recording, transcribing, correcting, enriching, and analysing meeting speech.

## Pipeline stages

1. **Record and transcribe** — capture speech from team members using Vosk
2. **Correct with AI** — fix spelling/punctuation via Ollama
3. **Enrich with Python** — add calculated columns (word count, speech rate, etc.)
4. **Validate** — check data quality before analysis
5. **Analyse** — produce speaking analytics

## CLI commands

| Command                               | Description                               |
| ------------------------------------- | ----------------------------------------- |
| `correct-transcripts`                 | Correct raw Vosk transcripts with AI      |
| `python -m speechsense.analyse <csv>` | Run speaking analytics on an enriched CSV |

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
