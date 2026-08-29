"""add approvals and activity logs

Revision ID: c81d4e6f2a10
Revises: f3c9a7b2d1e4
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "c81d4e6f2a10"
down_revision: Union[str, Sequence[str], None] = "f3c9a7b2d1e4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("approvals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("decision_id", sa.Integer(), nullable=False),
        sa.Column("reviewer_id", sa.Integer(), nullable=False),
        sa.Column("approval_level", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", sa.String(), nullable=False, server_default="Pending"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["decision_id"], ["decisions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reviewer_id"], ["users.id"]),
    )
    op.create_index("ix_approvals_id", "approvals", ["id"])
    op.create_index("ix_approvals_decision_id", "approvals", ["decision_id"])
    op.create_index("ix_approvals_reviewer_id", "approvals", ["reviewer_id"])
    op.create_index("ix_approvals_status", "approvals", ["status"])
    op.create_table("activity_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("entity_type", sa.String(), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    for column in ("id", "user_id", "action", "entity_type", "created_at"):
        op.create_index(f"ix_activity_logs_{column}", "activity_logs", [column])


def downgrade() -> None:
    op.drop_table("activity_logs")
    op.drop_table("approvals")