from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class DiscussionThread(Base):
    __tablename__ = "discussion_threads"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

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

    title = Column(
        String,
        nullable=False
    )

    description = Column(
        String,
        nullable=False
    )

    status = Column(
        String,
        nullable=False,
        default="Open"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # DiscussionThread -> Decision
    decision = relationship(
        "Decision",
        back_populates="discussion_threads"
    )

    # DiscussionThread -> User
    user = relationship(
        "User",
        back_populates="discussion_threads"
    )

    # DiscussionThread -> Many Replies
    comments = relationship(
        "Comment",
        back_populates="thread",
        cascade="all, delete-orphan"
    )