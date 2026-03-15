"""Transformation helpers: staging host tables -> 3NF host-domain row payloads.

Each function reads from staging ORM rows and returns dicts ready for
insertion into the corresponding 3NF table. The loader is responsible
for session management and insertion order.
"""

import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.staging.host import StgHostLogConfigRaw, StgHostRaw


def extract_os_releases(session: Session) -> list[dict]:
    """Return distinct os_release rows from stg_host_raw.

    Expected: 2 rows (bionic/Ubuntu/18.04, stretch/Debian/9.11).
    """
    stmt = select(
        StgHostRaw.distribution_release,
        StgHostRaw.distribution,
        StgHostRaw.distribution_version,
    ).distinct()

    return [
        {
            "distribution_release": row.distribution_release,
            "distribution": row.distribution,
            "distribution_version": row.distribution_version,
        }
        for row in session.execute(stmt)
    ]


def transform_hosts(session: Session, os_release_map: dict[str, int]) -> list[dict]:
    """Transform stg_host_raw rows into 3NF host rows.

    Args:
        session: Active DB session with staging data loaded.
        os_release_map: {distribution_release: os_release_id} lookup.

    Returns:
        List of dicts matching the Host model columns.
    """
    stg_hosts = session.scalars(select(StgHostRaw)).all()

    return [
        {
            "host_key": h.host_key,
            "hostname": h.hostname,
            "username": h.username,
            "openvpn_user": h.openvpn_user,
            "default_ipv4_address": h.default_ipv4_address,
            "default_ipv6_address": h.default_ipv6_address,
            "timezone": h.timezone,
            "os_release_id": os_release_map[h.distribution_release],
        }
        for h in stg_hosts
    ]


def explode_host_groups(session: Session, host_key_to_id: dict[str, int]) -> list[dict]:
    """Explode JSON groups array into host_group rows.

    Expected: 63 rows total (2-5 groups per host, 17 distinct group names).
    """
    stg_hosts = session.scalars(select(StgHostRaw)).all()
    rows = []
    for h in stg_hosts:
        host_id = host_key_to_id[h.host_key]
        for group_name in json.loads(h.groups):
            rows.append({"host_id": host_id, "group_name": group_name})
    return rows


def explode_host_fqdns(session: Session, host_key_to_id: dict[str, int]) -> list[dict]:
    """Explode JSON fqdns array into host_fqdn rows.

    Expected: 20 rows total. Hosts with NULL fqdns produce zero rows.
    """
    stg_hosts = session.scalars(select(StgHostRaw)).all()
    rows = []
    for h in stg_hosts:
        if h.fqdns is None:
            continue
        host_id = host_key_to_id[h.host_key]
        for fqdn in json.loads(h.fqdns):
            rows.append({"host_id": host_id, "fqdn": fqdn})
    return rows


def explode_host_ipv4(session: Session, host_key_to_id: dict[str, int]) -> list[dict]:
    """Explode JSON ipv4_addresses array into host_ipv4 rows.

    Expected: 24 rows total (21 hosts x 1 + inet-firewall x 3).
    """
    stg_hosts = session.scalars(select(StgHostRaw)).all()
    rows = []
    for h in stg_hosts:
        host_id = host_key_to_id[h.host_key]
        for addr in json.loads(h.ipv4_addresses):
            rows.append({"host_id": host_id, "ipv4_address": addr})
    return rows


def explode_host_ipv6(session: Session, host_key_to_id: dict[str, int]) -> list[dict]:
    """Explode JSON ipv6_addresses array into host_ipv6 rows.

    Expected: 24 rows total (same pattern as ipv4).
    """
    stg_hosts = session.scalars(select(StgHostRaw)).all()
    rows = []
    for h in stg_hosts:
        host_id = host_key_to_id[h.host_key]
        for addr in json.loads(h.ipv6_addresses):
            rows.append({"host_id": host_id, "ipv6_address": addr})
    return rows


def transform_host_log_configs(
    session: Session, host_key_to_final_id: dict[str, int]
) -> list[dict]:
    """Transform stg_host_log_config_raw -> host_log_config rows.

    FK resolution chain (from docs):
      stg_host_log_config_raw.host_id
      -> join stg_host_raw.host_id to recover host_key
      -> join final host.host_key to get final host.host_id

    The caller provides host_key_to_final_id from the already-loaded
    final host table, so we only need to recover host_key from staging.

    Expected: 66 rows total.
    """
    # Build staging host_id -> host_key lookup
    stg_hosts = session.scalars(select(StgHostRaw)).all()
    stg_id_to_key = {h.host_id: h.host_key for h in stg_hosts}

    stg_configs = session.scalars(select(StgHostLogConfigRaw)).all()
    rows = []
    for cfg in stg_configs:
        host_key = stg_id_to_key[cfg.host_id]
        final_host_id = host_key_to_final_id[host_key]
        rows.append(
            {
                "host_id": final_host_id,
                "log_path": cfg.log_path,
                "log_type": cfg.log_type,
                "codec": cfg.codec,
                "file_chunk_size": cfg.file_chunk_size,
                "add_field_json": cfg.add_field_json,
            }
        )
    return rows
