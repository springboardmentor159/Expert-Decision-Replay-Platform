from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


# =========================================================
# Create Discussion Thread
# =========================================================


class DiscussionThreadCreate(BaseModel):
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)

    @field_validator("title", "description")
    @classmethod
    def validate_not_empty(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("This field cannot be empty")

        return value


# =========================================================
# Update Discussion Thread
# =========================================================


class DiscussionThreadUpdate(BaseModel):
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    status: str = Field(..., min_length=1)

    @field_validator("title", "description", "status")
    @classmethod
    def validate_not_empty(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("This field cannot be empty")

        return value


# =========================================================
# Discussion Thread Response
# =========================================================


class DiscussionThreadResponse(BaseModel):
    id: int
    decision_id: int
    created_by: int
    title: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)