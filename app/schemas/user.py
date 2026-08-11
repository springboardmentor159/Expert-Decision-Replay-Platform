from typing import Optional, Literal

from pydantic import BaseModel, EmailStr


# restrict roles to these values
RoleType = Literal["Employee", "Reviewer", "Manager", "Administrator"]


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: RoleType

    employee_id: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    phone_number: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[RoleType] = None

    employee_id: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    phone_number: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: RoleType

    employee_id: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    phone_number: Optional[str] = None

    class Config:
        from_attributes = True
