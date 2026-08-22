"""create comments table

Revision ID: a18a01a008d6
Revises: 5f9caa31a79b
Create Date: 2026-08-22

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a18a01a008d6"
down_revision: Union[str, Sequence[str], None] = "5f9caa31a79b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create comments table."""

    op.create_table(
        "comments",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            nullable=False
        ),

        sa.Column(
            "decision_id",
            sa.Integer(),
            sa.ForeignKey("decisions.id"),
            nullable=False
        ),

        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id"),
            nullable=False
        ),

        sa.Column(
            "content",
            sa.Text(),
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
        )
    )

    op.create_index(
        "ix_comments_id",
        "comments",
        ["id"],
        unique=False
    )


def downgrade() -> None:
    """Remove comments table."""

    op.drop_index(
        "ix_comments_id",
        table_name="comments"
    )

    op.drop_table("comments")