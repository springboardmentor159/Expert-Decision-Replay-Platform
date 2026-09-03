from pydantic import BaseModel


class TeamReportItem(BaseModel):
    team_name: str
    number_of_members: int
    total_decisions: int
    approved_decisions: int
    rejected_decisions: int
    pending_decisions: int
    approval_rate: float


class TeamReportResponse(BaseModel):
    data: list[TeamReportItem]
    page: int
    page_size: int
    total_records: int