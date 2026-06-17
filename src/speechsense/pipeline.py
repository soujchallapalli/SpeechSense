from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from time import sleep

from speechsense.validation import validate_row


# Initializes the CSV (or recording) and returns the output CSV path
def record_to_file(context: dict) -> str:
    context["logging"].info("csv is initialized")
    return str(Path(__file__).resolve().parents[2] / "tests" / "mock_data.csv")


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


# Enrich the Dataset With Python
def analyze(context: dict, rows: list) -> list:
    sleep(3)
    context["logging"].info("data is analyzed with python")
    return rows


def write_to_new_csv(context: dict, row: dict) -> None:
    mutex = context["mutex"]
    sleep(3)
    mutex.acquire()
    context["logging"].info(f"row is written to csv:{row}")
    mutex.release()
    return


# all the parllel processing
def process_single_row(context: dict, row: dict) -> None:
    sanitized_row = sanitize_with_ai(context, row)
    processed_row = validate_row(sanitized_row)
    write_to_new_csv(context, processed_row)
    return


def process(context: dict) -> None:
    with ThreadPoolExecutor(max_workers=15) as executor:
        list(executor.map(lambda row: process_single_row(context, row), context["transcript_db"].get_all()))
