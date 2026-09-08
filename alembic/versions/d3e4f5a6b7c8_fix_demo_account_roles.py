"""fix demo account roles

Revision ID: d3e4f5a6b7c8
Revises: c2d3e4f5a6b7
"""
from typing import Sequence, Union

from alembic import op


revision: str = "d3e4f5a6b7c8"
down_revision: Union[str, Sequence[str], None] = "c2d3e4f5a6b7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE users SET role = 'Employee' WHERE email = 'employee@example.com'")
    op.execute("UPDATE users SET role = 'Reviewer' WHERE email = 'reviewer@example.com'")
    op.execute("UPDATE users SET role = 'Manager' WHERE email = 'manager@example.com'")
    op.execute("UPDATE users SET role = 'Administrator' WHERE email = 'admin@example.com'")


def downgrade() -> None:
    op.execute("UPDATE users SET role = 'Employee' WHERE email IN ('employee@example.com', 'reviewer@example.com', 'manager@example.com', 'admin@example.com')")
