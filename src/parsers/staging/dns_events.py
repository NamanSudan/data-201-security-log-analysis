"""Parsers for rows loaded into `staging.river_dns_events_staging`."""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator
from datetime import UTC, datetime
from pathlib import Path

DnsEventRow = dict[str, int | str | datetime | None]

MONTH = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12,
}
TARGET_YEAR = 2022

LINE_RX = re.compile(r"^(\S+)\s+(\d+)\s+(\d{2}:\d{2}:\d{2})\s+(\S+)\[(\d+)\]:\s+(.*)$")


def parse_dns_line(line_number: int, line: str) -> DnsEventRow:
    """Parse one `dnsmasq.log` line into the staging table shape."""
    record: DnsEventRow = {
        "line_number": line_number,
        "event_timestamp": None,
        "process": None,
        "message": "",
    }

    stripped_line = line.rstrip("\n")
    match = LINE_RX.match(stripped_line)
    if not match:
        record["message"] = stripped_line
        return record

    month_str, day, time_str, process_name, pid, message = match.groups()
    record["process"] = f"{process_name}[{pid}]"
    record["message"] = message

    try:
        month = MONTH[month_str]
        event_timestamp = datetime(
            TARGET_YEAR,
            month,
            int(day),
            int(time_str[:2]),
            int(time_str[3:5]),
            int(time_str[6:8]),
            tzinfo=UTC,
        )
    except (KeyError, ValueError):
        event_timestamp = None
    record["event_timestamp"] = event_timestamp

    return record


def parse_dns_lines(lines: Iterable[str]) -> list[DnsEventRow]:
    """Parse all dnsmasq log lines into staging rows."""
    return [parse_dns_line(line_number, line) for line_number, line in enumerate(lines, start=1)]


def parse_dns_file(path: str | Path) -> Iterator[DnsEventRow]:
    """Yield parsed staging rows from a dnsmasq log file."""
    with Path(path).open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            yield parse_dns_line(line_number, line)
