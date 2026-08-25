from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Enum as SqlAlchemyEnum, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base
from app.models.enums import RiskLevel


class Alternative(Base):
    __tablename__ = "alternatives"

    __table_args__ = (
        CheckConstraint(
            "feasibility_score BETWEEN 1 AND 5",
            name="check_valid_feasibility_score"
        ),
        CheckConstraint(
            "risk_level IN ('Low', 'Medium', 'High', 'Critical')",
            name="check_valid_risk_level"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    decision_id = Column(Integer, ForeignKey("decisions.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    pros = Column(String, nullable=True)
    cons = Column(String, nullable=True)
    estimated_cost = Column(Integer, nullable=True)
    feasibility_score = Column(Integer, nullable=True)
    risk_level = Column(
        SqlAlchemyEnum(RiskLevel, name="risklevel", native_enum=False, values_callable=lambda x: [e.value for e in x]),
        nullable=True,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    decision = relationship("Decision", back_populates="alternatives")