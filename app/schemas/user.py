from typing import Optional, Literal

from pydantic import BaseModel, EmailStr


# Controlled role values — only these four are accepted
RoleType = Literal["Employee", "Reviewer", "Manager", "Administrator"]

# Controlled department values — extend this list as new departments are onboarded
DepartmentType = Literal["IT", "CAC"]


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: RoleType

    employee_id: Optional[str] = None
    department: Optional[DepartmentType] = None
    designation: Optional[str] = None
    phone: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[RoleType] = None

    employee_id: Optional[str] = None
    department: Optional[DepartmentType] = None
    designation: Optional[str] = None
    phone: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: RoleType

    employee_id: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    phone: Optional[str] = None

    # password and password_hash are intentionally excluded from this schema

    class Config:
        from_attributes = True
