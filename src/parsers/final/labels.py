"""Transformation helpers: staging labels table + taxonomy seed -> 3NF labels-domain row payloads.

Seed data for attack_phase and attack_label comes from project taxonomy (naman_labels_findings.md §4).
Each function returns dicts ready for insertion into the corresponding 3NF table. The loader is
responsible for session management, insertion order, and resolving phase_name -> phase_id for labels.
"""

import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.staging.labels import StgAttackLabelLineRaw

# Canonical 7 phases (snake_case). Source: naman_labels_findings.md §4
PHASE_NAMES = [
    "exfiltration",
    "web_enumeration",
    "initial_access",
    "reconnaissance",
    "privilege_escalation",
    "password_cracking",
    "exploitation",
]

# 22 labels -> phase_name. Source: naman_labels_findings.md §4
LABEL_TO_PHASE: dict[str, str] = {
    "attacker": "exfiltration",
    "dnsteal": "exfiltration",
    "dnsteal-received": "exfiltration",
    "dnsteal-dropped": "exfiltration",
    "exfiltration-service": "exfiltration",
    "attacker_http": "web_enumeration",
    "dirb": "web_enumeration",
    "wpscan": "web_enumeration",
    "foothold": "initial_access",
    "attacker_vpn": "initial_access",
    "service_scan": "reconnaissance",
    "dns_scan": "reconnaissance",
    "network_scan": "reconnaissance",
    "traceroute": "reconnaissance",
    "escalate": "privilege_escalation",
    "escalated_command": "privilege_escalation",
    "escalated_sudo_command": "privilege_escalation",
    "attacker_change_user": "privilege_escalation",
    "escalated_sudo_session": "privilege_escalation",
    "crack_passwords": "password_cracking",
    "webshell_cmd": "exploitation",
    "webshell_upload": "exploitation",
}


def get_attack_phase_seed() -> list[dict]:
    """Return seed rows for attack_phase (no session needed).

    Expected: 7 rows. Loader inserts these and builds phase_name -> phase_id.
    """
    return [{"phase_name": name} for name in PHASE_NAMES]


def get_attack_label_seed() -> list[dict]:
    """Return seed rows for attack_label with phase_name (no session needed).

    Each dict has label_name and phase_name. Loader must resolve phase_name -> phase_id
    before inserting. Expected: 22 rows.
    """
    return [
        {"label_name": label_name, "phase_name": phase_name}
        for label_name, phase_name in LABEL_TO_PHASE.items()
    ]


def transform_labeled_lines(session: Session) -> list[dict]:
    """Transform stg_attack_label_line_raw rows into labeled_line rows.

    Returns list of dicts with source_host, source_log, line_number.
    Expected: 61,862 rows.
    """
    stg_rows = session.scalars(select(StgAttackLabelLineRaw)).all()
    return [
        {
            "source_host": row.source_host,
            "source_log": row.source_log,
            "line_number": row.line_number,
        }
        for row in stg_rows
    ]


def explode_labeled_line_labels(
    session: Session,
    provenance_to_labeled_line_id: dict[tuple[str, str, int], int],
    label_name_to_id: dict[str, int],
) -> list[dict]:
    """Explode labels_json into labeled_line_label rows.

    Args:
        session: Active DB session with staging data loaded.
        provenance_to_labeled_line_id: (source_host, source_log, line_number) -> labeled_line_id.
        label_name_to_id: label_name -> label_id from seeded attack_label.

    Returns:
        List of dicts with labeled_line_id, label_id. Expected: ~184,517 rows.
    """
    stg_rows = session.scalars(select(StgAttackLabelLineRaw)).all()
    rows = []
    for row in stg_rows:
        key = (row.source_host, row.source_log, row.line_number)
        labeled_line_id = provenance_to_labeled_line_id.get(key)
        if labeled_line_id is None:
            continue
        for label_name in json.loads(row.labels_json):
            label_id = label_name_to_id.get(label_name)
            if label_id is None:
                raise ValueError(f"Unknown label in taxonomy: {label_name!r}")
            rows.append({"labeled_line_id": labeled_line_id, "label_id": label_id})
    return rows


def explode_labeled_line_rules(
    session: Session,
    provenance_to_labeled_line_id: dict[tuple[str, str, int], int],
    label_name_to_id: dict[str, int],
) -> list[dict]:
    """Explode rules_json into labeled_line_rule rows.

    Args:
        session: Active DB session with staging data loaded.
        provenance_to_labeled_line_id: (source_host, source_log, line_number) -> labeled_line_id.
        label_name_to_id: label_name -> label_id from seeded attack_label.

    Returns:
        List of dicts with labeled_line_id, label_id, rule_name.
    """
    stg_rows = session.scalars(select(StgAttackLabelLineRaw)).all()
    rows = []
    for row in stg_rows:
        key = (row.source_host, row.source_log, row.line_number)
        labeled_line_id = provenance_to_labeled_line_id.get(key)
        if labeled_line_id is None:
            continue
        rules = json.loads(row.rules_json)
        for label_name, rule_names in rules.items():
            label_id = label_name_to_id.get(label_name)
            if label_id is None:
                raise ValueError(f"Unknown label in taxonomy: {label_name!r}")
            for rule_name in rule_names:
                rows.append(
                    {
                        "labeled_line_id": labeled_line_id,
                        "label_id": label_id,
                        "rule_name": rule_name,
                    }
                )
    return rows


def expected_labeled_line_rule_count(session: Session) -> int:
    """Compute expected number of labeled_line_rule rows from staging.

    Sums the number of rule names across all rules_json values. Used for verify_counts.
    """
    stg_rows = session.scalars(select(StgAttackLabelLineRaw)).all()
    total = 0
    for row in stg_rows:
        rules = json.loads(row.rules_json)
        for rule_list in rules.values():
            total += len(rule_list)
    return total
