from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user

from app.models.user import User
from app.models.decision import Decision
from app.models.decision_version import DecisionVersion
from app.models.tag import Tag
from app.models.alternative import Alternative
from app.models.comment import Comment
from app.models.discussion_thread import DiscussionThread
from app.models.meeting_note import MeetingNote
from app.models.audit_log import AuditLog

from app.services.activity import create_activity
from app.services.audit import create_audit_log
from app.services.access import create_access_log

from app.schemas.decision import (
    DecisionCreate,
    DecisionUpdate,
    DecisionStatusUpdate,
    DecisionResponse,
    DecisionRationaleUpdate,
    DecisionRationaleResponse,
    DecisionTimelineEvent,
)


router = APIRouter(
    prefix="/decisions",
    tags=["Decisions"],
)


# ============================================================
# CREATE DECISION
# ============================================================

@router.post(
    "",
    response_model=DecisionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_decision(
    decision_data: DecisionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_decision = Decision(
        title=decision_data.title,
        problem_statement=decision_data.problem_statement,
        category=decision_data.category,
        status="Draft",
        created_by=current_user.id,
    )

    db.add(new_decision)
    db.flush()

    # ========================================================
    # CREATE VERSION 1
    # ========================================================

    version = DecisionVersion(
        decision_id=new_decision.id,
        version_number=1,
        title=new_decision.title,
        problem_statement=new_decision.problem_statement,
        category=new_decision.category,
        status=new_decision.status,
        rationale=new_decision.rationale,
        created_by=current_user.id,
    )

    db.add(version)

    # ========================================================
    # ACTIVITY LOG
    # ========================================================

    create_activity(
        db=db,
        user_id=current_user.id,
        action="Decision created",
        entity_type="Decision",
        entity_id=new_decision.id,
        description=(
            f"User {current_user.id} created "
            f"Decision {new_decision.id}"
        ),
    )

    # ========================================================
    # AUDIT LOG
    # ========================================================

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="Decision",
        entity_id=new_decision.id,
        description=(
            f"User {current_user.id} created "
            f"Decision {new_decision.id}"
        ),
        new_value={
            "title": new_decision.title,
            "problem_statement": new_decision.problem_statement,
            "category": new_decision.category,
            "status": new_decision.status,
            "rationale": new_decision.rationale,
        },
        request_method="POST",
        endpoint="/decisions",
    )

    db.commit()
    db.refresh(new_decision)

    return new_decision


# ============================================================
# GET ALL DECISIONS
# SEARCH + FILTERING + PAGINATION + SORTING
# ============================================================

@router.get(
    "",
    response_model=List[DecisionResponse],
)
def get_decisions(
    status_filter: Optional[str] = Query(
        default=None,
        alias="status",
    ),

    category: Optional[str] = None,

    q: Optional[str] = None,

    tag: Optional[str] = None,

    page: int = Query(
        default=1,
        ge=1,
    ),

    page_size: int = Query(
        default=10,
        ge=1,
        le=100,
    ),

    sort: str = Query(
        default="created_at",
        pattern="^(created_at|updated_at|title)$",
    ),

    order: str = Query(
        default="desc",
        pattern="^(asc|desc)$",
    ),

    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Decision)

    # ========================================================
    # KEYWORD SEARCH
    # ========================================================

    if q:
        search_term = f"%{q}%"

        query = query.filter(
            or_(
                Decision.title.ilike(search_term),
                Decision.problem_statement.ilike(search_term),
                Decision.rationale.ilike(search_term),
            )
        )

    # ========================================================
    # STATUS FILTER
    # ========================================================

    if status_filter is not None:
        query = query.filter(
            Decision.status == status_filter
        )

    # ========================================================
    # CATEGORY FILTER
    # ========================================================

    if category is not None:
        query = query.filter(
            Decision.category == category
        )

    # ========================================================
    # TAG FILTER
    # ========================================================

    if tag is not None:
        query = query.join(
            Decision.tags
        ).filter(
            Tag.name == tag
        )

    # ========================================================
    # SORTING
    # ========================================================

    sort_column = {
        "created_at": Decision.created_at,
        "updated_at": Decision.updated_at,
        "title": Decision.title,
    }[sort]

    if order == "asc":
        query = query.order_by(
            sort_column.asc()
        )
    else:
        query = query.order_by(
            sort_column.desc()
        )

    # ========================================================
    # PAGINATION
    # ========================================================

    offset = (page - 1) * page_size

    query = query.offset(offset).limit(page_size)

    return query.all()


# ============================================================
# SEARCH DECISIONS
# ============================================================

@router.get(
    "/search",
    response_model=List[DecisionResponse],
)
def search_decisions(
    q: str = Query(
        ...,
        min_length=1,
    ),

    category: Optional[str] = None,

    status_filter: Optional[str] = Query(
        default=None,
        alias="status",
    ),

    tag: Optional[str] = None,

    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    search_term = f"%{q}%"

    query = db.query(Decision).filter(
        or_(
            Decision.title.ilike(search_term),
            Decision.problem_statement.ilike(search_term),
            Decision.rationale.ilike(search_term),
        )
    )

    if category is not None:
        query = query.filter(
            Decision.category == category
        )

    if status_filter is not None:
        query = query.filter(
            Decision.status == status_filter
        )

    if tag is not None:
        query = query.join(
            Decision.tags
        ).filter(
            Tag.name == tag
        )

    return query.all()


# ============================================================
# UPDATE DECISION RATIONALE
# ============================================================

@router.put(
    "/{decision_id}/rationale",
    response_model=DecisionRationaleResponse,
)
def update_decision_rationale(
    decision_id: int,
    rationale_data: DecisionRationaleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    if decision.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission to "
                "update this decision rationale"
            ),
        )

    # ========================================================
    # OLD VALUE
    # ========================================================

    old_value = {
        "rationale": decision.rationale,
    }

    # ========================================================
    # UPDATE
    # ========================================================

    decision.rationale = rationale_data.rationale

    db.flush()

    # ========================================================
    # NEXT VERSION
    # ========================================================

    last_version = (
        db.query(DecisionVersion)
        .filter(
            DecisionVersion.decision_id == decision.id
        )
        .order_by(
            DecisionVersion.version_number.desc()
        )
        .first()
    )

    next_version = (
        last_version.version_number + 1
        if last_version
        else 1
    )

    version = DecisionVersion(
        decision_id=decision.id,
        version_number=next_version,
        title=decision.title,
        problem_statement=decision.problem_statement,
        category=decision.category,
        status=decision.status,
        rationale=decision.rationale,
        created_by=current_user.id,
    )

    db.add(version)

    # ========================================================
    # AUDIT
    # ========================================================

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="Decision",
        entity_id=decision.id,
        description=(
            f"User {current_user.id} updated "
            f"rationale of Decision {decision.id}"
        ),
        old_value=old_value,
        new_value={
            "rationale": decision.rationale,
        },
        request_method="PUT",
        endpoint=f"/decisions/{decision.id}/rationale",
    )

    # ========================================================
    # ACTIVITY
    # ========================================================

    create_activity(
        db=db,
        user_id=current_user.id,
        action="Decision rationale updated",
        entity_type="Decision",
        entity_id=decision.id,
        description=(
            f"User {current_user.id} updated "
            f"rationale of Decision {decision.id}"
        ),
    )

    db.commit()
    db.refresh(decision)

    return {
        "decision_id": decision.id,
        "rationale": decision.rationale,
    }


