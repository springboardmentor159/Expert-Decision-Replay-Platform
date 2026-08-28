"""add audit compliance logs

Revision ID: d4e8f1a2b3c4
Revises: c81d4e6f2a10
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "d4e8f1a2b3c4"
down_revision: Union[str, Sequence[str], None] = "c81d4e6f2a10"
branch_labels = None
depends_on = None


def _common(table):
    op.create_index(f"ix_{table}_id", table, ["id"])
    op.create_index(f"ix_{table}_user_id", table, ["user_id"])
    op.create_index(f"ix_{table}_created_at", table, ["created_at"])


def upgrade() -> None:
    op.create_table("audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(), nullable=False), sa.Column("entity_type", sa.String(), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=True), sa.Column("description", sa.Text(), nullable=False),
        sa.Column("old_value", sa.JSON(), nullable=True), sa.Column("new_value", sa.JSON(), nullable=True),
        sa.Column("request_method", sa.String(), nullable=True), sa.Column("endpoint", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False), sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    for column in ("action", "entity_type", "entity_id"):
        op.create_index(f"ix_audit_logs_{column}", "audit_logs", [column])
    _common("audit_logs")
    for table, columns in (("security_logs", [("event_type", sa.String(), False), ("description", sa.Text(), False), ("ip_address", sa.String(), True)]), ("access_logs", [("resource_type", sa.String(), False), ("resource_id", sa.Integer(), True), ("action", sa.String(), False), ("ip_address", sa.String(), True)])):
        op.create_table(table, sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), nullable=True), *[sa.Column(name, kind, nullable=nullable) for name, kind, nullable in columns], sa.Column("created_at", sa.DateTime(), nullable=False), sa.ForeignKeyConstraint(["user_id"], ["users.id"]))
        _common(table)
    op.create_table("decision_versions",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("decision_id", sa.Integer(), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False), sa.Column("title", sa.String(), nullable=False),
        sa.Column("problem_statement", sa.Text(), nullable=False), sa.Column("rationale", sa.Text(), nullable=True),
        sa.Column("category", sa.String(), nullable=False), sa.Column("status", sa.String(), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["decision_id"], ["decisions.id"], ondelete="CASCADE"), sa.ForeignKeyConstraint(["created_by"], ["users.id"]), sa.UniqueConstraint("decision_id", "version_number"),
    )
    op.create_index("ix_decision_versions_created_by", "decision_versions", ["created_by"])
    op.create_index("ix_decision_versions_created_at", "decision_versions", ["created_at"])
    op.create_index("ix_decision_versions_decision_id", "decision_versions", ["decision_id"])


def downgrade() -> None:
    op.drop_table("decision_versions")
    op.drop_table("access_logs")
    op.drop_table("security_logs")
    op.drop_table("audit_logs")