from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.db.base import Base


class Alternative(Base):
    __tablename__ = "alternatives"

    id = Column(Integer, primary_key=True, index=True)

    decision_id = Column(
        Integer,
        ForeignKey("decisions.id"),
        nullable=False,
    )

    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    pros = Column(Text, nullable=False)
    cons = Column(Text, nullable=False)

    estimated_cost = Column(Float, nullable=False)
    feasibility_score = Column(Integer, nullable=False)
    risk_level = Column(String, nullable=False)

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

    decision = relationship(
        "Decision",
        back_populates="alternatives",
    )