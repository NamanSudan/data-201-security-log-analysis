"""Parser for Apache access log -> stg_http_access.

Reads intranet_smith_russellmitchell_com-access_log.2 (Combined Log Format)
and produces staging-shaped dicts ready for ORM insertion.

Source log format (CLF + referer + user-agent):
    IP ident authuser [timestamp] "METHOD path proto" status bytes "referer" "ua"
"""

import re
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd

# ---------------------------------------------------------------------------
# Regex pattern
# ---------------------------------------------------------------------------

CLF_RE = re.compile(
    r"^(?P<client_ip>\S+)\s+"
    r"(?P<ident>\S+)\s+"
    r"(?P<authuser>\S+)\s+"
    r"\[(?P<timestamp>[^\]]+)\]\s+"
    r'"(?P<request_line>[^"]*)"\s+'
    r"(?P<status>\d{3})\s+"
    r"(?P<bytes>\S+)\s+"
    r'"(?P<referer>[^"]*)"\s+'
    r'"(?P<user_agent>[^"]*)"'
)


# ---------------------------------------------------------------------------
# Public parse function
# ---------------------------------------------------------------------------


def parse_http_access(
    log_path: Path,
    source_host: str,
) -> list[dict]:
    """Parse an Apache Combined Log Format access log into stg_http_access rows.

    Args:
        log_path:    Path to the raw Apache access log file.
        source_host: YAML host_key for this host, e.g. "intranet-server".

    Returns:
        List of dicts matching stg_http_access columns.
    """
    source_log = log_path.name

    with open(log_path) as fh:
        raw_lines = fh.readlines()

    rows = []
    for line_number, line in enumerate(raw_lines, 1):
        line = line.rstrip()
        m = CLF_RE.match(line)
        if not m:
            continue

        # --- decompose request line ---------------------------------------
        req = m.group("request_line")
        if req and req != "-":
            parts = req.split(" ")
            http_method = parts[0] if len(parts) > 0 else None
            raw_path = parts[1] if len(parts) > 1 else None
            http_proto = parts[2] if len(parts) > 2 else None
        else:
            http_method = raw_path = http_proto = None

        # --- split path and query string ----------------------------------
        path = query_string = None
        if raw_path:
            parsed_url = urlparse(raw_path)
            path = parsed_url.path
            query_string = parsed_url.query or None

        # --- normalize sentinel values ------------------------------------
        referer = m.group("referer") if m.group("referer") != "-" else None
        user_agent = m.group("user_agent") if m.group("user_agent") != "-" else None
        ident = m.group("ident") if m.group("ident") != "-" else None
        authuser = m.group("authuser") if m.group("authuser") != "-" else None

        bytes_raw = m.group("bytes")
        bytes_sent = int(bytes_raw) if bytes_raw.isdigit() else None

        # --- timestamp ----------------------------------------------------
        try:
            timestamp = pd.to_datetime(m.group("timestamp"), format="%d/%b/%Y:%H:%M:%S %z")
        except Exception:
            timestamp = None

        rows.append(
            {
                "source_host": source_host,
                "source_log": source_log,
                "line_number": line_number,
                "timestamp": timestamp,
                "raw_timestamp": m.group("timestamp"),
                "client_ip": m.group("client_ip"),
                "ident": ident,
                "authuser": authuser,
                "http_method": http_method,
                "path": path,
                "query_string": query_string,
                "http_proto": http_proto,
                "status": int(m.group("status")),
                "bytes_sent": bytes_sent,
                "referer": referer,
                "user_agent": user_agent,
                "request_line": req if req != "-" else None,
            }
        )

    return rows
