from sqlalchemy import Column, Integer, String, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


# Association table for the many-to-many relationship between
# Decisions and Tags. One decision can have many tags, and one tag
# can belong to many decisions.
decision_tags = Table(
    "decision_tags",
    Base.metadata,
    Column("decision_id", Integer, ForeignKey("decisions.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)

    # Tag names are unique so "PostgreSQL" is never stored twice.
    name = Column(String, unique=True, nullable=False, index=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    decisions = relationship(
        "Decision",
        secondary=decision_tags,
        back_populates="tags"
    )
