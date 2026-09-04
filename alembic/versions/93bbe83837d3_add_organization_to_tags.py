"""add organization to tags

Revision ID: 93bbe83837d3
Revises: af227556f94f
Create Date: 2026-08-28 14:03:51.554160

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Revision identifiers, used by Alembic.
revision: str = "93bbe83837d3"
down_revision: Union[str, Sequence[str], None] = "af227556f94f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Existing organization that will own the existing tags
DEFAULT_ORGANIZATION_ID = 1


def upgrade() -> None:
    """Upgrade schema."""

    # 1. Add organization_id as nullable temporarily
    op.add_column(
        "tags",
        sa.Column(
            "organization_id",
            sa.Integer(),
            nullable=True
        )
    )

    # 2. Remove the old globally-unique tag name constraint
    #
    # Previously:
    #     Tag.name = unique
    #
    # This prevented two organizations from having the same
    # tag name.
    op.drop_constraint(
        op.f("tags_name_key"),
        "tags",
        type_="unique"
    )

    # 3. Create index for organization_id
    op.create_index(
        op.f("ix_tags_organization_id"),
        "tags",
        ["organization_id"],
        unique=False
    )

    # 4. Assign all existing tags to the existing organization
    #
    # IMPORTANT:
    # Change DEFAULT_ORGANIZATION_ID if your organization
    # has another ID.
    op.execute(
        sa.text(
            """
            UPDATE tags
            SET organization_id = :organization_id
            WHERE organization_id IS NULL
            """
        ).bindparams(
            organization_id=DEFAULT_ORGANIZATION_ID
        )
    )

    # 5. Make sure no tags were left without an organization
    connection = op.get_bind()

    unassigned_tags = connection.execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM tags
            WHERE organization_id IS NULL
            """
        )
    ).scalar()

    if unassigned_tags and unassigned_tags > 0:
        raise RuntimeError(
            "Some tags could not be assigned to an organization."
        )

    # 6. organization_id is now mandatory
    op.alter_column(
        "tags",
        "organization_id",
        existing_type=sa.Integer(),
        nullable=False
    )

    # 7. A tag name must be unique only within an organization
    #
    # Example:
    #
    # Organization 1 → Urgent
    # Organization 2 → Urgent
    #
    # Both are valid.
    op.create_unique_constraint(
        "uq_tag_organization_name",
        "tags",
        ["organization_id", "name"]
    )

    # 8. Add foreign key to organizations
    op.create_foreign_key(
        "fk_tags_organization_id",
        "tags",
        "organizations",
        ["organization_id"],
        ["id"]
    )


def downgrade() -> None:
    """Downgrade schema."""

    # 1. Remove foreign key
    op.drop_constraint(
        "fk_tags_organization_id",
        "tags",
        type_="foreignkey"
    )

    # 2. Remove organization/name unique constraint
    op.drop_constraint(
        "uq_tag_organization_name",
        "tags",
        type_="unique"
    )

    # 3. Remove organization index
    op.drop_index(
        op.f("ix_tags_organization_id"),
        table_name="tags"
    )

    # 4. Restore globally unique tag names
    op.create_unique_constraint(
        op.f("tags_name_key"),
        "tags",
        ["name"],
        postgresql_nulls_not_distinct=False
    )

    # 5. Remove organization_id
    op.drop_column(
        "tags",
        "organization_id"
    )
