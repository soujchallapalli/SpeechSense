"""Pipeline that reads raw CSV, corrects transcripts with AI, and writes enriched CSV."""

import argparse
import csv
import logging
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from speechsense.correction import (
    GEMINI_MODEL,
    OLLAMA_MODEL,
    OLLAMA_URL,
    correct_transcript,
)

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = ["timestamp", "name", "raw_text_vosk", "time_taken_sec"]


def load_csv(path: str) -> tuple[list[str], list[dict[str, str]]]:
    """Read CSV header and rows, validate required columns.

    Returns:
        A tuple of (fieldnames, rows) where fieldnames are the CSV header columns
        and rows is a list of dicts (one per data row).
    """
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            msg = "CSV is empty or has no header row"
            raise ValueError(msg)
        missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
        if missing:
            msg = f"CSV is missing required columns: {missing}"
            raise ValueError(msg)
        rows: list[dict[str, str]] = list(reader)
        return list(reader.fieldnames), rows


def correct_row(
    row: dict[str, str],
    provider: str = "gemini",
    gemini_api_key: str | None = None,
    gemini_model: str = GEMINI_MODEL,
    ollama_model: str = OLLAMA_MODEL,
    ollama_url: str = OLLAMA_URL,
) -> dict[str, str]:
    """Correct a single row's transcript and add a ``text`` key.

    Returns a shallow copy of the row with an added ``text`` field.
    If correction fails, ``text`` is set to an empty string.
    """
    row = dict(row)
    try:
        row["text"] = correct_transcript(
            row["raw_text_vosk"],
            provider=provider,
            gemini_api_key=gemini_api_key,
            gemini_model=gemini_model,
            ollama_model=ollama_model,
            ollama_url=ollama_url,
        )
    except Exception:
        logger.exception("Failed to correct: %r", row["raw_text_vosk"])
        row["text"] = ""
    return row


def save_csv(fieldnames: list[str], rows: list[dict], path: str) -> None:
    """Write enriched CSV with an additional ``text`` column."""
    output_fieldnames = [*fieldnames, "text"]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=output_fieldnames, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)
    logger.info("Saved enriched CSV to %s (%d rows)", path, len(rows))


def process_pipeline(
    input_path: str,
    output_path: str,
    provider: str = "gemini",
    max_workers: int = 4,
    gemini_api_key: str | None = None,
    gemini_model: str = GEMINI_MODEL,
    ollama_model: str = OLLAMA_MODEL,
    ollama_url: str = OLLAMA_URL,
) -> None:
    """Read CSV, correct transcripts in parallel, write enriched CSV."""
    fieldnames, rows = load_csv(input_path)
    logger.info("Loaded %d rows from %s", len(rows), input_path)

    correct_fn = partial(
        correct_row,
        provider=provider,
        gemini_api_key=gemini_api_key,
        gemini_model=gemini_model,
        ollama_model=ollama_model,
        ollama_url=ollama_url,
    )

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        corrected = list(executor.map(correct_fn, rows))

    save_csv(fieldnames, corrected, output_path)


def build_arg_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Correct raw Vosk transcripts with AI.",
    )
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    parser.add_argument(
        "--provider",
        default="gemini",
        choices=["gemini", "ollama"],
        help="AI provider (default: gemini)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of parallel threads for AI correction (default: 4). "
        "Operational tuning knob -- Gemini may throttle bursts "
        "and Ollama may not scale linearly with more threads.",
    )
    parser.add_argument(
        "--gemini-api-key",
        default=None,
        help="Gemini API key (default: GEMINI_API_KEY env var)",
    )
    parser.add_argument(
        "--gemini-model",
        default=GEMINI_MODEL,
        help=f"Gemini model name (default: {GEMINI_MODEL})",
    )
    parser.add_argument(
        "--ollama-model",
        default=OLLAMA_MODEL,
        help=f"Ollama model name (default: {OLLAMA_MODEL})",
    )
    parser.add_argument(
        "--ollama-url",
        default=OLLAMA_URL,
        help=f"Ollama server URL (default: {OLLAMA_URL})",
    )
    return parser


def main() -> None:
    """CLI entry point for the correction pipeline."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    parser = build_arg_parser()
    args = parser.parse_args()

    process_pipeline(
        input_path=args.input,
        output_path=args.output,
        provider=args.provider,
        max_workers=args.workers,
        gemini_api_key=args.gemini_api_key,
        gemini_model=args.gemini_model,
        ollama_model=args.ollama_model,
        ollama_url=args.ollama_url,
    )
