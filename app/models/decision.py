from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.models.tag import decision_tags
from app.db.base import Base


class DecisionStatus(str, Enum):
    DRAFT = "Draft"
    UNDER_REVIEW = "Under Review"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    ARCHIVED = "Archived"


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
        SQLEnum(
            DecisionStatus,
            name="decision_status",
            values_callable=lambda enum_class: [
                status.value for status in enum_class
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

    organization_id = Column(
        Integer,
        ForeignKey("organizations.id"),
        nullable=True
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

    user = relationship(
        "User",
        back_populates="decisions"
    )

    organization = relationship(
        "Organization",
        back_populates="decisions"
    )

    meeting_notes = relationship(
        "MeetingNote",
        back_populates="decision"
    )

    comments = relationship(
        "Comment",
        back_populates="decision"
    )

    discussion_threads = relationship(
        "DiscussionThread",
        back_populates="decision"
    )

    alternatives = relationship(
        "Alternative",
        back_populates="decision",
        cascade="all, delete-orphan"
    )

    tags = relationship(
        "Tag",
        secondary=decision_tags,
        back_populates="decisions"
    )

    audit_logs = relationship(
        "AuditLog",
        back_populates="decision",
        cascade="all, delete-orphan"
    )

    approvals = relationship(
        "Approval",
        back_populates="decision",
        cascade="all, delete-orphan"
    )