from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    ForeignKey,
    Enum,
    Index
)
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.core.enums import UserRole


# =========================================================
# APPROVAL STATUS
# =========================================================

class ApprovalStatus(str, PyEnum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"


# =========================================================
# APPROVAL MODEL
# =========================================================

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
        nullable=False,
        index=True
    )

    assigned_to = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    assigned_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    assigned_role = Column(
        Enum(
            UserRole,
            name="approval_assigned_role",
            values_callable=lambda enum: [
                item.value for item in enum
            ]
        ),
        nullable=False
    )

    status = Column(
        Enum(
            ApprovalStatus,
            name="approval_status",
            values_callable=lambda enum: [
                item.value for item in enum
            ]
        ),
        nullable=False,
        default=ApprovalStatus.PENDING,
        index=True
    )

    comments = Column(
        Text,
        nullable=True
    )

    assigned_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    reviewed_at = Column(
        DateTime,
        nullable=True
    )

    # =====================================================
    # RELATIONSHIPS
    # =====================================================

    decision = relationship(
        "Decision"
    )

    assigned_user = relationship(
        "User",
        foreign_keys=[assigned_to]
    )

    assigning_user = relationship(
        "User",
        foreign_keys=[assigned_by]
    )

    # =====================================================
    # INDEXES
    # =====================================================

    __table_args__ = (
        Index(
            "ix_approvals_decision_status",
            "decision_id",
            "status"
        ),
    )