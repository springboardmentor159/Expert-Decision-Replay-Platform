"""add user password and profile fields

Revision ID: 20260811_add_user_password_and_profile
Revises: 053760f12e9a
Create Date: 2026-08-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260811_add_user_password_and_profile'
down_revision: Union[str, Sequence[str], None] = '053760f12e9a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # add new nullable columns so existing data isn't invalidated
    op.add_column('users', sa.Column('password', sa.String(), nullable=True))
    op.add_column('users', sa.Column('employee_id', sa.String(), nullable=True))
    op.add_column('users', sa.Column('department', sa.String(), nullable=True))
    op.add_column('users', sa.Column('designation', sa.String(), nullable=True))
    op.add_column('users', sa.Column('phone_number', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'phone_number')
    op.drop_column('users', 'designation')
    op.drop_column('users', 'department')
    op.drop_column('users', 'employee_id')
    op.drop_column('users', 'password')
