"""add_alternative_validation_constraints

Revision ID: 4869b7a3e2a0
Revises: 56c656d0956d
Create Date: 2026-08-18 20:45:21.371703

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4869b7a3e2a0'
down_revision: Union[str, Sequence[str], None] = '56c656d0956d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_check_constraint(
        'check_valid_feasibility_score',
        'alternatives',
        sa.column('feasibility_score').between(1, 5)
    )
    op.create_check_constraint(
        'check_valid_risk_level',
        'alternatives',
        sa.column('risk_level').in_(['Low', 'Medium', 'High', 'Critical'])
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('check_valid_risk_level', 'alternatives', type_='check')
    op.drop_constraint('check_valid_feasibility_score', 'alternatives', type_='check')
