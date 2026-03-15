"""create 3nf host domain tables

Revision ID: 358010f5f4cc
Revises: ff2c88ab6174
Create Date: 2026-03-14 18:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "358010f5f4cc"
down_revision: str | None = "ff2c88ab6174"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the 7 host-domain 3NF tables."""
    # 1. os_release (no FK deps)
    op.create_table(
        "os_release",
        sa.Column("os_release_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("distribution_release", sa.String(length=20), nullable=False),
        sa.Column("distribution", sa.String(length=50), nullable=False),
        sa.Column("distribution_version", sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint("os_release_id"),
        sa.UniqueConstraint("distribution_release"),
    )

    # 2. host (FK -> os_release)
    op.create_table(
        "host",
        sa.Column("host_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("host_key", sa.String(length=50), nullable=False),
        sa.Column("hostname", sa.String(length=100), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=True),
        sa.Column("openvpn_user", sa.String(length=50), nullable=True),
        sa.Column("default_ipv4_address", sa.String(length=45), nullable=False),
        sa.Column("default_ipv6_address", sa.String(length=45), nullable=False),
        sa.Column("timezone", sa.String(length=10), nullable=False),
        sa.Column("os_release_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["os_release_id"], ["os_release.os_release_id"]),
        sa.PrimaryKeyConstraint("host_id"),
        sa.UniqueConstraint("host_key"),
        sa.UniqueConstraint("hostname"),
    )

    # 3. host_group (FK -> host)
    op.create_table(
        "host_group",
        sa.Column("host_id", sa.Integer(), nullable=False),
        sa.Column("group_name", sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(["host_id"], ["host.host_id"]),
        sa.PrimaryKeyConstraint("host_id", "group_name"),
    )

    # 4. host_fqdn (FK -> host)
    op.create_table(
        "host_fqdn",
        sa.Column("host_id", sa.Integer(), nullable=False),
        sa.Column("fqdn", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(["host_id"], ["host.host_id"]),
        sa.PrimaryKeyConstraint("host_id", "fqdn"),
    )

    # 5. host_ipv4 (FK -> host)
    op.create_table(
        "host_ipv4",
        sa.Column("host_id", sa.Integer(), nullable=False),
        sa.Column("ipv4_address", sa.String(length=45), nullable=False),
        sa.ForeignKeyConstraint(["host_id"], ["host.host_id"]),
        sa.PrimaryKeyConstraint("host_id", "ipv4_address"),
    )

    # 6. host_ipv6 (FK -> host)
    op.create_table(
        "host_ipv6",
        sa.Column("host_id", sa.Integer(), nullable=False),
        sa.Column("ipv6_address", sa.String(length=45), nullable=False),
        sa.ForeignKeyConstraint(["host_id"], ["host.host_id"]),
        sa.PrimaryKeyConstraint("host_id", "ipv6_address"),
    )

    # 7. host_log_config (FK -> host)
    op.create_table(
        "host_log_config",
        sa.Column("config_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("host_id", sa.Integer(), nullable=False),
        sa.Column("log_path", sa.Text(), nullable=False),
        sa.Column("log_type", sa.String(length=50), nullable=False),
        sa.Column("codec", sa.Text(), nullable=True),
        sa.Column("file_chunk_size", sa.Integer(), nullable=True),
        sa.Column("add_field_json", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["host_id"], ["host.host_id"]),
        sa.PrimaryKeyConstraint("config_id"),
        sa.UniqueConstraint("host_id", "log_path", name="uq_host_log_config_host_path"),
    )


def downgrade() -> None:
    """Drop the 7 host-domain 3NF tables in reverse FK order."""
    op.drop_table("host_log_config")
    op.drop_table("host_ipv6")
    op.drop_table("host_ipv4")
    op.drop_table("host_fqdn")
    op.drop_table("host_group")
    op.drop_table("host")
    op.drop_table("os_release")
