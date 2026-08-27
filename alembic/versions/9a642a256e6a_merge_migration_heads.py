"""merge migration heads

Revision ID: 9a642a256e6a
Revises: 1f0cc071a002, a18a01a008d6
Create Date: 2026-08-26 22:05:45.761447

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9a642a256e6a'
down_revision: Union[str, Sequence[str], None] = ('1f0cc071a002', 'a18a01a008d6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
