"""3NF data loader: stg_audit_line_raw -> final normalized audit tables.

Reads from the staging table (already loaded by load_staging.py) and
populates the 3NF audit-domain tables in FK-dependency order.

Usage:
    python -m src.loaders.load_3nf_audit

Requires:
  - DATABASE_URL or DB_* env vars
  - Alembic migrations applied (both staging and 3NF)
  - Staging tables already populated (via load_staging.py)
  - Host-domain 3NF tables already populated (via load_3nf.py)
"""

import sys

from sqlalchemy import create_engine, func, select, text
from sqlalchemy.orm import Session

from src.models.final.audit import (
    AuditAvcEvent,
    AuditEvent,
    AuditLoginEvent,
    AuditMessage,
    AuditPamEvent,
    AuditProctitleEvent,
    AuditServiceEvent,
    AuditSyscallEvent,
    AuditUserCmdEvent,
    AuditUserLoginEvent,
)
from src.models.staging.audit import StgAuditLineRaw
from src.parsers.final.audit import (
    build_host_map,
    extract_audit_messages,
    extract_subtype_rows,
    transform_audit_events,
)

# Expected row counts for verification (from audit_3nf_normalization_plan.md §6)
EXPECTED_COUNTS = {
    "audit_event": 3048,
    "audit_message": 2614,
    "audit_pam_event": 2055,
    "audit_service_event": 555,
    "audit_user_login_event": 3,
    "audit_user_cmd_event": 1,
    "audit_login_event": 410,
    "audit_syscall_event": 8,
    "audit_avc_event": 8,
    "audit_proctitle_event": 8,
}

_SUBTYPE_MODEL_MAP = {
    "audit_pam_event": AuditPamEvent,
    "audit_service_event": AuditServiceEvent,
    "audit_user_login_event": AuditUserLoginEvent,
    "audit_user_cmd_event": AuditUserCmdEvent,
    "audit_login_event": AuditLoginEvent,
    "audit_syscall_event": AuditSyscallEvent,
    "audit_avc_event": AuditAvcEvent,
    "audit_proctitle_event": AuditProctitleEvent,
}


def get_database_url() -> str:
    """Get database URL from environment (mirrors alembic/env.py logic)."""
    import os

    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    user = os.getenv("DB_USER", "security_logs_user")
    password = os.getenv("DB_PASSWORD", "dev_password_change_me")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "security_logs")
    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"


def _load_audit_events(session: Session, host_map: dict[str, int]) -> dict[tuple[int, int], int]:
    """Phase 1: Insert audit_event rows.

    Returns:
        {(host_id, line_number): event_id} mapping for child table FK resolution.

    Expected: 3,048 rows.
    """
    rows = transform_audit_events(session, host_map)
    objects = [AuditEvent(**row) for row in rows]
    session.add_all(objects)
    session.flush()
    return {(obj.host_id, obj.line_number): obj.event_id for obj in objects}


def _load_audit_messages(
    session: Session,
    stg_rows: list,
    event_id_map: dict[tuple[int, int], int],
    host_map: dict[str, int],
) -> None:
    """Phase 2: Insert audit_message rows for events with non-null msg.

    Resolves event_id via the (host_id, line_number) -> event_id map built
    after Phase 1. Expected: 2,614 rows (validated).
    """
    # Attach resolved host_id to each staging row for the lookup key
    for r in stg_rows:
        r.host_id_resolved = host_map.get(r.source_host)

    rows = extract_audit_messages(stg_rows, event_id_map)
    session.add_all([AuditMessage(**row) for row in rows])
    session.flush()


def _load_subtypes(
    session: Session,
    stg_rows: list,
    event_id_map: dict[tuple[int, int], int],
    host_map: dict[str, int],
) -> None:
    """Phase 3: Insert exactly one subtype row per audit_event.

    Routes each staging row to the correct subtype table via event type.
    Expected total: 3,048 rows across all 8 subtype tables.
    """
    buckets = extract_subtype_rows(stg_rows, event_id_map, host_map)

    for table_name, model in _SUBTYPE_MODEL_MAP.items():
        for row in buckets.get(table_name, []):
            session.add(model(**row))

    session.flush()


