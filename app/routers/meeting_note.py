from typing import List

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
from app.core.security import get_current_user


router = APIRouter(
    tags=["Meeting Notes"]
)


# ==========================================
# CREATE MEETING NOTE
# ==========================================
@router.post(
    "/decisions/{decision_id}/meeting-notes",
    response_model=MeetingNoteResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_meeting_note(
    decision_id: int,
    note: MeetingNoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    new_note = MeetingNote(
        decision_id=decision_id,
        created_by=current_user.id,
        title=note.title,
        content=note.content,
    )

    db.add(new_note)
    db.commit()
    db.refresh(new_note)

    return new_note


# ==========================================
# GET ALL MEETING NOTES FOR A DECISION
# ==========================================
@router.get(
    "/decisions/{decision_id}/meeting-notes",
    response_model=List[MeetingNoteResponse],
)
def get_meeting_notes(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    return db.query(MeetingNote).filter(
        MeetingNote.decision_id == decision_id
    ).all()


# ==========================================
# GET MEETING NOTE BY ID
# ==========================================
@router.get(
    "/meeting-notes/{note_id}",
    response_model=MeetingNoteResponse,
)
def get_meeting_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = db.query(MeetingNote).filter(
        MeetingNote.id == note_id
    ).first()

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting note not found",
        )

    return note


# ==========================================
# UPDATE MEETING NOTE
# ==========================================
@router.put(
    "/meeting-notes/{note_id}",
    response_model=MeetingNoteResponse,
)
def update_meeting_note(
    note_id: int,
    note_data: MeetingNoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = db.query(MeetingNote).filter(
        MeetingNote.id == note_id
    ).first()

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting note not found",
        )

    if note.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this meeting note",
        )

    if note_data.title is not None:
        note.title = note_data.title

    if note_data.content is not None:
        note.content = note_data.content

    db.commit()
    db.refresh(note)

    return note


# ==========================================
# DELETE MEETING NOTE
# ==========================================
@router.delete(
    "/meeting-notes/{note_id}",
    status_code=status.HTTP_200_OK,
)
def delete_meeting_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = db.query(MeetingNote).filter(
        MeetingNote.id == note_id
    ).first()

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting note not found",
        )

    if note.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this meeting note",
        )

    db.delete(note)
    db.commit()

    return {
        "message": "Meeting note deleted successfully"
    }