from pydantic import BaseModel
from typing import Optional


class TeamCreate(BaseModel):
    name: str
    description: Optional[str] = None
    department: str
    team_lead_id: Optional[int] = None
    status: str = "Active"


class TeamResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    department: str
    team_lead_id: Optional[int] = None
    status: str

    class Config:
        from_attributes = True