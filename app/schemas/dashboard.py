from datetime import datetime

from pydantic import BaseModel


class DashboardActivity(BaseModel):
    id: int
    action: str
    entity_type: str
    entity_id: int | None
    description: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class DashboardResponse(BaseModel):
    role: str

    # Employee dashboard
    my_decisions: list[dict] = []
    pending_reviews: list[dict] = []
    recent_activities: list[DashboardActivity] = []

    # Manager dashboard
    team_decisions: list[dict] = []
    pending_approvals: list[dict] = []
    decision_statistics: dict = {}

    # Administrator dashboard
    system_analytics: dict = {}
    user_activity: list[dict] = []
    organization_reports: dict = {}