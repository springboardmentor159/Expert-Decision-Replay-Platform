from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


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
    department: Optional[str] = None
    designation: Optional[str] = None
    phone_number: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    password: Optional[str] = None
    employee_id: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    phone_number: Optional[str] = None


from typing import Optional, Union

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: Union[UserRole, str]
    employee_id: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    phone_number: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Optional[UserResponse] = None