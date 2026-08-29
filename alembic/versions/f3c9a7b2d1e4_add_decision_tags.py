"""add decision tags

Revision ID: f3c9a7b2d1e4
Revises: 0eb6079c8e8c
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "f3c9a7b2d1e4"
down_revision: Union[str, Sequence[str], None] = "6a0b3d617606"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_tags_id", "tags", ["id"])
    op.create_index("ix_tags_name", "tags", ["name"])
    op.create_table(
        "decision_tags",
        sa.Column("decision_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["decision_id"], ["decisions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("decision_id", "tag_id"),
    )


def downgrade() -> None:
    op.drop_table("decision_tags")
    op.drop_index("ix_tags_name", table_name="tags")
    op.drop_index("ix_tags_id", table_name="tags")
    op.drop_table("tags")