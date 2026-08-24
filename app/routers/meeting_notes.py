from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user
from app.models.decision import Decision
from app.models.meeting_note import MeetingNote
from app.schemas.meeting_note import (
    MeetingNoteCreate,
    MeetingNoteUpdate,
    MeetingNoteResponse
)


router = APIRouter(
    tags=["Meeting Notes"]
)


@router.post(
    "/decisions/{decision_id}/meeting-notes",
    response_model=MeetingNoteResponse,
    status_code=status.HTTP_201_CREATED
)
def create_meeting_note(
    decision_id: int,
    note_data: MeetingNoteCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if decision is None:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    note = MeetingNote(
        decision_id=decision_id,
        created_by=int(current_user["sub"]),
        title=note_data.title,
        content=note_data.content,
        meeting_date=note_data.meeting_date
    )

    db.add(note)
    db.commit()
    db.refresh(note)

    return note


@router.get(
    "/decisions/{decision_id}/meeting-notes",
    response_model=list[MeetingNoteResponse]
)
def get_meeting_notes(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if decision is None:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    return db.query(MeetingNote).filter(
        MeetingNote.decision_id == decision_id
    ).all()


@router.get(
    "/meeting-notes/{note_id}",
    response_model=MeetingNoteResponse
)
def get_meeting_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    note = db.query(MeetingNote).filter(
        MeetingNote.id == note_id
    ).first()

    if note is None:
        raise HTTPException(
            status_code=404,
            detail="Meeting note not found"
        )

    return note


@router.put(
    "/meeting-notes/{note_id}",
    response_model=MeetingNoteResponse
)
def update_meeting_note(
    note_id: int,
    note_data: MeetingNoteUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    note = db.query(MeetingNote).filter(
        MeetingNote.id == note_id
    ).first()

    if note is None:
        raise HTTPException(
            status_code=404,
            detail="Meeting note not found"
        )

    if note.created_by != int(current_user["sub"]):
        raise HTTPException(
            status_code=403,
            detail="You can only update your own meeting note"
        )

    note.title = note_data.title
    note.content = note_data.content
    note.meeting_date = note_data.meeting_date

    db.commit()
    db.refresh(note)

    return note


@router.delete("/meeting-notes/{note_id}")
def delete_meeting_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    note = db.query(MeetingNote).filter(
        MeetingNote.id == note_id
    ).first()

    if note is None:
        raise HTTPException(
            status_code=404,
            detail="Meeting note not found"
        )

    if note.created_by != int(current_user["sub"]):
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own meeting note"
        )

    db.delete(note)
    db.commit()

    return {
        "message": "Meeting note deleted successfully"
    }