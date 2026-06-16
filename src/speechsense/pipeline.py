from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from time import sleep

from speechsense.analyse import load_data, print_report


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
    csv_path = record_to_file(context)
    with open(csv_path) as rows, ThreadPoolExecutor(max_workers=15) as executor:
        list(executor.map(lambda row: process_single_row(context, row), rows))
    df = load_data(csv_path)
    print_report(df)
