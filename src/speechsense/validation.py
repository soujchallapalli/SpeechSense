import datetime
from typing import Any


def clean_string(context: dict, value: Any, default: str = "EMPTY") -> str:
    if value is None or type(value) is not str or str(value).strip() == "":
        context["logging"].warning(f"[PIPELINE WARNING]: Invalid string '{value}' found. Defaulting to '{default}'")
        return default

    cleaned = str(value).strip()
    return cleaned


def clean_numeric(context: dict, value: Any, default: float = 0.0) -> float:
    if value is None or str(value).strip() == "" or not isinstance(value, int | float):
        context["logging"].warning(
            f"[PIPELINE WARNING]: Invalid numeric value '{value}' found. Defaulting to '{default}'"
        )
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        context["logging"].warning(f"[PIPELINE WARNING]: Cannot convert '{value}' to float. Defaulting to {default}")
        return default


def clean_bool(context: dict, value: Any, default: bool = False) -> bool:
    if value is None or str(value).strip() == "":
        return default
    if isinstance(value, bool):
        return value
    str_val = str(value).strip().lower()
    if str_val in ["true", "1", "yes"]:
        return True
    elif str_val in ["false", "0", "no"]:
        return False
    else:
        context["logging"].warning(f"[PIPELINE WARNING]: Cannot convert '{value}' to boolean. Defaulting to {default}")
        return default


def reformat_timestamp(
    context: dict, value: Any, default: str = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
) -> str:
    if value is None or str(value).strip() == "":
        return default

    clean_val = str(value).strip()

    # Common formats your DB might throw at you
    formats_to_try = [
        "%Y-%m-%dT%H:%M:%SZ",  # Already matching our target format
        "%Y-%m-%dT%H:%M:%S",  # Already correct format
        "%Y-%m-%d %H:%M:%S",  # Standard SQL Space separated
        "%H:%M:%S",  # Just the time (we will prepend today's date)
        "%d/%m/%Y %H:%M:%S",  # European format
    ]

    for fmt in formats_to_try:
        try:
            parsed_dt = datetime.datetime.strptime(clean_val, fmt)

            # Special case: If the input was *just* a time (like "10:00:05"),
            # datetime defaults the year to 1900. Let's force it to 2026.
            if fmt == "%H:%M:%S":
                parsed_dt = parsed_dt.replace(
                    year=datetime.datetime.now().year,
                    month=datetime.datetime.now().month,
                    day=datetime.datetime.now().day,
                )
            return parsed_dt.strftime("%Y-%m-%dT%H:%M:%S")
        except ValueError:
            continue

    # If it loops through all formats and can't read it
    context["logging"].error(f"[PIPELINE ERROR]: Unrecognized timestamp format '{value}'. Defaulting to {default}")
    return default


def validate_row(context: dict, row: dict) -> dict:
    print(f"\n--- Processing Pipeline Step for Row ID: {row['_id']} ---")

    FIELD_TYPES_AND_DEFAULTS: dict[str, tuple[str, Any]] = {
        "name": ("string", "UNKNOWN_SPEAKER"),
        "raw_text_vosk": ("string", "UNRECOGNIZED_TEXT"),
        "time_taken_sec": ("numeric", 0.0),
        "timestamp": ("timestamp", datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")),
        "question_flag": ("boolean", False),
        "num_words": ("numeric", 0),
        "text_size_chars": ("numeric", 0),
        "speech_rate_wps": ("numeric", 0.0),
        "speaker_turn_id": ("numeric", 0),
    }

    new_row: dict[str, Any] = {}
    for key, value in row.items():
        expected_type, default_value = FIELD_TYPES_AND_DEFAULTS.get(key, (None, ""))

        if expected_type == "timestamp":
            new_row[key] = reformat_timestamp(context, value, str(default_value))
        elif expected_type == "string":
            new_row[key] = clean_string(context, value, str(default_value))
        elif expected_type == "boolean":
            new_row[key] = clean_bool(context, value, bool(default_value))
        elif expected_type == "numeric":
            new_row[key] = clean_numeric(context, value, float(default_value))
        else:
            new_row[key] = value  # Keep as is for other types
    return new_row
