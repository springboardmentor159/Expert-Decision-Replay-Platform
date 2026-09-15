from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models.role import UserRole


class UserCreate(BaseModel):
    """
    Used by authorized administrators to create users.
    Role is allowed here because this is not the public registration endpoint.
    """
    full_name: str
    email: EmailStr
    role: UserRole
    password: str = Field(min_length=6)
    employee_id: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    phone_number: Optional[str] = None


class UserRegister(BaseModel):
    """
    Public registration schema.

    Public users cannot choose their role.
    Every account created through /auth/register is an Employee.
    """
    full_name: str
    email: EmailStr
    password: str = Field(min_length=6)
    employee_id: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    phone_number: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
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
    employee_id: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    phone_number: Optional[str] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str