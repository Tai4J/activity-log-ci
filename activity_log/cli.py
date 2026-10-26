"""Command-line entry point: python -m activity_log.cli data/log.csv"""

from __future__ import annotations

import sys
from pathlib import Path

from .core import banner, by_activity, parse_line, total_minutes


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("usage: python -m activity_log.cli <log.csv>", file=sys.stderr)
        return 2
    lines = Path(args[0]).read_text(encoding="utf-8").splitlines()
    entries = [parse_line(line) for line in lines if line.strip() and not line.startswith("#")]
    print(banner())
    for activity, minutes in by_activity(entries).items():
        print(f"{activity:<12}{minutes:>6} min")
    print(f"{'TOTAL':<12}{total_minutes(entries):>6} min")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
