from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2f86943ad0af"
down_revision: Union[str, Sequence[str], None] = "a9e7ea1fde3f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create decisions table."""

    op.create_table(
        "decisions",

        sa.Column(
            "id",
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
            "created_by",
            sa.Integer(),
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
            ["created_by"],
            ["users.id"]
        ),

        sa.PrimaryKeyConstraint("id")
    )

    op.create_index(
        op.f("ix_decisions_id"),
        "decisions",
        ["id"],
        unique=False
    )


def downgrade() -> None:
    """Remove decisions table."""

    op.drop_index(
        op.f("ix_decisions_id"),
        table_name="decisions"
    )

    op.drop_table("decisions")