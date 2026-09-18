from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.decision import Decision
from app.models.meeting_note import MeetingNote
from app.models.user import User
from app.services.activity_service import log_activity
from app.services.audit_service import log_audit
from app.schemas.audit_log import AuditAction, AuditEntityType


router = APIRouter(
    prefix="/decisions",
    tags=["Meeting Notes"]
)


ALLOWED_ROLES = {
    "Employee",
    "Reviewer",
    "Manager",
    "Administrator",
}


class MeetingNoteCreate(BaseModel):
    content: str = Field(min_length=1, max_length=10000)


class MeetingNoteResponse(BaseModel):
    id: int
    decision_id: int
    user_id: int
    content: str

    model_config = ConfigDict(from_attributes=True)


def get_decision_or_404(
    decision_id: int,
    db: Session
) -> Decision:
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    return decision


def ensure_decision_access(
    decision: Decision,
    current_user: User
) -> None:
    role = current_user.role

    if role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid user role"
        )

    if role == "Employee" and decision.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this decision"
        )


def validate_content(content: str) -> str:
    cleaned = content.strip()

    if not cleaned:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Meeting note content cannot be empty"
        )

    return cleaned


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
    decision = get_decision_or_404(decision_id, db)
    ensure_decision_access(decision, current_user)

    content = validate_content(note_data.content)

    note = MeetingNote(
        decision_id=decision_id,
        user_id=current_user.id,
        content=content
    )

    db.add(note)
    db.flush()

    log_audit(
        db=db,
        user_id=current_user.id,
        action=AuditAction.CREATE,
        entity_type=AuditEntityType.MEETING_NOTE,
        entity_id=note.id,
        description=f"Created meeting note for decision {decision_id}",
        request_method="POST",
        endpoint=f"/decisions/{decision_id}/meeting-notes",
    )

    log_activity(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="MeetingNote",
        entity_id=note.id,
        description=f"Created meeting note for decision {decision_id}"
    )

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
    decision = get_decision_or_404(decision_id, db)
    ensure_decision_access(decision, current_user)

    return (
        db.query(MeetingNote)
        .filter(MeetingNote.decision_id == decision_id)
        .order_by(MeetingNote.id.desc())
        .all()
    )