import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from speechsense.config import AUDIO_FILE, RECORDING_START_TIME, VOSK_MODEL_DIR
from speechsense.speech_to_text.pipeline import process_audio_file


def main() -> None:
    process_audio_file(AUDIO_FILE, VOSK_MODEL_DIR, recording_start_time=RECORDING_START_TIME)


if __name__ == "__main__":
    main()
