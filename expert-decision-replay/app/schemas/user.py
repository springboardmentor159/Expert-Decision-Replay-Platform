from enum import Enum

from pydantic import BaseModel, EmailStr, ConfigDict


class UserRole(str, Enum):
    EMPLOYEE = "Employee"
    REVIEWER = "Reviewer"
    MANAGER = "Manager"
    ADMINISTRATOR = "Administrator"


class UserCreate(BaseModel):
    full_name: str
    employee_id: str
    email: EmailStr
    department: str
    designation: str
    phone_number: str
    password: str
    role: UserRole = UserRole.EMPLOYEE


class UserResponse(BaseModel):
    id: int
    full_name: str
    employee_id: str
    email: EmailStr
    department: str
    designation: str
    phone_number: str
    role: UserRole

    model_config = ConfigDict(from_attributes=True)