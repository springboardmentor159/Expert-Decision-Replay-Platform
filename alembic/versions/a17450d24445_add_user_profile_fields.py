"""add user profile fields

Revision ID: a17450d24445
Revises: 4f8e9d5cf10e
Create Date: 2026-08-10 20:14:59.585507

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a17450d24445"
down_revision: Union[str, Sequence[str], None] = "4f8e9d5cf10e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Add columns temporarily as nullable
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

    # Give existing users temporary values
    op.execute(
        sa.text(
            "UPDATE users "
            "SET employee_id = 'EMP-' || id, "
            "department = 'General', "
            "designation = 'Employee', "
            "phone_number = '0000000000' "
            "WHERE employee_id IS NULL"
        )
    )

    # Make the columns required
    op.alter_column("users", "employee_id", nullable=False)
    op.alter_column("users", "department", nullable=False)
    op.alter_column("users", "designation", nullable=False)
    op.alter_column("users", "phone_number", nullable=False)

    # Employee ID must be unique
    op.create_unique_constraint(
        "uq_users_employee_id",
        "users",
        ["employee_id"]
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "uq_users_employee_id",
        "users",
        type_="unique"
    )

    op.drop_column("users", "phone_number")
    op.drop_column("users", "designation")
    op.drop_column("users", "department")
    op.drop_column("users", "employee_id")