# SpeechSense

A speech processing pipeline for recording, transcribing, correcting, enriching, and analysing meeting speech.

## Pipeline stages

1. **Record and transcribe** — capture speech from team members using Vosk
2. **Correct with AI** — fix spelling/punctuation via Gemini or Ollama
3. **Enrich with Python** — add calculated columns (word count, speech rate, etc.)
4. **Validate** — check data quality before analysis
5. **Analyse** — produce speaking analytics

## CLI commands

| Command               | Description                          |
| --------------------- | ------------------------------------ |
| `correct-transcripts` | Correct raw Vosk transcripts with AI |
