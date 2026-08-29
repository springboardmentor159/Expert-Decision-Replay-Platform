from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class AuditAction(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    SUBMIT = "SUBMIT"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    ACCESS = "ACCESS"


class AuditEntity(str, Enum):
    Decision = "Decision"
    Alternative = "Alternative"
    Comment = "Comment"
    DiscussionThread = "DiscussionThread"
    MeetingNote = "MeetingNote"
    Approval = "Approval"
    User = "User"


class AuditResponse(BaseModel):
    id: int
    user_id: int | None
    action: str
    entity_type: str
    entity_id: int | None
    description: str
    old_value: dict | None
    new_value: dict | None
    request_method: str | None
    endpoint: str | None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class DecisionVersionResponse(BaseModel):
    id: int
    decision_id: int
    version_number: int
    title: str
    problem_statement: str
    rationale: str | None
    category: str
    status: str
    created_by: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PaginatedAuditResponse(BaseModel):
    items: list[AuditResponse]
    page: int
    page_size: int
    total: int


class SecurityResponse(BaseModel):
    id: int
    user_id: int | None
    event_type: str
    description: str
    ip_address: str | None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AccessResponse(BaseModel):
    id: int
    user_id: int | None
    resource_type: str
    resource_id: int | None
    action: str
    ip_address: str | None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)