"""Parser for Apache error log -> stg_http_errors.

Reads intranet_smith_russellmitchell_com-error_log.2 and produces
staging-shaped dicts ready for ORM insertion.

Source log format:
    [day Mon DD HH:MM:SS.usec YYYY] [module:level] [pid N] [client IP:port] message
"""

import re
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

LOG_RE = re.compile(
    r"^\[(?P<timestamp>[^\]]+)\]\s+"
    r"\[(?P<module>[^:]+):(?P<level>[^\]]+)\]\s+"
    r"\[pid\s+(?P<pid>\d+)\]\s+"
    r"(?:\[client\s+(?P<client_ip>[^:]+):(?P<client_port>\d+)\]\s+)?"
    r"(?P<message>.+)$"
)

REFERER_RE = re.compile(r",?\s*referer:\s*(\S+)$")
AHCODE_RE = re.compile(r"^(AH\d{5}):\s*(.*)")
PATH_RE = re.compile(r'(?:script|file|directory)\s+[\'"]?(/[^\s\'"]+)[\'"]?')


# ---------------------------------------------------------------------------
# Public parse function
# ---------------------------------------------------------------------------


def parse_http_errors(
    log_path: Path,
    source_host: str,
) -> list[dict]:
    """Parse an Apache error log into stg_http_errors rows.

    Args:
        log_path:    Path to the raw Apache error log file.
        source_host: YAML host_key for this host, e.g. "intranet-server".

    Returns:
        List of dicts matching stg_http_errors columns.
    """
    source_log = log_path.name

    with open(log_path) as fh:
        raw_lines = fh.readlines()

    rows = []
    for line_number, line in enumerate(raw_lines, 1):
        line = line.rstrip()
        m = LOG_RE.match(line)
        if not m:
            continue

        # --- referer extraction -------------------------------------------
        msg = m.group("message")
        ref_m = REFERER_RE.search(msg)
        if ref_m:
            referer = ref_m.group(1)
            msg = msg[: ref_m.start()].rstrip()
        else:
            referer = None

        # --- AH error code ------------------------------------------------
        ah_m = AHCODE_RE.match(msg)
        if ah_m:
            error_code = ah_m.group(1)
            message = ah_m.group(2)
        else:
            error_code = None
            message = msg

        # --- file/directory path ------------------------------------------
        path_m = PATH_RE.search(message)
        target_path = path_m.group(1) if path_m else None

        # --- timestamp ----------------------------------------------------
        try:
            timestamp = pd.to_datetime(
                m.group("timestamp"), format="%a %b %d %H:%M:%S.%f %Y", utc=True
            )
        except Exception:
            timestamp = None

        rows.append(
            {
                "source_host": source_host,
                "source_log": source_log,
                "line_number": line_number,
                "timestamp": timestamp,
                "raw_timestamp": m.group("timestamp"),
                "module": m.group("module"),
                "level": m.group("level"),
                "pid": int(m.group("pid")) if m.group("pid") else None,
                "client_ip": m.group("client_ip"),
                "client_port": int(m.group("client_port")) if m.group("client_port") else None,
                "error_code": error_code,
                "message": message,
                "message_raw": m.group("message"),
                "target_path": target_path,
                "referer": referer,
            }
        )

    return rows
