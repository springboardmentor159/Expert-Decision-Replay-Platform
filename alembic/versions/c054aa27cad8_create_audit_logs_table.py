"""create audit logs table

Revision ID: c054aa27cad8
Revises: 2a971b66b7df
Create Date: 2026-09-01 17:11:55.483765

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c054aa27cad8"
down_revision: Union[str, Sequence[str], None] = "2a971b66b7df"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create audit_logs table."""

    op.create_table(
        "audit_logs",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            "action",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "entity_type",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "entity_id",
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=False
        ),
        sa.Column(
            "ip_address",
            sa.String(),
            nullable=True
        ),
        sa.Column(
            "old_value",
            sa.Text(),
            nullable=True
        ),
        sa.Column(
            "new_value",
            sa.Text(),
            nullable=True
        ),
        sa.Column(
            "request_method",
            sa.String(),
            nullable=True
        ),
        sa.Column(
            "endpoint",
            sa.String(),
            nullable=True
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"]
        ),
        sa.PrimaryKeyConstraint("id")
    )

    op.create_index(
        op.f("ix_audit_logs_id"),
        "audit_logs",
        ["id"],
        unique=False
    )


def downgrade() -> None:
    """Drop audit_logs table."""

    op.drop_index(
        op.f("ix_audit_logs_id"),
        table_name="audit_logs"
    )

    op.drop_table("audit_logs")