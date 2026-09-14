from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AttachmentResponse(BaseModel):
    id: int
    decision_id: int
    uploaded_by: int
    original_filename: str
    stored_filename: str
    file_path: str
    content_type: str | None
    file_size: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)