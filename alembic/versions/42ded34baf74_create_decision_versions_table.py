"""create decision versions table

Revision ID: 42ded34baf74
Revises: c054aa27cad8
Create Date: 2026-09-01 17:18:31.286180

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "42ded34baf74"
down_revision: Union[str, Sequence[str], None] = "c054aa27cad8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create decision_versions table."""

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
            "category",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "status",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "changed_by",
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            "change_summary",
            sa.Text(),
            nullable=True
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["decision_id"],
            ["decisions.id"]
        ),
        sa.ForeignKeyConstraint(
            ["changed_by"],
            ["users.id"]
        ),
        sa.PrimaryKeyConstraint("id")
    )

    op.create_index(
        op.f("ix_decision_versions_id"),
        "decision_versions",
        ["id"],
        unique=False
    )


def downgrade() -> None:
    """Drop decision_versions table."""

    op.drop_index(
        op.f("ix_decision_versions_id"),
        table_name="decision_versions"
    )

    op.drop_table("decision_versions")