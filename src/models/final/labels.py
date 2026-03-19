"""3NF models for the labels domain.

Tables:
  attack_phase       - Lookup for 7 attack phases (7 rows)
  attack_label       - Lookup for 22 labels + phase_id (22 rows)
  labeled_line       - One row per (source_host, source_log, line_number) (61,862 rows)
  labeled_line_label - Junction line <-> label (~184,517 rows)
  labeled_line_rule  - Junction (line, label, rule_name)

Source: docs/schema/labels_normalization_staging_to_3nf.md
"""

from sqlalchemy import ForeignKey, ForeignKeyConstraint, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class AttackPhase(Base):
    """3NF lookup table for 7 attack phases. Seeded from project taxonomy."""

    __tablename__ = "attack_phase"

    phase_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    phase_name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)


class AttackLabel(Base):
    """3NF lookup table for 22 labels with phase_id (resolves FD label_name -> attack_phase)."""

    __tablename__ = "attack_label"

    label_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    label_name: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    phase_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("attack_phase.phase_id"), nullable=False
    )


class LabeledLine(Base):
    """One row per (source_host, source_log, line_number); provenance for joins to host/audit."""

    __tablename__ = "labeled_line"
    __table_args__ = (
        UniqueConstraint(
            "source_host", "source_log", "line_number", name="uq_labeled_line_provenance"
        ),
    )

    labeled_line_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_host: Mapped[str] = mapped_column(String(30), nullable=False)
    source_log: Mapped[str] = mapped_column(String(50), nullable=False)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)


class LabeledLineLabel(Base):
    """Junction table: which labels apply to which line (1NF resolution of labels_json)."""

    __tablename__ = "labeled_line_label"

    labeled_line_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("labeled_line.labeled_line_id", ondelete="CASCADE"),
        primary_key=True,
    )
    label_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("attack_label.label_id"), primary_key=True
    )


class LabeledLineRule(Base):
    """Junction table: (line, label, rule_name); 1NF resolution of rules_json.

    Composite FK (labeled_line_id, label_id) -> labeled_line_label enforces that
    a rule can only exist for a (line, label) pair already in the label assignment junction.
    """

    __tablename__ = "labeled_line_rule"
    __table_args__ = (
        ForeignKeyConstraint(
            ["labeled_line_id", "label_id"],
            ["labeled_line_label.labeled_line_id", "labeled_line_label.label_id"],
        ),
    )

    labeled_line_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("labeled_line.labeled_line_id", ondelete="CASCADE"),
        primary_key=True,
    )
    label_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rule_name: Mapped[str] = mapped_column(String(120), nullable=False, primary_key=True)