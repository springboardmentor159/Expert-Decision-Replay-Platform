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

    employee_id = Column(
        String,
        unique=True,
        nullable=False
    )

    email = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    department = Column(
        String,
        nullable=False
    )

    designation = Column(
        String,
        nullable=False
    )

    phone_number = Column(
        String,
        nullable=False
    )

    role = Column(
        String,
        nullable=False
    )

    password = Column(
        String,
        nullable=False
    )

    # =====================================================
    # One User -> Many Decisions
    # =====================================================

    decisions = relationship(
        "Decision",
        back_populates="user"
    )

    # =====================================================
    # One User -> Many Comments
    # =====================================================

    comments = relationship(
        "Comment",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # =====================================================
    # One User -> Many Discussion Threads
    # =====================================================

    discussion_threads = relationship(
        "DiscussionThread",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # =====================================================
    # One User -> Many Meeting Notes
    # =====================================================

    meeting_notes = relationship(
        "MeetingNote",
        back_populates="creator",
        cascade="all, delete-orphan"
    )

    # =====================================================
    # One User -> Many Approvals
    # =====================================================

    approvals = relationship(
        "Approval",
        back_populates="reviewer"
    )

    # =====================================================
    # One User -> Many Activity Logs
    # =====================================================

    activity_logs = relationship(
        "ActivityLog",
        back_populates="user",
        cascade="all, delete-orphan"
    )