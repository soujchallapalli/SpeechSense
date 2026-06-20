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
from speechsense.database.processed_db import ProcessedRepository
from speechsense.speech_to_text.speech_to_text_pipeline import process_audio_file
from speechsense.validation import validate_row

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


# Correct the Transcript With AI
def sanitize_with_ai(context: dict, row: dict) -> dict:
    sleep(3)
    context["logging"].info("AI processing done")
    return row


# how many times this speaker talked so far
def add_speaker_counter(context: dict, row: dict) -> dict:
    sleep(3)
    context["logging"].info("speaker counter added")
    return row


def write_processed_data(context: dict, row: dict) -> None:
    mutex = context["mutex"]
    sleep(3)
    mutex.acquire()
    ProcessedTranscriptDB: ProcessedRepository = context["ProcessedTranscript"]
    inserted_id = ProcessedTranscriptDB.insert(row["_id"], row)
    context["logging"].info(f"Inserted row {inserted_id} into ProcessedRepository DB.")
    mutex.release()
    return


# all the parllel processing
def process_single_row(context: dict, row: dict) -> None:
    sanitized_row = sanitize_with_ai(context, row)
    processed_row = validate_row(context, sanitized_row)
    write_processed_data(context, processed_row)
    return


def process(context: dict) -> None:
    context["logging"].info("Starting the processing pipeline...")
    transcribe_diarize_audio(context, AUDIO_FILE, VOSK_MODEL_DIR, RECORDING_START_TIME)
    process_pipeline(input_path=CSV_OUTPUT_PATH, output_path=CORRECTED_CSV_OUTPUT_PATH)
    context["logging"].info("Complete: diarized transcript corrected with AI -> %s", CORRECTED_CSV_OUTPUT_PATH)

    # with open(CORRECTED_CSV_OUTPUT_PATH) as f:
    #     rows = f.readlines()

    df = load_data(CORRECTED_CSV_OUTPUT_PATH)
    with ThreadPoolExecutor(max_workers=15) as executor:
        list(executor.map(lambda row: process_single_row(context, row), context["transcript_db"].get_all()))
    report_path = str(Path(__file__).resolve().parents[2] / "docs" / "report.md")
    write_report(df, report_path)
    print_report(df)
