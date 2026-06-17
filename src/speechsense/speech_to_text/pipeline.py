import logging
from datetime import datetime

from .transcription import transcribe_wav_with_vosk
from .utils import build_csv_rows, save_csv

# Configure logging to show INFO level and above
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def process_audio_file(audio_path: str, model_path: str, recording_start_time: datetime | None = None) -> None:
    """Transcribe and save CSV."""
    if recording_start_time is None:
        recording_start_time = datetime.now()

    transcript_segments = transcribe_wav_with_vosk(audio_path, model_path)

    csv_rows = build_csv_rows(transcript_segments, recording_start_time)
    save_csv(csv_rows)

    logging.info("CSV preview:")
    logging.info(csv_rows)
