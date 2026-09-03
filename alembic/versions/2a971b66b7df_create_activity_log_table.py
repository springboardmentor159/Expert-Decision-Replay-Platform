"""create activity log table

Revision ID: 2a971b66b7df
Revises: f5d5a8e8d292
Create Date: 2026-08-31 21:11:45.241003

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2a971b66b7df"
down_revision: Union[str, Sequence[str], None] = "f5d5a8e8d292"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create activities table."""

    op.create_table(
        "activities",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            "action",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "entity_type",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "entity_id",
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            "description",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"]
        ),
        sa.PrimaryKeyConstraint("id")
    )

    op.create_index(
        op.f("ix_activities_id"),
        "activities",
        ["id"],
        unique=False
    )


def downgrade() -> None:
    """Drop activities table."""

    op.drop_index(
        op.f("ix_activities_id"),
        table_name="activities"
    )

    op.drop_table("activities")