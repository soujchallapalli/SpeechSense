import pandas as pd
import pytest
from speechsense.analyse import (
    avg_speaking_time_per_speaker,
    avg_speech_rate_per_speaker,
    least_words,
    most_questions,
    most_words,
    top_speakers_by_time,
    total_speaking_time,
)


@pytest.fixture()
def sample_df() -> pd.DataFrame:
    return pd.DataFrame({
        "timestamp": [
            "2026-04-28T10:00:05",
            "2026-04-28T10:00:18",
            "2026-04-28T10:00:30",
            "2026-04-28T10:00:40",
        ],
        "name": ["Stelios", "Mary", "Kate", "Stelios"],
        "raw_text_vosk": [
            "helo team today we discuss mobile app growth",
            "can we target students first",
            "i think we need lower pricing for early users",
            "ok lets proceed",
        ],
        "text": [
            "Hello team, today we discuss mobile app growth.",
            "Can we target students first?",
            "I think we need lower pricing for early users.",
            "Ok, let's proceed!",
        ],
        "time_taken_sec": [6.2, 3.8, 5.1, 3.2],
        "question_flag": [False, True, False, False],
        "num_words": [8, 6, 10, 3],
        "text_size_chars": [48, 30, 47, 19],
        "speech_rate_wps": [1.29, 1.58, 1.96, 0.94],
        "speaker_turn_id": [1, 1, 1, 2],
    })


def test_most_words(sample_df: pd.DataFrame) -> None:
    name, count = most_words(sample_df)
    assert name == "Stelios"
    assert count == 11


def test_least_words(sample_df: pd.DataFrame) -> None:
    name, count = least_words(sample_df)
    assert name == "Mary"
    assert count == 6


def test_total_speaking_time(sample_df: pd.DataFrame) -> None:
    assert total_speaking_time(sample_df) == 18.3


def test_avg_speaking_time_per_speaker(sample_df: pd.DataFrame) -> None:
    assert avg_speaking_time_per_speaker(sample_df) == 6.1


def test_most_questions(sample_df: pd.DataFrame) -> None:
    name, count = most_questions(sample_df)
    assert name == "Mary"
    assert count == 1


def test_top_speakers_by_time(sample_df: pd.DataFrame) -> None:
    result = top_speakers_by_time(sample_df)
    assert result[0] == ("Stelios", 9.4)
    assert result[1] == ("Kate", 5.1)
    assert result[2] == ("Mary", 3.8)


def test_avg_speech_rate_per_speaker(sample_df: pd.DataFrame) -> None:
    result = dict(avg_speech_rate_per_speaker(sample_df))
    assert result["Kate"] == 1.96
    assert result["Mary"] == 1.58
    assert result["Stelios"] == 1.11
