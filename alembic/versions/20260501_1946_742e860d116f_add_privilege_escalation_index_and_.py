"""add privilege escalation index and timeline view

Revision ID: 742e860d116f
Revises: b4258b656aa5
Create Date: 2026-05-01 19:46:17.351568

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "742e860d116f"
down_revision: str | None = "b4258b656aa5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# Names kept in module-level constants so upgrade and downgrade stay in sync.
# Canonical DDL also lives in sql/3nf/_indexes.sql and sql/3nf/_views.sql for
# rubric reproducibility (schema.sql / indexes.sql / views.sql artifacts).
INDEX_NAME = "idx_audit_event_host_timestamp"
INDEX_TABLE = "audit_event"
INDEX_COLUMNS = ["host_id", "timestamp"]

VIEW_NAME = "v_privilege_escalation_timeline"

VIEW_DDL = """
CREATE OR REPLACE VIEW v_privilege_escalation_timeline AS
SELECT h.host_key,
       ae.event_id,
       ae.timestamp,
       ae.type                 AS audit_type,
       am.op                   AS pam_operation,
       am.acct                 AS target_account,
       am.exe                  AS executable,
       am.terminal,
       string_agg(DISTINCT al.label_name, ', '
                  ORDER BY al.label_name) AS labels,
       string_agg(DISTINCT llr.rule_name, ', '
                  ORDER BY llr.rule_name) AS rules
FROM audit_event ae
JOIN host h               ON h.host_id = ae.host_id
JOIN labeled_line ll      ON ll.source_host = h.host_key
                         AND ll.source_log  = 'audit.log'
                         AND ll.line_number = ae.line_number
JOIN labeled_line_label lll ON lll.labeled_line_id = ll.labeled_line_id
JOIN attack_label al      ON al.label_id = lll.label_id
JOIN attack_phase ap      ON ap.phase_id = al.phase_id
LEFT JOIN audit_message am ON am.event_id = ae.event_id
LEFT JOIN labeled_line_rule llr
       ON llr.labeled_line_id = ll.labeled_line_id
      AND llr.label_id        = al.label_id
WHERE ap.phase_name = 'privilege_escalation'
GROUP BY h.host_key, ae.event_id, ae.timestamp, ae.type,
         am.op, am.acct, am.exe, am.terminal;
"""


def upgrade() -> None:
    """Upgrade database schema."""
    op.create_index(
        INDEX_NAME,
        INDEX_TABLE,
        INDEX_COLUMNS,
        unique=False,
    )
    op.execute(VIEW_DDL)


def downgrade() -> None:
    """Downgrade database schema."""
    op.execute(f"DROP VIEW IF EXISTS {VIEW_NAME}")
    op.drop_index(
        INDEX_NAME,
        table_name=INDEX_TABLE,
    )
