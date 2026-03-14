"""Parser for host inventory (servers.yaml) -> stg_host_raw + stg_host_log_config_raw.

Reads the YAML config and produces staging-shaped dicts ready for ORM insertion.
Multi-valued fields are serialized as JSON-array strings via json.dumps().
"""

import json
from pathlib import Path

import yaml


def parse_hosts(yaml_path: Path) -> tuple[list[dict], list[dict]]:
    """Parse servers.yaml into staging rows.

    Returns:
        (host_rows, log_config_rows) where:
        - host_rows: list of dicts matching stg_host_raw columns (22 expected)
        - log_config_rows: list of dicts matching stg_host_log_config_raw columns (66 expected)
          Each log_config row has a 'host_key' field for FK resolution after host insertion.
    """
    with open(yaml_path) as f:
        servers = yaml.safe_load(f)

    host_rows = []
    log_config_rows = []

    for host_key, info in servers.items():
        host_row = {
            "host_key": host_key,
            "hostname": info["hostname"],
            "groups": json.dumps(info.get("groups", [])),
            "username": info.get("username"),
            "openvpn_user": info.get("openvpn_user"),
            "distribution": info["distribution"],
            "distribution_release": info["distribution_release"],
            "distribution_version": info["distribution_version"],
            "default_ipv4_address": info["default_ipv4_address"],
            "default_ipv6_address": info["default_ipv6_address"],
            "ipv4_addresses": json.dumps(info.get("ipv4_addresses", [])),
            "ipv6_addresses": json.dumps(info.get("ipv6_addresses", [])),
            "fqdns": json.dumps(info["fqdns"]) if info.get("fqdns") else None,
            "timezone": info["timezone"],
        }
        host_rows.append(host_row)

        for log_entry in info.get("logs", []):
            log_config_rows.append({
                "host_key": host_key,
                "log_path": log_entry["path"],
                "log_type": log_entry["type"],
                "codec": log_entry.get("codec"),
                "file_chunk_size": log_entry.get("file_chunk_size"),
                "add_field_json": (
                    json.dumps(log_entry["add_field"]) if log_entry.get("add_field") else None
                ),
            })

    return host_rows, log_config_rows
