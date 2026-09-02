from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class AccessLog(Base):
    """
    Sprint 11: Resource access log.

    Lighter-weight than AuditLog - records that a user *viewed* a
    sensitive resource (a decision, an approval, the audit log itself),
    not that they changed anything.
    """
    __tablename__ = "access_logs"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    resource_type = Column(String, nullable=False, index=True)
    resource_id = Column(Integer, nullable=True)

    # e.g. VIEW, LIST
    action = Column(String, nullable=False, default="VIEW")

    ip_address = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = relationship("User")
