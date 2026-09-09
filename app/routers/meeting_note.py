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

from app.services.audit_log import create_audit_log
from app.services.access_log import create_access_log

from app.models.audit_action import AuditAction
from app.models.audit_entity import AuditEntityType


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
    db.flush()

    # ==========================================
    # AUDIT LOG
    # ==========================================

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action=AuditAction.CREATE,
        entity_type=AuditEntityType.MEETING_NOTE,
        entity_id=new_note.id,
        description=f"Created meeting note: {new_note.title}",
        new_value={
            "decision_id": decision_id,
            "created_by": current_user.id,
            "title": new_note.title,
            "content": new_note.content,
        },
        request_method="POST",
        endpoint=f"/decisions/{decision_id}/meeting-notes",
    )

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

    notes = db.query(MeetingNote).filter(
        MeetingNote.decision_id == decision_id
    ).all()

    # ==========================================
    # ACCESS LOG
    # ==========================================

    create_access_log(
        db=db,
        user_id=current_user.id,
        resource_type="MeetingNote",
        resource_id=decision_id,
        action="LIST",
    )

    db.commit()

    return notes


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

    # ==========================================
    # ACCESS LOG
    # ==========================================

    create_access_log(
        db=db,
        user_id=current_user.id,
        resource_type="MeetingNote",
        resource_id=note.id,
        action="VIEW",
    )

    db.commit()

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

    # ==========================================
    # SAVE OLD VALUES
    # ==========================================

    old_value = {
        "title": note.title,
        "content": note.content,
    }

    if note_data.title is not None:
        note.title = note_data.title

    if note_data.content is not None:
        note.content = note_data.content

    db.flush()

    # ==========================================
    # AUDIT LOG
    # ==========================================

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action=AuditAction.UPDATE,
        entity_type=AuditEntityType.MEETING_NOTE,
        entity_id=note.id,
        description=f"Updated meeting note: {note.title}",
        old_value=old_value,
        new_value={
            "title": note.title,
            "content": note.content,
        },
        request_method="PUT",
        endpoint=f"/meeting-notes/{note_id}",
    )

    # ==========================================
    # ACCESS LOG
    # ==========================================

    create_access_log(
        db=db,
        user_id=current_user.id,
        resource_type="MeetingNote",
        resource_id=note.id,
        action="UPDATE",
    )

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

    # ==========================================
    # SAVE OLD VALUES BEFORE DELETE
    # ==========================================

    old_value = {
        "decision_id": note.decision_id,
        "created_by": note.created_by,
        "title": note.title,
        "content": note.content,
    }

    # ==========================================
    # AUDIT LOG
    # ==========================================

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action=AuditAction.DELETE,
        entity_type=AuditEntityType.MEETING_NOTE,
        entity_id=note.id,
        description=f"Deleted meeting note: {note.title}",
        old_value=old_value,
        request_method="DELETE",
        endpoint=f"/meeting-notes/{note_id}",
    )

    # ==========================================
    # ACCESS LOG
    # ==========================================

    create_access_log(
        db=db,
        user_id=current_user.id,
        resource_type="MeetingNote",
        resource_id=note.id,
        action="DELETE",
    )

    db.delete(note)
    db.commit()

    return {
        "message": "Meeting note deleted successfully"
    }