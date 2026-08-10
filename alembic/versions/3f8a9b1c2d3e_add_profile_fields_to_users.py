"""add_profile_fields_to_users

Revision ID: 3f8a9b1c2d3e
Revises: 2e79a8249243
Create Date: 2026-08-10 16:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3f8a9b1c2d3e'
down_revision: Union[str, None] = '2e79a8249243'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('employee_id', sa.String(), nullable=True))
    op.add_column('users', sa.Column('department', sa.String(), nullable=True))
    op.add_column('users', sa.Column('designation', sa.String(), nullable=True))
    op.add_column('users', sa.Column('phone_number', sa.String(), nullable=True))
    op.create_index(op.f('ix_users_employee_id'), 'users', ['employee_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_users_employee_id'), table_name='users')
    op.drop_column('users', 'phone_number')
    op.drop_column('users', 'designation')
    op.drop_column('users', 'department')
    op.drop_column('users', 'employee_id')
