"""Parsers for rows loaded into `staging.river_vpn_events_staging`."""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator
from datetime import UTC, datetime
from pathlib import Path

VpnEventRow = dict[str, int | str | datetime | None]

LINE_RX = re.compile(r"^(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}) (\S+) (.*)$")


def parse_vpn_line(line_number: int, line: str) -> VpnEventRow:
    """Parse one `openvpn.log` line into the staging table shape."""
    record: VpnEventRow = {
        "line_number": line_number,
        "event_timestamp": None,
        "client": None,
        "message": "",
    }

    stripped_line = line.rstrip("\n")
    match = LINE_RX.match(stripped_line)
    if not match:
        record["message"] = stripped_line.strip()
        return record

    date_str, time_str, client, message = match.groups()
    record["client"] = client
    record["message"] = message.strip() if message else ""

    ts_str = f"{date_str} {time_str}"
    try:
        event_timestamp = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)
    except ValueError:
        event_timestamp = None
    record["event_timestamp"] = event_timestamp

    return record


def parse_vpn_lines(lines: Iterable[str]) -> list[VpnEventRow]:
    """Parse all OpenVPN log lines into staging rows."""
    return [parse_vpn_line(line_number, line) for line_number, line in enumerate(lines, start=1)]


def parse_vpn_file(path: str | Path) -> Iterator[VpnEventRow]:
    """Yield parsed staging rows from an OpenVPN log file."""
    with Path(path).open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            yield parse_vpn_line(line_number, line)
