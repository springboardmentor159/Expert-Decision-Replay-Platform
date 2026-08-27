from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import relationship

from app.base import Base


class Alternative(Base):
    __tablename__ = "alternatives"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    decision_id = Column(
        Integer,
        ForeignKey(
            "decisions.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    name = Column(
        String(255),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    pros = Column(
        Text,
        nullable=True
    )

    cons = Column(
        Text,
        nullable=True
    )

    estimated_cost = Column(
        Integer,
        nullable=True
    )

    feasibility_score = Column(
        Integer,
        nullable=True
    )

    risk_level = Column(
        String(20),
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    decision = relationship(
        "Decision",
        back_populates="alternatives"
    )