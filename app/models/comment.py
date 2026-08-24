from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Comment(Base):
    __tablename__ = "comments"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # Comment directly related to a decision
    decision_id = Column(
        Integer,
        ForeignKey("decisions.id"),
        nullable=False
    )

    # User who created the comment
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    # Optional thread ID for thread replies
    thread_id = Column(
        Integer,
        ForeignKey("discussion_threads.id"),
        nullable=True
    )

    content = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Decision relationship
    decision = relationship(
        "Decision",
        back_populates="comments"
    )

    # User relationship
    user = relationship(
        "User",
        back_populates="comments"
    )

    # Discussion thread relationship
    thread = relationship(
        "DiscussionThread",
        back_populates="comments"
    )