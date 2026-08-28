from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class UserCreate(BaseModel):
    full_name: str = Field(
        min_length=1
    )

    email: EmailStr

    password: str = Field(
        min_length=8
    )

    # Only predefined organizational roles are allowed
    role: UserRole

    # Professional profile information
    employee_id: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    phone_number: Optional[str] = None

    # Organization to which the user belongs
    organization_id: int


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(
        default=None,
        min_length=1
    )

    email: Optional[EmailStr] = None

    password: Optional[str] = Field(
        default=None,
        min_length=8
    )

    # Only predefined organizational roles are allowed
    role: Optional[UserRole] = None

    # Professional profile information
    employee_id: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    phone_number: Optional[str] = None

    # Organization can be changed only through authorized logic
    organization_id: Optional[int] = None


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: UserRole

    employee_id: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    phone_number: Optional[str] = None

    organization_id: Optional[int] = None

    model_config = ConfigDict(
        from_attributes=True
    )