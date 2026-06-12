import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from time import sleep

# Configure logging to show INFO level and above
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# Initializes the CSV (or recording) and returns the output CSV path
def record_to_file() -> str:
    logging.info("csv is initialized")
    return str(Path(__file__).resolve().parents[2] / "tests" / "mock_data.csv")


# Correct the Transcript With AI
def sanitize_with_ai(context: dict, row: str) -> str:
    sleep(3)
    row = row.rstrip("\n") + ",sanitized"
    logging.info("AI processing done")
    return row


# how many times this speaker talked so far
def add_speaker_counter(context: dict, row: str) -> str:
    sleep(3)
    row = row.rstrip("\n") + ",speaker_counter"
    logging.info("speaker counter added")
    return row


# Enrich the Dataset With Python
def analyze(context: dict, rows: list) -> list:
    sleep(3)
    for row in rows:
        row = row.rstrip("\n") + ",analyzed"
    logging.info("data is analyzed with python")
    return rows


# Validate the CSV
def validate(context: dict, row: str) -> str:
    sleep(3)
    row = row.rstrip("\n") + ",validated"
    logging.info("CSV is validated")
    return row


def write_to_new_csv(context: dict, row: str) -> None:
    mutex = context["mutex"]
    sleep(3)
    mutex.acquire()
    logging.info(f"row is written to csv:{row}")
    mutex.release()
    return


# all the parllel processing
def process_single_row(context: dict, row: str) -> None:
    sanitized_row = sanitize_with_ai(context, row)
    processed_row = validate(context, sanitized_row)
    write_to_new_csv(context, processed_row)
    return


def process() -> None:
    csv_path = record_to_file()
    context = {"mutex": threading.Lock()}
    with open(csv_path) as rows, ThreadPoolExecutor(max_workers=15) as executor:
        list(executor.map(lambda row: process_single_row(context, row), rows))
        analyze(context, rows.readlines())
