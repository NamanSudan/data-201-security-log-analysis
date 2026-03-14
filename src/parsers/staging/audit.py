"""Parser for audit.log files -> stg_audit_line_raw.

Handles both intranet_server and internal_share audit logs.
Each line becomes one row with 43 columns + provenance.
The msg='...' blob is stored as-is; unpacking is deferred to 3NF.
"""

import re
from datetime import UTC, datetime
from pathlib import Path

# Regex patterns for audit line parsing
RE_TYPE = re.compile(r"type=(\S+)")
RE_TIMESTAMP = re.compile(r"msg=audit\((\d+\.\d+):(\d+)\)")
RE_NESTED_MSG = re.compile(r"msg='([^']+)'")
RE_OUTER_KV = re.compile(r'([\w-]+)=("[^"]*"|\([^)]*\)|\S+)')

# Columns that should be parsed as integers
INT_COLUMNS = {"pid", "uid", "syscall", "items", "ppid", "gid", "euid", "suid", "fsuid",
               "egid", "sgid", "fsgid"}
BIGINT_COLUMNS = {"auid", "ses", "old_auid", "old_ses", "exit"}

# Audit sources in scope (host_key -> file path relative to gather/)
AUDIT_SOURCES = [
    {
        "source_host": "intranet_server",
        "source_log": "audit.log",
        "rel_path": "gather/intranet_server/logs/audit/audit.log",
    },
    {
        "source_host": "internal_share",
        "source_log": "audit.log",
        "rel_path": "gather/internal_share/logs/audit/audit.log",
    },
]


def _parse_audit_line(line_num: int, line: str) -> dict:
    """Parse a single audit log line into a flat dict matching stg_audit_line_raw columns."""
    record = {"line_number": line_num}
    line = line.rstrip()
    record["raw_line"] = line

    # Extract type
    m_type = RE_TYPE.match(line)
    if not m_type:
        record["type"] = "UNKNOWN"
        return record
    record["type"] = m_type.group(1)

    # Extract audit timestamp and serial
    m_ts = RE_TIMESTAMP.search(line)
    if m_ts:
        epoch = float(m_ts.group(1))
        record["epoch"] = epoch
        record["serial"] = int(m_ts.group(2))
        record["timestamp"] = datetime.fromtimestamp(epoch, tz=UTC)

    # Extract nested msg='...' content
    m_nested = RE_NESTED_MSG.search(line)
    if m_nested:
        record["msg"] = m_nested.group(1)

    # Parse outer key=value pairs
    outer = re.sub(r"^type=\S+\s+msg=audit\([^)]+\):\s*", "", line)
    if m_nested:
        outer = outer.replace(f"msg='{m_nested.group(1)}'", "")

    for m_kv in RE_OUTER_KV.finditer(outer):
        key = m_kv.group(1).replace("-", "_")
        val = m_kv.group(2).strip('"')
        if key not in record:
            record[key] = val

    # Type-convert numeric fields
    for col in INT_COLUMNS:
        if col in record:
            try:
                record[col] = int(record[col])
            except (ValueError, TypeError):
                record[col] = None

    for col in BIGINT_COLUMNS:
        if col in record:
            try:
                record[col] = int(record[col])
            except (ValueError, TypeError):
                record[col] = None

    return record


def parse_audit_files(dataset_root: Path) -> list[dict]:
    """Parse all in-scope audit.log files into staging rows.

    Args:
        dataset_root: Path to the russellmitchell/ directory.

    Returns:
        List of dicts matching stg_audit_line_raw columns (3,048 expected).
    """
    all_rows = []

    for source in AUDIT_SOURCES:
        file_path = dataset_root / source["rel_path"]
        with open(file_path) as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, 1):
            record = _parse_audit_line(line_num, line)
            record["source_host"] = source["source_host"]
            record["source_log"] = source["source_log"]
            all_rows.append(record)

    return all_rows
