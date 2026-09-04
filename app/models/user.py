from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    full_name = Column(
        String,
        nullable=False
    )

    email = Column(
        String,
        unique=True,
        nullable=False
    )

    role = Column(
        String,
        nullable=False
    )

    hashed_password = Column(
        String,
        nullable=True
    )

    employee_id = Column(
        String,
        unique=True,
        nullable=True
    )

    department = Column(
        String,
        nullable=True
    )

    designation = Column(
        String,
        nullable=True
    )

    phone_number = Column(
        String,
        nullable=True
    )

    decisions = relationship(
        "Decision",
        back_populates="user"
    )

    comments = relationship(
        "Comment",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    approvals = relationship(
        "Approval",
        foreign_keys="Approval.assigned_to"
    )

    activity_logs = relationship(
        "ActivityLog",
        foreign_keys="ActivityLog.user_id"
    )

    teams = relationship(
        "Team",
        secondary="team_members",
        back_populates="members"
    )