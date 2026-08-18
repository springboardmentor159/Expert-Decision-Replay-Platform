"""add archived status to decision enum

Revision ID: 4236dadc121d
Revises: c175cdd6608e
Create Date: 2026-08-18 14:21:38.866822

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4236dadc121d'
down_revision: Union[str, Sequence[str], None] = 'c175cdd6608e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE decisionstatus ADD VALUE IF NOT EXISTS 'ARCHIVED'")


def downgrade() -> None:
    """Downgrade schema."""
    # Postgres does not support removing enum values directly.
    # A downgrade would require recreating the enum type without 'ARCHIVED'.
    pass