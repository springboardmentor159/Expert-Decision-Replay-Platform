from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


# Many-to-many association table between decisions and tags
decision_tags = Table(
    "decision_tags",
    Base.metadata,
    Column(
        "decision_id",
        Integer,
        ForeignKey("decisions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id",
        Integer,
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


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
        Text,
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

    # User who created the decision
    user = relationship(
        "User",
        back_populates="decisions"
    )

    # Alternatives belonging to this decision
    alternatives = relationship(
        "Alternative",
        back_populates="decision",
        cascade="all, delete-orphan"
    )

    # Comments belonging to this decision
    comments = relationship(
        "Comment",
        back_populates="decision",
        cascade="all, delete-orphan"
    )

    # Discussion threads belonging to this decision
    discussion_threads = relationship(
        "DiscussionThread",
        back_populates="decision",
        cascade="all, delete-orphan"
    )

    # Meeting notes belonging to this decision
    meeting_notes = relationship(
        "MeetingNote",
        back_populates="decision",
        cascade="all, delete-orphan"
    )

    # Decision rationale
    rationale = Column(
        Text,
        nullable=True
    )

    # Attachments belonging to this decision
    attachments = relationship(
        "Attachment",
        back_populates="decision"
    )

    # Tags assigned to this decision
    tags = relationship(
        "Tag",
        secondary=decision_tags,
        back_populates="decisions"
    )