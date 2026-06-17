import datetime
from typing import Any


def clean_string(value: Any, default: str = "N/A") -> str:
    if value is None:
        return default

    cleaned = str(value).strip()
    return cleaned if cleaned != "" else default


def clean_numeric(value: Any, default: float = 0.0) -> float:
    if value is None or str(value).strip() == "":
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        print(f"[PIPELINE WARNING]: Cannot convert '{value}' to float. Defaulting to {default}")
        return default


def reformat_timestamp(value: Any, default: str = "2026-01-01T00:00:00") -> str:
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
    print(f"[PIPELINE ERROR]: Unrecognized timestamp format '{value}'. Defaulting to {default}")
    return default


def validate_row(row: dict) -> dict:
    print(f"\n--- Processing Pipeline Step for Row ID: {row['_id']} ---")

    new_row = {}
    for key, value in row.items():
        if key == "timestamp":
            new_row[key] = reformat_timestamp(value)
        if isinstance(value, str):
            new_row[key] = clean_string(value)
        elif isinstance(value, int | float):
            new_row[key] = clean_numeric(value)
        else:
            new_row[key] = value  # Keep as is for other types
    return new_row
