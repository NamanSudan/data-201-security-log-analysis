"""Parser for Metricbeat system/cpu log -> stg_system_cpu_events.

Reads 2022-01-21-system_cpu.log (newline-delimited JSON) from the
internal_share gather and produces staging-shaped dicts ready for
ORM insertion.

Each line is a Metricbeat JSON document containing system.cpu.* fields.
"""

import json
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Field mapping: Metricbeat dot-notation key -> stg column name
# ---------------------------------------------------------------------------

_CPU_FIELDS = {
    "system.cpu.total.pct": "cpu_total_pct",
    "system.cpu.user.pct": "cpu_user_pct",
    "system.cpu.system.pct": "cpu_system_pct",
    "system.cpu.idle.pct": "cpu_idle_pct",
    "system.cpu.iowait.pct": "cpu_iowait_pct",
    "system.cpu.steal.pct": "cpu_steal_pct",
    "system.cpu.softirq.pct": "cpu_softirq_pct",
    "system.cpu.irq.pct": "cpu_irq_pct",
    "system.cpu.nice.pct": "cpu_nice_pct",
    "system.cpu.cores": "cpu_cores",
}


def _get_nested(doc: dict, dotted_key: str):
    """Traverse a nested dict using a dot-separated key string."""
    parts = dotted_key.split(".")
    value = doc
    for part in parts:
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


# ---------------------------------------------------------------------------
# Public parse function
# ---------------------------------------------------------------------------


def parse_system_cpu(
    log_path: Path,
    source_host: str,
) -> list[dict]:
    """Parse a Metricbeat system/cpu JSONL log into stg_system_cpu_events rows.

    Args:
        log_path:    Path to the raw JSONL CPU log file.
        source_host: YAML host_key for this host, e.g. "internal-share".

    Returns:
        List of dicts matching stg_system_cpu_events columns.
    """
    source_log = log_path.name

    rows = []
    with open(log_path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue

            doc = json.loads(line)

            # --- timestamp ------------------------------------------------
            raw_ts = doc.get("@timestamp")
            try:
                timestamp = pd.to_datetime(raw_ts, utc=True)
            except Exception:
                timestamp = None

            # --- cpu pct fields -------------------------------------------
            cpu_cols = {col: _get_nested(doc, key) for key, col in _CPU_FIELDS.items()}

            rows.append(
                {
                    "source_host": source_host,
                    "source_log": source_log,
                    "event_timestamp": timestamp,
                    "hostname": _get_nested(doc, "host.name"),
                    **cpu_cols,
                    "event_duration_ns": _get_nested(doc, "event.duration"),
                    "metricset_period_ms": _get_nested(doc, "metricset.period"),
                }
            )

    return rows
