"""Parsers for rows loaded into `staging.ishaan_http_access_staging`."""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlparse

HttpAccessRow = dict[str, int | str | datetime | None]

# Combined Log Format: ip - - [day/Mon/year:HH:MM:SS +tz] "METHOD /path HTTP/x.x" status bytes "referer" "ua"
LINE_RX = re.compile(
    r"^(\S+)\s+-\s+-\s+"
    r"\[(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}\s+[+-]\d{4})\]\s+"
    r'"(\S+)\s+(\S+)\s+\S+"\s+'
    r"(\d{3})\s+"
    r"(\d+|-)"
)


def parse_http_access_line(line_number: int, line: str) -> HttpAccessRow:
    """Parse one Apache access log line into the staging table shape."""
    record: HttpAccessRow = {
        "line_number": line_number,
        "event_timestamp": None,
        "client_ip": None,
        "http_method": None,
        "request_url": None,
        "url_path": None,
        "query_string": None,
        "status_code": None,
        "bytes_sent": None,
    }

    stripped_line = line.rstrip("\n")
    match = LINE_RX.match(stripped_line)
    if not match:
        return record

    client_ip, ts_str, http_method, request_url, status_code, bytes_sent = match.groups()

    record["client_ip"] = client_ip
    record["http_method"] = http_method
    record["request_url"] = request_url

    parsed = urlparse(request_url)
    record["url_path"] = parsed.path or None
    record["query_string"] = parsed.query or None

    record["status_code"] = int(status_code)
    record["bytes_sent"] = int(bytes_sent) if bytes_sent != "-" else None

    try:
        record["event_timestamp"] = datetime.strptime(ts_str, "%d/%b/%Y:%H:%M:%S %z").astimezone(
            UTC
        )
    except ValueError:
        pass

    return record


def parse_http_access_lines(lines: Iterable[str]) -> list[HttpAccessRow]:
    """Parse all Apache access log lines into staging rows."""
    return [
        parse_http_access_line(line_number, line) for line_number, line in enumerate(lines, start=1)
    ]


def parse_http_access_file(path: str | Path) -> Iterator[HttpAccessRow]:
    """Yield parsed staging rows from an Apache access log file."""
    with Path(path).open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            yield parse_http_access_line(line_number, line)
