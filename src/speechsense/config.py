from datetime import datetime

from dotenv import load_dotenv

load_dotenv()


CSV_OUTPUT_PATH = "output/meeting_transcript.csv"
CSV_HEADERS = ["timestamp", "raw_text_vosk", "time_taken_sec"]

VOSK_MODEL_DIR = "vosk-model-en-us-0.42-gigaspeech"
AUDIO_FILE = "datasets/short_meeting.wav"

RECORDING_START_TIME = datetime(2026, 4, 28, 10, 0, 0)

# Number of audio frames read per chunk during recognition.
FRAMES_PER_READ = 4000
