from datetime import datetime
from enum import Enum
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.db.base import Base


class NotificationType(str, Enum):
    APPROVAL_REQUESTED = "APPROVAL_REQUESTED"
    APPROVAL_COMPLETED = "APPROVAL_COMPLETED"
    DECISION_SUBMITTED = "DECISION_SUBMITTED"
    DECISION_STATUS_CHANGED = "DECISION_STATUS_CHANGED"
    COMMENT_ADDED = "COMMENT_ADDED"
    ESCALATION = "ESCALATION"
    SYSTEM = "SYSTEM"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    link = Column(String, nullable=True)
    notification_type = Column(
        SQLEnum(
            NotificationType,
            name="notification_type",
            values_callable=lambda enum_class: [t.value for t in enum_class],
        ),
        default=NotificationType.SYSTEM,
        nullable=False,
    )
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = relationship("User", backref="user_notifications")
