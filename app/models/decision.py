from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Table,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.db.base import Base
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

from sqlalchemy.orm import relationship
class Decision(Base):
    __tablename__ = "decisions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    problem_statement = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    status = Column(String, nullable=False, default="Draft")

    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user = relationship("User", back_populates="decisions")

    alternatives = relationship(
        "Alternative",
        back_populates="decision",
        cascade="all, delete-orphan",
    )

    comments = relationship(
        "Comment",
        back_populates="decision",
        cascade="all, delete-orphan",
    )
    discussion_threads = relationship(
    "DiscussionThread",
    back_populates="decision",
)
    tags = relationship(
    "Tag",
    secondary=decision_tags,
    back_populates="decisions",
)
    alternatives = relationship(
    "Alternative",
    back_populates="decision",
    cascade="all, delete-orphan",
)