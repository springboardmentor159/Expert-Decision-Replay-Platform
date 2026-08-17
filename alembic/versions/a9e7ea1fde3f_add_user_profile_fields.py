from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a9e7ea1fde3f"
down_revision: Union[str, Sequence[str], None] = "1ba3e2a6509e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Add Employee ID
    op.add_column(
        "users",
        sa.Column(
            "employee_id",
            sa.String(),
            nullable=True
        )
    )

    # Add Department
    op.add_column(
        "users",
        sa.Column(
            "department",
            sa.String(),
            nullable=True
        )
    )

    # Add Designation
    op.add_column(
        "users",
        sa.Column(
            "designation",
            sa.String(),
            nullable=True
        )
    )

    # Add Phone Number
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


def downgrade() -> None:
    """Downgrade schema."""

    # Remove Employee ID unique constraint
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