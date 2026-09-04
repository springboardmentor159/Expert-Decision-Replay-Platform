"""create users table

Revision ID: 9f73a03d878f
Revises:
Create Date: 2026-07-31 20:34:39.990304
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.

revision: str = "9f73a03d878f"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            "full_name",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "email",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "role",
            sa.String(),
            nullable=False
        ),
        sa.Column(
            "password",
            sa.String(),
            nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    op.create_index(
        op.f("ix_users_id"),
        "users",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_users_id"),
        table_name="users"
    )

    op.drop_table("users")
