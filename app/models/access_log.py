from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Index
)

from app.db.base import Base


class AccessLog(Base):
    __tablename__ = "access_logs"

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

    resource_type = Column(
        String(50),
        nullable=False,
        index=True
    )

    resource_id = Column(
        Integer,
        nullable=True,
        index=True
    )

    action = Column(
        String(50),
        nullable=False,
        index=True
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
    "ix_access_logs_resource",
    AccessLog.resource_type,
    AccessLog.resource_id
)

Index(
    "ix_access_logs_created_at",
    AccessLog.created_at
)