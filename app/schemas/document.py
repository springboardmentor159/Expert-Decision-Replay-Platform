from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    id: int
    decision_id: int
    uploaded_by: int
    original_filename: str
    content_type: str
    file_size: int
    created_at: datetime
    download_url: str

    model_config = ConfigDict(from_attributes=True)