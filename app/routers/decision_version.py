from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.decision import Decision
from app.models.decision_version import DecisionVersion
from app.models.alternative import Alternative
from app.models.comment import Comment
from app.models.discussion_thread import DiscussionThread
from app.models.user import User
from app.schemas.decision_version import (
    DecisionVersionCreate,
    DecisionVersionResponse,
)
from app.services.audit_service import log_audit
from datetime import datetime
router = APIRouter(
    prefix="/decisions",
    tags=["Decision Versions"]
)


@router.post(
    "/{decision_id}/versions",
    response_model=DecisionVersionResponse,
    status_code=status.HTTP_201_CREATED
)
def create_decision_version(
    decision_id: int,
    version_data: DecisionVersionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()

    if decision is None:
        raise HTTPException(status_code=404, detail="Decision not found")

    last_version = (
        db.query(DecisionVersion)
        .filter(DecisionVersion.decision_id == decision_id)
        .order_by(DecisionVersion.version_number.desc())
        .first()
    )

    next_version = 1 if last_version is None else last_version.version_number + 1

    new_version = DecisionVersion(
        decision_id=decision_id,
        version_number=next_version,
        title=version_data.title,
        description=version_data.description,
        status=version_data.status,
        created_by=current_user.id,
    )

    db.add(new_version)
    db.flush()

    log_audit(
        db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="DecisionVersion",
        entity_id=new_version.id,
        description=f"Version {next_version} created for Decision {decision_id}",
        new_value={"version_number": next_version, "title": new_version.title},
    )

    db.commit()
    db.refresh(new_version)

    return new_version

@router.get(
    "/{decision_id}/versions",
    response_model=List[DecisionVersionResponse]
)
def get_decision_versions(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()

    if decision is None:
        raise HTTPException(status_code=404, detail="Decision not found")

    versions = (
        db.query(DecisionVersion)
        .filter(DecisionVersion.decision_id == decision_id)
        .order_by(DecisionVersion.version_number.asc())
        .all()
    )

    return versions


@router.get(
    "/{decision_id}/versions/{version_number}",
    response_model=DecisionVersionResponse
)
def get_specific_version(
    decision_id: int,
    version_number: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    version = (
        db.query(DecisionVersion)
        .filter(
            DecisionVersion.decision_id == decision_id,
            DecisionVersion.version_number == version_number
        )
        .first()
    )

    if version is None:
        raise HTTPException(status_code=404, detail="Version not found")

    return version


@router.get("/{decision_id}/history")
def get_decision_history(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()

    if decision is None:
        raise HTTPException(status_code=404, detail="Decision not found")

    history = []

    history.append({
        "event": "Decision Created",
        "timestamp": decision.created_at,
        "description": f"Decision '{decision.title}' was created",
    })


    alternatives = (
        db.query(Alternative)
        .filter(Alternative.decision_id == decision_id)
        .order_by(Alternative.created_at)
        .all()
    )
    for alt in alternatives:
        history.append({
            "event": "Alternative Added",
            "timestamp": alt.created_at,
            "description": f"Alternative '{alt.name}' was added",
        })

    
    comments = (
        db.query(Comment)
        .filter(Comment.decision_id == decision_id)
        .order_by(Comment.created_at)
        .all()
    )
    for comment in comments:
        history.append({
            "event": "Comment Added",
            "timestamp": comment.created_at,
            "description": "A comment was added",
        })

    
    threads = (
        db.query(DiscussionThread)
        .filter(DiscussionThread.decision_id == decision_id)
        .order_by(DiscussionThread.created_at)
        .all()
    )
    for thread in threads:
        history.append({
            "event": "Discussion Thread Created",
            "timestamp": thread.created_at,
            "description": f"Thread '{thread.title}' was created",
        })

    
    versions = (
        db.query(DecisionVersion)
        .filter(DecisionVersion.decision_id == decision_id)
        .order_by(DecisionVersion.created_at)
        .all()
    )
    for version in versions:
        history.append({
            "event": f"Version {version.version_number} Created",
            "timestamp": version.created_at,
            "description": f"Decision version {version.version_number} was saved",
        })

    
        
    def normalize(dt):
        if dt is None:
            return datetime.min
        if hasattr(dt, 'tzinfo') and dt.tzinfo is not None:
            return dt.replace(tzinfo=None)
        return dt

    history.sort(key=lambda x: normalize(x["timestamp"]))

    return {"decision_id": decision_id, "history": history}