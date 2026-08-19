from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from app.core.enums import DecisionStatus
from sqlalchemy.orm import relationship

from app.db.base import Base


class Decision(Base):
    __tablename__ = "decisions"

    alternatives = relationship(
    "Alternative",
    back_populates="decision",
    cascade="all, delete-orphan"
)

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)

    problem_statement = Column(Text, nullable=False)

    category = Column(String, nullable=False)

    status = Column(
    Enum(
        DecisionStatus,
        name="decision_status",
        values_callable=lambda enum: [item.value for item in enum]
    ),
    nullable=False,
    default=DecisionStatus.DRAFT
)

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
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

    creator = relationship(
        "User",
        back_populates="decisions"
    )