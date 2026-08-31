from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    employee_id = Column(String, unique=True, nullable=True, index=True)
    department = Column(String, nullable=True)
    designation = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)

    decisions = relationship("Decision", back_populates="creator")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    threads = relationship("DiscussionThread", back_populates="creator", cascade="all, delete-orphan")
    meeting_notes = relationship("MeetingNote", back_populates="creator", cascade="all, delete-orphan")
    approvals_assigned = relationship("Approval", back_populates="reviewer", cascade="all, delete-orphan")
    activities = relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
