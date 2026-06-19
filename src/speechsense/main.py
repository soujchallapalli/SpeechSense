import sys
from pathlib import Path

from speechsense.config import initialize
from speechsense.pipeline import process
from speechsense.analyse import main as run_analysis


def foo(bar: str) -> str:
    """Summary line."""
    return bar


def main() -> None:
    if len(sys.argv) == 2:
        csv_path = sys.argv[1]
        if not Path(csv_path).exists():
            print(f"Error: file not found: {csv_path}")
            sys.exit(1)
        run_analysis(csv_path)
    else:
        # Fallback to the default pipeline if no CSV is provided
        context = initialize()
        process(context)


if __name__ == "__main__":  # pragma: no cover
    main()