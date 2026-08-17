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
