from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.decision import Decision
from app.models.meeting_note import MeetingNote
from app.models.user import User
from app.schemas.meeting_note import (
    MeetingNoteCreate,
    MeetingNoteUpdate,
    MeetingNoteResponse,
)
from app.utils.security import get_current_user


router = APIRouter(tags=["Meeting Notes"])


def get_decision_or_404(decision_id: int, db: Session) -> Decision:
    decision = db.query(Decision).filter(Decision.id == decision_id).first()

    if decision is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    return decision


def get_meeting_note_or_404(note_id: int, db: Session) -> MeetingNote:
    note = db.query(MeetingNote).filter(MeetingNote.id == note_id).first()

    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting note not found"
        )

    return note


def ensure_owner(note: MeetingNote, current_user: User) -> None:
    if note.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this meeting note"
        )


# CREATE MEETING NOTE
@router.post(
    "/decisions/{decision_id}/meeting-notes",
    response_model=MeetingNoteResponse,
    status_code=status.HTTP_201_CREATED
)
def create_meeting_note(
    decision_id: int,
    note: MeetingNoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_decision_or_404(decision_id, db)

    new_note = MeetingNote(
        decision_id=decision_id,
        created_by=current_user.id,
        title=note.title,
        content=note.content,
        meeting_date=note.meeting_date
    )

    db.add(new_note)
    db.commit()
    db.refresh(new_note)

    return new_note


# GET ALL MEETING NOTES FOR A DECISION
@router.get(
    "/decisions/{decision_id}/meeting-notes",
    response_model=list[MeetingNoteResponse]
)
def get_meeting_notes(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_decision_or_404(decision_id, db)

    return (
        db.query(MeetingNote)
        .filter(MeetingNote.decision_id == decision_id)
        .all()
    )


# GET MEETING NOTE BY ID
@router.get(
    "/meeting-notes/{note_id}",
    response_model=MeetingNoteResponse
)
def get_meeting_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_meeting_note_or_404(note_id, db)


# UPDATE MEETING NOTE
@router.put(
    "/meeting-notes/{note_id}",
    response_model=MeetingNoteResponse
)
def update_meeting_note(
    note_id: int,
    data: MeetingNoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note = get_meeting_note_or_404(note_id, db)

    ensure_owner(note, current_user)

    # Only these fields can ever be updated.
    # id, decision_id, created_by, created_at are never touched.
    if data.title is not None:
        note.title = data.title

    if data.content is not None:
        note.content = data.content

    if data.meeting_date is not None:
        note.meeting_date = data.meeting_date

    note.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(note)

    return note


# DELETE MEETING NOTE
@router.delete("/meeting-notes/{note_id}")
def delete_meeting_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note = get_meeting_note_or_404(note_id, db)

    ensure_owner(note, current_user)

    db.delete(note)
    db.commit()

    return {"message": "Meeting note deleted successfully"}
