"""create approvals

Revision ID: ab1c2d3e4f5a
Revises: 9a0b1c2d3e4f
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "ab1c2d3e4f5a"
down_revision: Union[str, Sequence[str], None] = "9a0b1c2d3e4f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "approvals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("decision_id", sa.Integer(), nullable=False),
        sa.Column("reviewer_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="Pending"),
        sa.Column("comments", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["decision_id"], ["decisions.id"]),
        sa.ForeignKeyConstraint(["reviewer_id"], ["users.id"]),
    )
    for column in ("id", "decision_id", "reviewer_id", "status"):
        op.create_index(f"ix_approvals_{column}", "approvals", [column], unique=False)


def downgrade() -> None:
    op.drop_table("approvals")