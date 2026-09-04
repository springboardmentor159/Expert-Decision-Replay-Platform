from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String,
        unique=True,
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Users belonging to this organization
    users = relationship(
        "User",
        back_populates="organization"
    )

    # Decisions belonging to this organization
    decisions = relationship(
        "Decision",
        back_populates="organization"
    )

    # Tags belonging to this organization
    tags = relationship(
        "Tag",
        back_populates="organization"
    )
