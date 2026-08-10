"""add user profile fields and role

Revision ID: c1380e0fa61e
Revises: adf18151215c
Create Date: 2026-08-10 16:44:46.045750

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c1380e0fa61e"
down_revision: Union[str, Sequence[str], None] = "adf18151215c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Add new user profile fields
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

    # Create PostgreSQL enum type
    user_role_enum = sa.Enum(
        "EMPLOYEE",
        "REVIEWER",
        "MANAGER",
        "ADMINISTRATOR",
        name="user_role"
    )

    user_role_enum.create(op.get_bind(), checkfirst=True)

    # Convert existing roles to valid roles.
    # Old/invalid roles are mapped to EMPLOYEE.
    op.execute(
        """
        UPDATE users
        SET role = CASE
            WHEN LOWER(role) = 'manager' THEN 'MANAGER'
            WHEN LOWER(role) = 'reviewer' THEN 'REVIEWER'
            WHEN LOWER(role) = 'administrator' THEN 'ADMINISTRATOR'
            WHEN LOWER(role) = 'employee' THEN 'EMPLOYEE'
            ELSE 'EMPLOYEE'
        END
        """
    )

    # Change role column from VARCHAR to PostgreSQL ENUM
    op.execute(
        """
        ALTER TABLE users
        ALTER COLUMN role TYPE user_role
        USING role::user_role
        """
    )

    # Employee ID should be unique
    op.create_unique_constraint(
        "uq_users_employee_id",
        "users",
        ["employee_id"]
    )


def downgrade() -> None:
    """Downgrade schema."""

    # Convert enum back to VARCHAR
    op.execute(
        """
        ALTER TABLE users
        ALTER COLUMN role TYPE VARCHAR
        USING role::text
        """
    )

    # Remove unique constraint
    op.drop_constraint(
        "uq_users_employee_id",
        "users",
        type_="unique"
    )

    # Remove new profile fields
    op.drop_column("users", "phone_number")
    op.drop_column("users", "designation")
    op.drop_column("users", "department")
    op.drop_column("users", "employee_id")

    # Remove PostgreSQL enum
    sa.Enum(
        "EMPLOYEE",
        "REVIEWER",
        "MANAGER",
        "ADMINISTRATOR",
        name="user_role"
    ).drop(op.get_bind(), checkfirst=True)