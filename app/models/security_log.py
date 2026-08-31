from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
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
        nullable=True
    )

    ip_address = Column(
        String(45),
        nullable=True
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True
    )

    __table_args__ = (
        Index(
            "ix_security_logs_user_created",
            "user_id",
            "created_at"
        ),
        Index(
            "ix_security_logs_event_created",
            "event_type",
            "created_at"
        ),
    )