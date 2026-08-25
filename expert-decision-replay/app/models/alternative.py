from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

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

    estimated_cost = Column(Float, nullable=False)

    feasibility_score = Column(Integer, nullable=False)

    risk_level = Column(String, nullable=False)

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

    decision = relationship(
        "Decision",
        back_populates="alternatives"
    )