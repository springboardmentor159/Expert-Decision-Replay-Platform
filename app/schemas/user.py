from typing import Optional
from enum import Enum
from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict


class UserRole(str, Enum):
    EMPLOYEE = "Employee"
    REVIEWER = "Reviewer"
    MANAGER = "Manager"
    ADMINISTRATOR = "Administrator"


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    role: UserRole
    password: str
    employee_id: str
    department: str
    designation: str
    phone_number: str


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
    employee_id: str
    department: str
    designation: str
    phone_number: str

    model_config = ConfigDict(from_attributes=True)


class DecisionCreate(BaseModel):
    title: str
    problem_statement: str
    category: str


class DecisionResponse(BaseModel):
    id: int
    title: str
    problem_statement: str
    category: str
    status: str
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)