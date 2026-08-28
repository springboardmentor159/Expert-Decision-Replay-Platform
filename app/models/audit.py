from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class AuditAction(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    STATUS_CHANGE = "STATUS_CHANGE"
    TAG_ADDED = "TAG_ADDED"
    TAG_REMOVED = "TAG_REMOVED"
    COMMENT_ADDED = "COMMENT_ADDED"
    COMMENT_UPDATED = "COMMENT_UPDATED"
    THREAD_CREATED = "THREAD_CREATED"
    THREAD_UPDATED = "THREAD_UPDATED"
    MEETING_NOTE_CREATED = "MEETING_NOTE_CREATED"
    MEETING_NOTE_UPDATED = "MEETING_NOTE_UPDATED"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    decision_id = Column(
        Integer,
        ForeignKey("decisions.id"),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    action = Column(
        String,
        nullable=False
    )

    entity_type = Column(
        String,
        nullable=False
    )

    entity_id = Column(
        Integer,
        nullable=True
    )

    description = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    decision = relationship(
        "Decision",
        back_populates="audit_logs"
    )

    user = relationship(
        "User",
        back_populates="audit_logs"
    )