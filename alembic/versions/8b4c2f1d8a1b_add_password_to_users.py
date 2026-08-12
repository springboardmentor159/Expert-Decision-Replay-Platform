"""add password to users

Revision ID: 8b4c2f1d8a1b
Revises: dc80369e9b6e
Create Date: 2026-08-06 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '8b4c2f1d8a1b'
down_revision: Union[str, Sequence[str], None] = 'c66c34b36787'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('password', sa.String(), nullable=False, server_default=''))


def downgrade() -> None:
    op.drop_column('users', 'password')
