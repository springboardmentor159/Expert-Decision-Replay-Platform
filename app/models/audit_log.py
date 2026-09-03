from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text

from app.db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

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

    action = Column(
        String(50),
        nullable=False,
        index=True
    )

    entity_type = Column(
        String(100),
        nullable=False,
        index=True
    )

    entity_id = Column(
        Integer,
        nullable=True,
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

    request_method = Column(
        String(10),
        nullable=True
    )

    endpoint = Column(
        String(255),
        nullable=True
    )

    old_value = Column(
        JSON,
        nullable=True
    )

    new_value = Column(
        JSON,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )