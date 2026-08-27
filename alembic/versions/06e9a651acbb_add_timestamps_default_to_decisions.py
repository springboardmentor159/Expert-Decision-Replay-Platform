from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = "06e9a651acbb"
down_revision = "9a642a256e6a"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "decisions",
        "created_at",
        server_default=sa.text("CURRENT_TIMESTAMP"),
        existing_type=sa.DateTime(),
        existing_nullable=False
    )

    op.alter_column(
        "decisions",
        "updated_at",
        server_default=sa.text("CURRENT_TIMESTAMP"),
        existing_type=sa.DateTime(),
        existing_nullable=False
    )


def downgrade():
    op.alter_column(
        "decisions",
        "created_at",
        server_default=None,
        existing_type=sa.DateTime(),
        existing_nullable=False
    )

    op.alter_column(
        "decisions",
        "updated_at",
        server_default=None,
        existing_type=sa.DateTime(),
        existing_nullable=False
    )