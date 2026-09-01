from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


class Decision(Base):
    __tablename__ = "decisions"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(200), nullable=False)

    problem_statement = Column(Text, nullable=False)

    category = Column(String(100), nullable=False)

    status = Column(String(50), nullable=False, default="Draft")

    rationale = Column(Text, nullable=True)

    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    creator = relationship("User", back_populates="decisions")

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
    approvals = relationship(
        "Approval",
        back_populates="decision",
        cascade="all, delete-orphan"
    )
    versions = relationship(
        "DecisionVersion",
        back_populates="decision",
        cascade="all, delete-orphan"
    )