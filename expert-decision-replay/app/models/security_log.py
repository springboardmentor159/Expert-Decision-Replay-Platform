from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


class SecurityLog(Base):
    __tablename__ = "security_logs"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    event_type = Column(
        String,
        nullable=False
    )

    description = Column(
        String,
        nullable=False
    )

    ip_address = Column(
        String,
        nullable=True
    )

    request_method = Column(
        String,
        nullable=True
    )

    endpoint = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="security_logs"
    )