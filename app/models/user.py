from enum import Enum

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.db.base import Base


class UserRole(str, Enum):
    EMPLOYEE = "Employee"
    REVIEWER = "Reviewer"
    MANAGER = "Manager"
    ADMINISTRATOR = "Administrator"


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
        SQLEnum(
            UserRole,
            name="user_role",
            values_callable=lambda enum_class: [
                role.value for role in enum_class
            ]
        ),
        nullable=False
    )

    password = Column(
        String,
        nullable=False
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

    organization_id = Column(
        Integer,
        ForeignKey("organizations.id"),
        nullable=True
    )

    organization = relationship(
        "Organization",
        back_populates="users"
    )

    decisions = relationship(
        "Decision",
        back_populates="user"
    )

    comments = relationship(
        "Comment",
        back_populates="user"
    )

    discussion_threads = relationship(
        "DiscussionThread",
        back_populates="user"
    )

    meeting_notes = relationship(
        "MeetingNote",
        back_populates="user"
    )

    audit_logs = relationship(
        "AuditLog",
        back_populates="user"
    )

    approvals = relationship(
        "Approval",
        back_populates="reviewer"
    )
