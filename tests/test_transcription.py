import json
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from speechsense.speech_to_text import transcription, utils
from speechsense.speech_to_text.speech_to_text_pipeline import process_audio_file

# =====================================================================
# build_csv_rows — data correctness
# =====================================================================


def test_timestamp_offset_by_start_seconds():
    start = datetime(2024, 1, 1, 10, 0, 0)
    segs = [{"start": 65.0, "end": 66.0, "text": "x", "speaker": "SPEAKER_00"}]
    rows = utils.build_csv_rows(segs, start)
    assert rows[0]["timestamp"] == "2024-01-01T10:01:05"


def test_time_taken_rounded_one_decimal():
    start = datetime(2024, 1, 1)
    segs = [{"start": 1.0, "end": 3.46, "text": "x", "speaker": "SPEAKER_01"}]
    rows = utils.build_csv_rows(segs, start)
    assert rows[0]["time_taken_sec"] == "2.5"


def test_time_taken_always_one_decimal_place():
    start = datetime(2024, 1, 1)
    segs = [{"start": 0.0, "end": 2.0, "text": "x", "speaker": "SPEAKER_02"}]
    rows = utils.build_csv_rows(segs, start)
    assert rows[0]["time_taken_sec"] == "2.0"


def test_zero_duration():
    start = datetime(2024, 1, 1)
    segs = [{"start": 4.0, "end": 4.0, "text": "x", "speaker": "SPEAKER_00"}]
    rows = utils.build_csv_rows(segs, start)
    assert rows[0]["time_taken_sec"] == "0.0"


def test_full_row_fields():
    start = datetime(2024, 1, 1, 10, 0, 0)
    segs = [{"start": 0.0, "end": 2.5, "text": "hello", "speaker": "SPEAKER_00"}]
    with patch("speechsense.speech_to_text.utils.SPEAKER_NAME_MAP", {"SPEAKER_00": "Arron"}):
        rows = utils.build_csv_rows(segs, start)
    assert rows == [
        {
            "timestamp": "2024-01-01T10:00:00",
            "name": "Arron",
            "raw_text_vosk": "hello",
            "time_taken_sec": "2.5",
        }
    ]


# =====================================================================
# transcribe_wav_with_vosk — segment assembly
# =====================================================================


def make_wav_mock(nchannels=1, sampwidth=2, framerate=16000, frame_chunks=None):
    wf = MagicMock()
    wf.getnchannels.return_value = nchannels
    wf.getsampwidth.return_value = sampwidth
    wf.getframerate.return_value = framerate
    wf.readframes.side_effect = [*list(frame_chunks or []), b""]
    # Make it usable as a context manager: `with wave.open(...) as x` yields wf itself
    wf.__enter__.return_value = wf
    wf.__exit__.return_value = False
    return wf


@pytest.fixture
def patch_env():
    with (
        patch("speechsense.speech_to_text.transcription.os.path.exists", return_value=True),
        patch("speechsense.speech_to_text.transcription.wave.open") as wave_open,
        patch("speechsense.speech_to_text.transcription.Model"),
        patch("speechsense.speech_to_text.transcription.KaldiRecognizer") as recognizer_cls,
    ):
        recognizer = MagicMock()
        recognizer_cls.return_value = recognizer
        yield {"wave_open": wave_open, "recognizer": recognizer}


def test_single_accepted_segment(patch_env):
    patch_env["wave_open"].return_value = make_wav_mock(frame_chunks=[b"data"])
    patch_env["recognizer"].AcceptWaveform.return_value = True
    patch_env["recognizer"].Result.return_value = json.dumps({
        "text": "hello world",
        "result": [
            {"word": "hello", "start": 0.0, "end": 0.5},
            {"word": "world", "start": 0.5, "end": 1.0},
        ],
    })
    patch_env["recognizer"].FinalResult.return_value = json.dumps({"text": "", "result": []})
    segs = transcription.transcribe_wav_with_vosk("audio.wav", "model/path")
    assert segs == [{"start": 0.0, "end": 1.0, "text": "hello world"}]


def test_final_result_appended(patch_env):
    patch_env["wave_open"].return_value = make_wav_mock(frame_chunks=[b"data"])
    patch_env["recognizer"].AcceptWaveform.return_value = False
    patch_env["recognizer"].FinalResult.return_value = json.dumps({
        "text": "bye",
        "result": [{"word": "bye", "start": 2.0, "end": 2.4}],
    })
    segs = transcription.transcribe_wav_with_vosk("audio.wav", "model/path")
    assert segs == [{"start": 2.0, "end": 2.4, "text": "bye"}]


