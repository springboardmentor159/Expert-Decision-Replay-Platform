from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
    JSON,
    Index,
)
from sqlalchemy.orm import relationship

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
        nullable=False,
        index=True
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

    old_value = Column(
        JSON,
        nullable=True
    )

    new_value = Column(
        JSON,
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

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )

    user = relationship(
        "User",
        back_populates="audit_logs"
    )

    __table_args__ = (
        Index(
            "ix_audit_logs_user_entity",
            "user_id",
            "entity_type",
            "entity_id"
        ),
        Index(
            "ix_audit_logs_created_action",
            "created_at",
            "action"
        ),
    )