"""add user profile fields and role enum

Revision ID: 2a3f6c8d4e11
Revises: 9f73a03d878f
Create Date: 2026-08-11
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.

revision: str = "2a3f6c8d4e11"
down_revision: Union[str, Sequence[str], None] = "9f73a03d878f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # Create PostgreSQL enum for user roles
    user_role_enum = sa.Enum(
        "Employee",
        "Reviewer",
        "Manager",
        "Administrator",
        name="user_role",
    )

    user_role_enum.create(
        op.get_bind(),
        checkfirst=True
    )

    # Add employee ID
    op.add_column(
        "users",
        sa.Column(
            "employee_id",
            sa.String(),
            nullable=True
        )
    )

    # Add department
    op.add_column(
        "users",
        sa.Column(
            "department",
            sa.String(),
            nullable=True
        )
    )

    # Add designation
    op.add_column(
        "users",
        sa.Column(
            "designation",
            sa.String(),
            nullable=True
        )
    )

    # Add phone number
    op.add_column(
        "users",
        sa.Column(
            "phone_number",
            sa.String(),
            nullable=True
        )
    )

    # Employee ID must be unique
    op.create_unique_constraint(
        "uq_users_employee_id",
        "users",
        ["employee_id"]
    )

    # Convert role from VARCHAR to PostgreSQL enum
    op.execute(
        """
        ALTER TABLE users
        ALTER COLUMN role TYPE user_role
        USING role::user_role
        """
    )


def downgrade() -> None:

    # Convert role back to VARCHAR
    op.execute(
        """
        ALTER TABLE users
        ALTER COLUMN role TYPE VARCHAR
        USING role::text
        """
    )

    # Remove employee ID unique constraint
    op.drop_constraint(
        "uq_users_employee_id",
        "users",
        type_="unique"
    )

    # Remove profile fields
    op.drop_column(
        "users",
        "phone_number"
    )

    op.drop_column(
        "users",
        "designation"
    )

    op.drop_column(
        "users",
        "department"
    )

    op.drop_column(
        "users",
        "employee_id"
    )

    # Remove PostgreSQL enum
    user_role_enum = sa.Enum(
        "Employee",
        "Reviewer",
        "Manager",
        "Administrator",
        name="user_role",
    )

    user_role_enum.drop(
        op.get_bind(),
        checkfirst=True
    )
