import logging
import threading

from dotenv import load_dotenv

from speechsense.data.processed_db import ProcessedRepository
from speechsense.data.transcript_db import TranscriptRepository


def initialize() -> dict:
    """
    Initializes the configuration for the SpeechSense application.
    This function sets up logging, loads environment variables, and performs any other necessary
    configuration steps required before the application starts.
    """

    # load environment variables from a .env file
    load_dotenv()

    # Configure logging to show INFO level and above
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
