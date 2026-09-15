from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Team(Base):
    __tablename__ = "teams"

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
        String,
        nullable=True
    )

    department = Column(
        String,
        nullable=False
    )

    team_lead_id = Column(
        Integer,
        nullable=True
    )

    status = Column(
        String,
        nullable=False,
        default="Active"
    )

    # =====================================================
    # One Team -> Many Users
    # =====================================================

    members = relationship(
        "User",
        primaryjoin="Team.id == foreign(User.team_id)",
        back_populates="team"
    )