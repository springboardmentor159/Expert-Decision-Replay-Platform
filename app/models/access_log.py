from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
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
        nullable=True,
        index=True
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
            "ix_access_logs_user_created",
            "user_id",
            "created_at"
        ),
        Index(
            "ix_access_logs_resource",
            "resource_type",
            "resource_id"
        ),
    )