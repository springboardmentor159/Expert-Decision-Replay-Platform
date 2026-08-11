"""add user profile fields

Revision ID: ca7359da1593
Revises: 52b2d69037d3
Create Date: 2026-08-11 13:01:27.070465

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ca7359da1593"
down_revision: Union[str, Sequence[str], None] = "52b2d69037d3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "users",
        sa.Column("employee_id", sa.String(), nullable=True),
    )

    op.add_column(
        "users",
        sa.Column("department", sa.String(), nullable=True),
    )

    op.add_column(
        "users",
        sa.Column("designation", sa.String(), nullable=True),
    )

    op.add_column(
        "users",
        sa.Column("phone_number", sa.String(), nullable=True),
    )

    op.create_unique_constraint(
        "uq_users_employee_id",
        "users",
        ["employee_id"],
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "uq_users_employee_id",
        "users",
        type_="unique",
    )

    op.drop_column("users", "phone_number")
    op.drop_column("users", "designation")
    op.drop_column("users", "department")
    op.drop_column("users", "employee_id")