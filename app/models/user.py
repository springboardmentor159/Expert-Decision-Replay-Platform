from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    role = Column(String, nullable=False, default="Employee")  # Employee/Reviewer/Manager/Administrator
    password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())