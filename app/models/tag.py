from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from app.db.base import Base

# Association table for Many-to-Many relationship between Decision and Tag
decision_tags = Table(
    "decision_tags",
    Base.metadata,
    Column("decision_id", Integer, ForeignKey("decisions.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    decisions = relationship("Decision", secondary=decision_tags, back_populates="tags")
