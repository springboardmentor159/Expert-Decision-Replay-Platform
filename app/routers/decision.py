from typing import List, Optional
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db

from app.models.decision import Decision
from app.models.user import User
from app.models.decision_version import DecisionVersion
from app.models.audit_log import AuditLog
from app.models.comment import Comment
from app.models.alternative import Alternative
from app.models.discussion_thread import DiscussionThread
from app.models.tag import Tag

from app.services.activity import create_activity_log
from app.services.audit import create_audit_log

from app.schemas.decision import (
    DecisionCreate,
    DecisionResponse,
    DecisionStatus,
    DecisionStatusUpdate,
    DecisionUpdate,
    DecisionVersionResponse,
)

from app.schemas.tag import (
    TagResponse,
    DecisionTagsUpdate,
)

from app.core.security import get_current_user


router = APIRouter(
    prefix="/decisions",
    tags=["Decisions"],
)


# =========================================================
# HELPERS
# =========================================================

def check_decision_history_access(
    decision: Decision,
    current_user,
    db: Session,
):
    role = current_user.role

    # Administrator
    if role in {"Admin", "Administrator"}:
        return

    # Employee
    if role == "Employee":
        if decision.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Employees can only access history "
                    "of their own decisions"
                ),
            )
        return

    # Reviewer
    if role == "Reviewer":
        if (
            decision.created_by == current_user.id
            or decision.status != "Draft"
        ):
            return

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Reviewer is not permitted to access "
                "this decision history"
            ),
        )

    # Manager
    if role == "Manager":
        creator = (
            db.query(User)
            .filter(User.id == decision.created_by)
            .first()
        )

        if (
            creator
            and current_user.department
            and creator.department == current_user.department
        ):
            return

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Manager can only access history "
                "of decisions from their team"
            ),
        )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=(
            "You are not permitted to access "
            "decision history"
        ),
    )


def check_decision_edit_access(
    decision: Decision,
    current_user,
):
    """
    Only the decision creator can modify a Draft decision.
    Administrators can modify any decision.
    Final decisions cannot be edited.
    """

    if current_user.role in {"Admin", "Administrator"}:
        return

    if current_user.role != "Employee":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only the decision creator or Administrator "
                "can modify a decision"
            ),
        )

    if decision.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You can only modify your own decisions"
            ),
        )

    if decision.status != "Draft":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Decision cannot be modified when its "
                f"status is '{decision.status}'"
            ),
        )


def create_decision_version(
    db: Session,
    decision: Decision,
    user_id: int,
):
    latest_version = (
        db.query(DecisionVersion)
        .filter(
            DecisionVersion.decision_id == decision.id
        )
        .order_by(
            DecisionVersion.version_number.desc()
        )
        .first()
    )

    next_version_number = (
        latest_version.version_number + 1
        if latest_version
        else 1
    )

    version = DecisionVersion(
        decision_id=decision.id,
        version_number=next_version_number,
        title=decision.title,
        problem_statement=decision.problem_statement,
        description=None,
        category=decision.category,
        status=decision.status,
        created_by=user_id,
    )

    db.add(version)

    return version


# =========================================================
# GET ALL DECISIONS
# =========================================================
@router.get(
    "",
    response_model=List[DecisionResponse],
)
def get_decisions(
    status_filter: Optional[DecisionStatus] = Query(
        default=None,
        alias="status",
    ),
    category: Optional[str] = None,
    q: Optional[str] = None,
    tag: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    sort: str = Query(default="created_at"),
    order: str = Query(default="desc"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = db.query(Decision)

    if status_filter:
        query = query.filter(
            Decision.status == status_filter.value
        )

    if category:
        query = query.filter(
            Decision.category == category
        )

    if q:
        search = f"%{q}%"

        query = query.filter(
            (Decision.title.ilike(search))
            | (Decision.problem_statement.ilike(search))
        )

    if tag:
        query = (
            query
            .join(Decision.tags)
            .filter(Tag.name.ilike(f"%{tag}%"))
        )

    allowed_sort_fields = {
        "id",
        "title",
        "category",
        "status",
        "created_at",
        "updated_at",
    }

    if sort not in allowed_sort_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid sort field",
        )

    sort_column = getattr(Decision, sort)

    if order.lower() == "asc":
        query = query.order_by(sort_column.asc())

    elif order.lower() == "desc":
        query = query.order_by(sort_column.desc())

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must be 'asc' or 'desc'",
        )

    offset = (page - 1) * page_size

    return (
        query
        .offset(offset)
        .limit(page_size)
        .all()
    )


