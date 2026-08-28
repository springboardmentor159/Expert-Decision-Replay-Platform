from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.audit import AuditAction
from app.models.decision import Decision
from app.models.meeting_note import MeetingNote
from app.models.user import User, UserRole
from app.schemas.meeting_note import (
    MeetingNoteCreate,
    MeetingNoteResponse,
    MeetingNoteUpdate,
)
from app.services.audit import create_audit_log
from app.services.auth import get_current_user


router = APIRouter(
    tags=["Meeting Notes"]
)


# ============================================================
# DECISION ACCESS HELPERS
# ============================================================

def get_decision_or_404(
    decision_id: int,
    db: Session,
    current_user: User,
) -> Decision:
    """
    Return the decision only when it belongs
    to the current user's organization.
    """

    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if decision is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    # Organization isolation
    if decision.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    return decision


def can_access_decision(
    decision: Decision,
    current_user: User,
) -> bool:
    """
    A user can access a decision when:
    - The decision belongs to their organization, AND
    - They created it, OR
    - They are a Manager, OR
    - They are an Administrator.
    """

    if decision.organization_id != current_user.organization_id:
        return False

    return (
        decision.created_by == current_user.id
        or current_user.role in (
            UserRole.MANAGER,
            UserRole.ADMINISTRATOR,
        )
    )


# ============================================================
# CREATE MEETING NOTE
# ============================================================

@router.post(
    "/decisions/{decision_id}/meeting-notes",
    response_model=MeetingNoteResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_meeting_note(
    decision_id: int,
    note_data: MeetingNoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = get_decision_or_404(
        decision_id,
        db,
        current_user,
    )

    if not can_access_decision(
        decision,
        current_user,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission to create "
                "a meeting note for this decision"
            ),
        )

    note = MeetingNote(
        decision_id=decision.id,
        created_by=current_user.id,
        title=note_data.title,
        content=note_data.content,
        meeting_date=note_data.meeting_date,
    )

    db.add(note)
    db.flush()

    create_audit_log(
        db=db,
        decision_id=decision.id,
        user_id=current_user.id,
        action=AuditAction.MEETING_NOTE_CREATED,
        entity_type="MeetingNote",
        entity_id=note.id,
        description=(
            f"Meeting note '{note.title}' "
            f"was created for decision '{decision.title}'"
        ),
    )

    db.commit()
    db.refresh(note)

    return note


# ============================================================
# GET ALL MEETING NOTES FOR A DECISION
# ============================================================

@router.get(
    "/decisions/{decision_id}/meeting-notes",
    response_model=list[MeetingNoteResponse],
)
def get_decision_meeting_notes(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = get_decision_or_404(
        decision_id,
        db,
        current_user,
    )

    if not can_access_decision(
        decision,
        current_user,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission to view "
                "meeting notes for this decision"
            ),
        )

    notes = (
        db.query(MeetingNote)
        .filter(
            MeetingNote.decision_id == decision_id
        )
        .order_by(
            MeetingNote.meeting_date.desc()
        )
        .all()
    )

    return notes


# ============================================================
# GET MEETING NOTE BY ID
# ============================================================

@router.get(
    "/meeting-notes/{note_id}",
    response_model=MeetingNoteResponse,
)
def get_meeting_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = (
        db.query(MeetingNote)
        .filter(MeetingNote.id == note_id)
        .first()
    )

    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting note not found",
        )

    decision = get_decision_or_404(
        note.decision_id,
        db,
        current_user,
    )

    if not can_access_decision(
        decision,
        current_user,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission to view "
                "this meeting note"
            ),
        )

    return note


# ============================================================
# UPDATE MEETING NOTE
# ============================================================

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
    note = (
        db.query(MeetingNote)
        .filter(MeetingNote.id == note_id)
        .first()
    )

    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting note not found",
        )

    decision = get_decision_or_404(
        note.decision_id,
        db,
        current_user,
    )

    if not can_access_decision(
        decision,
        current_user,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission "
                "to modify this meeting note"
            ),
        )

    # Only the creator can update the note.
    if note.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You can only update your own "
                "meeting notes"
            ),
        )

    note.title = note_data.title
    note.content = note_data.content
    note.meeting_date = note_data.meeting_date

    create_audit_log(
        db=db,
        decision_id=note.decision_id,
        user_id=current_user.id,
        action=AuditAction.MEETING_NOTE_UPDATED,
        entity_type="MeetingNote",
        entity_id=note.id,
        description=(
            f"Meeting note '{note.title}' was updated"
        ),
    )

    db.commit()
    db.refresh(note)

    return note


# ============================================================
# DELETE MEETING NOTE
# ============================================================

@router.delete(
    "/meeting-notes/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_meeting_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = (
        db.query(MeetingNote)
        .filter(MeetingNote.id == note_id)
        .first()
    )

    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting note not found",
        )

    decision = get_decision_or_404(
        note.decision_id,
        db,
        current_user,
    )

    if not can_access_decision(
        decision,
        current_user,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission "
                "to delete this meeting note"
            ),
        )

    # Only the creator can delete the note.
    if note.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You can only delete your own "
                "meeting notes"
            ),
        )

    decision_id = note.decision_id
    note_title = note.title

    create_audit_log(
        db=db,
        decision_id=decision_id,
        user_id=current_user.id,
        action=AuditAction.DELETE,
        entity_type="MeetingNote",
        entity_id=note.id,
        description=(
            f"Meeting note '{note_title}' was deleted"
        ),
    )

    db.delete(note)
    db.commit()

    return None