from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class DecisionVersionResponse(BaseModel):
    id: int
    decision_id: int
    version_number: int
    title: str
    problem_statement: str
    description: Optional[str] = None
    category: str
    status: str
    created_by: int
    created_by_name: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DecisionHistoryItem(BaseModel):
    id: Optional[int] = None
    timestamp: datetime
    action: str
    entity_type: str
    entity_id: Optional[int] = None
    description: str
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    old_value: Optional[Dict[str, Any]] = None
    new_value: Optional[Dict[str, Any]] = None


class DecisionHistoryResponse(BaseModel):
    decision_id: int
    decision_title: str
    total_events: int
    history: List[DecisionHistoryItem]
