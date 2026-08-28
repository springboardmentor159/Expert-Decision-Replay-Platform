from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.db.base import Base


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

    approval_level = Column(
        Integer,
        nullable=False,
        default=1
    )

    status = Column(
        String,
        nullable=False,
        default="Pending"
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

    decision = relationship(
        "Decision",
        back_populates="approvals"
    )

    reviewer = relationship(
        "User",
        back_populates="approvals"
    )