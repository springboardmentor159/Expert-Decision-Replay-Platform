"""add hashed password column

Revision ID: e7e9b0bfd9ed
Revises:
Create Date: 2026-08-06
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e7e9b0bfd9ed"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # The hashed_password column already exists in the current database.
    # This migration is restored only to repair the Alembic history.
    pass


def downgrade() -> None:
    # Do not remove the existing column from the current database.
    pass