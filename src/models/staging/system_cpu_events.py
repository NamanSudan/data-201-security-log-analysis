"""Parsers for rows loaded into `staging.ishaan_system_cpu_staging`."""

from __future__ import annotations

import json
from collections.abc import Iterable, Iterator
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

SystemCpuRow = dict[str, int | str | Decimal | datetime | None]


def _to_pct(value: float | int | None) -> Decimal | None:
    """Convert a Metricbeat fraction (0.0561) to a percentage (5.61)."""
    if value is None:
        return None
    return Decimal(str(round(float(value) * 100, 4)))


def parse_system_cpu_line(line_number: int, line: str) -> SystemCpuRow:
    """Parse one Metricbeat system.cpu JSON line into the staging table shape."""
    record: SystemCpuRow = {
        "line_number": line_number,
        "event_timestamp": None,
        "hostname": None,
        "cpu_total_pct": None,
        "cpu_user_pct": None,
        "cpu_system_pct": None,
        "cpu_idle_pct": None,
        "cpu_iowait_pct": None,
        "cpu_steal_pct": None,
        "cpu_softirq_pct": None,
        "cpu_cores": None,
    }

    stripped_line = line.rstrip("\n").strip()
    if not stripped_line:
        return record

    try:
        doc = json.loads(stripped_line)
    except json.JSONDecodeError:
        return record

    record["hostname"] = doc.get("host", {}).get("name")

    ts_str = doc.get("@timestamp")
    if ts_str:
        try:
            record["event_timestamp"] = datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(
                tzinfo=UTC
            )
        except ValueError:
            pass

    cpu = doc.get("system", {}).get("cpu", {})
    record["cpu_total_pct"] = _to_pct(cpu.get("total", {}).get("pct"))
    record["cpu_user_pct"] = _to_pct(cpu.get("user", {}).get("pct"))
    record["cpu_system_pct"] = _to_pct(cpu.get("system", {}).get("pct"))
    record["cpu_idle_pct"] = _to_pct(cpu.get("idle", {}).get("pct"))
    record["cpu_iowait_pct"] = _to_pct(cpu.get("iowait", {}).get("pct"))
    record["cpu_steal_pct"] = _to_pct(cpu.get("steal", {}).get("pct"))
    record["cpu_softirq_pct"] = _to_pct(cpu.get("softirq", {}).get("pct"))
    record["cpu_cores"] = cpu.get("cores")

    return record


def parse_system_cpu_lines(lines: Iterable[str]) -> list[SystemCpuRow]:
    """Parse all system CPU log lines into staging rows."""
    return [
        parse_system_cpu_line(line_number, line) for line_number, line in enumerate(lines, start=1)
    ]


def parse_system_cpu_file(path: str | Path) -> Iterator[SystemCpuRow]:
    """Yield parsed staging rows from a system CPU log file."""
    with Path(path).open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            yield parse_system_cpu_line(line_number, line)
