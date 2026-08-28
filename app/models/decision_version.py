from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base import Base


class DecisionVersion(Base):
    __tablename__ = "decision_versions"
    __table_args__ = (UniqueConstraint("decision_id", "version_number"),)

    id = Column(Integer, primary_key=True, index=True)
    decision_id = Column(Integer, ForeignKey("decisions.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    problem_statement = Column(Text, nullable=False)
    rationale = Column(Text, nullable=True)
    category = Column(String, nullable=False)
    status = Column(String, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    decision = relationship("Decision", back_populates="versions")
    user = relationship("User", back_populates="decision_versions")