"""create alternatives table

Revision ID: 89a5a22f4820
Revises: b3998a6e3d85
Create Date: 2026-08-19 19:29:33.331953

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '89a5a22f4820'
down_revision: Union[str, Sequence[str], None] = 'b3998a6e3d85'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'alternatives',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('decision_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('pros', sa.String(), nullable=False),
        sa.Column('cons', sa.String(), nullable=False),
        sa.Column('estimated_cost', sa.Integer(), nullable=False),
        sa.Column('feasibility_score', sa.Integer(), nullable=False),
        sa.Column('risk_level', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ['decision_id'],
            ['decisions.id']
        ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index(
        op.f('ix_alternatives_id'),
        'alternatives',
        ['id'],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f('ix_alternatives_id'),
        table_name='alternatives'
    )
    op.drop_table('alternatives')