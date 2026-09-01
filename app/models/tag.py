from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base
from app.models.decision_tag import decision_tags


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, unique=True, nullable=False, index=True)

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