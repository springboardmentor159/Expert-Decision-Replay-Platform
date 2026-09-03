from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Alternative(Base):
    __tablename__ = "alternatives"

    id = Column(Integer, primary_key=True, index=True)

    decision_id = Column(
        Integer,
        ForeignKey("decisions.id"),
        nullable=False
    )

    name = Column(String, nullable=False)

    description = Column(String, nullable=False)

    pros = Column(String, nullable=False)

    cons = Column(String, nullable=False)

    estimated_cost = Column(Integer, nullable=False)

    feasibility_score = Column(Integer, nullable=False)

    risk_level = Column(String, nullable=False)

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

    decision = relationship(
        "Decision",
        back_populates="alternatives"
    )