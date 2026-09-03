"""add activity logs

Revision ID: 9a0b1c2d3e4f
Revises: f1a2b3c4d5e6
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9a0b1c2d3e4f"
down_revision: Union[str, Sequence[str], None] = "f1a2b3c4d5e6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "activity_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("entity_type", sa.String(), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index("ix_activity_logs_id", "activity_logs", ["id"], unique=False)
    op.create_index("ix_activity_logs_user_id", "activity_logs", ["user_id"], unique=False)
    op.create_index("ix_activity_logs_action", "activity_logs", ["action"], unique=False)
    op.create_index("ix_activity_logs_entity_type", "activity_logs", ["entity_type"], unique=False)
    op.create_index("ix_activity_logs_created_at", "activity_logs", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_table("activity_logs")