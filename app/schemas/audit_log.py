from enum import Enum
from datetime import datetime
from typing import Optional

from pydantic import BaseModel



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

class AuditLogResponse(BaseModel):
    id: int
    user_id: int
    action: str
    entity_type: str
    entity_id: int
    description: str
    ip_address: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    request_method: Optional[str] = None
    endpoint: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True