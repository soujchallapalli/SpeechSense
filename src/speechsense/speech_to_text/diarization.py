import logging
import warnings
from typing import cast

import soundfile as sf
import torch
from pyannote.audio import Pipeline
from pyannote.audio.pipelines.utils.hook import ProgressHook

from speechsense.config import DIARIZATION_MODEL, HUGGINGFACE_TOKEN

warnings.filterwarnings("ignore", category=UserWarning, module="pyannote")

# Configure logging to show INFO level and above
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

_pipeline: Pipeline | None = None


def _get_pipeline() -> Pipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = Pipeline.from_pretrained(DIARIZATION_MODEL, token=HUGGINGFACE_TOKEN)
    return cast(Pipeline, _pipeline)


def diarize_audio(file_path: str) -> list[dict]:
    """Run speaker diarization and return speaker turns with timestamps."""
    waveform, sample_rate = sf.read(file_path, dtype="float32", always_2d=True)
    waveform = torch.from_numpy(waveform.T)
    audio_input = {"waveform": waveform, "sample_rate": sample_rate}

    with ProgressHook() as hook:
        diarization = _get_pipeline()(audio_input, hook=hook)

    annotation = diarization.speaker_diarization

    speaker_turns = []
    for segment, _, speaker in annotation.itertracks(yield_label=True):
        speaker_turns.append({"start": segment.start, "end": segment.end, "speaker": speaker})
    return speaker_turns


def assign_speakers(transcript_segments: list[dict], speaker_turns: list[dict]) -> list[dict]:
    """Assign speaker to each transcript segment by maximum time overlap."""
    results = []
    for seg in transcript_segments:
        seg_start, seg_end = seg["start"], seg["end"]
        best_speaker = "UNKNOWN"
        best_overlap = 0.0

        for turn in speaker_turns:
            overlap = min(seg_end, turn["end"]) - max(seg_start, turn["start"])
            if overlap > best_overlap:
                best_overlap = overlap
                best_speaker = turn["speaker"]

        results.append({"speaker": best_speaker, "start": seg_start, "end": seg_end, "text": seg["text"]})
    return results


def merge_consecutive_speakers(diarized_segments: list[dict]) -> list[dict]:
    """Merge consecutive segments from the same speaker into one turn."""
    if not diarized_segments:
        return []

    merged = []
    current = diarized_segments[0].copy()

    for seg in diarized_segments[1:]:
        if seg["speaker"] == current["speaker"]:
            current["text"] += " " + seg["text"]
            current["end"] = seg["end"]
        else:
            merged.append(current)
            current = seg.copy()
    merged.append(current)
    return merged
