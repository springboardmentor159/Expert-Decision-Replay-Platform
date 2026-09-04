from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
    Index,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


class SecurityLog(Base):
    __tablename__ = "security_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        index=True
    )

    event_type = Column(
        String(50),
        nullable=False,
        index=True
    )

    description = Column(
        Text,
        nullable=False
    )

    ip_address = Column(
        String(45),
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )

    user = relationship(
        "User"
    )

    __table_args__ = (
        Index(
            "ix_security_logs_created_event",
            "created_at",
            "event_type"
        ),
    )