def verify_counts(session: Session) -> bool:
    """Verify row counts match expected values. Returns True if all pass."""
    all_models = {"audit_event": AuditEvent, "audit_message": AuditMessage, **_SUBTYPE_MODEL_MAP}

    all_ok = True
    for table_name, model in all_models.items():
        actual = session.scalar(select(func.count()).select_from(model))
        expected = EXPECTED_COUNTS[table_name]
        ok = actual == expected
        status = "OK" if ok else "MISMATCH"
        if not ok:
            all_ok = False
        print(f"  {table_name}: {actual} rows (expected {expected}) [{status}]")

    return all_ok


def verify_integrity(session: Session) -> bool:
    """Run FK and coverage integrity checks. Returns True if all pass."""
    all_ok = True

    # Every audit_event must have exactly one subtype row
    union_parts = " UNION ALL ".join(f"SELECT event_id FROM {t}" for t in _SUBTYPE_MODEL_MAP)
    orphaned = session.execute(
        text(f"""
            SELECT ae.event_id
            FROM audit_event ae
            LEFT JOIN ({union_parts}) sub ON sub.event_id = ae.event_id
            WHERE sub.event_id IS NULL
        """)
    ).fetchall()
    if orphaned:
        print(f"  FAIL: {len(orphaned)} audit_event rows with no subtype row")
        all_ok = False
    else:
        print("  audit_event -> subtype coverage: OK")

    # No event_id should appear in more than one subtype
    duplicates = session.execute(
        text(f"""
            SELECT event_id, COUNT(*) AS cnt
            FROM ({union_parts}) sub
            GROUP BY event_id
            HAVING COUNT(*) > 1
        """)
    ).fetchall()
    if duplicates:
        print(f"  FAIL: {len(duplicates)} event_ids appear in more than one subtype")
        all_ok = False
    else:
        print("  subtype disjoint check: OK")

    # Every audit_event.host_id must exist in host
    bad_host = session.execute(
        text("""
            SELECT ae.event_id, ae.host_id
            FROM audit_event ae
            LEFT JOIN host h ON h.host_id = ae.host_id
            WHERE h.host_id IS NULL
        """)
    ).fetchall()
    if bad_host:
        print(f"  FAIL: {len(bad_host)} audit_event rows with invalid host_id")
        all_ok = False
    else:
        print("  audit_event.host_id FK: OK")

    # Every audit_message.event_id must exist in audit_event
    bad_msg = session.execute(
        text("""
            SELECT am.event_id
            FROM audit_message am
            LEFT JOIN audit_event ae ON ae.event_id = am.event_id
            WHERE ae.event_id IS NULL
        """)
    ).fetchall()
    if bad_msg:
        print(f"  FAIL: {len(bad_msg)} audit_message rows with invalid event_id")
        all_ok = False
    else:
        print("  audit_message.event_id FK: OK")

    return all_ok


def load_3nf_audit() -> None:
    """Main entry point: transform stg_audit_line_raw -> 3NF audit-domain tables."""
    engine = create_engine(get_database_url())

    print("Loading 3NF audit-domain tables from staging...")

    with Session(engine) as session:
        # Fail fast if audit tables are already populated (prevents double-load)
        existing = session.scalar(select(func.count()).select_from(AuditEvent))
        if existing and existing > 0:
            print(
                f"  ABORT: audit_event already has {existing} rows. "
                "Drop and recreate tables before re-running."
            )
            sys.exit(1)

        print("  Building host_map from final host table...")
        host_map = build_host_map(session)

        # Pre-fetch staging rows once; reused across all three phases
        stg_rows = session.scalars(select(StgAuditLineRaw)).all()
        print(f"  Fetched {len(stg_rows)} rows from stg_audit_line_raw.")

        print("  Phase 1: audit_event...")
        event_id_map = _load_audit_events(session, host_map)

        print("  Phase 2: audit_message...")
        _load_audit_messages(session, stg_rows, event_id_map, host_map)

        print("  Phase 3: subtype tables...")
        _load_subtypes(session, stg_rows, event_id_map, host_map)

        session.commit()
        print("\nAll 3NF audit-domain tables committed.")

        print("\nRow count verification:")
        counts_ok = verify_counts(session)

        print("\nIntegrity verification:")
        integrity_ok = verify_integrity(session)

    if counts_ok and integrity_ok:
        print("\nAll verifications passed. 3NF audit-domain load complete.")
    else:
        print("\nWARNING: Some verifications failed.")
        sys.exit(1)


if __name__ == "__main__":
    load_3nf_audit()
