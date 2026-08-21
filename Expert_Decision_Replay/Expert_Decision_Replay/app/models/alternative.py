from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Alternative(Base):
    __tablename__ = "alternatives"

    id = Column(Integer, primary_key=True, index=True)

    decision_id = Column(
        Integer,
        ForeignKey("decisions.id"),
        nullable=False,
        index=True
    )

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    pros = Column(Text, nullable=False)
    cons = Column(Text, nullable=False)

    estimated_cost = Column(Integer, nullable=False)

    feasibility_score = Column(Integer, nullable=False)

    risk_level = Column(String(20), nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    decision = relationship(
        "Decision",
        back_populates="alternatives"
    )