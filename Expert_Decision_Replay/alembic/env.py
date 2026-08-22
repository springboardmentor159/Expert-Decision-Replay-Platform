import sys
from pathlib import Path

# Add inner Expert_Decision_Replay folder to Python path
sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "Expert_Decision_Replay")
)

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import settings
from app.base import Base

# Import all models so Alembic can detect their tables
from app.models.user import User
from app.models.decision import Decision
from app.models.alternative import Alternative
from app.models.comment import Comment

config = context.config

# Use the application's PostgreSQL database
config.set_main_option(
    "sqlalchemy.url",
    settings.DATABASE_URL.replace("%", "%%")
)

target_metadata = Base.metadata


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


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
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


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()