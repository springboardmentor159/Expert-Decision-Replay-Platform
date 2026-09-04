"""create alternatives table

Revision ID: 7d7636eccd7d
Revises: 297c34e8513a
Create Date: 2026-08-18 15:55:10.699238

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "7d7636eccd7d"
down_revision: Union[str, Sequence[str], None] = "297c34e8513a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Create risk_level enum if it does not already exist.
    risk_level_enum = postgresql.ENUM(
        "Low",
        "Medium",
        "High",
        "Critical",
        name="risk_level"
    )

    risk_level_enum.create(
        op.get_bind(),
        checkfirst=True
    )

    # Use the already-existing enum when creating the table.
    risk_level_column = postgresql.ENUM(
        "Low",
        "Medium",
        "High",
        "Critical",
        name="risk_level",
        create_type=False
    )

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
            sa.Numeric(
                precision=12,
                scale=2
            ),
            nullable=False
        ),

        sa.Column(
            "feasibility_score",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "risk_level",
            risk_level_column,
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

        sa.PrimaryKeyConstraint("id"),

        sa.CheckConstraint(
            "feasibility_score >= 1 AND feasibility_score <= 5",
            name="check_feasibility_score"
        )
    )

    op.create_index(
        op.f("ix_alternatives_id"),
        "alternatives",
        ["id"],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_alternatives_id"),
        table_name="alternatives"
    )

    op.drop_table(
        "alternatives"
    )

    risk_level_enum = postgresql.ENUM(
        "Low",
        "Medium",
        "High",
        "Critical",
        name="risk_level"
    )

    risk_level_enum.drop(
        op.get_bind(),
        checkfirst=True
    )
