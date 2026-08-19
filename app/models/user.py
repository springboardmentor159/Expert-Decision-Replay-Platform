from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    role = Column(String(50), nullable=False)
    password = Column(String(255), nullable=False)

    employee_id = Column(String(50), unique=True, nullable=False)
    department = Column(String(100), nullable=False)
    designation = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=False)

    decisions = relationship(
        "Decision",
        back_populates="creator",
        cascade="all, delete-orphan"
    )