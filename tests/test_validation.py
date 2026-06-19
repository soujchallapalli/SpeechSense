import datetime

from speechsense.validation import validate_row


class mocklogging:
    def __init__(self) -> None:
        return

    def error(self, message: str) -> None:
        return

    def info(self, message: str) -> list:
        return

    def warning(self, message: str) -> None:
        return


# return none if there is no row with the given id
def test_all_correct_data():
    context = {"logging": mocklogging()}
    raw_row = {
        "_id": 1,
        "name": "SpeechSenseUnitTest",
        "raw_text_vosk": "A test row for unit testing.",
        "time_taken_sec": 5,
        "timestamp": "2026-06-19T23:25:15",
    }
    validated_row = validate_row(context, raw_row)
    assert validated_row == raw_row


# return the row if it exists
def test_all_incorrect_data():
    context = {"logging": mocklogging()}
    raw_row = {"_id": "1", "name": 123, "raw_text_vosk": 456, "time_taken_sec": "7", "timestamp": "no time stamp"}
    validated_row = validate_row(context, raw_row)
    assert validated_row == {
        "_id": "1",
        "name": "UNKNOWN_SPEAKER",
        "raw_text_vosk": "UNRECOGNIZED_TEXT",
        "time_taken_sec": 0,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    }


# return empty list if the DB is empty without failing
def test_incorrect_name():
    context = {"logging": mocklogging()}
    raw_row = {
        "_id": 1,
        "name": 123,
        "raw_text_vosk": "A test row for unit testing.",
        "time_taken_sec": 5,
        "timestamp": "2026-06-19T23:25:15",
    }
    validated_row = validate_row(context, raw_row)
    assert validated_row == {
        "_id": 1,
        "name": "UNKNOWN_SPEAKER",
        "raw_text_vosk": "A test row for unit testing.",
        "time_taken_sec": 5,
        "timestamp": "2026-06-19T23:25:15",
    }


# return all rows if the DB has data
def test_incorrect_timestamp():
    context = {"logging": mocklogging()}
    raw_row = {
        "_id": 1,
        "name": "SpeechSenseUnitTest",
        "raw_text_vosk": "A test row for unit testing.",
        "time_taken_sec": 5,
        "timestamp": "no time stamp",
    }
    validated_row = validate_row(context, raw_row)
    assert validated_row == {
        "_id": 1,
        "name": "SpeechSenseUnitTest",
        "raw_text_vosk": "A test row for unit testing.",
        "time_taken_sec": 5,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    }


# return all rows if the DB has data
def test_incomplete_timestamp():
    context = {"logging": mocklogging()}
    raw_row = {
        "_id": 1,
        "name": "SpeechSenseUnitTest",
        "raw_text_vosk": "A test row for unit testing.",
        "time_taken_sec": 5,
        "timestamp": "23:15:10",
    }
    validated_row = validate_row(context, raw_row)
    assert validated_row == {
        "_id": 1,
        "name": "SpeechSenseUnitTest",
        "raw_text_vosk": "A test row for unit testing.",
        "time_taken_sec": 5,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%dT23:15:10"),
    }


# test insert row
def test_incorrect_time_taken_sec():
    context = {"logging": mocklogging()}
    raw_row = {
        "_id": 1,
        "name": "SpeechSenseUnitTest",
        "raw_text_vosk": "A test row for unit testing.",
        "time_taken_sec": "123",
        "timestamp": "2026-06-19T23:25:15",
    }
    validated_row = validate_row(context, raw_row)
    assert validated_row == {
        "_id": 1,
        "name": "SpeechSenseUnitTest",
        "raw_text_vosk": "A test row for unit testing.",
        "time_taken_sec": 0,
        "timestamp": "2026-06-19T23:25:15",
    }


# test update row
def test_incorrect_question_flag():
    context = {"logging": mocklogging()}
    raw_row = {
        "_id": 1,
        "name": "SpeechSenseUnitTest",
        "raw_text_vosk": "A test row for unit testing.",
        "time_taken_sec": 5,
        "timestamp": "2026-06-19T23:25:15",
        "question_flag": "text",
    }
    validated_row = validate_row(context, raw_row)
    assert validated_row == {
        "_id": 1,
        "name": "SpeechSenseUnitTest",
        "raw_text_vosk": "A test row for unit testing.",
        "time_taken_sec": 5,
        "timestamp": "2026-06-19T23:25:15",
        "question_flag": False,
    }


# test update row
def test_text_question_flag():
    context = {"logging": mocklogging()}
    raw_row = {
        "_id": 1,
        "name": "SpeechSenseUnitTest",
        "raw_text_vosk": "A test row for unit testing.",
        "time_taken_sec": 5,
        "timestamp": "2026-06-19T23:25:15",
        "question_flag": "yes",
    }
    validated_row = validate_row(context, raw_row)
    assert validated_row == {
        "_id": 1,
        "name": "SpeechSenseUnitTest",
        "raw_text_vosk": "A test row for unit testing.",
        "time_taken_sec": 5,
        "timestamp": "2026-06-19T23:25:15",
        "question_flag": True,
    }
