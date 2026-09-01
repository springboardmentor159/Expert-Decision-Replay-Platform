"""merge migration heads

Revision ID: 639444e1665c
Revises: 4e1c0b50b762, 51d961854aeb, c66c34b36787, e8ce975c8d11
Create Date: 2026-09-01 18:27:14.379484

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '639444e1665c'
down_revision: Union[str, Sequence[str], None] = ('4e1c0b50b762', '51d961854aeb', 'c66c34b36787', 'e8ce975c8d11')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
