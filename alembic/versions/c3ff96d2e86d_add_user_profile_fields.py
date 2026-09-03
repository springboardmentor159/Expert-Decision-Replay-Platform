"""add user profile fields

Revision ID: c3ff96d2e86d
Revises: d21df3dfb7b6
Create Date: 2026-08-10 20:27:48.330701

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3ff96d2e86d'
down_revision: Union[str, Sequence[str], None] = 'd21df3dfb7b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("employee_id", sa.String(), nullable=True)
    )
    op.add_column(
        "users",
        sa.Column("department", sa.String(), nullable=True)
    )
    op.add_column(
        "users",
        sa.Column("designation", sa.String(), nullable=True)
    )
    op.add_column(
        "users",
        sa.Column("phone_number", sa.String(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("users", "phone_number")
    op.drop_column("users", "designation")
    op.drop_column("users", "department")
    op.drop_column("users", "employee_id")