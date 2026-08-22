from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)

    # Every comment belongs to a Decision (even when it was created
    # through a thread reply - see thread_id below).
    decision_id = Column(Integer, ForeignKey("decisions.id"), nullable=False)

    # Optional: set only when the comment is a reply inside a
    # discussion thread. NULL means it's a top-level decision comment.
    thread_id = Column(
        Integer,
        ForeignKey("discussion_threads.id"),
        nullable=True
    )

    # Ownership is always taken from the authenticated JWT user,
    # never from client input.
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    content = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    decision = relationship("Decision", back_populates="comments")
    thread = relationship("DiscussionThread", back_populates="comments")
    user = relationship("User")
