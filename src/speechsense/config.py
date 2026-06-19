import logging
import os
import threading
from datetime import datetime

from dotenv import load_dotenv

from speechsense.data.processed_db import ProcessedRepository
from speechsense.data.transcript_db import TranscriptRepository

load_dotenv()


HUGGINGFACE_TOKEN = os.getenv("HF_TOKEN", None)
CSV_OUTPUT_PATH = "output/meeting_transcript.csv"
CORRECTED_CSV_OUTPUT_PATH = "output/meeting_transcript_corrected.csv"
CSV_HEADERS = ["timestamp", "name", "raw_text_vosk", "time_taken_sec"]

VOSK_MODEL_DIR = "vosk-model-en-us-0.42-gigaspeech"
AUDIO_FILE = "datasets/short_meeting.wav"

SPEAKER_NAME_MAP = {"SPEAKER_00": "Stefan", "SPEAKER_01": "Souji", "SPEAKER_02": "Rania", "SPEAKER_03": "Karley"}

RECORDING_START_TIME = datetime(2026, 4, 28, 10, 0, 0)

# Number of audio frames read per chunk during recognition.
FRAMES_PER_READ = 4000
DIARIZATION_MODEL = "pyannote/speaker-diarization-3.1"

OLLAMA_MODEL = "gemma3"
OLLAMA_URL = "http://localhost:11434/api/generate"


def initialize() -> dict:
    """
    Initializes the configuration for the SpeechSense application.
    This function sets up logging, loads environment variables, and performs any other necessary
    configuration steps required before the application starts.
    """

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    # set up the input and output DBs
    transcript_db = TranscriptRepository()
    processed_db = ProcessedRepository()

    # Set up the context dictionary to be passed around the application
    context = {
        "mutex": threading.Lock(),
        "logging": logging,
        "transcript_db": transcript_db,
        "processed_db": processed_db,
    }

    return context
