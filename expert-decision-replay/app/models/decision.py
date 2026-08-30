from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class Decision(Base):
    __tablename__ = "decisions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    title = Column(
        String,
        nullable=False
    )

    problem_statement = Column(
        String,
        nullable=False
    )

    category = Column(
        String,
        nullable=False
    )

    status = Column(
        String,
        nullable=False,
        default="Draft"
    )

    rationale = Column(
        String,
        nullable=True
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

    # =====================================================
    # Many Decisions -> One User
    # =====================================================

    user = relationship(
        "User",
        back_populates="decisions"
    )

    # =====================================================
    # One Decision -> Many Alternatives
    # =====================================================

    alternatives = relationship(
        "Alternative",
        back_populates="decision",
        cascade="all, delete-orphan"
    )

    # =====================================================
    # One Decision -> Many Comments
    # =====================================================

    comments = relationship(
        "Comment",
        back_populates="decision",
        cascade="all, delete-orphan"
    )

    # =====================================================
    # One Decision -> Many Discussion Threads
    # =====================================================

    discussion_threads = relationship(
        "DiscussionThread",
        back_populates="decision",
        cascade="all, delete-orphan"
    )

    # =====================================================
    # One Decision -> Many Meeting Notes
    # =====================================================

    meeting_notes = relationship(
        "MeetingNote",
        back_populates="decision",
        cascade="all, delete-orphan"
    )

    # =====================================================
    # Many Decisions <-> Many Tags
    # =====================================================

    tags = relationship(
        "Tag",
        secondary="decision_tags",
        back_populates="decisions"
    )