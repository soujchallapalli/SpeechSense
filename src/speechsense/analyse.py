import sys
from pathlib import Path

import pandas as pd


def load_data(csv_path: str) -> pd.DataFrame:
    return pd.read_csv(csv_path)


def most_words(df: pd.DataFrame) -> tuple[str, int]:
    totals = df.groupby("name")["num_words"].sum()
    speaker = str(totals.idxmax())
    return speaker, int(totals[speaker])


def least_words(df: pd.DataFrame) -> tuple[str, int]:
    totals = df.groupby("name")["num_words"].sum()
    speaker = str(totals.idxmin())
    return speaker, int(totals[speaker])


def total_speaking_time(df: pd.DataFrame) -> float:
    return float(round(df["time_taken_sec"].sum(), 1))


def avg_speaking_time_per_speaker(df: pd.DataFrame) -> float:
    total = df["time_taken_sec"].sum()
    num_speakers = df["name"].nunique()
    return float(round(total / num_speakers, 1))


def most_questions(df: pd.DataFrame) -> tuple[str, int]:
    questions = df[df["question_flag"]].groupby("name").size()
    if questions.empty:
        return ("", 0)
    speaker = str(questions.idxmax())
    return speaker, int(questions[speaker])


def top_speakers_by_time(df: pd.DataFrame, n: int = 5) -> list[tuple[str, float]]:
    totals = df.groupby("name")["time_taken_sec"].sum().sort_values(ascending=False)
    return [(str(name), float(round(time, 1))) for name, time in totals.head(n).items()]


def avg_speech_rate_per_speaker(df: pd.DataFrame) -> list[tuple[str, float]]:
    rates = df.groupby("name")["speech_rate_wps"].mean()
    return [(str(name), float(round(rate, 2))) for name, rate in rates.items()]


def generate_report(df: pd.DataFrame) -> str:
    most_w_name, most_w_count = most_words(df)
    least_w_name, least_w_count = least_words(df)
    total_time = total_speaking_time(df)
    avg_time = avg_speaking_time_per_speaker(df)
    most_q_name, most_q_count = most_questions(df)
    top_speakers = top_speakers_by_time(df)
    speech_rates = avg_speech_rate_per_speaker(df)

    lines = [
        "# Meeting Report",
        "",
        "## Overview",
        "",
        "| Metric | Result |",
        "| --- | --- |",
        f"| Most words | {most_w_name}, {most_w_count} words |",
        f"| Least words | {least_w_name}, {least_w_count} words |",
        f"| Total speaking time | {total_time} seconds |",
        f"| Avg speaking time per speaker | {avg_time} seconds |",
        f"| Most questions | {most_q_name}, {most_q_count} question(s) |",
        "",
        "## Top Speakers by Time",
        "",
        "| Rank | Speaker | Time (seconds) |",
        "| --- | --- | --- |",
    ]

    for rank, (name, time) in enumerate(top_speakers, 1):
        lines.append(f"| {rank} | {name} | {time} |")

    lines += [
        "",
        "## Speech Rate per Speaker",
        "",
        "| Speaker | Avg words/second |",
        "| --- | --- |",
    ]

    for name, rate in speech_rates:
        lines.append(f"| {name} | {rate} |")

    lines.append("")
    return "\n".join(lines)


def write_report(df: pd.DataFrame, output_path: str) -> None:
    report = generate_report(df)
    Path(output_path).write_text(report)


def print_report(df: pd.DataFrame) -> None:
    print(generate_report(df))


def main(csv_path: str) -> None:
    df = load_data(csv_path)
    print_report(df)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m speechsense.analyse <csv_path>")
        sys.exit(1)
    path = sys.argv[1]
    if not Path(path).exists():
        print(f"Error: file not found: {path}")
        sys.exit(1)
    main(path)
