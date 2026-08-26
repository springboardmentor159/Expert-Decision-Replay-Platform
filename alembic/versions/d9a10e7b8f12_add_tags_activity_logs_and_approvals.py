"""add tags decision_tags activity_logs and approvals tables

Revision ID: d9a10e7b8f12
Revises: c85c9a9cd851
Create Date: 2026-08-26 20:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd9a10e7b8f12'
down_revision: Union[str, None] = 'c85c9a9cd851'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Tags Table
    op.create_table(
        'tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tags_id'), 'tags', ['id'], unique=False)
    op.create_index(op.f('ix_tags_name'), 'tags', ['name'], unique=True)

    # 2. Decision Tags Association Table
    op.create_table(
        'decision_tags',
        sa.Column('decision_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['decision_id'], ['decisions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('decision_id', 'tag_id')
    )

    # 3. Activity Logs Table
    op.create_table(
        'activity_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('entity_type', sa.String(), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_activity_logs_id'), 'activity_logs', ['id'], unique=False)
    op.create_index(op.f('ix_activity_logs_user_id'), 'activity_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_activity_logs_action'), 'activity_logs', ['action'], unique=False)
    op.create_index(op.f('ix_activity_logs_entity_type'), 'activity_logs', ['entity_type'], unique=False)
    op.create_index(op.f('ix_activity_logs_entity_id'), 'activity_logs', ['entity_id'], unique=False)
    op.create_index(op.f('ix_activity_logs_created_at'), 'activity_logs', ['created_at'], unique=False)

    # 4. Approvals Table
    op.create_table(
        'approvals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('decision_id', sa.Integer(), nullable=False),
        sa.Column('reviewer_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('approval_level', sa.Integer(), nullable=False),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['decision_id'], ['decisions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reviewer_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_approvals_id'), 'approvals', ['id'], unique=False)
    op.create_index(op.f('ix_approvals_decision_id'), 'approvals', ['decision_id'], unique=False)
    op.create_index(op.f('ix_approvals_reviewer_id'), 'approvals', ['reviewer_id'], unique=False)
    op.create_index(op.f('ix_approvals_status'), 'approvals', ['status'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_approvals_status'), table_name='approvals')
    op.drop_index(op.f('ix_approvals_reviewer_id'), table_name='approvals')
    op.drop_index(op.f('ix_approvals_decision_id'), table_name='approvals')
    op.drop_index(op.f('ix_approvals_id'), table_name='approvals')
    op.drop_table('approvals')

    op.drop_index(op.f('ix_activity_logs_created_at'), table_name='activity_logs')
    op.drop_index(op.f('ix_activity_logs_entity_id'), table_name='activity_logs')
    op.drop_index(op.f('ix_activity_logs_entity_type'), table_name='activity_logs')
    op.drop_index(op.f('ix_activity_logs_action'), table_name='activity_logs')
    op.drop_index(op.f('ix_activity_logs_user_id'), table_name='activity_logs')
    op.drop_index(op.f('ix_activity_logs_id'), table_name='activity_logs')
    op.drop_table('activity_logs')

    op.drop_table('decision_tags')

    op.drop_index(op.f('ix_tags_name'), table_name='tags')
    op.drop_index(op.f('ix_tags_id'), table_name='tags')
    op.drop_table('tags')
