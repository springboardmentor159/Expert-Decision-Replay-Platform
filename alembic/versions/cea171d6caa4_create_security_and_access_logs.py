"""create security and access logs

Revision ID: cea171d6caa4
Revises: 8b5aa2dc5d1c
Create Date: 2026-09-08 19:26:47.570194

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "cea171d6caa4"
down_revision: Union[str, Sequence[str], None] = "8b5aa2dc5d1c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create security_logs and access_logs tables."""

    # ==========================================
    # Create access_logs table
    # ==========================================
    op.create_table(
        "access_logs",
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
            "resource_type",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "resource_id",
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            "action",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "ip_address",
            sa.String(),
            nullable=True
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"]
        ),
        sa.PrimaryKeyConstraint("id")
    )

    op.create_index(
        "ix_access_logs_action",
        "access_logs",
        ["action"],
        unique=False
    )

    op.create_index(
        "ix_access_logs_created_at",
        "access_logs",
        ["created_at"],
        unique=False
    )

    op.create_index(
        "ix_access_logs_id",
        "access_logs",
        ["id"],
        unique=False
    )

    op.create_index(
        "ix_access_logs_resource_id",
        "access_logs",
        ["resource_id"],
        unique=False
    )

    op.create_index(
        "ix_access_logs_resource_type",
        "access_logs",
        ["resource_type"],
        unique=False
    )

    op.create_index(
        "ix_access_logs_user_id",
        "access_logs",
        ["user_id"],
        unique=False
    )

    # ==========================================
    # Create security_logs table
    # ==========================================
    op.create_table(
        "security_logs",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=True
        ),
        sa.Column(
            "event_type",
            sa.String(),
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
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"]
        ),
        sa.PrimaryKeyConstraint("id")
    )

    op.create_index(
        "ix_security_logs_created_at",
        "security_logs",
        ["created_at"],
        unique=False
    )

    op.create_index(
        "ix_security_logs_event_type",
        "security_logs",
        ["event_type"],
        unique=False
    )

    op.create_index(
        "ix_security_logs_id",
        "security_logs",
        ["id"],
        unique=False
    )

    op.create_index(
        "ix_security_logs_user_id",
        "security_logs",
        ["user_id"],
        unique=False
    )


def downgrade() -> None:
    """Remove security_logs and access_logs tables."""

    # ==========================================
    # Remove security_logs
    # ==========================================
    op.drop_index(
        "ix_security_logs_user_id",
        table_name="security_logs"
    )

    op.drop_index(
        "ix_security_logs_id",
        table_name="security_logs"
    )

    op.drop_index(
        "ix_security_logs_event_type",
        table_name="security_logs"
    )

    op.drop_index(
        "ix_security_logs_created_at",
        table_name="security_logs"
    )

    op.drop_table("security_logs")

    # ==========================================
    # Remove access_logs
    # ==========================================
    op.drop_index(
        "ix_access_logs_user_id",
        table_name="access_logs"
    )

    op.drop_index(
        "ix_access_logs_resource_type",
        table_name="access_logs"
    )

    op.drop_index(
        "ix_access_logs_resource_id",
        table_name="access_logs"
    )

    op.drop_index(
        "ix_access_logs_id",
        table_name="access_logs"
    )

    op.drop_index(
        "ix_access_logs_created_at",
        table_name="access_logs"
    )

    op.drop_index(
        "ix_access_logs_action",
        table_name="access_logs"
    )

    op.drop_table("access_logs")