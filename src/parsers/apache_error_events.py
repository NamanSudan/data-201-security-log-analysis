"""Parsers for rows loaded into `staging.ishaan_apache_error_staging`."""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator
from datetime import UTC, datetime
from pathlib import Path

ApacheErrorRow = dict[str, int | str | datetime | None]

# Format: [Day Mon DD HH:MM:SS.usec YYYY] [module:level] [pid NNNN] [client ip:port] message[, referer: ...]
LINE_RX = re.compile(
    r"^\[(\w{3}\s+\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\.\d+\s+\d{4})\]\s+"
    r"\[([^\]]+)\]\s+"
    r"\[pid\s+\d+\]\s+"
    r"(?:\[client\s+(\d{1,3}(?:\.\d{1,3}){3})(?::\d+)?\]\s+)?"
    r"(.*)$"
)

REFERER_SUFFIX_RX = re.compile(r",\s*referer:\s+\S+$")


def parse_apache_error_line(line_number: int, line: str) -> ApacheErrorRow:
    """Parse one Apache error log line into the staging table shape."""
    record: ApacheErrorRow = {
        "line_number": line_number,
        "event_timestamp": None,
        "log_level": None,
        "client_ip": None,
        "message": "",
    }

    stripped_line = line.rstrip("\n")
    match = LINE_RX.match(stripped_line)
    if not match:
        record["message"] = stripped_line.strip()
        return record

    ts_str, module_level, client_ip, message = match.groups()

    # module_level is e.g. "authz_core:error" or "php7:error" — store as-is
    record["log_level"] = module_level
    record["client_ip"] = client_ip or None

    # strip trailing ", referer: ..." from message
    message = REFERER_SUFFIX_RX.sub("", message.strip()) if message else ""
    record["message"] = message

    try:
        record["event_timestamp"] = datetime.strptime(ts_str, "%a %b %d %H:%M:%S.%f %Y").replace(
            tzinfo=UTC
        )
    except ValueError:
        pass

    return record


def parse_apache_error_lines(lines: Iterable[str]) -> list[ApacheErrorRow]:
    """Parse all Apache error log lines into staging rows."""
    return [
        parse_apache_error_line(line_number, line)
        for line_number, line in enumerate(lines, start=1)
    ]


def parse_apache_error_file(path: str | Path) -> Iterator[ApacheErrorRow]:
    """Yield parsed staging rows from an Apache error log file."""
    with Path(path).open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            yield parse_apache_error_line(line_number, line)
