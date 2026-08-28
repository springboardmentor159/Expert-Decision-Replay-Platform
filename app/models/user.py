from sqlalchemy import Column, Integer, String
from app.db.base import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String, nullable=False)

    email = Column(String, unique=True, nullable=False)

    role = Column(String, nullable=False)

    password = Column(String, nullable=False)

    employee_id = Column(String, unique=True, nullable=False)

    department = Column(String, nullable=False)

    designation = Column(String, nullable=False)

    phone_number = Column(String, nullable=False)

    decisions = relationship(
    "Decision",
    back_populates="user"
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