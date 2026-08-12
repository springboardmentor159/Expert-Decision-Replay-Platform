from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr


class Role(str, Enum):
    Employee = "Employee"
    Reviewer = "Reviewer"
    Manager = "Manager"
    Administrator = "Administrator"


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    role: Role
    employee_id: str
    department: str
    designation: str
    phone_number: str
    password: str


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    employee_id: str
    department: str
    designation: str
    phone_number: str

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None
