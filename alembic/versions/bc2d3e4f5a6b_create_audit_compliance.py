"""create audit compliance tables

Revision ID: bc2d3e4f5a6b
Revises: ab1c2d3e4f5a
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "bc2d3e4f5a6b"
down_revision: Union[str, Sequence[str], None] = "ab1c2d3e4f5a"
branch_labels = None
depends_on = None


def _indexes(table, columns):
    for column in columns:
        op.create_index(f"ix_{table}_{column}", table, [column], unique=False)


def upgrade() -> None:
    op.create_table("audit_logs", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), nullable=True), sa.Column("action", sa.String(), nullable=False), sa.Column("entity_type", sa.String(), nullable=False), sa.Column("entity_id", sa.Integer(), nullable=True), sa.Column("description", sa.Text(), nullable=False), sa.Column("old_value", sa.JSON(), nullable=True), sa.Column("new_value", sa.JSON(), nullable=True), sa.Column("ip_address", sa.String(), nullable=True), sa.Column("request_method", sa.String(), nullable=True), sa.Column("endpoint", sa.String(), nullable=True), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.ForeignKeyConstraint(["user_id"], ["users.id"]))
    op.create_table("decision_versions", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("decision_id", sa.Integer(), nullable=False), sa.Column("version_number", sa.Integer(), nullable=False), sa.Column("title", sa.String(), nullable=False), sa.Column("problem_statement", sa.Text(), nullable=False), sa.Column("category", sa.String(), nullable=False), sa.Column("status", sa.String(), nullable=False), sa.Column("rationale", sa.Text(), nullable=True), sa.Column("created_by", sa.Integer(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.ForeignKeyConstraint(["decision_id"], ["decisions.id"]), sa.ForeignKeyConstraint(["created_by"], ["users.id"]), sa.UniqueConstraint("decision_id", "version_number", name="uq_decision_version_number"))
    op.create_table("security_logs", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), nullable=True), sa.Column("event_type", sa.String(), nullable=False), sa.Column("description", sa.Text(), nullable=False), sa.Column("ip_address", sa.String(), nullable=True), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.ForeignKeyConstraint(["user_id"], ["users.id"]))
    op.create_table("access_logs", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), nullable=False), sa.Column("resource_type", sa.String(), nullable=False), sa.Column("resource_id", sa.Integer(), nullable=True), sa.Column("action", sa.String(), nullable=False), sa.Column("ip_address", sa.String(), nullable=True), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.ForeignKeyConstraint(["user_id"], ["users.id"]))
    _indexes("audit_logs", ["id", "user_id", "action", "entity_type", "entity_id", "created_at"])
    _indexes("decision_versions", ["id", "decision_id"])
    _indexes("security_logs", ["id", "user_id", "event_type", "created_at"])
    _indexes("access_logs", ["id", "user_id", "resource_type", "created_at"])


def downgrade() -> None:
    for table in ("access_logs", "security_logs", "decision_versions", "audit_logs"):
        op.drop_table(table)
