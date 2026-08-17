from typing import Optional
from pydantic import BaseModel, EmailStr
from app.models.enums import UserRole


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.EMPLOYEE
    employee_id: str
    department: Optional[str] = None
    designation: Optional[str] = None
    phone_number: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None
    employee_id: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    phone_number: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: UserRole
    employee_id: str
    department: Optional[str] = None
    designation: Optional[str] = None
    phone_number: Optional[str] = None

    class Config:
        from_attributes = True