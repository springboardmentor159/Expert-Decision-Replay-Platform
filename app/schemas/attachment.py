from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.user import UserResponse


class AttachmentResponse(BaseModel):
    id: int
    decision_id: int
    filename: str
    file_size: int
    content_type: str | None = None
    uploaded_by: int | None = None
    uploader: UserResponse | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
