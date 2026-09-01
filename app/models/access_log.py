from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


class AccessLog(Base):
    __tablename__ = "access_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )

    resource_type = Column(
        String(50),
        nullable=False,
    )

    resource_id = Column(
        Integer,
        nullable=True,
    )

    action = Column(
        String(30),
        nullable=False,
    )

    ip_address = Column(
        String(45),
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="access_logs",
    )

    __table_args__ = (
        Index("ix_access_logs_user_id", "user_id"),
        Index("ix_access_logs_resource_type", "resource_type"),
        Index("ix_access_logs_resource_id", "resource_id"),
        Index("ix_access_logs_action", "action"),
        Index("ix_access_logs_created_at", "created_at"),
    )