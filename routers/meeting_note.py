"""
Meeting Notes API router.

Endpoints:
    POST   /decisions/{decision_id}/meeting-notes     create a meeting note
    GET    /decisions/{decision_id}/meeting-notes     list meeting notes for a decision
    GET    /meeting-notes/{note_id}                   get a specific meeting note
    PUT    /meeting-notes/{note_id}                   update a meeting note
    DELETE /meeting-notes/{note_id}                   delete a meeting note
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.database import get_db
from app.models.decision import Decision
from app.models.meeting_note import MeetingNote
from app.models.user import User
from app.services.activity import record_activity
from app.schemas.meeting_note import (
    MeetingNoteCreate,
    MeetingNoteUpdate,
    MeetingNoteResponse,
)

router = APIRouter(tags=["Meeting Notes"])


def _get_decision_or_404(db: Session, decision_id: int) -> Decision:
    """Get a decision or raise 404"""
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Decision not found"
        )
    return decision


def _get_meeting_note_or_404(db: Session, note_id: int) -> MeetingNote:
    """Get a meeting note or raise 404"""
    note = db.query(MeetingNote).filter(MeetingNote.id == note_id).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Meeting note not found"
        )
    return note


def _ensure_owner_or_privileged(obj, current_user: User, owner_field: str = "created_by") -> None:
    """Verify user owns the object or has admin/manager role"""
    is_owner = getattr(obj, owner_field) == current_user.id
    is_privileged = current_user.role in {"admin", "manager"}
    if not (is_owner or is_privileged):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this resource",
        )


@router.post(
    "/decisions/{decision_id}/meeting-notes",
    response_model=MeetingNoteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a meeting note for a decision",
)
def create_meeting_note(
    decision_id: int,
    payload: MeetingNoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new meeting note for a decision"""
    _get_decision_or_404(db, decision_id)

    note = MeetingNote(
        decision_id=decision_id,
        created_by=current_user.id,
        title=payload.title,
        content=payload.content,
        meeting_date=payload.meeting_date,
    )
    db.add(note)
    db.flush()
    record_activity(db, current_user.id, "meeting_note_created", "MeetingNote", "Meeting note created", note.id)
    db.commit()
    db.refresh(note)
    return note


@router.get(
    "/decisions/{decision_id}/meeting-notes",
    response_model=list[MeetingNoteResponse],
    summary="Get all meeting notes for a decision",
)
def get_meeting_notes_for_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all meeting notes for a specific decision"""
    _get_decision_or_404(db, decision_id)

    notes = (
        db.query(MeetingNote)
        .filter(MeetingNote.decision_id == decision_id)
        .order_by(MeetingNote.created_at.asc())
        .all()
    )
    return notes


@router.get(
    "/meeting-notes/{note_id}",
    response_model=MeetingNoteResponse,
    summary="Get a specific meeting note",
)
def get_meeting_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific meeting note by ID"""
    return _get_meeting_note_or_404(db, note_id)


@router.put(
    "/meeting-notes/{note_id}",
    response_model=MeetingNoteResponse,
    summary="Update a meeting note",
)
def update_meeting_note(
    note_id: int,
    payload: MeetingNoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a meeting note (only creator or admin can update)"""
    note = _get_meeting_note_or_404(db, note_id)
    _ensure_owner_or_privileged(note, current_user)

    if payload.title is not None:
        note.title = payload.title
    if payload.content is not None:
        note.content = payload.content
    if payload.meeting_date is not None:
        note.meeting_date = payload.meeting_date

    db.commit()
    db.refresh(note)
    return note


@router.delete(
    "/meeting-notes/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a meeting note",
)
def delete_meeting_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a meeting note (only creator or admin can delete)"""
    note = _get_meeting_note_or_404(db, note_id)
    _ensure_owner_or_privileged(note, current_user)

    db.delete(note)
    db.commit()
