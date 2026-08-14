"""add user profile fields

Revision ID: 7ed9a8fbb2c3
Revises: e5deb0bffa19
Create Date: 2026-08-11 21:14:08.575376

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7ed9a8fbb2c3"
down_revision: Union[str, Sequence[str], None] = "e5deb0bffa19"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add the new columns temporarily as nullable
    op.add_column(
        "users",
        sa.Column("employee_id", sa.String(length=50), nullable=True),
    )

    op.add_column(
        "users",
        sa.Column("department", sa.String(length=100), nullable=True),
    )

    op.add_column(
        "users",
        sa.Column("designation", sa.String(length=100), nullable=True),
    )

    op.add_column(
        "users",
        sa.Column("phone_number", sa.String(length=20), nullable=True),
    )

    # 2. Give existing users safe default values
    op.execute(
        """
        UPDATE users
        SET
            employee_id = 'EMP-' || id,
            department = 'General',
            designation = 'Employee',
            phone_number = 'Not Provided'
        WHERE employee_id IS NULL
        """
    )

    # 3. Make the columns required
    op.alter_column(
        "users",
        "employee_id",
        existing_type=sa.String(length=50),
        nullable=False,
    )

    op.alter_column(
        "users",
        "department",
        existing_type=sa.String(length=100),
        nullable=False,
    )

    op.alter_column(
        "users",
        "designation",
        existing_type=sa.String(length=100),
        nullable=False,
    )

    op.alter_column(
        "users",
        "phone_number",
        existing_type=sa.String(length=20),
        nullable=False,
    )

    # 4. Employee ID must be unique
    op.create_unique_constraint(
        "uq_users_employee_id",
        "users",
        ["employee_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_users_employee_id",
        "users",
        type_="unique",
    )

    op.drop_column("users", "phone_number")
    op.drop_column("users", "designation")
    op.drop_column("users", "department")
    op.drop_column("users", "employee_id")