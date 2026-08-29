from pydantic import BaseModel


class EmployeeDashboardResponse(BaseModel):
    total_decisions: int
    draft_decisions: int
    under_review: int
    approved_decisions: int
    rejected_decisions: int
    archived_decisions: int
    pending_reviews: int


class ManagerDashboardResponse(BaseModel):
    team_decisions: int
    pending_approvals: int
    approved_decisions: int
    rejected_decisions: int
    under_review: int
    draft_decisions: int


class AdminDashboardResponse(BaseModel):
    total_users: int
    total_decisions: int
    approved_decisions: int
    rejected_decisions: int
    under_review: int
    pending_approvals: int