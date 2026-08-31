from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

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


class AuditEntityType(str, Enum):
    DECISION = "Decision"
    ALTERNATIVE = "Alternative"
    COMMENT = "Comment"
    DISCUSSION_THREAD = "DiscussionThread"
    MEETING_NOTE = "MeetingNote"
    APPROVAL = "Approval"
    USER = "User"
    TAG = "Tag"
    AUDIT_LOG = "AuditLog"
    SECURITY_LOG = "SecurityLog"
    ACCESS_LOG = "AccessLog"


class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    action: str
    entity_type: str
    entity_id: Optional[int] = None
    description: str
    ip_address: Optional[str] = None
    old_value: Optional[Dict[str, Any]] = None
    new_value: Optional[Dict[str, Any]] = None
    request_method: Optional[str] = None
    endpoint: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedAuditLogsResponse(BaseModel):
    items: List[AuditLogResponse]
    page: int
    page_size: int
    total: int
