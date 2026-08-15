"""add decision status enum

Revision ID: c73276f3932b
Revises: 86cc5829e2b3
Create Date: 2026-08-15 22:14:11.693529

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c73276f3932b'
down_revision: Union[str, Sequence[str], None] = '86cc5829e2b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    decision_status = sa.Enum(
        'Draft',
        'Under Review',
        'Approved',
        'Rejected',
        'Archived',
        name='decision_status'
    )

    decision_status.create(op.get_bind(), checkfirst=True)

    op.execute(
        """
        ALTER TABLE decisions
        ALTER COLUMN status
        TYPE decision_status
        USING status::text::decision_status
        """
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE decisions
        ALTER COLUMN status
        TYPE VARCHAR
        USING status::text
        """
    )

    decision_status = sa.Enum(
        'Draft',
        'Under Review',
        'Approved',
        'Rejected',
        'Archived',
        name='decision_status'
    )

    decision_status.drop(op.get_bind(), checkfirst=True)
    # ### end Alembic commands ###
