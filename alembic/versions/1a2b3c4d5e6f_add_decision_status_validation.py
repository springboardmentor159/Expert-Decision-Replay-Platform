"""add_decision_status_validation

Revision ID: 1a2b3c4d5e6f
Revises: 2c3d8c3e66fc
Create Date: 2026-08-17 21:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1a2b3c4d5e6f'
down_revision: Union[str, Sequence[str], None] = '2c3d8c3e66fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_check_constraint(
        'check_valid_status',
        'decisions',
        sa.column('status').in_(['Draft', 'Under Review', 'Approved', 'Rejected', 'Archived'])
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('check_valid_status', 'decisions', type_='check')
