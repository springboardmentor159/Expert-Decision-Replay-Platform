from sqlalchemy import Column, Integer, String

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(String, nullable=False)
    password = Column(String, nullable=False)

    employee_id = Column(String, unique=True, index=True, nullable=True)
    department = Column(String, nullable=True)
    designation = Column(String, nullable=True)
    phone_number = Column(String(20), nullable=True)