from sqlalchemy import Column, Integer, String, Enum
from app.core.enums import UserRole
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String, nullable=False)

    email = Column(String, unique=True, nullable=False)

    role = Column(
        Enum(UserRole, name="user_role"),
        nullable=False
    )

    password = Column(String, nullable=False)

    employee_id = Column(String, unique=True, nullable=True)

    department = Column(String, nullable=True)

    designation = Column(String, nullable=True)

    phone_number = Column(String, nullable=True)