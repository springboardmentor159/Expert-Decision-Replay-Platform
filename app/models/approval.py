from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.db.base import Base


class ApprovalStatus(str, Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"


class Approval(Base):
    __tablename__ = "approvals"

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

    reviewer_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    status = Column(
        SQLEnum(
            ApprovalStatus,
            name="approval_status",
            values_callable=lambda enum_class: [
                status.value for status in enum_class
            ]
        ),
        nullable=False,
        default=ApprovalStatus.PENDING
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    completed_at = Column(
        DateTime,
        nullable=True
    )

    sequence_order = Column(
        Integer,
        nullable=False,
        default=1
    )

    due_date = Column(
        DateTime,
        nullable=True
    )

    is_escalated = Column(
        Integer,
        nullable=False,
        default=0
    )

    escalated_to_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    decision = relationship(
        "Decision",
        back_populates="approvals"
    )

    reviewer = relationship(
        "User",
        foreign_keys=[reviewer_id],
        back_populates="approvals"
    )

    escalated_to = relationship(
        "User",
        foreign_keys=[escalated_to_id]
    )

