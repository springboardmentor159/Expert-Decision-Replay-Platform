from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


class Decision(Base):
    __tablename__ = "decisions"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)

    problem_statement = Column(Text, nullable=False)

    
    rationale = Column(Text, nullable=True)

    category = Column(String, nullable=False)

    status = Column(String, nullable=False, default="Draft")

  

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

    user = relationship(
        "User",
        back_populates="decisions"
    )

    alternatives = relationship(
        "Alternative",
        back_populates="decision",
        cascade="all, delete-orphan"
    )
    comments = relationship(
    "Comment",
    back_populates="decision",
    cascade="all, delete-orphan"
    )
    discussion_threads = relationship(
    "DiscussionThread",
    back_populates="decision",
    cascade="all, delete-orphan"
    )
    meeting_notes = relationship(
    "MeetingNote",
    back_populates="decision",
    cascade="all, delete-orphan"
    )
    tags = relationship(
        "Tag",
        secondary="decision_tags",
        back_populates="decisions",
    )
    approvals = relationship("Approval", back_populates="decision", cascade="all, delete-orphan")