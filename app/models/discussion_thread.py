from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


class DiscussionThread(Base):
    __tablename__ = "discussion_threads"

    id = Column(Integer, primary_key=True, index=True)

    decision_id = Column(
        Integer,
        ForeignKey("decisions.id"),
        nullable=False
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    title = Column(String, nullable=False)

    description = Column(Text, nullable=False)

    status = Column(
        String,
        nullable=False,
        default="Open"
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    decision = relationship(
        "Decision",
        back_populates="discussion_threads"
    )

    user = relationship(
        "User",
        back_populates="discussion_threads"
    )