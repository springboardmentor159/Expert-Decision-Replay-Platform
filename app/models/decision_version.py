from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Enum,
    UniqueConstraint,
    Index
)
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.core.enums import DecisionStatus


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
        nullable=False,
        index=True
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

    rationale = Column(
        Text,
        nullable=True
    )

    category = Column(
        String,
        nullable=False
    )

    status = Column(
        Enum(
            DecisionStatus,
            name="decision_version_status",
            values_callable=lambda enum: [
                item.value for item in enum
            ]
        ),
        nullable=False
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True
    )

    decision = relationship(
        "Decision",
        back_populates="versions"
    )

    creator = relationship(
        "User"
    )

    __table_args__ = (
        UniqueConstraint(
            "decision_id",
            "version_number",
            name="uq_decision_version_number"
        ),
        Index(
            "ix_decision_versions_decision_created",
            "decision_id",
            "created_at"
        ),
    )