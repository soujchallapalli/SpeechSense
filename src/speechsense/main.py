import sys
from pathlib import Path

from speechsense.analyse import main as run_analysis


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: speechsense <csv_path>")
        sys.exit(1)
    csv_path = sys.argv[1]
    if not Path(csv_path).exists():
        print(f"Error: file not found: {csv_path}")
        sys.exit(1)
    run_analysis(csv_path)


if __name__ == "__main__":
    main()
