"""3NF labels loader: staging -> labels-domain normalized tables.

Reads from stg_attack_label_line_raw (already loaded by load_staging.py) and
populates the 5 labels 3NF tables in FK-dependency order.

Usage:
    python -m src.loaders.load_3nf_labels

Requires:
  - DATABASE_URL or DB_* env vars
  - Labels 3NF tables created (via DDL in sql/3nf/ or migration)
  - Staging table stg_attack_label_line_raw populated (via load_staging.py)
"""

import os
import sys

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from src.models.final.labels import (
    AttackLabel,
    AttackPhase,
    LabeledLine,
    LabeledLineLabel,
    LabeledLineRule,
)
from src.parsers.final.labels import (
    expected_labeled_line_rule_count,
    explode_labeled_line_labels,
    explode_labeled_line_rules,
    get_attack_label_seed,
    get_attack_phase_seed,
    transform_labeled_lines,
)

# Expected row counts (from docs/schema/labels_normalization_staging_to_3nf.md)
EXPECTED_COUNTS = {
    "attack_phase": 7,
    "attack_label": 22,
    "labeled_line": 61_862,
    "labeled_line_label": 184_517,
    # labeled_line_rule: set at runtime from expected_labeled_line_rule_count(session)
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


def _load_attack_phase(session: Session) -> dict[str, int]:
    """Phase 1: Load attack_phase lookup table (seed from taxonomy).

    Returns: {phase_name: phase_id} mapping.
    """
    rows = get_attack_phase_seed()
    objects = [AttackPhase(**row) for row in rows]
    session.add_all(objects)
    session.flush()
    return {obj.phase_name: obj.phase_id for obj in objects}


def _load_attack_label(
    session: Session, phase_name_to_id: dict[str, int]
) -> dict[str, int]:
    """Phase 2: Load attack_label lookup table (seed from taxonomy).

    Resolves phase_name -> phase_id from seed rows. Returns: {label_name: label_id} mapping.
    """
    rows = get_attack_label_seed()
    objects = []
    for row in rows:
        phase_id = phase_name_to_id[row["phase_name"]]
        objects.append(AttackLabel(label_name=row["label_name"], phase_id=phase_id))
    session.add_all(objects)
    session.flush()
    return {obj.label_name: obj.label_id for obj in objects}


def _load_labeled_line(
    session: Session,
) -> dict[tuple[str, str, int], int]:
    """Phase 3: Load labeled_line from staging.

    Returns: {(source_host, source_log, line_number): labeled_line_id} mapping.
    """
    rows = transform_labeled_lines(session)
    objects = [LabeledLine(**row) for row in rows]
    session.add_all(objects)
    session.flush()
    return {
        (obj.source_host, obj.source_log, obj.line_number): obj.labeled_line_id
        for obj in objects
    }


def _load_labeled_line_junctions(
    session: Session,
    provenance_to_id: dict[tuple[str, str, int], int],
    label_name_to_id: dict[str, int],
) -> None:
    """Phase 4: Load labeled_line_label and labeled_line_rule (FK -> labeled_line, attack_label)."""
    for row in explode_labeled_line_labels(session, provenance_to_id, label_name_to_id):
        session.add(LabeledLineLabel(**row))
    for row in explode_labeled_line_rules(session, provenance_to_id, label_name_to_id):
        session.add(LabeledLineRule(**row))
    session.flush()


def verify_counts(session: Session, expected_labeled_line_rule: int | None = None) -> bool:
    """Verify row counts match expected values. Returns True if all pass."""
    tables = {
        "attack_phase": AttackPhase,
        "attack_label": AttackLabel,
        "labeled_line": LabeledLine,
        "labeled_line_label": LabeledLineLabel,
        "labeled_line_rule": LabeledLineRule,
    }

    all_ok = True
    for table_name, model in tables.items():
        actual = session.scalar(select(func.count()).select_from(model))
        expected = EXPECTED_COUNTS.get(table_name)
        if table_name == "labeled_line_rule" and expected_labeled_line_rule is not None:
            expected = expected_labeled_line_rule
        if expected is None:
            print(f"  {table_name}: {actual} rows (no expected set)")
            continue
        status = "OK" if actual == expected else "MISMATCH"
        if actual != expected:
            all_ok = False
        print(f"  {table_name}: {actual} rows (expected {expected}) [{status}]")

    return all_ok


def load_3nf_labels() -> None:
    """Main entry point: transform staging -> 3NF labels-domain tables."""
    engine = create_engine(get_database_url())

    print("Loading 3NF labels-domain tables from staging...")

    with Session(engine) as session:
        # Compute expected labeled_line_rule count from staging (for verify_counts)
        expected_labeled_line_rule = expected_labeled_line_rule_count(session)

        print("  Phase 1: attack_phase...")
        phase_name_to_id = _load_attack_phase(session)

        print("  Phase 2: attack_label...")
        label_name_to_id = _load_attack_label(session, phase_name_to_id)

        print("  Phase 3: labeled_line...")
        provenance_to_id = _load_labeled_line(session)

        print("  Phase 4: labeled_line_label, labeled_line_rule...")
        _load_labeled_line_junctions(session, provenance_to_id, label_name_to_id)

        session.commit()
        print("\nAll 3NF labels-domain tables committed.")

        print("\nRow count verification:")
        counts_ok = verify_counts(session, expected_labeled_line_rule=expected_labeled_line_rule)

    if counts_ok:
        print("\nAll verifications passed. 3NF labels-domain load complete.")
    else:
        print("\nWARNING: Some verifications failed.")
        sys.exit(1)


if __name__ == "__main__":
    load_3nf_labels()
