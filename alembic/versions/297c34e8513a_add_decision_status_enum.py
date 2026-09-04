"""add decision status enum

Revision ID: 297c34e8513a
Revises: 39bcc6216b66
Create Date: 2026-08-17 19:30:29.914034

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "297c34e8513a"
down_revision: Union[str, Sequence[str], None] = "39bcc6216b66"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Create the PostgreSQL enum type.
    decision_status = sa.Enum(
        "Draft",
        "Under Review",
        "Approved",
        "Rejected",
        "Archived",
        name="decision_status"
    )

    decision_status.create(op.get_bind(), checkfirst=True)

    # Convert the existing status column from VARCHAR to the enum.
    op.alter_column(
        "decisions",
        "status",
        existing_type=sa.String(),
        type_=decision_status,
        existing_nullable=False,
        postgresql_using="status::decision_status"
    )


def downgrade() -> None:
    """Downgrade schema."""

    # Convert the enum back to VARCHAR.
    op.alter_column(
        "decisions",
        "status",
        existing_type=sa.Enum(
            "Draft",
            "Under Review",
            "Approved",
            "Rejected",
            "Archived",
            name="decision_status"
        ),
        type_=sa.String(),
        existing_nullable=False,
        postgresql_using="status::text"
    )

    # Remove the PostgreSQL enum type.
    decision_status = sa.Enum(
        "Draft",
        "Under Review",
        "Approved",
        "Rejected",
        "Archived",
        name="decision_status"
    )

    decision_status.drop(op.get_bind(), checkfirst=True)
