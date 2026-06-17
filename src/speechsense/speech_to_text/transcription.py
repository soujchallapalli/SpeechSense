import json
import logging
import os
import wave

from vosk import KaldiRecognizer, Model

from speechsense.config import FRAMES_PER_READ

# Configure logging to show INFO level and above
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def _validate_paths(audio_path: str, model_path: str) -> None:
    """Ensure both the Vosk model and the audio file exist."""
    if not os.path.exists(model_path):
        raise VoskModelNotFoundError(model_path)
    if not os.path.exists(audio_path):
        raise AudioFileNotFoundError(audio_path)


def _validate_wav_format(wf: wave.Wave_read) -> None:
    """Ensure the WAV is mono, 16-bit PCM, as Vosk requires."""
    if wf.getnchannels() != 1:
        raise InvalidWavFormat("mono", f"{wf.getnchannels()} channels")
    if wf.getsampwidth() != 2:
        raise InvalidWavFormat("16-bit", f"sample width {wf.getsampwidth()}")


def _build_recognizer(model_path: str, sample_rate: int) -> KaldiRecognizer:
    """Create a Vosk recognizer with word-level timing enabled."""
    model = Model(model_path)
    recognizer = KaldiRecognizer(model, sample_rate)
    recognizer.SetWords(True)
    return recognizer


def _to_segment(result: dict) -> dict | None:
    """Convert a raw Vosk result into a transcript segment, or None if empty."""
    if result.get("text") and result.get("result"):
        words = result["result"]
        return {
            "start": words[0]["start"],
            "end": words[-1]["end"],
            "text": result["text"],
        }
    return None


def _run_recognition(recognizer: KaldiRecognizer, wf: wave.Wave_read) -> list[dict]:
    """Stream audio frames through the recognizer and collect transcript segments."""
    segments: list[dict] = []

    while data := wf.readframes(FRAMES_PER_READ):
        if recognizer.AcceptWaveform(data) and (seg := _to_segment(json.loads(recognizer.Result()))):
            segments.append(seg)

    if seg := _to_segment(json.loads(recognizer.FinalResult())):
        segments.append(seg)

    return segments


def transcribe_wav_with_vosk(audio_path: str, model_path: str) -> list[dict]:
    """
    Transcribe a WAV file using Vosk.
    Returns segments with start, end, and text.

    Requirements:
    - WAV format, Mono, PCM 16-bit, 16kHz recommended

    Raises:
        FileNotFoundError: if the model or audio file does not exist.
        InvalidWavFormat: if the WAV is not mono 16-bit PCM.
    """
    _validate_paths(audio_path, model_path)

    with wave.open(audio_path, "rb") as wf:
        _validate_wav_format(wf)
        recognizer = _build_recognizer(model_path, wf.getframerate())

        logging.info("Vosk is transcribing...")
        return _run_recognition(recognizer, wf)


class VoskModelNotFoundError(FileNotFoundError):
    def __init__(self, path):
        super().__init__(f"Vosk model not found at: {path}")


class AudioFileNotFoundError(FileNotFoundError):
    def __init__(self, path):
        super().__init__(f"Audio file not found: {path}")


class InvalidWavFormat(ValueError):
    """Raised when a WAV file does not meet Vosk's format requirements."""

    def __init__(self, requirement: str, found: object) -> None:
        super().__init__(f"WAV must be {requirement}. Found {found}.")
