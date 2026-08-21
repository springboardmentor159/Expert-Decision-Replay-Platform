from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.decision import Decision
from app.models.meeting_note import MeetingNote
from app.models.user import User
from app.schemas.meeting_note import (
    MeetingNoteCreate,
    MeetingNoteResponse,
    MeetingNoteUpdate
)
from app.services.auth import get_current_user


router = APIRouter(
    tags=["Meeting Notes"]
)


# Create a meeting note for a decision
@router.post(
    "/decisions/{decision_id}/meeting-notes",
    response_model=MeetingNoteResponse,
    status_code=status.HTTP_201_CREATED
)
def create_meeting_note(
    decision_id: int,
    note_data: MeetingNoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if decision is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    note = MeetingNote(
        decision_id=decision.id,
        created_by=current_user.id,
        title=note_data.title,
        content=note_data.content,
        meeting_date=note_data.meeting_date
    )

    db.add(note)
    db.commit()
    db.refresh(note)

    return note


# Get all meeting notes for a decision
@router.get(
    "/decisions/{decision_id}/meeting-notes",
    response_model=list[MeetingNoteResponse]
)
def get_decision_meeting_notes(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if decision is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    notes = (
        db.query(MeetingNote)
        .filter(MeetingNote.decision_id == decision_id)
        .order_by(MeetingNote.meeting_date.desc())
        .all()
    )

    return notes


# Get a meeting note by ID
@router.get(
    "/meeting-notes/{note_id}",
    response_model=MeetingNoteResponse
)
def get_meeting_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note = (
        db.query(MeetingNote)
        .filter(MeetingNote.id == note_id)
        .first()
    )

    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting note not found"
        )

    return note


# Update a meeting note
@router.put(
    "/meeting-notes/{note_id}",
    response_model=MeetingNoteResponse
)
def update_meeting_note(
    note_id: int,
    note_data: MeetingNoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note = (
        db.query(MeetingNote)
        .filter(MeetingNote.id == note_id)
        .first()
    )

    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting note not found"
        )

    if note.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own meeting notes"
        )

    note.title = note_data.title
    note.content = note_data.content
    note.meeting_date = note_data.meeting_date

    db.commit()
    db.refresh(note)

    return note


# Delete a meeting note
@router.delete(
    "/meeting-notes/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_meeting_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note = (
        db.query(MeetingNote)
        .filter(MeetingNote.id == note_id)
        .first()
    )

    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting note not found"
        )

    if note.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own meeting notes"
        )

    db.delete(note)
    db.commit()

    return None