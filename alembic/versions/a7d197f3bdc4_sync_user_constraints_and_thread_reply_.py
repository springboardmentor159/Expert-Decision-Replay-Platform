"""sync user constraints and thread reply index

Revision ID: a7d197f3bdc4
Revises: 42ded34baf74
Create Date: 2026-09-01 17:51:29.878529

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a7d197f3bdc4"
down_revision: Union[str, Sequence[str], None] = "42ded34baf74"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Synchronize existing user constraints and thread reply index."""

    # Populate missing employee IDs.
    # EMP003 is already used by user ID 26, so start
    # generated values from a separate range.

    op.execute(
        """
        UPDATE users
        SET employee_id = 'TEMP' || LPAD(id::text, 3, '0')
        WHERE employee_id IS NULL
        """
    )

    # Populate other required profile fields.

    op.execute(
        """
        UPDATE users
        SET department = 'General'
        WHERE department IS NULL
        """
    )

    op.execute(
        """
        UPDATE users
        SET designation = 'Employee'
        WHERE designation IS NULL
        """
    )

    op.execute(
        """
        UPDATE users
        SET phone_number = 'Not Provided'
        WHERE phone_number IS NULL
        """
    )

    # Enforce NOT NULL constraints.

    op.alter_column(
        "users",
        "employee_id",
        existing_type=sa.VARCHAR(),
        nullable=False
    )

    op.alter_column(
        "users",
        "department",
        existing_type=sa.VARCHAR(),
        nullable=False
    )

    op.alter_column(
        "users",
        "designation",
        existing_type=sa.VARCHAR(),
        nullable=False
    )

    op.alter_column(
        "users",
        "phone_number",
        existing_type=sa.VARCHAR(),
        nullable=False
    )

    # Enforce unique employee IDs.

    op.create_unique_constraint(
        "uq_users_employee_id",
        "users",
        ["employee_id"]
    )

    # Add index declared by ThreadReply model.

    op.create_index(
        "ix_thread_replies_id",
        "thread_replies",
        ["id"],
        unique=False
    )


def downgrade() -> None:
    """Revert user constraints and thread reply index."""

    op.drop_index(
        "ix_thread_replies_id",
        table_name="thread_replies"
    )

    op.drop_constraint(
        "uq_users_employee_id",
        "users",
        type_="unique"
    )

    op.alter_column(
        "users",
        "phone_number",
        existing_type=sa.VARCHAR(),
        nullable=True
    )

    op.alter_column(
        "users",
        "designation",
        existing_type=sa.VARCHAR(),
        nullable=True
    )

    op.alter_column(
        "users",
        "department",
        existing_type=sa.VARCHAR(),
        nullable=True
    )

    op.alter_column(
        "users",
        "employee_id",
        existing_type=sa.VARCHAR(),
        nullable=True
    )