# =========================================================
# CREATE DECISION
# =========================================================
@router.post(
    "",
    response_model=DecisionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_decision(
    decision: DecisionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Decisions are created by Employees.
    if current_user.role not in {
        "Employee",
        "Admin",
        "Administrator",
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only Employees or Administrators "
                "can create decisions"
            ),
        )

    new_decision = Decision(
        title=decision.title,
        problem_statement=decision.problem_statement,
        category=decision.category,
        status="Draft",
        created_by=current_user.id,
    )

    db.add(new_decision)
    db.flush()

    initial_version = DecisionVersion(
        decision_id=new_decision.id,
        version_number=1,
        title=new_decision.title,
        problem_statement=new_decision.problem_statement,
        description=None,
        category=new_decision.category,
        status=new_decision.status,
        created_by=current_user.id,
    )

    db.add(initial_version)

    create_audit_log(
        db=db,
        decision_id=new_decision.id,
        user_id=current_user.id,
        action="CREATE",
        description=(
            f"Decision '{new_decision.title}' was created"
        ),
        entity_type="Decision",
        entity_id=new_decision.id,
        new_value={
            "title": new_decision.title,
            "problem_statement": new_decision.problem_statement,
            "category": new_decision.category,
            "status": new_decision.status,
        },
    )

    create_activity_log(
        db=db,
        user_id=current_user.id,
        action="created",
        entity_type="Decision",
        entity_id=new_decision.id,
        description=(
            f"User {current_user.id} created "
            f"Decision {new_decision.id}"
        ),
    )

    db.commit()
    db.refresh(new_decision)

    return new_decision


# =========================================================
# DECISION SEARCH
# =========================================================
@router.get(
    "/search",
    response_model=List[DecisionResponse],
)
def search_decisions(
    q: str = Query(..., min_length=1),
    category: Optional[str] = None,
    status_filter: Optional[DecisionStatus] = Query(
        default=None,
        alias="status",
    ),
    tag: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = db.query(Decision)

    search = f"%{q}%"

    query = query.filter(
        (Decision.title.ilike(search))
        | (Decision.problem_statement.ilike(search))
    )

    if category:
        query = query.filter(
            Decision.category == category
        )

    if status_filter:
        query = query.filter(
            Decision.status == status_filter.value
        )

    if tag:
        query = (
            query
            .join(Decision.tags)
            .filter(Tag.name.ilike(f"%{tag}%"))
        )

    query = query.order_by(
        Decision.created_at.desc()
    )

    offset = (page - 1) * page_size

    return (
        query
        .offset(offset)
        .limit(page_size)
        .all()
    )


# =========================================================
# DECISION TIMELINE
# =========================================================
@router.get(
    "/{decision_id}/timeline",
)
def get_decision_timeline(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
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

    timeline = []

    if decision.created_at:
        timeline.append(
            {
                "event_type": "Decision Created",
                "timestamp": decision.created_at,
                "description": (
                    f"Decision '{decision.title}' was created"
                ),
            }
        )

    alternatives = (
        db.query(Alternative)
        .filter(
            Alternative.decision_id == decision_id
        )
        .all()
    )

    for alternative in alternatives:
        if alternative.created_at:
            timeline.append(
                {
                    "event_type": "Alternative Added",
                    "timestamp": alternative.created_at,
                    "description": (
                        f"Alternative '{alternative.name}' "
                        f"was added"
                    ),
                }
            )

    comments = (
        db.query(Comment)
        .filter(
            Comment.decision_id == decision_id
        )
        .all()
    )

    for comment in comments:
        if comment.created_at:
            timeline.append(
                {
                    "event_type": "Comment Added",
                    "timestamp": comment.created_at,
                    "description": (
                        "A comment was added to the decision"
                    ),
                }
            )

    threads = (
        db.query(DiscussionThread)
        .filter(
            DiscussionThread.decision_id == decision_id
        )
        .all()
    )

    for thread in threads:
        if thread.created_at:
            timeline.append(
                {
                    "event_type": "Discussion Thread Created",
                    "timestamp": thread.created_at,
                    "description": (
                        "A discussion thread was created"
                    ),
                }
            )

    if (
        decision.updated_at
        and decision.created_at
        and decision.updated_at != decision.created_at
    ):
        timeline.append(
            {
                "event_type": "Decision Updated",
                "timestamp": decision.updated_at,
                "description": (
                    "Decision information was updated"
                ),
            }
        )

    if decision.status == "Approved":
        timeline.append(
            {
                "event_type": "Decision Approved",
                "timestamp": decision.updated_at,
                "description": "Decision was approved",
            }
        )

    elif decision.status == "Rejected":
        timeline.append(
            {
                "event_type": "Decision Rejected",
                "timestamp": decision.updated_at,
                "description": "Decision was rejected",
            }
        )

    elif decision.status == "Archived":
        timeline.append(
            {
                "event_type": "Decision Archived",
                "timestamp": decision.updated_at,
                "description": "Decision was archived",
            }
        )

    timeline.sort(
        key=lambda event: event["timestamp"]
        if event["timestamp"]
        else datetime.min.replace(tzinfo=timezone.utc)
    )

    return {
        "decision_id": decision_id,
        "timeline": timeline,
    }


# =========================================================
# GET DECISION VERSIONS
# =========================================================
@router.get(
    "/{decision_id}/versions",
    response_model=List[DecisionVersionResponse],
)
def get_decision_versions(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
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

    check_decision_history_access(
        decision=decision,
        current_user=current_user,
        db=db,
    )

    versions = (
        db.query(DecisionVersion)
        .filter(
            DecisionVersion.decision_id == decision_id
        )
        .order_by(
            DecisionVersion.version_number.desc()
        )
        .all()
    )

    return versions


# =========================================================
# GET SPECIFIC DECISION VERSION
# =========================================================
@router.get(
    "/{decision_id}/versions/{version_number}",
    response_model=DecisionVersionResponse,
)
def get_decision_version(
    decision_id: int,
    version_number: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
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

    check_decision_history_access(
        decision=decision,
        current_user=current_user,
        db=db,
    )

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


# =========================================================
# GET DECISION HISTORY
# =========================================================
@router.get(
    "/{decision_id}/history",
)
def get_decision_history(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
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

    check_decision_history_access(
        decision=decision,
        current_user=current_user,
        db=db,
    )

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

    audit_logs = (
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

    return {
        "decision_id": decision_id,
        "versions": versions,
        "audit_logs": audit_logs,
    }


# =========================================================
# GET DECISION BY ID
# =========================================================
@router.get(
    "/{decision_id}",
    response_model=DecisionResponse,
)
def get_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
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

    return decision


# =========================================================
# UPDATE DECISION
# =========================================================
@router.put(
    "/{decision_id}",
    response_model=DecisionResponse,
)
def update_decision(
    decision_id: int,
    decision_data: DecisionUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
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

    check_decision_edit_access(
        decision=decision,
        current_user=current_user,
    )

    old_value = {
        "title": decision.title,
        "problem_statement": decision.problem_statement,
        "category": decision.category,
        "status": decision.status,
    }

    decision.title = decision_data.title
    decision.problem_statement = decision_data.problem_statement
    decision.category = decision_data.category

    db.flush()

    new_version = create_decision_version(
        db=db,
        decision=decision,
        user_id=current_user.id,
    )

    new_value = {
        "title": decision.title,
        "problem_statement": decision.problem_statement,
        "category": decision.category,
        "status": decision.status,
    }

    create_audit_log(
        db=db,
        decision_id=decision.id,
        user_id=current_user.id,
        action="UPDATE",
        description=(
            f"Decision '{decision.title}' was updated"
        ),
        entity_type="Decision",
        entity_id=decision.id,
        old_value=old_value,
        new_value=new_value,
    )

    create_activity_log(
        db=db,
        user_id=current_user.id,
        action="updated",
        entity_type="Decision",
        entity_id=decision.id,
        description=(
            f"User {current_user.id} updated "
            f"Decision {decision.id}"
        ),
    )

    db.commit()
    db.refresh(decision)

    return decision


# =========================================================
# UPDATE DECISION STATUS
#
# Controlled lifecycle:
#
# Draft -> Under Review
# Under Review -> Approved  ❌ blocked here
# Under Review -> Rejected  ❌ blocked here
# Approved -> Archived
#
# Approval/rejection must happen through /approvals.
# =========================================================
@router.patch(
    "/{decision_id}/status",
    response_model=DecisionResponse,
)
def update_decision_status(
    decision_id: int,
    status_data: DecisionStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
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

    old_status = decision.status
    new_status = status_data.status.value

    if old_status == new_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Decision already has this status",
        )

    # -----------------------------------------------------
    # Controlled transition: Draft -> Under Review
    # -----------------------------------------------------
    if old_status == "Draft" and new_status == "Under Review":

        if current_user.role not in {
            "Employee",
            "Admin",
            "Administrator",
        }:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Only the decision creator or "
                    "Administrator can submit a decision"
                ),
            )

        if (
            current_user.role == "Employee"
            and decision.created_by != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You can only submit your own decisions"
                ),
            )

        decision.status = "Under Review"

        db.flush()

        create_decision_version(
            db=db,
            decision=decision,
            user_id=current_user.id,
        )

        create_audit_log(
            db=db,
            decision_id=decision.id,
            user_id=current_user.id,
            action="SUBMIT",
            description=(
                f"Decision '{decision.title}' was "
                f"submitted for review"
            ),
            entity_type="Decision",
            entity_id=decision.id,
            old_value={
                "status": old_status,
            },
            new_value={
                "status": new_status,
            },
        )

        create_activity_log(
            db=db,
            user_id=current_user.id,
            action="submitted",
            entity_type="Decision",
            entity_id=decision.id,
            description=(
                f"User {current_user.id} submitted "
                f"Decision {decision.id} for review"
            ),
        )

        db.commit()
        db.refresh(decision)

        return decision

    # -----------------------------------------------------
    # Controlled transition: Approved -> Archived
    # -----------------------------------------------------
    if old_status == "Approved" and new_status == "Archived":

        if current_user.role not in {
            "Manager",
            "Admin",
            "Administrator",
        }:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Only Managers or Administrators "
                    "can archive an approved decision"
                ),
            )

        decision.status = "Archived"

        db.flush()

        create_decision_version(
            db=db,
            decision=decision,
            user_id=current_user.id,
        )

        create_audit_log(
            db=db,
            decision_id=decision.id,
            user_id=current_user.id,
            action="UPDATE",
            description=(
                f"Decision '{decision.title}' was archived"
            ),
            entity_type="Decision",
            entity_id=decision.id,
            old_value={
                "status": old_status,
            },
            new_value={
                "status": new_status,
            },
        )

        create_activity_log(
            db=db,
            user_id=current_user.id,
            action="archived",
            entity_type="Decision",
            entity_id=decision.id,
            description=(
                f"User {current_user.id} archived "
                f"Decision {decision.id}"
            ),
        )

        db.commit()
        db.refresh(decision)

        return decision

    # -----------------------------------------------------
    # Everything else is invalid.
    #
    # This prevents:
    # Draft -> Approved
    # Draft -> Rejected
    # Draft -> Archived
    # Under Review -> Approved
    # Under Review -> Rejected
    # Rejected -> Approved
    # Archived -> anything
    # -----------------------------------------------------
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=(
            f"Invalid decision status transition: "
            f"'{old_status}' -> '{new_status}'. "
            f"Use the Approval workflow for approval/rejection."
        ),
    )


# =========================================================
# DELETE DECISION
# =========================================================
@router.delete(
    "/{decision_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
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

    # Only creator can delete Draft.
    # Administrators can delete any decision.
    if current_user.role in {"Admin", "Administrator"}:
        pass

    elif current_user.role == "Employee":
        if decision.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You can only delete your own decisions"
                ),
            )

        if decision.status != "Draft":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Decision cannot be deleted when its "
                    f"status is '{decision.status}'"
                ),
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only the decision creator or "
                "Administrator can delete a decision"
            ),
        )

    decision_title = decision.title

    create_audit_log(
        db=db,
        decision_id=decision.id,
        user_id=current_user.id,
        action="DELETE",
        description=(
            f"Decision '{decision.title}' was deleted"
        ),
        entity_type="Decision",
        entity_id=decision.id,
        old_value={
            "title": decision.title,
            "problem_statement": decision.problem_statement,
            "category": decision.category,
            "status": decision.status,
        },
    )

    create_activity_log(
        db=db,
        user_id=current_user.id,
        action="deleted",
        entity_type="Decision",
        entity_id=decision.id,
        description=(
            f"User {current_user.id} deleted "
            f"Decision {decision.id} "
            f"('{decision_title}')"
        ),
    )

    db.delete(decision)
    db.commit()

    return None


