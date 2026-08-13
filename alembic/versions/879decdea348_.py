"""empty message

Revision ID: 879decdea348
Revises: ca7359da1593
Create Date: 2026-08-13 18:29:02.584338

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "879decdea348"
down_revision: Union[str, Sequence[str], None] = "ca7359da1593"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass