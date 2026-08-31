from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    action: str
    entity_type: str
    entity_id: Optional[int]
    description: str
    old_value: Optional[str]
    new_value: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class DecisionVersionResponse(BaseModel):
    id: int
    decision_id: int
    version_number: int
    title: str
    problem_statement: str
    category: str
    rationale: Optional[str]
    status: str
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True


class SecurityLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    event_type: str
    description: str
    ip_address: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AccessLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    resource_type: str
    resource_id: Optional[int]
    action: str
    ip_address: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True