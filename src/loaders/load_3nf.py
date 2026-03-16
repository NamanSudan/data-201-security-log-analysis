"""3NF data loader: staging -> final normalized tables.

Reads from staging tables (already loaded by load_staging.py) and
populates the 3NF host-domain tables in FK-dependency order.

Usage:
    python -m src.loaders.load_3nf

Requires:
  - DATABASE_URL or DB_* env vars
  - Alembic migrations applied (both staging and 3NF)
  - Staging tables already populated (via load_staging.py)
"""

import os
import sys

from sqlalchemy import create_engine, func, select, text
from sqlalchemy.orm import Session

from src.models.final.host import (
    Host,
    HostFqdn,
    HostGroup,
    HostIpv4,
    HostIpv6,
    HostLogConfig,
    OsRelease,
)
from src.parsers.final.hosts import (
    explode_host_fqdns,
    explode_host_groups,
    explode_host_ipv4,
    explode_host_ipv6,
    extract_os_releases,
    transform_host_log_configs,
    transform_hosts,
)

# Expected row counts for verification (from docs/schema/data_model_3nf.md)
EXPECTED_COUNTS = {
    "os_release": 2,
    "host": 22,
    "host_group": 63,
    "host_fqdn": 20,
    "host_ipv4": 24,
    "host_ipv6": 24,
    "host_log_config": 66,
}


def get_database_url() -> str:
    """Get database URL from environment (mirrors alembic/env.py logic)."""
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    user = os.getenv("DB_USER", "security_logs_user")
    password = os.getenv("DB_PASSWORD", "dev_password_change_me")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "security_logs")
    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"


def _load_os_release(session: Session) -> dict[str, int]:
    """Phase 1: Load os_release lookup table.

    Returns: {distribution_release: os_release_id} mapping.
    """
    rows = extract_os_releases(session)
    objects = [OsRelease(**row) for row in rows]
    session.add_all(objects)
    session.flush()
    return {obj.distribution_release: obj.os_release_id for obj in objects}


def _load_host(session: Session, os_release_map: dict[str, int]) -> dict[str, int]:
    """Phase 2: Load host table.

    Returns: {host_key: host_id} mapping for child table FK resolution.
    """
    rows = transform_hosts(session, os_release_map)
    objects = [Host(**row) for row in rows]
    session.add_all(objects)
    session.flush()
    return {obj.host_key: obj.host_id for obj in objects}


def _load_host_children(session: Session, host_key_to_id: dict[str, int]) -> None:
    """Phase 3: Load all host child/junction tables (independent, FK -> host)."""
    # host_group
    for row in explode_host_groups(session, host_key_to_id):
        session.add(HostGroup(**row))

    # host_fqdn
    for row in explode_host_fqdns(session, host_key_to_id):
        session.add(HostFqdn(**row))

    # host_ipv4
    for row in explode_host_ipv4(session, host_key_to_id):
        session.add(HostIpv4(**row))

    # host_ipv6
    for row in explode_host_ipv6(session, host_key_to_id):
        session.add(HostIpv6(**row))

    # host_log_config (needs staging join for FK resolution)
    for row in transform_host_log_configs(session, host_key_to_id):
        session.add(HostLogConfig(**row))

    session.flush()


def verify_counts(session: Session) -> bool:
    """Verify row counts match expected values. Returns True if all pass."""
    tables = {
        "os_release": OsRelease,
        "host": Host,
        "host_group": HostGroup,
        "host_fqdn": HostFqdn,
        "host_ipv4": HostIpv4,
        "host_ipv6": HostIpv6,
        "host_log_config": HostLogConfig,
    }

    all_ok = True
    for table_name, model in tables.items():
        actual = session.scalar(select(func.count()).select_from(model))
        expected = EXPECTED_COUNTS[table_name]
        status = "OK" if actual == expected else "MISMATCH"
        if actual != expected:
            all_ok = False
        print(f"  {table_name}: {actual} rows (expected {expected}) [{status}]")

    return all_ok


def verify_integrity(session: Session) -> bool:
    """Run integrity checks from the docs. Returns True if all pass."""
    all_ok = True

    # default_ipv4_address must exist in host_ipv4 for same host
    bad_ipv4 = session.execute(
        text("""
            SELECT h.host_key, h.default_ipv4_address
            FROM host h
            WHERE NOT EXISTS (
                SELECT 1 FROM host_ipv4 ip
                WHERE ip.host_id = h.host_id
                  AND ip.ipv4_address = h.default_ipv4_address
            )
        """)
    ).fetchall()
    if bad_ipv4:
        print(f"  FAIL: {len(bad_ipv4)} hosts with default_ipv4 not in host_ipv4")
        all_ok = False
    else:
        print("  default_ipv4 in host_ipv4: OK")

    # default_ipv6_address must exist in host_ipv6 for same host
    bad_ipv6 = session.execute(
        text("""
            SELECT h.host_key, h.default_ipv6_address
            FROM host h
            WHERE NOT EXISTS (
                SELECT 1 FROM host_ipv6 ip
                WHERE ip.host_id = h.host_id
                  AND ip.ipv6_address = h.default_ipv6_address
            )
        """)
    ).fetchall()
    if bad_ipv6:
        print(f"  FAIL: {len(bad_ipv6)} hosts with default_ipv6 not in host_ipv6")
        all_ok = False
    else:
        print("  default_ipv6 in host_ipv6: OK")

    # (host_id, log_path) uniqueness in host_log_config
    # Already enforced by UNIQUE constraint, but verify explicitly
    dupes = session.execute(
        text("""
            SELECT host_id, log_path, COUNT(*)
            FROM host_log_config
            GROUP BY host_id, log_path
            HAVING COUNT(*) > 1
        """)
    ).fetchall()
    if dupes:
        print(f"  FAIL: {len(dupes)} duplicate (host_id, log_path) in host_log_config")
        all_ok = False
    else:
        print("  host_log_config (host_id, log_path) unique: OK")

    return all_ok


def load_3nf() -> None:
    """Main entry point: transform staging -> 3NF host-domain tables."""
    engine = create_engine(get_database_url())

    print("Loading 3NF host-domain tables from staging...")

    with Session(engine) as session:
        print("  Phase 1: os_release...")
        os_release_map = _load_os_release(session)

        print("  Phase 2: host...")
        host_key_to_id = _load_host(session, os_release_map)

        print("  Phase 3: host_group, host_fqdn, host_ipv4, host_ipv6, host_log_config...")
        _load_host_children(session, host_key_to_id)

        session.commit()
        print("\nAll 3NF host-domain tables committed.")

        print("\nRow count verification:")
        counts_ok = verify_counts(session)

        print("\nIntegrity verification:")
        integrity_ok = verify_integrity(session)

    if counts_ok and integrity_ok:
        print("\nAll verifications passed. 3NF host-domain load complete.")
    else:
        print("\nWARNING: Some verifications failed.")
        sys.exit(1)


if __name__ == "__main__":
    load_3nf()
