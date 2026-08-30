from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class ExpertEvaluation(Base):
    __tablename__ = "expert_evaluations"

    id = Column(Integer, primary_key=True, index=True)

    decision_id = Column(
        Integer,
        ForeignKey("decisions.id"),
        nullable=False
    )

    alternative_id = Column(
        Integer,
        ForeignKey("alternatives.id"),
        nullable=False
    )

    expert_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    feasibility_score = Column(
        Integer,
        nullable=False
    )

    risk_score = Column(
        Integer,
        nullable=False
    )

    cost_score = Column(
        Integer,
        nullable=False
    )

    comments = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    decision = relationship(
        "Decision",
        back_populates="expert_evaluations"
    )

    alternative = relationship(
        "Alternative",
        back_populates="expert_evaluations"
    )

    expert = relationship(
        "User",
        back_populates="expert_evaluations"
    )