from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Index,
)
from sqlalchemy.orm import relationship

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
        nullable=False,
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
        nullable=False
    )

    ip_address = Column(
        String(45),
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

    __table_args__ = (
        Index(
            "ix_access_logs_user_resource",
            "user_id",
            "resource_type",
            "resource_id"
        ),
        Index(
            "ix_access_logs_created_at",
            "created_at"
        ),
    )