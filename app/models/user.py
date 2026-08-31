from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    role = Column(String, nullable=False)
    employee_id = Column(String, nullable=True, unique=True, index=True)
    department = Column(String, nullable=True)
    designation = Column(String, nullable=True)
    phone_number = Column(String(20), nullable=True)
    password = Column(String, nullable=False)

    decisions = relationship(
        "Decision",
        back_populates="creator"
    )
    comments = relationship(
        "Comment",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    discussion_threads = relationship(
        "DiscussionThread",
        back_populates="creator",
        cascade="all, delete-orphan"
    )
    decision_versions = relationship(
        "DecisionVersion",
        back_populates="user"
    )
    meeting_notes = relationship(
        "MeetingNote",
        back_populates="creator",
        cascade="all, delete-orphan"
    )
    activity_logs = relationship(
        "ActivityLog",
        back_populates="user"
    )
    audit_logs = relationship(
        "AuditLog",
        back_populates="user"
    )
    security_logs = relationship(
        "SecurityLog",
        back_populates="user"
    )
    access_logs = relationship(
        "AccessLog",
        back_populates="user"
    )