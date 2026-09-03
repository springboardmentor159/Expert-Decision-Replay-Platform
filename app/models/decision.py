from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Decision(Base):
    __tablename__ = "decisions"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)

    problem_statement = Column(String, nullable=False)

    category = Column(String, nullable=False)

    status = Column(
        String,
        nullable=False,
        default="Draft"
    )

    tags = Column(
        String,
        nullable=True
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
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

    creator = relationship(
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

    rationale = relationship(
        "DecisionRationale",
        back_populates="decision",
        uselist=False,
        cascade="all, delete-orphan"
    )

    versions = relationship(
        "DecisionVersion",
        back_populates="decision",
        cascade="all, delete-orphan"
    )

    approvals = relationship(
        "Approval",
        back_populates="decision",
        cascade="all, delete-orphan"
    )