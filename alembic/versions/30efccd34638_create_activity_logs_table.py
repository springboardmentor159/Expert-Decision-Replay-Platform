"""create activity logs table

Revision ID: 30efccd34638
Revises: 06e9a651acbb
Create Date: 2026-08-27
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "30efccd34638"
down_revision: Union[str, Sequence[str], None] = "06e9a651acbb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create activity logs table."""

    op.create_table(
        "activity_logs",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            nullable=False
        ),

        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey(
                "users.id",
                ondelete="CASCADE"
            ),
            nullable=False
        ),

        sa.Column(
            "action",
            sa.String(length=100),
            nullable=False
        ),

        sa.Column(
            "entity_type",
            sa.String(length=50),
            nullable=False
        ),

        sa.Column(
            "entity_id",
            sa.Integer(),
            nullable=True
        ),

        sa.Column(
            "description",
            sa.Text(),
            nullable=False
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False
        )
    )

    op.create_index(
        "ix_activity_logs_id",
        "activity_logs",
        ["id"],
        unique=False
    )


def downgrade() -> None:
    """Remove activity logs table."""

    op.drop_index(
        "ix_activity_logs_id",
        table_name="activity_logs"
    )

    op.drop_table("activity_logs")