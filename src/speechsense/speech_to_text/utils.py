import csv
import logging
import os
from datetime import datetime, timedelta

from speechsense.config import CSV_HEADERS, CSV_OUTPUT_PATH

# Configure logging to show INFO level and above
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def format_transcript(transcript_segments: list[dict]) -> str:
    """Pretty-print the transcript to console."""
    lines = []
    for seg in transcript_segments:
        timestamp = f"[{seg['start']:.1f}s - {seg['end']:.1f}s]"
        lines.append(f"{timestamp}:\n  {seg['text']}")
    return "\n\n".join(lines)


def build_csv_rows(transcript_segments: list[dict], recording_start: datetime) -> list[dict]:
    """Convert transcript segments into CSV row dicts."""
    rows = []
    for seg in transcript_segments:
        timestamp = recording_start + timedelta(seconds=seg["start"])
        time_taken = f"{round(seg['end'] - seg['start'], 1):.1f}"

        rows.append({
            "timestamp": timestamp.strftime("%Y-%m-%dT%H:%M:%S"),
            "raw_text_vosk": seg["text"],
            "time_taken_sec": time_taken,
        })
    return rows


def save_csv(rows: list[dict], output_path: str = CSV_OUTPUT_PATH) -> None:
    """Write rows to CSV, creating output directory if needed."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        writer.writerows(rows)
    logging.info(f"CSV saved to: {output_path}")
