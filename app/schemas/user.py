from typing import Optional

from pydantic import BaseModel, EmailStr


# =========================
# CREATE USER
# =========================
class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    role: str
    password: str

    employee_id: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    phone_number: Optional[str] = None


# =========================
# UPDATE USER
# =========================
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None

    employee_id: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    phone_number: Optional[str] = None


# =========================
# USER RESPONSE
# =========================
class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str

    employee_id: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    phone_number: Optional[str] = None

    class Config:
        from_attributes = True


# =========================
# LOGIN
# =========================
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# =========================
# JWT TOKEN RESPONSE
# =========================
class TokenResponse(BaseModel):
    access_token: str
    token_type: str