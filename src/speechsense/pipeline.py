from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from time import sleep

from speechsense.analyse import load_data, print_report, write_report
from speechsense.database.processed_db import ProcessedRepository
from speechsense.validation import validate_row


# Initializes the CSV (or recording) and returns the output CSV path
def record_to_file(context: dict) -> str:
    context["logging"].info("csv is initialized")
    return str(Path(__file__).resolve().parents[2] / "data" / "mock_stage_5.csv")


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
    inserted_id = ProcessedTranscriptDB.insert(row)
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
    csv_path = record_to_file(context)
    with ThreadPoolExecutor(max_workers=15) as executor:
        list(executor.map(lambda row: process_single_row(context, row), context["transcript_db"].get_all()))
    df = load_data(csv_path)
    report_path = str(Path(__file__).resolve().parents[2] / "docs" / "report.md")
    write_report(df, report_path)
    print_report(df)
