"""Core logic for the activity log."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date

APP_NAME = "Activity Tracker"
VERSION = "0.1.0"


@dataclass(frozen=True)
class Entry:
    day: date
    activity: str
    minutes: int


def banner() -> str:
    return f"{APP_NAME} v{VERSION}"


def parse_line(line: str) -> Entry:
    """Parse one line in the form 'YYYY-MM-DD,activity,minutes'."""
    parts = [p.strip() for p in line.split(",")]
    if len(parts) != 3:
        raise ValueError(f"expected 3 fields, got {len(parts)}: {line!r}")
    day_s, activity, minutes_s = parts
    if not activity:
        raise ValueError("activity must not be empty")
    minutes = int(minutes_s)
    if minutes <= 0:
        raise ValueError("minutes must be positive")
    return Entry(date.fromisoformat(day_s), activity, minutes)


def total_minutes(entries: Iterable[Entry]) -> int:
    return sum(e.minutes for e in entries)


def by_activity(entries: Iterable[Entry]) -> dict[str, int]:
    totals: dict[str, int] = {}
    for e in entries:
        totals[e.activity] = totals.get(e.activity, 0) + e.minutes
    return dict(sorted(totals.items(), key=lambda kv: (-kv[1], kv[0])))
