"""Staging model for attack label lines.

Table:
  stg_attack_label_line_raw - merged table for all 8 label JSONL files (61,862 rows)

labels_json and rules_json are stored as JSON-serialized TEXT.
Decomposition into junction tables is deferred to 3NF ETL.
"""

from sqlalchemy import Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class StgAttackLabelLineRaw(Base):
    """Staging table for attack label lines from 8 JSONL files.

    Candidate key (source_host, source_log, line_number) is unique; enforced
    so duplicate loads or re-runs do not create duplicate rows.
    """

    __tablename__ = "stg_attack_label_line_raw"
    __table_args__ = (
        UniqueConstraint(
            "source_host",
            "source_log",
            "line_number",
            name="uq_stg_attack_label_line_raw_provenance",
        ),
    )

    row_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_host: Mapped[str] = mapped_column(String(30), nullable=False)
    source_log: Mapped[str] = mapped_column(String(50), nullable=False)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    labels_json: Mapped[str] = mapped_column(Text, nullable=False)
    rules_json: Mapped[str] = mapped_column(Text, nullable=False)
