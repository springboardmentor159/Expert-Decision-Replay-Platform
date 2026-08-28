"""add approvals table

Revision ID: 56cc816c1296
Revises: a937f5b3e69e
Create Date: 2026-08-27 13:34:33.103538

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "56cc816c1296"
down_revision: Union[str, Sequence[str], None] = "a937f5b3e69e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # The enum may already exist from a previous failed migration attempt.
    approval_status = postgresql.ENUM(
        "Pending",
        "Approved",
        "Rejected",
        name="approval_status",
        create_type=False,
    )

    # Create the enum only if it does not already exist.
    bind = op.get_bind()

    enum_exists = bind.execute(
        sa.text(
            """
            SELECT EXISTS (
                SELECT 1
                FROM pg_type
                WHERE typname = 'approval_status'
            )
            """
        )
    ).scalar()

    if not enum_exists:
        approval_status.create(bind)

    op.create_table(
        "approvals",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "decision_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "reviewer_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "status",
            approval_status,
            nullable=False,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),

        sa.Column(
            "completed_at",
            sa.DateTime(),
            nullable=True,
        ),

        sa.ForeignKeyConstraint(
            ["decision_id"],
            ["decisions.id"],
        ),

        sa.ForeignKeyConstraint(
            ["reviewer_id"],
            ["users.id"],
        ),

        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_approvals_id"),
        "approvals",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_approvals_id"),
        table_name="approvals",
    )

    op.drop_table("approvals")

    approval_status = postgresql.ENUM(
        "Pending",
        "Approved",
        "Rejected",
        name="approval_status",
        create_type=False,
    )

    approval_status.drop(
        op.get_bind(),
        checkfirst=True,
    )