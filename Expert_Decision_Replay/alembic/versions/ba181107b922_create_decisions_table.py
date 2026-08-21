"""baseline existing database

Revision ID: ba181107b922
Revises:
Create Date: 2026-08-21
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "ba181107b922"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Baseline existing database."""
    pass


def downgrade() -> None:
    """Baseline existing database."""
    pass