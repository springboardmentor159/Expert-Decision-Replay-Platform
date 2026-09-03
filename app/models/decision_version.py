from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class DecisionVersion(Base):
    __tablename__ = "decision_versions"

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

    version_number = Column(
        Integer,
        nullable=False
    )

    title = Column(
        String,
        nullable=False
    )

    problem_statement = Column(
        Text,
        nullable=False
    )

    category = Column(
        String,
        nullable=False
    )

    status = Column(
        String,
        nullable=False
    )

    changed_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    change_summary = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    decision = relationship(
        "Decision",
        back_populates="versions"
    )

    user = relationship(
        "User",
        back_populates="decision_versions"
    )