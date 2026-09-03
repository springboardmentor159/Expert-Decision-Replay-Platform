from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.db.base import Base


class TeamMember(Base):
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True)

    team_id = Column(
        Integer,
        ForeignKey("teams.id"),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    joined_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    team = relationship(
        "Team",
        back_populates="members"
    )

    user = relationship(
        "User",
        back_populates="team_memberships"
    )