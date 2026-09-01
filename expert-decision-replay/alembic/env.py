from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

from app.core.config import settings
from app.db.base import Base


# =========================================================
# IMPORT ALL MODELS
# =========================================================
# These imports allow Alembic to detect all SQLAlchemy models.

from app.models.user import User
from app.models.decision import Decision
from app.models.alternative import Alternative
from app.models.comment import Comment
from app.models.discussion_thread import DiscussionThread
from app.models.meeting_note import MeetingNote
from app.models.tag import Tag
from app.models.approval import Approval
from app.models.activity_log import ActivityLog


# =========================================================
# ALEMBIC CONFIG
# =========================================================

config = context.config


if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# =========================================================
# DATABASE URL
# =========================================================

config.set_main_option(
    "sqlalchemy.url",
    settings.DATABASE_URL,
)


# =========================================================
# TARGET METADATA
# =========================================================

target_metadata = Base.metadata


# =========================================================
# OFFLINE MIGRATIONS
# =========================================================

def run_migrations_offline() -> None:

    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# =========================================================
# ONLINE MIGRATIONS
# =========================================================

def run_migrations_online() -> None:

    connectable = engine_from_config(
        config.get_section(
            config.config_ini_section,
            {}
        ),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


# =========================================================
# RUN MIGRATION
# =========================================================

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()