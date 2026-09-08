"""allow document audit entities

Revision ID: c2d3e4f5a6b7
Revises: b1c2d3e4f5a6
"""
from typing import Sequence, Union

from alembic import op


revision: str = "c2d3e4f5a6b7"
down_revision: Union[str, Sequence[str], None] = "b1c2d3e4f5a6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("check_valid_audit_entity_type", "audit_log", type_="check")
    op.create_check_constraint(
        "check_valid_audit_entity_type",
        "audit_log",
        "entity_type IN ('decision','alternative','comment','discussion_thread','meeting_note','document','user','auth','system')",
    )


def downgrade() -> None:
    op.drop_constraint("check_valid_audit_entity_type", "audit_log", type_="check")
    op.create_check_constraint(
        "check_valid_audit_entity_type",
        "audit_log",
        "entity_type IN ('decision','alternative','comment','discussion_thread','meeting_note','user','auth','system')",
    )