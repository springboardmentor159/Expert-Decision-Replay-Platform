"""create decision documents table

Revision ID: f7a1c9d2e4b6
Revises: d4e8f1a2b3c4
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f7a1c9d2e4b6"
down_revision: Union[str, Sequence[str], None] = "d4e8f1a2b3c4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "decision_documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("decision_id", sa.Integer(), nullable=False),
        sa.Column("uploaded_by", sa.Integer(), nullable=False),
        sa.Column("original_filename", sa.String(), nullable=False),
        sa.Column("stored_filename", sa.String(), nullable=False),
        sa.Column("content_type", sa.String(), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["decision_id"], ["decisions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"]),
        sa.UniqueConstraint("stored_filename"),
    )
    for column in ("decision_id", "uploaded_by", "created_at"):
        op.create_index(f"ix_decision_documents_{column}", "decision_documents", [column])
    op.create_index("ix_decision_documents_id", "decision_documents", ["id"])


def downgrade() -> None:
    op.drop_table("decision_documents")
