from speechsense.initial_config import initialize
from speechsense.pipeline import process


def main() -> None:
    context = initialize()
    process(context)


if __name__ == "__main__":  # pragma: no cover
    main()
