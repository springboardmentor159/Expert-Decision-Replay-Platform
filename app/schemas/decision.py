from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.decision import DecisionStatus, ImplementationStatus


class DecisionCreate(BaseModel):
    title: str
    problem_statement: str
    category: str
    evaluation_criteria: str | None = None
    rationale: str | None = None


class DecisionUpdate(BaseModel):
    title: str
    problem_statement: str
    category: str
    evaluation_criteria: str | None = None


class DecisionRationaleUpdate(BaseModel):
    rationale: str


class DecisionCriteriaUpdate(BaseModel):
    evaluation_criteria: str


class DecisionImplementationUpdate(BaseModel):
    implementation_status: ImplementationStatus


class DecisionOutcomesUpdate(BaseModel):
    final_outcomes: str


class DecisionStatusUpdate(BaseModel):
    status: DecisionStatus


class DecisionResponse(BaseModel):
    id: int
    title: str
    problem_statement: str
    rationale: str | None = None
    evaluation_criteria: str | None = None
    final_outcomes: str | None = None
    category: str
    status: DecisionStatus
    implementation_status: ImplementationStatus = ImplementationStatus.NOT_STARTED
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )



class DecisionListResponse(BaseModel):
    items: list[DecisionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

    model_config = ConfigDict(
        from_attributes=True
    )


class DecisionSearchResult(BaseModel):
    id: int
    title: str
    problem_statement: str | None = None
    category: str
    status: str
    tags: list[str] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class DecisionSearchResponse(BaseModel):
    results: list[DecisionSearchResult]
    total: int
    page: int
    page_size: int
    total_pages: int


class DecisionHistoryItem(BaseModel):
    id: int
    action: str
    entity_type: str
    entity_id: int | None
    description: str
    user_id: int
    old_value: str | None = None
    new_value: str | None = None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )