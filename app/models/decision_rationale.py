from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class DecisionRationale(Base):
    __tablename__ = "decision_rationales"

    id = Column(Integer, primary_key=True, index=True)

    decision_id = Column(
        Integer,
        ForeignKey("decisions.id"),
        nullable=False,
        unique=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    content = Column(
        String,
        nullable=False
    )

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
        back_populates="rationale"
    )

    user = relationship(
        "User",
        back_populates="decision_rationales"
    )