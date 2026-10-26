from datetime import date

import pytest

from activity_log import Entry, banner, by_activity, parse_line, total_minutes


def test_banner_contains_version():
    assert banner().startswith("Activity Log v")


def test_parse_line_ok():
    assert parse_line("2026-10-26, run, 30") == Entry(date(2026, 10, 26), "run", 30)


@pytest.mark.parametrize(
    "line",
    ["2026-10-26,run", "2026-10-26,,30", "2026-10-26,run,0", "not-a-date,run,30"],
)
def test_parse_line_rejects_bad_input(line):
    with pytest.raises(ValueError):
        parse_line(line)


def test_totals():
    entries = [
        Entry(date(2026, 10, 26), "run", 30),
        Entry(date(2026, 10, 26), "read", 45),
        Entry(date(2026, 10, 27), "run", 20),
    ]
    assert total_minutes(entries) == 95
    assert list(by_activity(entries).items()) == [("run", 50), ("read", 45)]
