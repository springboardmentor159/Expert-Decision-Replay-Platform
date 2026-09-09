"""create audit logs table

Revision ID: b35f2c901c80
Revises: b5feb4225796
Create Date: 2026-09-07 15:23:53.415613

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b35f2c901c80"
down_revision: Union[str, Sequence[str], None] = "b5feb4225796"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create audit_logs table."""

    op.create_table(
        "audit_logs",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            nullable=False
        ),

        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id"),
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
            sa.JSON(),
            nullable=True
        ),

        sa.Column(
            "new_value",
            sa.JSON(),
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
            server_default=sa.text("now()"),
            nullable=False
        )
    )

    op.create_index(
        "ix_audit_logs_id",
        "audit_logs",
        ["id"],
        unique=False
    )

    op.create_index(
        "ix_audit_logs_action",
        "audit_logs",
        ["action"],
        unique=False
    )

    op.create_index(
        "ix_audit_logs_entity_type",
        "audit_logs",
        ["entity_type"],
        unique=False
    )

    op.create_index(
        "ix_audit_logs_entity_id",
        "audit_logs",
        ["entity_id"],
        unique=False
    )

    op.create_index(
        "ix_audit_logs_created_at",
        "audit_logs",
        ["created_at"],
        unique=False
    )


def downgrade() -> None:
    """Drop audit_logs table."""

    op.drop_index(
        "ix_audit_logs_created_at",
        table_name="audit_logs"
    )

    op.drop_index(
        "ix_audit_logs_entity_id",
        table_name="audit_logs"
    )

    op.drop_index(
        "ix_audit_logs_entity_type",
        table_name="audit_logs"
    )

    op.drop_index(
        "ix_audit_logs_action",
        table_name="audit_logs"
    )

    op.drop_index(
        "ix_audit_logs_id",
        table_name="audit_logs"
    )

    op.drop_table("audit_logs")