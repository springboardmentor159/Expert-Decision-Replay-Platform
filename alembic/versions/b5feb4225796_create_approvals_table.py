"""create approvals table

Revision ID: b5feb4225796
Revises: 03c51590d7a5
Create Date: 2026-09-04 12:52:58.434970

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b5feb4225796"
down_revision: Union[str, Sequence[str], None] = "03c51590d7a5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create approvals table."""

    approval_status = sa.Enum(
        "PENDING",
        "APPROVED",
        "REJECTED",
        name="approvalstatus",
        create_type=False
    )

    op.create_table(
        "approvals",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "decision_id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "reviewer_id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "status",
            approval_status,
            nullable=False
        ),

        sa.Column(
            "approval_level",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False
        ),

        sa.ForeignKeyConstraint(
            ["decision_id"],
            ["decisions.id"]
        ),

        sa.ForeignKeyConstraint(
            ["reviewer_id"],
            ["users.id"]
        ),

        sa.PrimaryKeyConstraint("id")
    )

    op.create_index(
        op.f("ix_approvals_id"),
        "approvals",
        ["id"],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass