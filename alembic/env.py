from alembic import context
from app.core.config import settings
from app.db.base import Base

config = context.config

config.set_main_option(
    "sqlalchemy.url",
    settings.DATABASE_URL
)

target_metadata = Base.metadata
