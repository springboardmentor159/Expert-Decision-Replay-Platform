from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # e.g. "decision_created", "decision_status_changed", "comment_added"
    action = Column(String, nullable=False, index=True)

    # e.g. "Decision", "Alternative", "Comment", "Approval"
    entity_type = Column(String, nullable=False, index=True)

    entity_id = Column(Integer, nullable=False)

    description = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = relationship("User")
