from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.decision import Decision
from app.models.meeting_note import MeetingNote
from app.models.user import User


router = APIRouter(
    prefix="/decisions",
    tags=["Meeting Notes"]
)


class MeetingNoteCreate(BaseModel):
    content: str


class MeetingNoteResponse(BaseModel):
    id: int
    decision_id: int
    user_id: int
    content: str

    class Config:
        from_attributes = True


@router.post(
    "/{decision_id}/meeting-notes",
    response_model=MeetingNoteResponse,
    status_code=status.HTTP_201_CREATED
)
def create_meeting_note(
    decision_id: int,
    note_data: MeetingNoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    note = MeetingNote(
        decision_id=decision_id,
        user_id=current_user.id,
        content=note_data.content
    )

    db.add(note)
    db.commit()
    db.refresh(note)

    return note


@router.get(
    "/{decision_id}/meeting-notes",
    response_model=list[MeetingNoteResponse]
)
def get_meeting_notes(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    return db.query(MeetingNote).filter(
        MeetingNote.decision_id == decision_id
    ).all()