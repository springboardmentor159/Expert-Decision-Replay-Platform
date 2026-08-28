"""create approvals table"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b27811ffd910"
down_revision: Union[str, Sequence[str], None] = "3f54708142fa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "approvals",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            nullable=False
        ),
        sa.Column(
            "decision_id",
            sa.Integer(),
            sa.ForeignKey("decisions.id"),
            nullable=False
        ),
        sa.Column(
            "reviewer_id",
            sa.Integer(),
            sa.ForeignKey("users.id"),
            nullable=False
        ),
        sa.Column(
            "approval_level",
            sa.Integer(),
            nullable=False,
            server_default="1"
        ),
        sa.Column(
            "status",
            sa.String(),
            nullable=False,
            server_default="Pending"
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now()
        ),
        sa.Column(
            "completed_at",
            sa.DateTime(),
            nullable=True
        ),
    )

    op.create_index(
        "ix_approvals_id",
        "approvals",
        ["id"]
    )


def downgrade() -> None:
    op.drop_index(
        "ix_approvals_id",
        table_name="approvals"
    )

    op.drop_table("approvals")