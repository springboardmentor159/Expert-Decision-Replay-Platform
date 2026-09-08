"""create documents table

Revision ID: b1c2d3e4f5a6
Revises: 6492a6c5b989
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b1c2d3e4f5a6"
down_revision: Union[str, Sequence[str], None] = "6492a6c5b989"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("decision_id", sa.Integer(), nullable=False),
        sa.Column("uploaded_by", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("storage_name", sa.String(), nullable=False),
        sa.Column("content_type", sa.String(), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["decision_id"], ["decisions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"]),
        sa.UniqueConstraint("storage_name"),
    )
    op.create_index("ix_documents_decision_id", "documents", ["decision_id"])
    op.create_index("ix_documents_uploaded_by", "documents", ["uploaded_by"])


def downgrade() -> None:
    op.drop_index("ix_documents_uploaded_by", table_name="documents")
    op.drop_index("ix_documents_decision_id", table_name="documents")
    op.drop_table("documents")
