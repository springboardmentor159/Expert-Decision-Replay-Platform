"""Add user profile fields

Revision ID: 35d36a5d70f6
Revises: fe0e609741be
Create Date: 2026-08-10 21:33:26.229314

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "35d36a5d70f6"
down_revision: Union[str, Sequence[str], None] = "fe0e609741be"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new profile columns as nullable first
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

    # Give existing users profile values
    op.execute(
        """
        UPDATE users
        SET employee_id = 'EMP003',
            department = 'IT',
            designation = 'Employee',
            phone_number = 'Not Provided'
        WHERE id = 3
        """
    )

    op.execute(
        """
        UPDATE users
        SET employee_id = 'EMP004',
            department = 'IT',
            designation = 'Employee',
            phone_number = 'Not Provided'
        WHERE id = 4
        """
    )

    op.execute(
        """
        UPDATE users
        SET employee_id = 'EMP005',
            department = 'IT',
            designation = 'Employee',
            phone_number = 'Not Provided'
        WHERE id = 5
        """
    )

    op.execute(
        """
        UPDATE users
        SET employee_id = 'EMP006',
            department = 'IT',
            designation = 'Employee',
            phone_number = 'Not Provided'
        WHERE id = 6
        """
    )

    # Make profile fields required
    op.alter_column(
        "users",
        "employee_id",
        existing_type=sa.String(),
        nullable=False,
    )

    op.alter_column(
        "users",
        "department",
        existing_type=sa.String(),
        nullable=False,
    )

    op.alter_column(
        "users",
        "designation",
        existing_type=sa.String(),
        nullable=False,
    )

    op.alter_column(
        "users",
        "phone_number",
        existing_type=sa.String(),
        nullable=False,
    )

    # Make employee_id unique
    op.create_unique_constraint(
        "uq_users_employee_id",
        "users",
        ["employee_id"],
    )

    # Password must not be NULL
    op.alter_column(
        "users",
        "password",
        existing_type=sa.VARCHAR(),
        nullable=False,
    )


def downgrade() -> None:
    # Remove employee_id unique constraint
    op.drop_constraint(
        "uq_users_employee_id",
        "users",
        type_="unique",
    )

    # Make password nullable again
    op.alter_column(
        "users",
        "password",
        existing_type=sa.VARCHAR(),
        nullable=True,
    )

    # Remove profile fields
    op.drop_column("users", "phone_number")
    op.drop_column("users", "designation")
    op.drop_column("users", "department")
    op.drop_column("users", "employee_id")