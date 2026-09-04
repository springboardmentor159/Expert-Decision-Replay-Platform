from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base
from app.models.decision_tag import decision_tags


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

    tags = relationship(
        "Tag",
        secondary=decision_tags,
        back_populates="decisions"
    )

    versions = relationship(
        "DecisionVersion",
        back_populates="decision",
        cascade="all, delete-orphan"
    )