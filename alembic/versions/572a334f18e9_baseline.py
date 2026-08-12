"""baseline

Revision ID: 572a334f18e9
Revises:
Create Date: 2026-08-11

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '572a334f18e9'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
