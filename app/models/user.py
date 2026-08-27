from sqlalchemy import (
    Column,
    Integer,
    String
)
from sqlalchemy.orm import relationship

from app.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    full_name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(150),
        unique=True,
        index=True,
        nullable=False
    )

    hashed_password = Column(
        String(255),
        nullable=False
    )

    role = Column(
        String(50),
        default="Employee"
    )

    employee_id = Column(
        String(50),
        unique=True,
        nullable=True
    )

    department = Column(
        String(100),
        nullable=True
    )

    designation = Column(
        String(100),
        nullable=True
    )

    phone_number = Column(
        String(20),
        nullable=True
    )

    decisions = relationship(
        "Decision",
        back_populates="creator"
    )