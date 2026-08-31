from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models.decision import Decision
from app.models.enums import UserRole
from app.models.meeting_note import MeetingNote
from app.models.user import User
from app.services.audit import log_audit
from app.schemas.meeting_note import MeetingNoteCreate, MeetingNoteResponse, MeetingNoteUpdate

router = APIRouter(
    prefix="/decisions",
    tags=["Meeting Notes"]
)

meeting_notes_router = APIRouter(
    prefix="/meeting-notes",
    tags=["Meeting Notes"]
)


def _get_decision_or_404(db: Session, decision_id: int) -> Decision:
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )
    return decision


def _get_note_or_404(db: Session, note_id: int) -> MeetingNote:
    note = db.query(MeetingNote).filter(MeetingNote.id == note_id).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting note not found"
        )
    return note


@router.post(
    "/{decision_id}/meeting-notes",
    response_model=MeetingNoteResponse,
    status_code=status.HTTP_201_CREATED
)
def create_meeting_note(
    request: Request,
    decision_id: int,
    note_data: MeetingNoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    _get_decision_or_404(db, decision_id)

    new_note = MeetingNote(
        decision_id=decision_id,
        created_by=current_user.id,
        title=note_data.title,
        content=note_data.content,
        meeting_date=note_data.meeting_date,
    )

    db.add(new_note)
    db.commit()
    db.refresh(new_note)

    log_audit(
        db,
        current_user.id,
        "create",
        "meeting_note",
        new_note.id,
        f"Created meeting note '{new_note.title}' for decision {decision_id}",
        ip_address=request.client.host if request.client else None,
    )

    return new_note


@router.get(
    "/{decision_id}/meeting-notes",
    response_model=List[MeetingNoteResponse]
)
def get_meeting_notes_by_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    _get_decision_or_404(db, decision_id)

    notes = db.query(MeetingNote).filter(
        MeetingNote.decision_id == decision_id
    ).all()

    return notes


@meeting_notes_router.get(
    "/{note_id}",
    response_model=MeetingNoteResponse
)
def get_meeting_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return _get_note_or_404(db, note_id)


@meeting_notes_router.put(
    "/{note_id}",
    response_model=MeetingNoteResponse
)
def update_meeting_note(
    request: Request,
    note_id: int,
    note_data: MeetingNoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note = _get_note_or_404(db, note_id)

    if note.created_by != current_user.id and current_user.role != UserRole.ADMINISTRATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this meeting note"
        )

    if note_data.title is not None:
        note.title = note_data.title
    if note_data.content is not None:
        note.content = note_data.content
    if note_data.meeting_date is not None:
        note.meeting_date = note_data.meeting_date

    note.updated_at = func.now()

    db.commit()
    db.refresh(note)

    log_audit(
        db,
        current_user.id,
        "update",
        "meeting_note",
        note.id,
        f"Updated meeting note '{note.title}'",
        ip_address=request.client.host if request.client else None,
    )

    return note


@meeting_notes_router.delete(
    "/{note_id}"
)
def delete_meeting_note(
    request: Request,
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note = _get_note_or_404(db, note_id)

    if note.created_by != current_user.id and current_user.role != UserRole.ADMINISTRATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this meeting note"
        )

    db.delete(note)
    db.commit()

    log_audit(
        db,
        current_user.id,
        "delete",
        "meeting_note",
        note_id,
        f"Deleted meeting note {note_id}",
        ip_address=request.client.host if request.client else None,
    )

    return {"message": "Meeting note deleted successfully"}
