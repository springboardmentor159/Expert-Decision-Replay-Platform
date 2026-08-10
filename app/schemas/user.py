from pydantic import BaseModel, EmailStr
from typing import Optional

from app.core.enums import UserRole


# CREATE USER
class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    role: UserRole
    password: str

    employee_id: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    phone_number: Optional[str] = None


# UPDATE USER
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None

    employee_id: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    phone_number: Optional[str] = None


# RESPONSE
class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: UserRole

    employee_id: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    phone_number: Optional[str] = None

    class Config:
        from_attributes = True