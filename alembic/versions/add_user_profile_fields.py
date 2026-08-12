"""add user profile fields

Revision ID: add_user_profile_fields
Revises: 8b4c2f1d8a1b
Create Date: 2026-08-12 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'add_user_profile_fields'
down_revision: Union[str, Sequence[str], None] = '8b4c2f1d8a1b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('employee_id', sa.String(), nullable=False, server_default=''))
    op.add_column('users', sa.Column('department', sa.String(), nullable=False, server_default=''))
    op.add_column('users', sa.Column('designation', sa.String(), nullable=False, server_default=''))
    op.add_column('users', sa.Column('phone_number', sa.String(), nullable=False, server_default=''))


def downgrade() -> None:
    op.drop_column('users', 'phone_number')
    op.drop_column('users', 'designation')
    op.drop_column('users', 'department')
    op.drop_column('users', 'employee_id')
