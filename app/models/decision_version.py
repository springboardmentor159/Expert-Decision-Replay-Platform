from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class DecisionVersion(Base):
    """
    Sprint 11: Version Tracking.

    A snapshot of a Decision's important fields, written every time the
    decision is created or meaningfully changed (title, problem
    statement, category, status, rationale). The live `decisions` row
    always reflects the latest state; this table preserves every prior
    state so it can be replayed.

    version_number is assigned by the backend (see
    app.utils.audit.create_decision_version) and is never accepted from
    the client, so it can't be spoofed or made non-sequential.
    """
    __tablename__ = "decision_versions"
    __table_args__ = (
        UniqueConstraint(
            "decision_id", "version_number", name="uq_decision_version"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    decision_id = Column(Integer, ForeignKey("decisions.id"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False, index=True)

    title = Column(String, nullable=False)
    problem_statement = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    status = Column(String, nullable=False)
    rationale = Column(Text, nullable=True)

    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    decision = relationship("Decision")
    author = relationship("User")
