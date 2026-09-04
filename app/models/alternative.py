from datetime import datetime
from enum import Enum

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.db.base import Base


class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class Alternative(Base):
    __tablename__ = "alternatives"

    __table_args__ = (
        CheckConstraint(
            "feasibility_score >= 1 AND feasibility_score <= 5",
            name="check_feasibility_score"
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    decision_id = Column(
        Integer,
        ForeignKey("decisions.id"),
        nullable=False
    )

    name = Column(
        String,
        nullable=False
    )

    description = Column(
        Text,
        nullable=False
    )

    pros = Column(
        Text,
        nullable=False
    )

    cons = Column(
        Text,
        nullable=False
    )

    estimated_cost = Column(
        Numeric(12, 2),
        nullable=False
    )

    feasibility_score = Column(
        Integer,
        nullable=False
    )

    risk_level = Column(
        SQLEnum(
            RiskLevel,
            name="risk_level",
            values_callable=lambda enum_class: [
                risk.value for risk in enum_class
            ]
        ),
        nullable=False
    )

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