# =========================================================
# ASSIGN TAGS
# =========================================================
@router.post(
    "/{decision_id}/tags",
    response_model=List[TagResponse],
)
def assign_tags_to_decision(
    decision_id: int,
    tag_data: DecisionTagsUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
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

    check_decision_edit_access(
        decision=decision,
        current_user=current_user,
    )

    tags = (
        db.query(Tag)
        .filter(Tag.id.in_(tag_data.tag_ids))
        .all()
    )

    if len(tags) != len(set(tag_data.tag_ids)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more tags not found",
        )

    existing_tag_ids = {
        tag.id for tag in decision.tags
    }

    added_tags = []

    for tag in tags:
        if tag.id not in existing_tag_ids:
            decision.tags.append(tag)
            added_tags.append(tag)

    for tag in added_tags:
        create_activity_log(
            db=db,
            user_id=current_user.id,
            action="tag_added",
            entity_type="Decision",
            entity_id=decision.id,
            description=(
                f"User {current_user.id} added "
                f"Tag {tag.id} to Decision {decision.id}"
            ),
        )

    db.commit()
    db.refresh(decision)

    return decision.tags


# =========================================================
# GET TAGS
# =========================================================
@router.get(
    "/{decision_id}/tags",
    response_model=List[TagResponse],
)
def get_decision_tags(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
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

    return decision.tags


# =========================================================
# REMOVE TAG
# =========================================================
@router.delete(
    "/{decision_id}/tags/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_tag_from_decision(
    decision_id: int,
    tag_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
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

    check_decision_edit_access(
        decision=decision,
        current_user=current_user,
    )

    tag = (
        db.query(Tag)
        .filter(Tag.id == tag_id)
        .first()
    )

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    if tag not in decision.tags:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag is not assigned to this decision",
        )

    decision.tags.remove(tag)

    create_activity_log(
        db=db,
        user_id=current_user.id,
        action="tag_removed",
        entity_type="Decision",
        entity_id=decision.id,
        description=(
            f"User {current_user.id} removed "
            f"Tag {tag.id} from Decision {decision.id}"
        ),
    )

    db.commit()

    return None