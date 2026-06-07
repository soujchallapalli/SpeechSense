from collections.abc import Iterator


def foo(bar: str) -> str:
    """Summary line.

    Extended description of function.

    Args:
        bar: Description of input argument.

    Returns:
        Description of return value
    """

    return bar


# processess the whole file and returns the whole CSV
def record_to_file() -> str:
    print("csv is initialized")
    return "tests/mock_data.csv"


# Correct the Transcript With AI
def sanitize_with_AI(row: list):
    print("AI processing done")
    return


# how many times this speaker talked so far
def add_speaker_counter():
    print("speaker counter added")
    return


# Enrich the Dataset With Python
def analyze(row: Iterator):
    print("data is analyised with python")
    return


# Validate the CSV
def validate(row: Iterator):
    print("CSV is validated")
    return


## all the parllel processing
def process(row: Iterator):
    sanitize_with_AI(row)
    validate(row)
    analyze(row)

    return


if __name__ == "__main__":  # pragma: no cover
    csv_path = record_to_file()

    with open(csv_path) as f:
        it = iter(f)
        for row in it:
            process(row)
