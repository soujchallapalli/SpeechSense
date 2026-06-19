import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from time import sleep

from speechsense.analyse import load_data, print_report, write_report
from speechsense.config import (
    AUDIO_FILE,
    CORRECTED_CSV_OUTPUT_PATH,
    CSV_OUTPUT_PATH,
    RECORDING_START_TIME,
    VOSK_MODEL_DIR,
)
from speechsense.correction_pipeline import process_pipeline
from speechsense.speech_to_text.speech_to_text_pipeline import process_audio_file

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# Transcribes and performs speaker diarization on the audio file
def transcribe_diarize_audio(
    context: dict,
    audio_file: str,
    vosk_model_dir_name: str,
    recording_start_time: datetime,
) -> None:
    context["logging"].info("Transcribing the audio file to text and speaker diarization...")

    process_audio_file(
        audio_file,
        vosk_model_dir_name,
        recording_start_time=recording_start_time,
    )


# Initializes the CSV (or recording) and returns the output CSV path
def record_to_file(context: dict) -> str:
    context["logging"].info("csv is initialized")
    return str(Path(__file__).resolve().parents[2] / "data" / "mock_stage_5.csv")


# Correct the Transcript With AI
def sanitize_with_ai(context: dict, row: str) -> str:
    sleep(3)
    row = row.rstrip("\n") + ",sanitized"
    context["logging"].info("AI processing done")
    return row


# how many times this speaker talked so far
def add_speaker_counter(context: dict, row: str) -> str:
    sleep(3)
    row = row.rstrip("\n") + ",speaker_counter"
    context["logging"].info("speaker counter added")
    return row


# Validate the CSV
def validate(context: dict, row: str) -> str:
    sleep(3)
    row = row.rstrip("\n") + ",validated"
    context["logging"].info("CSV is validated")
    return row


def write_to_new_csv(context: dict, row: str) -> None:
    mutex = context["mutex"]
    sleep(3)
    mutex.acquire()
    context["logging"].info(f"row is written to csv:{row}")
    mutex.release()
    return


# all the parllel processing
def process_single_row(context: dict, row: str) -> None:
    sanitized_row = sanitize_with_ai(context, row)
    processed_row = validate(context, sanitized_row)
    write_to_new_csv(context, processed_row)
    return


def process(context: dict) -> None:
    context["logging"].info("Starting the processing pipeline...")
    transcribe_diarize_audio(context, AUDIO_FILE, VOSK_MODEL_DIR, RECORDING_START_TIME)
    process_pipeline(input_path=CSV_OUTPUT_PATH, output_path=CORRECTED_CSV_OUTPUT_PATH)
    context["logging"].info("Complete: diarized transcript corrected with AI -> %s", CORRECTED_CSV_OUTPUT_PATH)

    with open(CORRECTED_CSV_OUTPUT_PATH) as f:
        rows = f.readlines()

    with ThreadPoolExecutor(max_workers=15) as executor:
        _ = [executor.submit(process_single_row, context, row) for row in rows]

    df = load_data(CORRECTED_CSV_OUTPUT_PATH)
    report_path = str(Path(__file__).resolve().parents[2] / "docs" / "report.md")
    write_report(df, report_path)
    print_report(df)
