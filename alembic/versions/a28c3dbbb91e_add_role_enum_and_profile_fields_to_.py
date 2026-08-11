"""add role enum and profile fields to users

Revision ID: a28c3dbbb91e
Revises: 9e09f049017e
Create Date: 2026-08-11 19:02:11.098250

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a28c3dbbb91e"
down_revision: Union[str, Sequence[str], None] = "9e09f049017e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Create the PostgreSQL enum type first
    userrole_enum = sa.Enum(
        "EMPLOYEE",
        "REVIEWER",
        "MANAGER",
        "ADMINISTRATOR",
        name="userrole",
    )
    userrole_enum.create(op.get_bind(), checkfirst=True)

    # Add new profile fields
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

    # Convert role column from VARCHAR to PostgreSQL enum
    op.alter_column(
        "users",
        "role",
        existing_type=sa.VARCHAR(),
        type_=userrole_enum,
        existing_nullable=False,
        postgresql_using="role::userrole",
    )

    # Employee ID must be unique
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

    # Convert enum back to VARCHAR
    op.alter_column(
        "users",
        "role",
        existing_type=sa.Enum(
            "EMPLOYEE",
            "REVIEWER",
            "MANAGER",
            "ADMINISTRATOR",
            name="userrole",
        ),
        type_=sa.VARCHAR(),
        existing_nullable=False,
        postgresql_using="role::text",
    )

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
        name="userrole",
    ).drop(op.get_bind(), checkfirst=True)