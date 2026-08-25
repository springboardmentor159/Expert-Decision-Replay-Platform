from sqlalchemy import Column, DateTime, Integer, String, Enum as SqlAlchemyEnum, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from app.models.enums import UserRole


class User(Base):
    __tablename__ = "users"

    __table_args__ = (
        CheckConstraint(
            "role IN ('Employee', 'Reviewer', 'Manager', 'Administrator')",
            name="check_valid_role"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    role = Column(
        SqlAlchemyEnum(UserRole, name="userrole", native_enum=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=UserRole.EMPLOYEE,
    )
    password = Column(String, nullable=False)
    employee_id = Column(String, unique=True, nullable=False)
    department = Column(String, nullable=True)
    designation = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    decisions = relationship("Decision", back_populates="creator", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    threads = relationship("DiscussionThread", back_populates="creator", cascade="all, delete-orphan")
