from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr


class UserRole(str, Enum):
    EMPLOYEE = "Employee"
    REVIEWER = "Reviewer"
    MANAGER = "Manager"
    ADMINISTRATOR = "Administrator"


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: UserRole

    employee_id: str | None = None
    department: str | None = None
    designation: str | None = None
    phone_number: str | None = None


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: UserRole

    employee_id: str | None = None
    department: str | None = None
    designation: str | None = None
    phone_number: str | None = None

    model_config = ConfigDict(from_attributes=True)