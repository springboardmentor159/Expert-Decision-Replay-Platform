from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base
from app.models.alternative_enums import RiskLevel


class Alternative(Base):
    __tablename__ = "alternatives"

    id = Column(Integer, primary_key=True, index=True)
    decision_id = Column(Integer, ForeignKey("decisions.id"), nullable=False)

    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    pros = Column(Text, nullable=True)
    cons = Column(Text, nullable=True)
    estimated_cost = Column(Integer, nullable=True)
    feasibility_score = Column(Integer, nullable=False)
    risk_level = Column(SQLAlchemyEnum(RiskLevel), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    decision = relationship("Decision", back_populates="alternatives")
    