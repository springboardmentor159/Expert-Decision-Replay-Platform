from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.approval_status import ApprovalStatus


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True, index=True)

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
        SQLAlchemyEnum(ApprovalStatus),
        nullable=False,
        default=ApprovalStatus.PENDING
    )

    approval_level = Column(
        Integer,
        nullable=False,
        default=1
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    decision = relationship(
        "Decision"
    )

    reviewer = relationship(
        "User"
    )