from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String, nullable=False, index=True)  # CREATE, UPDATE, DELETE, APPROVE, REJECT, SUBMIT, LOGIN, LOGOUT, ACCESS
    entity_type = Column(String, nullable=False, index=True)  # Decision, Alternative, Comment, DiscussionThread, MeetingNote, Approval, User, etc.
    entity_id = Column(Integer, nullable=True, index=True)
    description = Column(Text, nullable=False)
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    ip_address = Column(String, nullable=True)
    request_method = Column(String, nullable=True)
    endpoint = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = relationship("User")
