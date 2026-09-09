"""add unique constraint to decision versions

Revision ID: 19b38961d3b1
Revises: cea171d6caa4
"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "19b38961d3b1"
down_revision = "cea171d6caa4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_decision_version_number",
        "decision_versions",
        ["decision_id", "version_number"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_decision_version_number",
        "decision_versions",
        type_="unique",
    )