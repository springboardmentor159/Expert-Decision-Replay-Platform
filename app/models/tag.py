from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Table
)
from sqlalchemy.orm import relationship

from app.base import Base


decision_tags = Table(
    "decision_tags",
    Base.metadata,

    Column(
        "decision_id",
        Integer,
        ForeignKey("decisions.id", ondelete="CASCADE"),
        primary_key=True
    ),

    Column(
        "tag_id",
        Integer,
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True
    )
)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    decisions = relationship(
        "Decision",
        secondary=decision_tags,
        back_populates="tags"
    )