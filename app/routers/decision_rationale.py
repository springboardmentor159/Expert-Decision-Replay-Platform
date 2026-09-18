from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.decision import Decision
from app.models.decision_rationale import DecisionRationale
from app.models.user import User
from app.services.activity_service import log_activity
from app.services.audit_service import log_audit
from app.schemas.audit_log import AuditAction, AuditEntityType


router = APIRouter(
    prefix="/decisions",
    tags=["Decision Rationale"]
)


ALLOWED_ROLES = {
    "Employee",
    "Reviewer",
    "Manager",
    "Administrator",
}


class RationaleCreate(BaseModel):
    content: str = Field(min_length=1, max_length=10000)


class RationaleResponse(BaseModel):
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
            detail="Rationale content cannot be empty"
        )

    return cleaned


@router.post(
    "/{decision_id}/rationale",
    response_model=RationaleResponse,
    status_code=status.HTTP_201_CREATED
)
def create_rationale(
    decision_id: int,
    rationale_data: RationaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = get_decision_or_404(decision_id, db)
    ensure_decision_access(decision, current_user)

    content = validate_content(rationale_data.content)

    existing = (
        db.query(DecisionRationale)
        .filter(
            DecisionRationale.decision_id == decision_id
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rationale already exists"
        )

    rationale = DecisionRationale(
        decision_id=decision_id,
        user_id=current_user.id,
        content=content
    )

    db.add(rationale)
    db.flush()

    log_audit(
        db=db,
        user_id=current_user.id,
        action=AuditAction.CREATE,
        entity_type=AuditEntityType.DECISION,
        entity_id=decision_id,
        description=f"Created rationale for decision {decision_id}",
        request_method="POST",
        endpoint=f"/decisions/{decision_id}/rationale",
    )

    log_activity(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="DecisionRationale",
        entity_id=rationale.id,
        description=f"Created rationale for decision {decision_id}"
    )

    db.commit()
    db.refresh(rationale)

    return rationale


@router.get(
    "/{decision_id}/rationale",
    response_model=RationaleResponse
)
def get_rationale(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = get_decision_or_404(decision_id, db)
    ensure_decision_access(decision, current_user)

    rationale = (
        db.query(DecisionRationale)
        .filter(
            DecisionRationale.decision_id == decision_id
        )
        .first()
    )

    if not rationale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rationale not found"
        )

    return rationale