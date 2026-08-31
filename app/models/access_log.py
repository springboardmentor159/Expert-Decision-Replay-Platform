from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class AccessLog(Base):
    __tablename__ = "access_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    resource_type = Column(String(100), nullable=True)  # Decision, Approval etc.
    resource_id = Column(Integer, nullable=True)
    action = Column(String(50), nullable=True)          # VIEW, ACCESS etc.
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="access_logs")

    __table_args__ = (
        Index("ix_access_logs_user_id", "user_id"),
        Index("ix_access_logs_resource_type", "resource_type"),
        Index("ix_access_logs_created_at", "created_at"),
    )