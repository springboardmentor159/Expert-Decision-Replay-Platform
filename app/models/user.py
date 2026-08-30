from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship

from app.core.enums import UserRole
from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String, nullable=False)

    email = Column(String, unique=True, nullable=False)

    role = Column(
        Enum(UserRole, name="user_role"),
        nullable=False
    )

    password = Column(String, nullable=False)

    employee_id = Column(String, unique=True, nullable=True)

    department = Column(String, nullable=True)

    designation = Column(String, nullable=True)

    phone_number = Column(String, nullable=True)

    decisions = relationship(
        "Decision",
        back_populates="creator"
    )

    comments = relationship(
        "Comment",
        back_populates="user"
    )

    meeting_notes = relationship(
        "MeetingNote",
        back_populates="creator"
    )

    expert_evaluations = relationship(
        "ExpertEvaluation",
        back_populates="expert"
    )
    activity_logs = relationship(
        "ActivityLog",
        back_populates="user",
        cascade="all, delete-orphan"
    )