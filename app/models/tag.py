from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Tag(Base):
    __tablename__ = "tags"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Decisions using this tag
    decisions = relationship(
        "Decision",
        secondary="decision_tags",
        back_populates="tags"
    )