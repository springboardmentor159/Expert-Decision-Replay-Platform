from sqlalchemy import Column, Integer, String, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.role import UserRole


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(SQLAlchemyEnum(UserRole), nullable=False)
    hashed_password = Column(String, nullable=False)

    employee_id = Column(String, unique=True, nullable=True)
    department = Column(String, nullable=True)
    designation = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)

    decisions = relationship("Decision", back_populates="creator")