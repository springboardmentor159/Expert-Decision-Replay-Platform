from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.decision import Decision
from app.models.meeting_note import MeetingNote
from app.models.user import User
from app.schemas.meeting_note import (
    MeetingNoteCreate,
    MeetingNoteResponse,
    MeetingNoteUpdate,
)
from app.services.activity_logger import log_activity
from app.services.audit_service import log_audit

router = APIRouter(tags=["Meeting Notes"])


@router.post(
    "/decisions/{decision_id}/meeting-notes",
    response_model=MeetingNoteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record a meeting note for a decision (Automatic Audit Logging)"
)
def create_meeting_note(
    decision_id: int,
    note_in: MeetingNoteCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    meeting_dt = note_in.meeting_date if note_in.meeting_date is not None else datetime.utcnow()

    new_note = MeetingNote(
        decision_id=decision_id,
        created_by=current_user.id,
        title=note_in.title,
        content=note_in.content,
        meeting_date=meeting_dt
    )
    db.add(new_note)
    db.commit()
    db.refresh(new_note)

    client_ip = request.client.host if request.client else None
    log_audit(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="MeetingNote",
        entity_id=new_note.id,
        description=f"Meeting note '{new_note.title}' recorded for decision '{decision.title}'",
        ip_address=client_ip,
        old_value=None,
        new_value={"title": new_note.title, "decision_id": decision_id, "meeting_date": str(meeting_dt)},
        request_method="POST",
        endpoint=f"/decisions/{decision_id}/meeting-notes"
    )

    log_activity(
        db=db,
        user_id=current_user.id,
        action="create_meeting_note",
        entity_type="meeting_note",
        entity_id=new_note.id,
        description=f"User {current_user.full_name} recorded meeting note '{new_note.title}' on decision '{decision.title}'"
    )

    return new_note


@router.get(
    "/decisions/{decision_id}/meeting-notes",
    response_model=List[MeetingNoteResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all meeting notes for a decision"
)
def get_meeting_notes_for_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    notes = db.query(MeetingNote).filter(MeetingNote.decision_id == decision_id).order_by(MeetingNote.meeting_date.desc()).all()
    return notes


@router.get(
    "/meeting-notes/{note_id}",
    response_model=MeetingNoteResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a meeting note by ID"
)
def get_meeting_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note = db.query(MeetingNote).filter(MeetingNote.id == note_id).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting note not found"
        )
    return note


@router.put(
    "/meeting-notes/{note_id}",
    response_model=MeetingNoteResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a meeting note (Automatic Audit Diff)"
)
def update_meeting_note(
    note_id: int,
    note_in: MeetingNoteUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note = db.query(MeetingNote).filter(MeetingNote.id == note_id).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting note not found"
        )

    # Ownership / authorization check
    if note.created_by != current_user.id and current_user.role not in ["Administrator", "Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this meeting note"
        )

    old_snapshot = {
        "title": note.title,
        "content": note.content,
        "meeting_date": str(note.meeting_date) if note.meeting_date else None
    }

    if note_in.title is not None:
        note.title = note_in.title
    if note_in.content is not None:
        note.content = note_in.content
    if note_in.meeting_date is not None:
        note.meeting_date = note_in.meeting_date

    db.commit()
    db.refresh(note)

    new_snapshot = {
        "title": note.title,
        "content": note.content,
        "meeting_date": str(note.meeting_date) if note.meeting_date else None
    }

    client_ip = request.client.host if request.client else None
    log_audit(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="MeetingNote",
        entity_id=note.id,
        description=f"Meeting note '{note.title}' updated",
        ip_address=client_ip,
        old_value=old_snapshot,
        new_value=new_snapshot,
        request_method="PUT",
        endpoint=f"/meeting-notes/{note.id}"
    )

    log_activity(
        db=db,
        user_id=current_user.id,
        action="update_meeting_note",
        entity_type="meeting_note",
        entity_id=note.id,
        description=f"User {current_user.full_name} updated meeting note '{note.title}'"
    )

    return note


@router.delete(
    "/meeting-notes/{note_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a meeting note (Automatic Audit Logging)"
)
def delete_meeting_note(
    note_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note = db.query(MeetingNote).filter(MeetingNote.id == note_id).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting note not found"
        )

    # Ownership / authorization check
    if note.created_by != current_user.id and current_user.role not in ["Administrator", "Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this meeting note"
        )

    old_snapshot = {"id": note.id, "title": note.title, "decision_id": note.decision_id}

    client_ip = request.client.host if request.client else None
    log_audit(
        db=db,
        user_id=current_user.id,
        action="DELETE",
        entity_type="MeetingNote",
        entity_id=note.id,
        description=f"Meeting note '{note.title}' deleted",
        ip_address=client_ip,
        old_value=old_snapshot,
        new_value=None,
        request_method="DELETE",
        endpoint=f"/meeting-notes/{note.id}"
    )

    db.delete(note)
    db.commit()
    return {"message": "Meeting note deleted successfully"}
