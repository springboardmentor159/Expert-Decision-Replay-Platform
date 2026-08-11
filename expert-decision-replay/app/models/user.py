from sqlalchemy import Column, Integer, String
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    employee_id = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    department = Column(String, nullable=False)
    designation = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    role = Column(String, nullable=False)
    password = Column(String, nullable=False)