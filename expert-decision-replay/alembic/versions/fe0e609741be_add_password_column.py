"""add password column

Revision ID: fe0e609741be
Revises: c66c34b36787
Create Date: 2026-08-09 16:05:41.400793

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "fe0e609741be"
down_revision: Union[str, Sequence[str], None] = "c66c34b36787"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("password", sa.String(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("users", "password")