"""create approvals table

Revision ID: 0c599cdc5eaf
Revises: a7d197f3bdc4
Create Date: 2026-09-03 11:21:04.222687

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0c599cdc5eaf"
down_revision: Union[str, Sequence[str], None] = "a7d197f3bdc4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create approvals table."""

    op.create_table(
        "approvals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("decision_id", sa.Integer(), nullable=False),
        sa.Column("reviewer_id", sa.Integer(), nullable=False),
        sa.Column("approval_level", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.String(),
            nullable=False,
            server_default="Pending"
        ),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["decision_id"],
            ["decisions.id"],
        ),
        sa.ForeignKeyConstraint(
            ["reviewer_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_approvals_id"),
        "approvals",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    """Drop approvals table."""

    op.drop_index(
        op.f("ix_approvals_id"),
        table_name="approvals",
    )

    op.drop_table("approvals")