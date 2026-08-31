"""create_activity_log_table

Revision ID: c77b74289e7d
Revises: 6a0d2fb180b3
Create Date: 2026-08-27 20:12:55.114809

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c77b74289e7d'
down_revision: Union[str, Sequence[str], None] = '6a0d2fb180b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'activity_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('entity_type', sa.String(), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_activity_log_id', 'activity_log', ['id'])
    op.create_index('ix_activity_log_user_id', 'activity_log', ['user_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_activity_log_user_id', table_name='activity_log')
    op.drop_index('ix_activity_log_id', table_name='activity_log')
    op.drop_table('activity_log')
