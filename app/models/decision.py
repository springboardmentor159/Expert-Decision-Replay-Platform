from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Enum
)
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.core.enums import DecisionStatus
from app.models.tag import decision_tags


class Decision(Base):
    __tablename__ = "decisions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
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
            name="decision_status",
            values_callable=lambda enum: [
                item.value for item in enum
            ]
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
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # =====================================================
    # RELATIONSHIPS
    # =====================================================

    creator = relationship(
        "User",
        back_populates="decisions"
    )

    alternatives = relationship(
        "Alternative",
        back_populates="decision",
        cascade="all, delete-orphan"
    )

    comments = relationship(
        "Comment",
        back_populates="decision"
    )

    meeting_notes = relationship(
        "MeetingNote",
        back_populates="decision"
    )

    tags = relationship(
        "Tag",
        secondary=decision_tags,
        back_populates="decisions"
    )

    expert_evaluations = relationship(
        "ExpertEvaluation",
        back_populates="decision",
        cascade="all, delete-orphan"
    )

    versions = relationship(
        "DecisionVersion",
        back_populates="decision",
        cascade="all, delete-orphan",
        order_by="DecisionVersion.version_number"
    )