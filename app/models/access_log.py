from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class AccessLog(Base):
    __tablename__ = "access_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    resource_type = Column(String, nullable=False, index=True)  # Decision, Approval, AuditLog, etc.
    resource_id = Column(Integer, nullable=True, index=True)
    action = Column(String, nullable=False, index=True)  # VIEW, LIST, EXPORT
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = relationship("User")
