from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(
        String,
        unique=True,
        nullable=False
    )

    department = Column(
        String,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    members = relationship(
        "TeamMember",
        back_populates="team",
        cascade="all, delete-orphan"
    )