def test_empty_text_segment_skipped(patch_env):
    patch_env["wave_open"].return_value = make_wav_mock(frame_chunks=[b"data"])
    patch_env["recognizer"].AcceptWaveform.return_value = True
    patch_env["recognizer"].Result.return_value = json.dumps({"text": "", "result": []})
    patch_env["recognizer"].FinalResult.return_value = json.dumps({"text": "", "result": []})
    segs = transcription.transcribe_wav_with_vosk("audio.wav", "model/path")
    assert segs == []


def test_text_present_but_no_result_skipped(patch_env):
    # guard requires BOTH text and result truthy
    patch_env["wave_open"].return_value = make_wav_mock(frame_chunks=[b"data"])
    patch_env["recognizer"].AcceptWaveform.return_value = True
    patch_env["recognizer"].Result.return_value = json.dumps({"text": "hi", "result": []})
    patch_env["recognizer"].FinalResult.return_value = json.dumps({"text": "", "result": []})
    segs = transcription.transcribe_wav_with_vosk("audio.wav", "model/path")
    assert segs == []


def test_start_end_from_first_and_last_word(patch_env):
    patch_env["wave_open"].return_value = make_wav_mock(frame_chunks=[b"data"])
    patch_env["recognizer"].AcceptWaveform.return_value = True
    patch_env["recognizer"].Result.return_value = json.dumps({
        "text": "a b c",
        "result": [
            {"word": "a", "start": 1.0, "end": 1.2},
            {"word": "b", "start": 1.2, "end": 1.4},
            {"word": "c", "start": 1.4, "end": 1.9},
        ],
    })
    patch_env["recognizer"].FinalResult.return_value = json.dumps({"text": "", "result": []})
    segs = transcription.transcribe_wav_with_vosk("audio.wav", "model/path")
    assert segs[0]["start"] == 1.0 and segs[0]["end"] == 1.9


# =====================================================================
# transcribe_wav_with_vosk — format validation
# =====================================================================


def test_raises_on_non_mono(patch_env):
    patch_env["wave_open"].return_value = make_wav_mock(nchannels=2)
    with pytest.raises(ValueError, match="mono"):
        transcription.transcribe_wav_with_vosk("audio.wav", "model/path")


def test_raises_on_non_16bit(patch_env):
    patch_env["wave_open"].return_value = make_wav_mock(sampwidth=1)
    with pytest.raises(ValueError, match="16-bit"):
        transcription.transcribe_wav_with_vosk("audio.wav", "model/path")


# =====================================================================
# process_audio_file — the orchestration tests
# =====================================================================


@pytest.fixture
def patched_main():
    with (
        patch(
            "speechsense.speech_to_text.speech_to_text_pipeline.transcribe_wav_with_vosk",
            return_value=[{"start": 0.0, "end": 1.0, "text": "hi"}],
        ) as transcribe,
        patch(
            "speechsense.speech_to_text.speech_to_text_pipeline.diarize_audio",
            return_value=[{"start": 0.0, "end": 1.0, "speaker": "S0"}],
        ) as diarize,
        patch(
            "speechsense.speech_to_text.speech_to_text_pipeline.assign_speakers",
            return_value=[{"speaker": "S0", "start": 0.0, "end": 1.0, "text": "hi"}],
        ) as assign,
        patch(
            "speechsense.speech_to_text.speech_to_text_pipeline.merge_consecutive_speakers",
            return_value=[{"speaker": "S0", "start": 0.0, "end": 1.0, "text": "hi"}],
        ) as merge,
        patch("speechsense.speech_to_text.speech_to_text_pipeline.format_transcript", return_value="hi"),
        patch("speechsense.speech_to_text.speech_to_text_pipeline.build_csv_rows", return_value=[{"x": 1}]) as build,
        patch("speechsense.speech_to_text.speech_to_text_pipeline.save_csv") as save,
    ):
        yield {
            "transcribe": transcribe,
            "diarize": diarize,
            "assign": assign,
            "merge": merge,
            "build": build,
            "save": save,
        }


def test_defaults_start_time_to_now_when_none(patched_main):
    fixed = datetime(2024, 5, 5, 9, 30, 0)
    with patch("speechsense.speech_to_text.speech_to_text_pipeline.datetime") as mock_dt:
        mock_dt.now.return_value = fixed
        process_audio_file("audio.wav", "", None)
    mock_dt.now.assert_called_once()
    assert patched_main["build"].call_args[0][1] == fixed


def test_transcribe_exception_propagates_and_skips_save(patched_main):
    patched_main["transcribe"].side_effect = RuntimeError("vosk failed")
    with pytest.raises(RuntimeError, match="vosk failed"):
        process_audio_file("audio.wav", "model/path")
    patched_main["build"].assert_not_called()
    patched_main["save"].assert_not_called()


def test_save_exception_propagates(patched_main):
    patched_main["save"].side_effect = OSError("disk full")
    with pytest.raises(IOError, match="disk full"):
        process_audio_file("audio.wav", "model/path")
