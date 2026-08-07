from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    role: str


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str

    model_config = {"from_attributes": True}
