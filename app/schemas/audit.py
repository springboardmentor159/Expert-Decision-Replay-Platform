from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any
from enum import Enum


class AuditAction(str, Enum):
    """Controlled action vocabulary - never accept a free-text action."""
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    SUBMIT = "SUBMIT"
    ARCHIVE = "ARCHIVE"
    ASSIGN = "ASSIGN"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    ACCESS = "ACCESS"


class EntityType(str, Enum):
    """Controlled entity-type vocabulary."""
    DECISION = "Decision"
    ALTERNATIVE = "Alternative"
    COMMENT = "Comment"
    DISCUSSION_THREAD = "DiscussionThread"
    MEETING_NOTE = "MeetingNote"
    APPROVAL = "Approval"
    USER = "User"
    AUDIT_LOG = "AuditLog"


class AuditLogResponse(BaseModel):
    id: int
    user_id: int
    action: str
    entity_type: str
    entity_id: int
    description: str
    old_value: Optional[dict[str, Any]] = None
    new_value: Optional[dict[str, Any]] = None
    request_method: Optional[str] = None
    endpoint: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedAuditLogs(BaseModel):
    items: list[AuditLogResponse]
    page: int
    page_size: int
    total: int


class SecurityLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    identifier: Optional[str] = None
    event_type: str
    description: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedSecurityLogs(BaseModel):
    items: list[SecurityLogResponse]
    page: int
    page_size: int
    total: int


class AccessLogResponse(BaseModel):
    id: int
    user_id: int
    resource_type: str
    resource_id: Optional[int] = None
    action: str
    ip_address: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedAccessLogs(BaseModel):
    items: list[AccessLogResponse]
    page: int
    page_size: int
    total: int
