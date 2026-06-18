import csv
import logging
import os
from datetime import datetime, timedelta

from speechsense.config import CSV_HEADERS, CSV_OUTPUT_PATH, SPEAKER_NAME_MAP

# Configure logging to show INFO level and above
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def format_transcript(merged_segments: list[dict], speaker_name_map: dict) -> str:
    """Pretty-print the diarized transcript to console."""
    lines = []
    for seg in merged_segments:
        name = speaker_name_map.get(seg["speaker"], seg["speaker"])
        timestamp = f"[{seg['start']:.1f}s - {seg['end']:.1f}s]"
        lines.append(f"{name} {timestamp}:\n  {seg['text']}")
    return "\n\n".join(lines)


def build_csv_rows(merged_segments: list[dict], recording_start: datetime) -> list[dict]:
    """Convert merged speaker segments into CSV row dicts."""
    rows = []
    for seg in merged_segments:
        timestamp = recording_start + timedelta(seconds=seg["start"])
        name = SPEAKER_NAME_MAP.get(seg["speaker"], seg["speaker"])
        time_taken = f"{round(seg['end'] - seg['start'], 1):.1f}"

        rows.append({
            "timestamp": timestamp.strftime("%Y-%m-%dT%H:%M:%S"),
            "name": name,
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
