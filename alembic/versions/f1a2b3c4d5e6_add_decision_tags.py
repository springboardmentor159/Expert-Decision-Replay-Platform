"""add tags and decision tag associations"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, Sequence[str], None] = "47fdcbff34b7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_tags_id", "tags", ["id"], unique=False)
    op.create_index("ix_tags_name", "tags", ["name"], unique=False)
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