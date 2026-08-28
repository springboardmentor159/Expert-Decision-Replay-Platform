from pydantic import BaseModel


class DecisionAnalyticsResponse(BaseModel):
    total_decisions: int

    draft_decisions: int
    under_review: int
    approved_decisions: int
    rejected_decisions: int
    archived_decisions: int

    total_approvals: int
    pending_approvals: int
    approved_approvals: int
    rejected_approvals: int