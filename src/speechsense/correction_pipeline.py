"""Pipeline that reads raw CSV, corrects transcripts with AI, and writes enriched CSV."""

import argparse
import logging

import pandas as pd

from speechsense.correction import correct_transcript

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = ["timestamp", "name", "raw_text_vosk", "time_taken_sec"]


def load_csv(path: str) -> pd.DataFrame:
    """Load raw transcript CSV and validate required columns."""
    df = pd.read_csv(path)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        msg = f"CSV is missing required columns: {missing}"
        raise ValueError(msg)
    return df


def apply_correction(
    df: pd.DataFrame,
    provider: str = "gemini",
    gemini_api_key: str | None = None,
    gemini_model: str = "gemini-2.5-flash",
    ollama_model: str = "gemma3",
    ollama_url: str = "http://localhost:11434/api/generate",
) -> pd.DataFrame:
    """Add a ``text`` column with AI-corrected versions of ``raw_text_vosk``."""
    texts: list[str] = []
    for raw in df["raw_text_vosk"]:
        try:
            corrected = correct_transcript(
                raw,
                provider=provider,
                gemini_api_key=gemini_api_key,
                gemini_model=gemini_model,
                ollama_model=ollama_model,
                ollama_url=ollama_url,
            )
            texts.append(corrected)
        except Exception:
            logger.exception("Failed to correct: %r", raw)
            texts.append("")
    df = df.copy()
    df["text"] = texts
    return df


def save_csv(df: pd.DataFrame, path: str) -> None:
    """Write enriched CSV to disk."""
    df.to_csv(path, index=False)
    logger.info("Saved enriched CSV to %s (%d rows)", path, len(df))


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
    return parser


def main() -> None:
    """CLI entry point for the correction pipeline."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    parser = build_arg_parser()
    args = parser.parse_args()

    df = load_csv(args.input)
    logger.info("Loaded %d rows from %s", len(df), args.input)

    df = apply_correction(df, provider=args.provider)
    save_csv(df, args.output)


if __name__ == "__main__":
    main()
