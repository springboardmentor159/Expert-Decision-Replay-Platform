"""add approval escalation fields

Revision ID: 15ccf26dfcf5
Revises: cdc23915ee0f
Create Date: 2026-09-15
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "15ccf26dfcf5"
down_revision: Union[str, None] = "cdc23915ee0f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "approvals",
        sa.Column("due_at", sa.DateTime(), nullable=True),
    )

    op.add_column(
        "approvals",
        sa.Column(
            "escalated",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )

    op.add_column(
        "approvals",
        sa.Column("escalated_at", sa.DateTime(), nullable=True),
    )

    op.add_column(
        "approvals",
        sa.Column("escalation_reason", sa.String(), nullable=True),
    )

    op.alter_column(
        "approvals",
        "escalated",
        server_default=None,
    )


def downgrade() -> None:
    op.drop_column("approvals", "escalation_reason")
    op.drop_column("approvals", "escalated_at")
    op.drop_column("approvals", "escalated")
    op.drop_column("approvals", "due_at")