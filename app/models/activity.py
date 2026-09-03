from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Activity(Base):
    __tablename__ = "activities"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    action = Column(
        String,
        nullable=False
    )

    entity_type = Column(
        String,
        nullable=False
    )

    entity_id = Column(
        Integer,
        nullable=False
    )

    description = Column(
        String,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    user = relationship(
        "User",
        back_populates="activities"
    )