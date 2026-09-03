from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class ThreadReply(Base):
    __tablename__ = "thread_replies"

    id = Column(Integer, primary_key=True, index=True)

    thread_id = Column(
        Integer,
        ForeignKey("discussion_threads.id"),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    content = Column(
        String,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    thread = relationship(
        "DiscussionThread",
        back_populates="replies"
    )

    user = relationship(
        "User",
        back_populates="thread_replies"
    )