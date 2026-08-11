from typing import Optional
from enum import Enum

from pydantic import BaseModel, EmailStr


# Controlled role values — only these four are accepted
# Using Enum (from Jamuna Rani) for strong type safety in Swagger UI
class UserRole(str, Enum):
    EMPLOYEE = "Employee"
    REVIEWER = "Reviewer"
    MANAGER = "Manager"
    ADMINISTRATOR = "Administrator"


# Controlled department values
class UserDepartment(str, Enum):
    IT = "IT"
    CAC = "CAC"


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: UserRole

    employee_id: Optional[str] = None
    department: Optional[UserDepartment] = None
    designation: Optional[str] = None
    phone: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None

    employee_id: Optional[str] = None
    department: Optional[UserDepartment] = None
    designation: Optional[str] = None
    phone: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: UserRole

    employee_id: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    phone: Optional[str] = None

    # password and password_hash are intentionally excluded from this schema

    class Config:
        from_attributes = True
