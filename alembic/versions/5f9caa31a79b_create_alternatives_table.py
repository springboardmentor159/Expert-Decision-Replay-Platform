"""create alternatives table

Revision ID: 5f9caa31a79b
Revises: ba181107b922
Create Date: 2026-08-21

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5f9caa31a79b"
down_revision: Union[str, Sequence[str], None] = "ba181107b922"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create alternatives table."""

    op.create_table(
        "alternatives",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            nullable=False
        ),

        sa.Column(
            "decision_id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "name",
            sa.String(length=255),
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
            sa.String(length=20),
            nullable=False
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False
        ),

        sa.ForeignKeyConstraint(
            ["decision_id"],
            ["decisions.id"]
        )
    )

    op.create_index(
        "ix_alternatives_id",
        "alternatives",
        ["id"],
        unique=False
    )

    op.create_index(
        "ix_alternatives_decision_id",
        "alternatives",
        ["decision_id"],
        unique=False
    )


def downgrade() -> None:
    """Remove alternatives table."""

    op.drop_index(
        "ix_alternatives_decision_id",
        table_name="alternatives"
    )

    op.drop_index(
        "ix_alternatives_id",
        table_name="alternatives"
    )

    op.drop_table("alternatives")
