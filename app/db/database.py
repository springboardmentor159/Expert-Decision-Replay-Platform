from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base


DATABASE_URL = "postgresql://postgres:12345@localhost:5432/expert-decision-replay"


engine = create_engine(DATABASE_URL)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()