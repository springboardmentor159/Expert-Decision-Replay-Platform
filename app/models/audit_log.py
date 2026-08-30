from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
    JSON,
    Index
)

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
        nullable=True
    )

    action = Column(
        String(50),
        nullable=False,
        index=True
    )

    entity_type = Column(
        String(50),
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
        nullable=False
    )

    ip_address = Column(
        String(100),
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

    request_method = Column(
        String(20),
        nullable=True
    )

    endpoint = Column(
        String(255),
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )


Index(
    "ix_audit_logs_user_action",
    AuditLog.user_id,
    AuditLog.action
)

Index(
    "ix_audit_logs_entity",
    AuditLog.entity_type,
    AuditLog.entity_id
)

Index(
    "ix_audit_logs_created_at",
    AuditLog.created_at
)