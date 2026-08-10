from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    EMPLOYEE = "Employee"
    REVIEWER = "Reviewer"
    MANAGER = "Manager"
    ADMINISTRATOR = "Administrator"


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    role: UserRole
    employee_id: str
    department: str
    designation: str
    phone_number: str
    password: str = Field(min_length=8, max_length=72)


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    employee_id: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    phone_number: Optional[str] = None
    password: Optional[str] = Field(default=None, min_length=8, max_length=72)


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


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"