"""Staging data loader.

Parses raw source files and inserts into the 4 staging tables.
Includes row-count verification after each table load.

Usage:
    python -m src.loaders.load_staging [--dataset-root PATH]

Requires DATABASE_URL or DB_* env vars (see alembic/env.py for defaults).
Run Alembic migrations first: alembic -c alembic/alembic.ini upgrade head
"""

import os
import sys
from pathlib import Path

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from src.models.staging.audit import StgAuditLineRaw
from src.models.staging.host import StgHostLogConfigRaw, StgHostRaw
from src.models.staging.labels import StgAttackLabelLineRaw
from src.parsers.staging.audit import parse_audit_files
from src.parsers.staging.hosts import parse_hosts
from src.parsers.staging.labels import parse_label_files

# Expected row counts for verification
EXPECTED_COUNTS = {
    "stg_host_raw": 22,
    "stg_host_log_config_raw": 66,
    "stg_audit_line_raw": 3048,
    "stg_attack_label_line_raw": 61862,
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


def _load_hosts(session: Session, yaml_path: Path) -> None:
    """Load stg_host_raw and stg_host_log_config_raw."""
    host_rows, log_config_rows = parse_hosts(yaml_path)

    # Insert hosts
    host_objects = [StgHostRaw(**row) for row in host_rows]
    session.add_all(host_objects)
    session.flush()  # Populate host_id values

    # Build host_key -> host_id lookup for FK resolution
    host_id_map = {h.host_key: h.host_id for h in host_objects}

    # Insert log configs with resolved FK
    for row in log_config_rows:
        host_key = row.pop("host_key")
        row["host_id"] = host_id_map[host_key]
        session.add(StgHostLogConfigRaw(**row))

    session.flush()


def _load_audit(session: Session, dataset_root: Path) -> None:
    """Load stg_audit_line_raw from both audit.log files."""
    rows = parse_audit_files(dataset_root)

    # Map parsed dicts to ORM column names only (ignore any extra keys from parsing)
    valid_columns = {c.key for c in StgAuditLineRaw.__table__.columns} - {"row_id"}

    for row in rows:
        filtered = {k: v for k, v in row.items() if k in valid_columns}
        session.add(StgAuditLineRaw(**filtered))

    session.flush()


def _load_labels(session: Session, dataset_root: Path) -> None:
    """Load stg_attack_label_line_raw from all 8 JSONL files."""
    rows = parse_label_files(dataset_root)

    for row in rows:
        session.add(StgAttackLabelLineRaw(**row))

    session.flush()


def verify_counts(session: Session) -> bool:
    """Verify row counts match expected values. Returns True if all pass."""
    tables = {
        "stg_host_raw": StgHostRaw,
        "stg_host_log_config_raw": StgHostLogConfigRaw,
        "stg_audit_line_raw": StgAuditLineRaw,
        "stg_attack_label_line_raw": StgAttackLabelLineRaw,
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


def load_staging(dataset_root: Path) -> None:
    """Main entry point: parse all raw files and load into staging tables."""
    engine = create_engine(get_database_url())
    yaml_path = dataset_root / "processing" / "config" / "servers.yaml"

    print("Loading staging tables...")

    with Session(engine) as session:
        print("  Loading stg_host_raw + stg_host_log_config_raw...")
        _load_hosts(session, yaml_path)

        print("  Loading stg_audit_line_raw...")
        _load_audit(session, dataset_root)

        print("  Loading stg_attack_label_line_raw...")
        _load_labels(session, dataset_root)

        session.commit()
        print("\nAll staging tables committed.")

        print("\nVerification:")
        ok = verify_counts(session)

    if ok:
        print("\nAll counts match. Staging load complete.")
    else:
        print("\nWARNING: Some counts do not match expected values.")
        sys.exit(1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Load raw data into staging tables")
    parser.add_argument(
        "--dataset-root",
        type=Path,
        default=Path(__file__).resolve().parents[2] / ".." / "russellmitchell",
        help="Path to russellmitchell/ dataset directory",
    )
    args = parser.parse_args()

    if not args.dataset_root.exists():
        print(f"ERROR: Dataset not found at {args.dataset_root}")
        print("Pass --dataset-root or place russellmitchell/ next to the repo.")
        sys.exit(1)

    load_staging(args.dataset_root)
