from enum import Enum

from sqlalchemy import Column, Integer, String
from sqlalchemy import Enum as SQLEnum

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