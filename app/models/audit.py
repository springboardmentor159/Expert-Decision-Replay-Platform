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
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    SUBMIT = "SUBMIT"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    ACCESS = "ACCESS"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    decision_id = Column(
        Integer,
        ForeignKey("decisions.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    action = Column(
        String,
        nullable=False,
        index=True
    )

    entity_type = Column(
        String,
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
        Text,
        nullable=True
    )

    new_value = Column(
        Text,
        nullable=True
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
        nullable=False,
        index=True
    )

    decision = relationship(
        "Decision",
        back_populates="audit_logs"
    )

    user = relationship(
        "User",
        back_populates="audit_logs"
    )


class DecisionVersion(Base):
    __tablename__ = "decision_versions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    decision_id = Column(
        Integer,
        ForeignKey("decisions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    version_number = Column(
        Integer,
        nullable=False,
        index=True
    )

    title = Column(
        String,
        nullable=False
    )

    problem_statement = Column(
        Text,
        nullable=False
    )

    rationale = Column(
        Text,
        nullable=True
    )

    category = Column(
        String,
        nullable=False
    )

    status = Column(
        String,
        nullable=False
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )

    decision = relationship(
        "Decision",
        back_populates="versions"
    )

    user = relationship(
        "User"
    )


class SecurityLog(Base):
    __tablename__ = "security_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    email = Column(
        String,
        nullable=True,
        index=True
    )

    event_type = Column(
        String,
        nullable=False,
        index=True
    )

    description = Column(
        Text,
        nullable=False
    )

    ip_address = Column(
        String,
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


class AccessLog(Base):
    __tablename__ = "access_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    resource_type = Column(
        String,
        nullable=False,
        index=True
    )

    resource_id = Column(
        Integer,
        nullable=True,
        index=True
    )

    action = Column(
        String,
        nullable=False
    )

    ip_address = Column(
        String,
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