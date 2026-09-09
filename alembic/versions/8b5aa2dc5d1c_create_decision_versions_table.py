"""create decision versions table

Revision ID: 8b5aa2dc5d1c
Revises: b35f2c901c80
Create Date: 2026-09-07 19:32:18.845662

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "8b5aa2dc5d1c"
down_revision: Union[str, Sequence[str], None] = "b35f2c901c80"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create decision_versions table."""

    decision_status_enum = postgresql.ENUM(
        "DRAFT",
        "UNDER_REVIEW",
        "APPROVED",
        "REJECTED",
        "ARCHIVED",
        name="decisionstatus",
        create_type=False,
    )

    op.create_table(
        "decision_versions",

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
            "version_number",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "title",
            sa.String(),
            nullable=False
        ),

        sa.Column(
            "problem_statement",
            sa.Text(),
            nullable=False
        ),

        sa.Column(
            "description",
            sa.Text(),
            nullable=True
        ),

        sa.Column(
            "category",
            sa.String(),
            nullable=True
        ),

        sa.Column(
            "status",
            decision_status_enum,
            nullable=False
        ),

        sa.Column(
            "created_by",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False
        ),

        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"]
        ),

        sa.ForeignKeyConstraint(
            ["decision_id"],
            ["decisions.id"]
        ),

        sa.PrimaryKeyConstraint("id")
    )

    op.create_index(
        "ix_decision_versions_decision_id",
        "decision_versions",
        ["decision_id"],
        unique=False
    )

    op.create_index(
        "ix_decision_versions_id",
        "decision_versions",
        ["id"],
        unique=False
    )


def downgrade() -> None:
    """Drop decision_versions table."""

    op.drop_index(
        "ix_decision_versions_id",
        table_name="decision_versions"
    )

    op.drop_index(
        "ix_decision_versions_decision_id",
        table_name="decision_versions"
    )

    op.drop_table("decision_versions")