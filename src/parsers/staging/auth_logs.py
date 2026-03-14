"""Parsers for rows loaded into `staging.river_auth_log_staging`."""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator
from datetime import UTC, datetime
from pathlib import Path

AuthLogRow = dict[str, int | str | datetime | None]

TARGET_YEAR = 2022

LINE_RX = re.compile(
    r"^([A-Z][a-z]{2})\s+(\d{1,2})\s+(\d{2}:\d{2}:\d{2})\s+(\S+)\s+([^\[\s]+)(?:\[(\d+)\])?:\s+(.*)$"
)


def parse_auth_line(line_number: int, line: str) -> AuthLogRow:
    """Parse one `auth.log` line into the staging table shape."""
    record: AuthLogRow = {
        "line_number": line_number,
        "event_timestamp": None,
        "hostname": None,
        "process_name": None,
        "pid": None,
        "message": "",
    }

    stripped_line = line.rstrip("\n")
    match = LINE_RX.match(stripped_line)
    if not match:
        record["message"] = stripped_line.strip()
        return record

    month, day, time_str, hostname, process_name, pid, message = match.groups()
    record["hostname"] = hostname
    record["process_name"] = process_name.strip() if process_name else None
    record["pid"] = int(pid) if pid else None
    record["message"] = message.strip() if message else ""

    ts_str = f"{TARGET_YEAR}-{month}-{int(day):02d} {time_str}"
    try:
        event_timestamp = datetime.strptime(ts_str, "%Y-%b-%d %H:%M:%S").replace(tzinfo=UTC)
    except ValueError:
        event_timestamp = None
    record["event_timestamp"] = event_timestamp

    return record


def parse_auth_lines(lines: Iterable[str]) -> list[AuthLogRow]:
    """Parse all auth log lines into staging rows."""
    return [parse_auth_line(line_number, line) for line_number, line in enumerate(lines, start=1)]


def parse_auth_file(path: str | Path) -> Iterator[AuthLogRow]:
    """Yield parsed staging rows from an auth log file."""
    with Path(path).open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            yield parse_auth_line(line_number, line)
