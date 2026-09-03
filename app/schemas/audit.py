from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditResponse(BaseModel):
    id: int
    user_id: int | None
    action: str
    entity_type: str
    entity_id: int | None
    description: str
    old_value: dict | None = None
    new_value: dict | None = None
    ip_address: str | None = None
    request_method: str | None = None
    endpoint: str | None = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class VersionResponse(BaseModel):
    id: int
    decision_id: int
    version_number: int
    title: str
    problem_statement: str
    category: str
    status: str
    rationale: str | None = None
    created_by: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
