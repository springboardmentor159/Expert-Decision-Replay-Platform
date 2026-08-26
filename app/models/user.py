from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(String, nullable=False)
    password = Column(String, nullable=False)

    employee_id = Column(String, unique=True, nullable=True)
    department = Column(String, nullable=True)
    designation = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)

    decisions = relationship("Decision", back_populates="user")

    comments = relationship(
        "Comment",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    discussion_threads = relationship(
    "DiscussionThread",
    back_populates="creator",
)