from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr


class Role(str, Enum):
    """Enum for User role values"""
    Employee = "Employee"
    Reviewer = "Reviewer"
    Manager = "Manager"
    Administrator = "Administrator"


class UserCreate(BaseModel):
    """Schema for creating a new user"""
    full_name: str
    email: EmailStr
    role: Role
    employee_id: str
    department: str
    designation: str
    phone_number: str
    password: str


class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    full_name: str
    email: EmailStr
    role: str
    employee_id: str
    department: str
    designation: str
    phone_number: str

    model_config = ConfigDict(from_attributes=True)


class TokenData(BaseModel):
    """Schema for token data"""
    email: str | None = None


class Token(BaseModel):
    """Schema for token response"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None
