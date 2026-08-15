"""create decisions table

Revision ID: e421141fef43
Revises: cc32d4da92a5
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e421141fef43"
down_revision: Union[str, Sequence[str], None] = "cc32d4da92a5"
branch_labels = None
depends_on = None


def upgrade() -> None:

    op.create_table(
        "decisions",

        sa.Column("id", sa.Integer(), primary_key=True, index=True),

        sa.Column("title", sa.String(), nullable=False),

        sa.Column(
            "problem_statement",
            sa.Text(),
            nullable=False
        ),

        sa.Column(
            "category",
            sa.String(),
            nullable=False
        ),

        sa.Column(
            "status",
            sa.String(),
            nullable=False,
            server_default="Draft"
        ),

        sa.Column(
            "created_by",
            sa.Integer(),
            sa.ForeignKey("users.id"),
            nullable=False
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False
        ),
    )


def downgrade() -> None:

    op.drop_table("decisions")