import sys
from pathlib import Path

import pandas as pd


def load_data(csv_path: str) -> pd.DataFrame:
    return pd.read_csv(csv_path)


def most_words(df: pd.DataFrame) -> tuple[str, int]:
    totals = df.groupby("name")["num_words"].sum()
    speaker = totals.idxmax()
    return speaker, int(totals[speaker])


def least_words(df: pd.DataFrame) -> tuple[str, int]:
    totals = df.groupby("name")["num_words"].sum()
    speaker = totals.idxmin()
    return speaker, int(totals[speaker])


def total_speaking_time(df: pd.DataFrame) -> float:
    return round(df["time_taken_sec"].sum(), 1)


def avg_speaking_time_per_speaker(df: pd.DataFrame) -> float:
    total = df["time_taken_sec"].sum()
    num_speakers = df["name"].nunique()
    return round(total / num_speakers, 1)


def most_questions(df: pd.DataFrame) -> tuple[str, int]:
    questions = df[df["question_flag"]].groupby("name").size()
    if questions.empty:
        return ("", 0)
    speaker = questions.idxmax()
    return speaker, int(questions[speaker])


def top_speakers_by_time(df: pd.DataFrame, n: int = 5) -> list[tuple[str, float]]:
    totals = df.groupby("name")["time_taken_sec"].sum().sort_values(ascending=False)
    return [(name, round(time, 1)) for name, time in totals.head(n).items()]


def avg_speech_rate_per_speaker(df: pd.DataFrame) -> list[tuple[str, float]]:
    rates = df.groupby("name")["speech_rate_wps"].mean()
    return [(name, round(rate, 2)) for name, rate in rates.items()]


def print_report(df: pd.DataFrame) -> None:
    most_w_name, most_w_count = most_words(df)
    least_w_name, least_w_count = least_words(df)
    total_time = total_speaking_time(df)
    avg_time = avg_speaking_time_per_speaker(df)
    most_q_name, most_q_count = most_questions(df)
    top_speakers = top_speakers_by_time(df)
    speech_rates = avg_speech_rate_per_speaker(df)

    print(f"{'Metric':<35} {'Result'}")
    print("-" * 55)
    print(f"{'Most words':<35} {most_w_name}, {most_w_count} words")
    print(f"{'Least words':<35} {least_w_name}, {least_w_count} words")
    print(f"{'Total speaking time':<35} {total_time} seconds")
    print(f"{'Avg speaking time per speaker':<35} {avg_time} seconds")
    print(f"{'Most questions':<35} {most_q_name}, {most_q_count} question(s)")

    for rank, (name, time) in enumerate(top_speakers, 1):
        label = f"#{rank} speaker by time"
        print(f"{label:<35} {name}, {time} seconds")

    for name, rate in speech_rates:
        label = f"{name} avg speech rate"
        print(f"{label:<35} {rate} words/second")


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