# ============================================================
# GET DECISION RATIONALE
# ============================================================

@router.get(
    "/{decision_id}/rationale",
    response_model=DecisionRationaleResponse,
)
def get_decision_rationale(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    return {
        "decision_id": decision.id,
        "rationale": decision.rationale,
    }


# ============================================================
# GET DECISION TIMELINE
# ============================================================

@router.get(
    "/{decision_id}/timeline",
    response_model=List[DecisionTimelineEvent],
)
def get_decision_timeline(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    events = []

    # ========================================================
    # DECISION CREATED
    # ========================================================

    events.append(
        {
            "event_type": "Decision created",
            "description": (
                f"Decision '{decision.title}' was created."
            ),
            "timestamp": decision.created_at,
        }
    )

    # ========================================================
    # ALTERNATIVES
    # ========================================================

    alternatives = (
        db.query(Alternative)
        .filter(
            Alternative.decision_id == decision_id
        )
        .all()
    )

    for alternative in alternatives:
        events.append(
            {
                "event_type": "Alternative created",
                "description": (
                    f"Alternative '{alternative.name}' "
                    f"was created."
                ),
                "timestamp": alternative.created_at,
            }
        )

    # ========================================================
    # DISCUSSION THREADS
    # ========================================================

    threads = (
        db.query(DiscussionThread)
        .filter(
            DiscussionThread.decision_id == decision_id
        )
        .all()
    )

    for thread in threads:
        events.append(
            {
                "event_type": "Discussion thread created",
                "description": (
                    f"Discussion thread '{thread.title}' "
                    f"was created."
                ),
                "timestamp": thread.created_at,
            }
        )

    # ========================================================
    # COMMENTS
    # ========================================================

    comments = (
        db.query(Comment)
        .filter(
            Comment.decision_id == decision_id
        )
        .all()
    )

    for comment in comments:
        events.append(
            {
                "event_type": "Comment added",
                "description": (
                    "A comment was added to the decision."
                ),
                "timestamp": comment.created_at,
            }
        )

    # ========================================================
    # MEETING NOTES
    # ========================================================

    meeting_notes = (
        db.query(MeetingNote)
        .filter(
            MeetingNote.decision_id == decision_id
        )
        .all()
    )

    for note in meeting_notes:
        events.append(
            {
                "event_type": "Meeting note added",
                "description": (
                    f"Meeting note '{note.title}' "
                    f"was added."
                ),
                "timestamp": note.created_at,
            }
        )

    # ========================================================
    # DECISION UPDATED
    # ========================================================

    if (
        decision.updated_at
        and decision.updated_at != decision.created_at
    ):
        events.append(
            {
                "event_type": "Decision updated",
                "description": (
                    f"Decision '{decision.title}' "
                    f"was updated."
                ),
                "timestamp": decision.updated_at,
            }
        )

    # ========================================================
    # STATUS EVENTS
    # ========================================================

    status_event_map = {
        "Approved": "Decision approved",
        "Rejected": "Decision rejected",
        "Archived": "Decision archived",
    }

    if decision.status in status_event_map:
        events.append(
            {
                "event_type": status_event_map[
                    decision.status
                ],
                "description": (
                    f"Decision status changed to "
                    f"'{decision.status}'."
                ),
                "timestamp": decision.updated_at,
            }
        )

    # ========================================================
    # CHRONOLOGICAL ORDER
    # ========================================================

    events.sort(
        key=lambda event: event["timestamp"]
    )

    return events

# ============================================================
# GET ALL DECISION VERSIONS
# ============================================================

@router.get(
    "/{decision_id}/versions",
)
def get_decision_versions(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # --------------------------------------------------------
    # CHECK DECISION EXISTS
    # --------------------------------------------------------

    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    # --------------------------------------------------------
    # GET VERSIONS
    # --------------------------------------------------------

    versions = (
        db.query(DecisionVersion)
        .filter(
            DecisionVersion.decision_id == decision_id
        )
        .order_by(
            DecisionVersion.version_number.asc()
        )
        .all()
    )

    return versions


# ============================================================
# GET SPECIFIC DECISION VERSION
# ============================================================

@router.get(
    "/{decision_id}/versions/{version_number}",
)
def get_decision_version(
    decision_id: int,
    version_number: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # --------------------------------------------------------
    # CHECK DECISION EXISTS
    # --------------------------------------------------------

    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    # --------------------------------------------------------
    # FIND VERSION
    # --------------------------------------------------------

    version = (
        db.query(DecisionVersion)
        .filter(
            DecisionVersion.decision_id == decision_id,
            DecisionVersion.version_number == version_number,
        )
        .first()
    )

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision version not found",
        )

    return version


# ============================================================
# GET DECISION CHANGE HISTORY
# ============================================================

@router.get(
    "/{decision_id}/history",
)
def get_decision_history(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # --------------------------------------------------------
    # CHECK DECISION EXISTS
    # --------------------------------------------------------

    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    # --------------------------------------------------------
    # GET AUDIT HISTORY
    # --------------------------------------------------------

    history = (
        db.query(AuditLog)
        .filter(
            AuditLog.entity_type == "Decision",
            AuditLog.entity_id == decision_id,
        )
        .order_by(
            AuditLog.created_at.asc()
        )
        .all()
    )

    return history

# ============================================================
# GET DECISION BY ID
# ============================================================

@router.get(
    "/{decision_id}",
    response_model=DecisionResponse,
)
def get_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )
    # Record decision access
    create_access_log(
        db=db,
        user_id=current_user.id,
        resource_type="Decision",
        resource_id=decision.id,
        action="VIEW",
    )

    db.commit()
    return {
        "id": decision.id,
        "title": decision.title,
        "problem_statement": decision.problem_statement,
        "category": decision.category,
        "status": decision.status,
        "created_by": decision.created_by,
        "rationale": decision.rationale,
        "created_at": decision.created_at,
        "updated_at": decision.updated_at,
    }

# ============================================================
# UPDATE DECISION STATUS
# ============================================================

@router.patch(
    "/{decision_id}/status",
    response_model=DecisionResponse,
)
def update_decision_status(
    decision_id: int,
    status_data: DecisionStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Find decision
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    old_status = decision.status
    new_status = status_data.status

    # No change
    if old_status == new_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Decision is already {new_status}",
        )

    # Capture complete old values
    old_value = {
        "title": decision.title,
        "problem_statement": decision.problem_statement,
        "category": decision.category,
        "status": old_status,
        "rationale": decision.rationale,
    }

    # Update status
    decision.status = new_status

    db.flush()

    # Get next version number
    last_version = (
        db.query(DecisionVersion)
        .filter(
            DecisionVersion.decision_id == decision.id
        )
        .order_by(
            DecisionVersion.version_number.desc()
        )
        .first()
    )

    next_version = (
        last_version.version_number + 1
        if last_version
        else 1
    )

    # Create decision version
    version = DecisionVersion(
        decision_id=decision.id,
        version_number=next_version,
        title=decision.title,
        problem_statement=decision.problem_statement,
        category=decision.category,
        status=decision.status,
        rationale=decision.rationale,
        created_by=current_user.id,
    )

    db.add(version)

    # Determine audit action
    audit_action = "UPDATE"

    if new_status == "Approved":
        audit_action = "APPROVE"
    elif new_status == "Rejected":
        audit_action = "REJECT"
    elif new_status == "Under Review":
        audit_action = "SUBMIT"
    elif new_status == "Archived":
        audit_action = "UPDATE"

    # Create audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action=audit_action,
        entity_type="Decision",
        entity_id=decision.id,
        description=(
            f"User {current_user.id} changed "
            f"Decision {decision.id} status "
            f"from {old_status} to {new_status}"
        ),
        old_value=old_value,
        new_value={
            "title": decision.title,
            "problem_statement": decision.problem_statement,
            "category": decision.category,
            "status": new_status,
            "rationale": decision.rationale,
        },
        request_method="PATCH",
        endpoint=f"/decisions/{decision.id}/status",
    )

    # Activity log
    create_activity(
        db=db,
        user_id=current_user.id,
        action=f"Decision status changed to {new_status}",
        entity_type="Decision",
        entity_id=decision.id,
        description=(
            f"Decision {decision.id} status changed "
            f"from {old_status} to {new_status}"
        ),
    )

    db.commit()
    db.refresh(decision)

    return decision

# ============================================================
# UPDATE DECISION
# ============================================================

@router.put(
    "/{decision_id}",
    response_model=DecisionResponse,
)
def update_decision(
    decision_id: int,
    decision_data: DecisionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ========================================================
    # FIND DECISION
    # ========================================================

    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    # ========================================================
    # CAPTURE OLD VALUES
    # ========================================================

    old_value = {
        "title": decision.title,
        "problem_statement": decision.problem_statement,
        "category": decision.category,
        "status": decision.status,
        "rationale": decision.rationale,
    }

    # ========================================================
    # UPDATE DECISION
    # ========================================================

    decision.title = decision_data.title
    decision.problem_statement = decision_data.problem_statement
    decision.category = decision_data.category

    db.flush()

    # ========================================================
    # GET NEXT VERSION NUMBER
    # ========================================================

    last_version = (
        db.query(DecisionVersion)
        .filter(
            DecisionVersion.decision_id == decision.id
        )
        .order_by(
            DecisionVersion.version_number.desc()
        )
        .first()
    )

    next_version = (
        last_version.version_number + 1
        if last_version
        else 1
    )

    # ========================================================
    # CREATE DECISION VERSION
    # ========================================================

    version = DecisionVersion(
        decision_id=decision.id,
        version_number=next_version,
        title=decision.title,
        problem_statement=decision.problem_statement,
        category=decision.category,
        status=decision.status,
        rationale=decision.rationale,
        created_by=current_user.id,
    )

    db.add(version)

    # ========================================================
    # CREATE AUDIT LOG
    # ========================================================

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="Decision",
        entity_id=decision.id,
        description=(
            f"User {current_user.id} updated "
            f"Decision {decision.id}"
        ),
        old_value=old_value,
        new_value={
            "title": decision.title,
            "problem_statement": decision.problem_statement,
            "category": decision.category,
            "status": decision.status,
            "rationale": decision.rationale,
        },
        request_method="PUT",
        endpoint=f"/decisions/{decision.id}",
    )

    # ========================================================
    # CREATE ACTIVITY LOG
    # ========================================================

    create_activity(
        db=db,
        user_id=current_user.id,
        action="Decision updated",
        entity_type="Decision",
        entity_id=decision.id,
        description=(
            f"User {current_user.id} updated "
            f"Decision {decision.id}"
        ),
    )

    # ========================================================
    # SAVE CHANGES
    # ========================================================

    db.commit()
    db.refresh(decision)

    return decision