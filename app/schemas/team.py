from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.user import UserResponse


class TeamBase(BaseModel):
    name: str
    description: str | None = None
    lead_id: int | None = None


class TeamCreate(TeamBase):
    organization_id: int | None = None


class TeamUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    lead_id: int | None = None


class TeamMemberAdd(BaseModel):
    user_id: int


class TeamResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    organization_id: int
    lead_id: int | None = None
    lead: UserResponse | None = None
    members: list[UserResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
