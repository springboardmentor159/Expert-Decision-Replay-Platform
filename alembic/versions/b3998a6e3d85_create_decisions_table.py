"""create decisions table

Revision ID: b3998a6e3d85
Revises: c3ff96d2e86d
Create Date: 2026-08-13 18:18:18.902671

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3998a6e3d85'
down_revision: Union[str, Sequence[str], None] = 'c3ff96d2e86d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'decisions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('problem_statement', sa.String(), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index(
        op.f('ix_decisions_id'),
        'decisions',
        ['id'],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f('ix_decisions_id'),
        table_name='decisions'
    )

    op.drop_table('decisions')