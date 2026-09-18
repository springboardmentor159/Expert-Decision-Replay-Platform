from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field


UserRole = Literal["Employee", "Reviewer", "Manager", "Administrator"]


class UserCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    role: UserRole
    password: str = Field(min_length=8, max_length=128)
    employee_id: str = Field(min_length=1, max_length=50)
    department: str = Field(min_length=1, max_length=100)
    designation: str = Field(min_length=1, max_length=100)
    phone_number: str = Field(min_length=7, max_length=30)


class UserRegistration(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    employee_id: str = Field(min_length=1, max_length=50)
    department: str = Field(min_length=1, max_length=100)
    designation: str = Field(min_length=1, max_length=100)
    phone_number: str = Field(min_length=7, max_length=30)


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    employee_id: Optional[str] = Field(default=None, min_length=1, max_length=50)
    department: Optional[str] = Field(default=None, min_length=1, max_length=100)
    designation: Optional[str] = Field(default=None, min_length=1, max_length=100)
    phone_number: Optional[str] = Field(default=None, min_length=7, max_length=30)


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: UserRole
    employee_id: str
    department: str
    designation: str
    phone_number: str

    class Config:
        from_attributes = True