"""extend audit logs for compliance

Revision ID: 9b3cffdc9c19
Revises: 6f3bcb866ea1
Create Date: 2026-09-02 18:25:55.335119

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "9b3cffdc9c19"
down_revision: Union[str, Sequence[str], None] = "6f3bcb866ea1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Add new audit fields as nullable first because
    # audit_logs may already contain existing records.
    op.add_column(
        "audit_logs",
        sa.Column(
            "entity_type",
            sa.String(length=100),
            nullable=True,
        ),
    )

    op.add_column(
        "audit_logs",
        sa.Column(
            "entity_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.add_column(
        "audit_logs",
        sa.Column(
            "ip_address",
            sa.String(length=45),
            nullable=True,
        ),
    )

    op.add_column(
        "audit_logs",
        sa.Column(
            "old_value",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )

    op.add_column(
        "audit_logs",
        sa.Column(
            "new_value",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )

    op.add_column(
        "audit_logs",
        sa.Column(
            "request_method",
            sa.String(length=10),
            nullable=True,
        ),
    )

    op.add_column(
        "audit_logs",
        sa.Column(
            "endpoint",
            sa.String(length=255),
            nullable=True,
        ),
    )

    # Preserve existing audit records.
    # Existing audit records are decision-related,
    # so populate the new generic entity fields from decision_id.
    op.execute(
        """
        UPDATE audit_logs
        SET entity_type = 'Decision',
            entity_id = decision_id
        WHERE entity_type IS NULL
           OR entity_id IS NULL
        """
    )

    # Existing foreign keys are changed from CASCADE
    # to SET NULL so audit history is not deleted.
    op.alter_column(
        "audit_logs",
        "decision_id",
        existing_type=sa.INTEGER(),
        nullable=True,
    )

    op.alter_column(
        "audit_logs",
        "user_id",
        existing_type=sa.INTEGER(),
        nullable=True,
    )

    # Now that existing rows have values, make these fields required.
    op.alter_column(
        "audit_logs",
        "entity_type",
        existing_type=sa.String(length=100),
        nullable=False,
    )

    op.alter_column(
        "audit_logs",
        "entity_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    # Indexes required for audit filtering and performance.
    op.create_index(
        op.f("ix_audit_logs_action"),
        "audit_logs",
        ["action"],
        unique=False,
    )

    op.create_index(
        op.f("ix_audit_logs_created_at"),
        "audit_logs",
        ["created_at"],
        unique=False,
    )

    op.create_index(
        op.f("ix_audit_logs_entity_id"),
        "audit_logs",
        ["entity_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_audit_logs_entity_type"),
        "audit_logs",
        ["entity_type"],
        unique=False,
    )

    # Replace old CASCADE foreign keys with SET NULL.
    op.drop_constraint(
        op.f("audit_logs_decision_id_fkey"),
        "audit_logs",
        type_="foreignkey",
    )

    op.drop_constraint(
        op.f("audit_logs_user_id_fkey"),
        "audit_logs",
        type_="foreignkey",
    )

    op.create_foreign_key(
        None,
        "audit_logs",
        "decisions",
        ["decision_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_foreign_key(
        None,
        "audit_logs",
        "users",
        ["user_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    """Downgrade schema."""

    # Remove the SET NULL foreign keys.
    op.drop_constraint(
        None,
        "audit_logs",
        type_="foreignkey",
    )

    op.drop_constraint(
        None,
        "audit_logs",
        type_="foreignkey",
    )

    # Restore the original CASCADE foreign keys.
    op.create_foreign_key(
        op.f("audit_logs_user_id_fkey"),
        "audit_logs",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_foreign_key(
        op.f("audit_logs_decision_id_fkey"),
        "audit_logs",
        "decisions",
        ["decision_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # Remove indexes.
    op.drop_index(
        op.f("ix_audit_logs_entity_type"),
        table_name="audit_logs",
    )

    op.drop_index(
        op.f("ix_audit_logs_entity_id"),
        table_name="audit_logs",
    )

    op.drop_index(
        op.f("ix_audit_logs_created_at"),
        table_name="audit_logs",
    )

    op.drop_index(
        op.f("ix_audit_logs_action"),
        table_name="audit_logs",
    )

    # Restore original NOT NULL constraints.
    op.alter_column(
        "audit_logs",
        "user_id",
        existing_type=sa.INTEGER(),
        nullable=False,
    )

    op.alter_column(
        "audit_logs",
        "decision_id",
        existing_type=sa.INTEGER(),
        nullable=False,
    )

    # Remove Sprint 11 columns.
    op.drop_column(
        "audit_logs",
        "endpoint",
    )

    op.drop_column(
        "audit_logs",
        "request_method",
    )

    op.drop_column(
        "audit_logs",
        "new_value",
    )

    op.drop_column(
        "audit_logs",
        "old_value",
    )

    op.drop_column(
        "audit_logs",
        "ip_address",
    )

    op.drop_column(
        "audit_logs",
        "entity_id",
    )

    op.drop_column(
        "audit_logs",
        "entity_type",
    )