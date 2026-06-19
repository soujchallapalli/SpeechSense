import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from speechsense.config import SPEAKER_NAME_MAP
from speechsense.speech_to_text.diarization import assign_speakers, diarize_audio, merge_consecutive_speakers

from .transcription import transcribe_wav_with_vosk
from .utils import build_csv_rows, format_transcript, save_csv

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def process_audio_file(audio_path: str, model_path: str, recording_start_time: datetime | None = None) -> None:
    """Transcribe + diarize in parallel, merge, save CSV."""
    if recording_start_time is None:
        recording_start_time = datetime.now()

    with ThreadPoolExecutor(max_workers=2) as executor:
        future_transcript = executor.submit(transcribe_wav_with_vosk, audio_path, model_path)
        future_diarization = executor.submit(diarize_audio, audio_path)

        transcript_segments = future_transcript.result()
        speaker_turns = future_diarization.result()

    diarized = assign_speakers(transcript_segments, speaker_turns)
    merged = merge_consecutive_speakers(diarized)

    logging.info("\n--- Transcript ---")
    logging.info(format_transcript(merged, SPEAKER_NAME_MAP))

    csv_rows = build_csv_rows(merged, recording_start_time)
    save_csv(csv_rows)
    logging.info("CSV preview:")
    logging.info(csv_rows)
