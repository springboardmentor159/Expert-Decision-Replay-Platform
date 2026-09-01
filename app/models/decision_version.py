from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


class DecisionVersion(Base):
    __tablename__ = "decision_versions"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    decision_id = Column(
        Integer,
        ForeignKey("decisions.id"),
        nullable=False,
    )

    version_number = Column(
        Integer,
        nullable=False,
    )

    title = Column(
        String(200),
        nullable=False,
    )

    problem_statement = Column(
        Text,
        nullable=False,
    )

    category = Column(
        String(100),
        nullable=False,
    )

    status = Column(
        String(50),
        nullable=False,
    )

    rationale = Column(
        Text,
        nullable=True,
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    decision = relationship(
        "Decision",
        back_populates="versions",
    )

    creator = relationship(
        "User",
    )

    __table_args__ = (
        UniqueConstraint(
            "decision_id",
            "version_number",
            name="uq_decision_version",
        ),
        Index(
            "ix_decision_versions_decision_id",
            "decision_id",
        ),
    )