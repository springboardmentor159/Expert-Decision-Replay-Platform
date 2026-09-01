"""create alternatives table

Revision ID: e8ce975c8d11
Revises: 3647104d5759
Create Date: 2026-08-25 17:57:49.947589

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e8ce975c8d11"
down_revision: Union[str, Sequence[str], None] = "3647104d5759"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create alternatives table."""

    op.create_table(
        "alternatives",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "decision_id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "name",
            sa.String(),
            nullable=False
        ),

        sa.Column(
            "description",
            sa.Text(),
            nullable=False
        ),

        sa.Column(
            "pros",
            sa.Text(),
            nullable=False
        ),

        sa.Column(
            "cons",
            sa.Text(),
            nullable=False
        ),

        sa.Column(
            "estimated_cost",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "feasibility_score",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "risk_level",
            sa.String(),
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

        sa.ForeignKeyConstraint(
            ["decision_id"],
            ["decisions.id"]
        ),

        sa.PrimaryKeyConstraint("id")
    )

    op.create_index(
        op.f("ix_alternatives_id"),
        "alternatives",
        ["id"],
        unique=False
    )


def downgrade() -> None:
    """Drop alternatives table."""

    op.drop_index(
        op.f("ix_alternatives_id"),
        table_name="alternatives"
    )

    op.drop_table("alternatives")