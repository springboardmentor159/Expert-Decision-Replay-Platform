from typing import Optional, Literal

from pydantic import BaseModel, EmailStr


# Only these four roles are allowed
Role = Literal[
    "Employee",
    "Reviewer",
    "Manager",
    "Administrator",
    "HR",
]


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    role: Role
    password: str

    employee_id: str
    department: str
    designation: str
    phone_number: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[Role] = None

    employee_id: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    phone_number: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: Role

    employee_id: str
    department: str
    designation: str
    phone_number: str

    class Config:
        from_attributes = True