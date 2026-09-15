from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentCreate(BaseModel):
    file_name: str
    file_path: str
    document_type: str | None = None
    description: str | None = None


class DocumentResponse(BaseModel):
    id: int
    decision_id: int
    uploaded_by: int
    file_name: str
    file_path: str
    document_type: str | None
    description: str | None
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)