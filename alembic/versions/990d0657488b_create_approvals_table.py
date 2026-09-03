"""create approvals table

Revision ID: 990d0657488b
Revises: 2af9914c82f2
Create Date: 2026-09-03

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "990d0657488b"
down_revision: Union[str, Sequence[str], None] = "2af9914c82f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "approvals",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "decision_id",
            sa.Integer(),
            sa.ForeignKey("decisions.id"),
            nullable=False
        ),
        sa.Column(
            "reviewer_id",
            sa.Integer(),
            sa.ForeignKey("users.id"),
            nullable=False
        ),
        sa.Column(
            "approval_level",
            sa.Integer(),
            nullable=False,
            server_default="1"
        ),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
            server_default="Pending"
        ),
        sa.Column(
            "assigned_at",
            sa.DateTime(),
            server_default=sa.func.now()
        ),
        sa.Column(
            "completed_at",
            sa.DateTime(),
            nullable=True
        )
    )


def downgrade() -> None:
    op.drop_table("approvals")