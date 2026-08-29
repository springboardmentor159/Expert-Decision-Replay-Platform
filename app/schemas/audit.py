from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    id: int
    decision_id: int | None = None
    user_id: int
    action: str
    entity_type: str
    entity_id: int | None = None
    description: str
    old_value: str | None = None
    new_value: str | None = None
    ip_address: str | None = None
    request_method: str | None = None
    endpoint: str | None = None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class AuditLogListResponse(BaseModel):
    items: list[AuditLogResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

    model_config = ConfigDict(
        from_attributes=True
    )


class TimelineResponse(BaseModel):
    id: int | None = None
    action: str
    entity_type: str
    entity_id: int | None = None
    description: str
    user_id: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class DecisionVersionResponse(BaseModel):
    id: int
    decision_id: int
    version_number: int
    title: str
    problem_statement: str
    rationale: str | None = None
    category: str
    status: str
    created_by: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class SecurityLogResponse(BaseModel):
    id: int
    user_id: int | None = None
    email: str | None = None
    event_type: str
    description: str
    ip_address: str | None = None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class SecurityLogListResponse(BaseModel):
    items: list[SecurityLogResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

    model_config = ConfigDict(
        from_attributes=True
    )


class AccessLogResponse(BaseModel):
    id: int
    user_id: int
    resource_type: str
    resource_id: int | None = None
    action: str
    ip_address: str | None = None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class AccessLogListResponse(BaseModel):
    items: list[AccessLogResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

    model_config = ConfigDict(
        from_attributes=True
    )