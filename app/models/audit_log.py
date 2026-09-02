from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # Kept for backward compatibility with the existing
    # GET /decisions/{decision_id}/audit-logs endpoint.
    decision_id = Column(
        Integer,
        ForeignKey("decisions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    action = Column(
        String(100),
        nullable=False,
        index=True,
    )

    entity_type = Column(
        String(100),
        nullable=False,
        index=True,
    )

    entity_id = Column(
        Integer,
        nullable=False,
        index=True,
    )

    description = Column(
        Text,
        nullable=False,
    )

    ip_address = Column(
        String(45),
        nullable=True,
    )

    old_value = Column(
        JSONB,
        nullable=True,
    )

    new_value = Column(
        JSONB,
        nullable=True,
    )

    request_method = Column(
        String(10),
        nullable=True,
    )

    endpoint = Column(
        String(255),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    decision = relationship("Decision")
    user = relationship("User")