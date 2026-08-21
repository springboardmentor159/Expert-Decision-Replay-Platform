from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

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

    title = Column(
        String,
        nullable=False
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
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

    decision = relationship(
        "Decision",
        back_populates="discussion_threads"
    )

    user = relationship(
        "User",
        back_populates="discussion_threads"
    )
    
    comments = relationship(
    "Comment",
    back_populates="thread"
    )