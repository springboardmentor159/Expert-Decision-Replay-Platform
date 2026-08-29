from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Table
)
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


# Many-to-many relationship between decisions and tags
decision_tags = Table(
    "decision_tags",
    Base.metadata,

    Column(
        "decision_id",
        ForeignKey("decisions.id", ondelete="CASCADE"),
        primary_key=True
    ),

    Column(
        "tag_id",
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True
    )
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

    rationale = Column(
        Text,
        nullable=True
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

    # Decision → Alternatives
    alternatives = relationship(
        "Alternative",
        back_populates="decision",
        cascade="all, delete-orphan"
    )

    # Decision → Comments
    comments = relationship(
        "Comment",
        back_populates="decision",
        cascade="all, delete-orphan"
    )

    # Decision → Discussion Threads
    threads = relationship(
        "DiscussionThread",
        back_populates="decision",
        cascade="all, delete-orphan"
    )

    # Decision ↔ Tags
    tags = relationship(
        "Tag",
        secondary=decision_tags,
        back_populates="decisions"
    )

    activities = relationship(
    "DecisionActivity",
    cascade="all, delete-orphan"
)

approvals = relationship(
        "Approval",
        cascade="all, delete-orphan"
    )