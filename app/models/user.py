from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String, nullable=False)

    email = Column(
        String,
        unique=True,
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

    employee_id = Column(
        String,
        unique=True,
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
        back_populates="user",
        cascade="all, delete-orphan"
    )

    thread_replies = relationship(
        "ThreadReply",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    meeting_notes = relationship(
        "MeetingNote",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    decision_rationales = relationship(
        "DecisionRationale",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    activities = relationship(
        "Activity",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    audit_logs = relationship(
        "AuditLog",
        back_populates="user"
    )

    decision_versions = relationship(
        "DecisionVersion",
        back_populates="user"
    )

    approvals = relationship(
        "Approval",
        back_populates="reviewer"
    )

    team_memberships = relationship(
        "TeamMember",
        back_populates="user",
        cascade="all, delete-orphan"
    )