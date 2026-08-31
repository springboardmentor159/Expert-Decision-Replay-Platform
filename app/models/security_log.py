from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class SecurityLog(Base):
    __tablename__ = "security_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    event_type = Column(String(50), nullable=False)   # LOGIN_SUCCESS, LOGIN_FAILED etc.
    description = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)        # for failed logins where user_id is unknown
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="security_logs")

    __table_args__ = (
        Index("ix_security_logs_user_id", "user_id"),
        Index("ix_security_logs_event_type", "event_type"),
        Index("ix_security_logs_created_at", "created_at"),
    )