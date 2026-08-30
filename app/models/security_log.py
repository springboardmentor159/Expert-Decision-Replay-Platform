from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
    Index
)

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
        nullable=True
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
        String(100),
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )


Index(
    "ix_security_logs_user_event",
    SecurityLog.user_id,
    SecurityLog.event_type
)