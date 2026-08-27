from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class Approval(Base):
    """
    Minimal approval-workflow table.

    NOTE: This did not exist in the project before Sprint 10. The Sprint 10
    brief assumes it was built in Sprint 8 — it wasn't, so this is a
    from-scratch, deliberately small version that gives the dashboard
    something real to read from.
    """
    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True, index=True)

    decision_id = Column(Integer, ForeignKey("decisions.id"), nullable=False)

    # Simple single-level approval. Bump this manually if you ever need
    # multi-level approval chains (level 1, level 2, ...).
    level = Column(Integer, nullable=False, default=1)

    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Pending / Approved / Rejected
    status = Column(String, nullable=False, default="Pending")

    comments = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    decision = relationship("Decision")
    reviewer = relationship("User")
