from pydantic import BaseModel


class RationaleUpdate(BaseModel):
    rationale: str


class RationaleResponse(BaseModel):
    id: int
    rationale: str

    class Config:
        from_attributes = True