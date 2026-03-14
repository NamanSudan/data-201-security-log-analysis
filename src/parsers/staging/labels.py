"""Parser for attack label JSONL files -> stg_attack_label_line_raw.

All 8 label files share an identical JSON schema (line, labels, rules).
source_host and source_log are derived from file paths, not from the JSONL data.
"""

import json
from pathlib import Path

# All 8 label files with their provenance mappings.
# "host" and "log" are the source_host / source_log values (matching notebook conventions).
# "rel_path" is relative to the russellmitchell/ dataset root.
LABEL_FILE_CONFIG = [
    {
        "host": "inet-firewall",
        "log": "dnsmasq.log",
        "rel_path": "labels/inet-firewall/logs/dnsmasq.log",
    },
    {
        "host": "intranet_server",
        "log": "access.log.2",
        "rel_path": "labels/intranet_server/logs/apache2/"
        "intranet.smith.russellmitchell.com-access.log.2",
    },
    {
        "host": "intranet_server",
        "log": "error.log.2",
        "rel_path": "labels/intranet_server/logs/apache2/"
        "intranet.smith.russellmitchell.com-error.log.2",
    },
    {
        "host": "intranet_server",
        "log": "audit.log",
        "rel_path": "labels/intranet_server/logs/audit/audit.log",
    },
    {
        "host": "intranet_server",
        "log": "auth.log",
        "rel_path": "labels/intranet_server/logs/auth.log",
    },
    {
        "host": "monitoring",
        "log": "cpu.log",
        "rel_path": "labels/monitoring/logs/logstash/intranet-server/2022-01-24-system.cpu.log",
    },
    {
        "host": "vpn",
        "log": "openvpn.log",
        "rel_path": "labels/vpn/logs/openvpn.log",
    },
    {
        "host": "internal_share",
        "log": "audit.log",
        "rel_path": "labels/internal_share/logs/audit/audit.log",
    },
]


def parse_label_files(dataset_root: Path) -> list[dict]:
    """Parse all 8 label JSONL files into staging rows.

    Args:
        dataset_root: Path to the russellmitchell/ directory.

    Returns:
        List of dicts matching stg_attack_label_line_raw columns (61,862 expected).
    """
    all_rows = []

    for config in LABEL_FILE_CONFIG:
        file_path = dataset_root / config["rel_path"]
        source_host = config["host"]
        source_log = config["log"]

        with open(file_path) as f:
            for raw_line in f:
                raw_line = raw_line.strip()
                if not raw_line:
                    continue
                obj = json.loads(raw_line)
                all_rows.append(
                    {
                        "source_host": source_host,
                        "source_log": source_log,
                        "line_number": obj["line"],
                        "labels_json": json.dumps(obj["labels"]),
                        "rules_json": json.dumps(obj["rules"]),
                    }
                )

    return all_rows
