from enum import Enum


class UserRole(str, Enum):
    EMPLOYEE = "Employee"
    REVIEWER = "Reviewer"
    MANAGER = "Manager"
    ADMINISTRATOR = "Administrator"


class DecisionStatus(str, Enum):
    DRAFT = "Draft"
    UNDER_REVIEW = "Under Review"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    ARCHIVED = "Archived"


class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class AuditAction(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    STATUS_CHANGE = "status_change"
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    ACCESS = "access"
    EXPORT = "export"
    APPROVE = "approve"
    REJECT = "reject"


class AuditEntityType(str, Enum):
    DECISION = "decision"
    ALTERNATIVE = "alternative"
    COMMENT = "comment"
    DISCUSSION_THREAD = "discussion_thread"
    MEETING_NOTE = "meeting_note"
    USER = "user"
    AUTH = "auth"
    SYSTEM = "system"


class SecurityEventType(str, Enum):
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGED = "password_changed"
    ROLE_CHANGED = "role_changed"
    TOKEN_REFRESHED = "token_refreshed"
    ACCOUNT_LOCKED = "account_locked"
    UNAUTHORIZED_ACCESS = "unauthorized_access"


class AccessMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
