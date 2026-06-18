import os
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()


HUGGINGFACE_TOKEN = os.getenv("HF_TOKEN", None)
CSV_OUTPUT_PATH = "output/meeting_transcript.csv"
CSV_HEADERS = ["timestamp", "name", "raw_text_vosk", "time_taken_sec"]

VOSK_MODEL_DIR = "vosk-model-en-us-0.42-gigaspeech"
AUDIO_FILE = "datasets/short_meeting.wav"

SPEAKER_NAME_MAP = {"SPEAKER_00": "Stefan", "SPEAKER_01": "Souji", "SPEAKER_02": "Rania", "SPEAKER_03": "Karley"}

RECORDING_START_TIME = datetime(2026, 4, 28, 10, 0, 0)

# Number of audio frames read per chunk during recognition.
FRAMES_PER_READ = 4000
DIARIZATION_MODEL = "pyannote/speaker-diarization-3.1"
