from enum import Enum
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from app.db.database import get_db
from app.models.alternative import Alternative
from app.models.comment import Comment
from app.models.decision import Decision
from app.models.discussion_thread import DiscussionThread
from app.models.tag import Tag
from app.schemas.decision import (
    DecisionCreate, DecisionResponse,
    DecisionCategory, DecisionStatus, DecisionStatusUpdate, DecisionUpdate,
    PaginatedDecisionResponse, TimelineEvent,
)
from app.schemas.tag import DecisionTagsUpdate, TagResponse
from app.routers.users import get_current_user
from app.utils.activity_logger import log_activity
from app.utils.audit_logger import log_audit, snapshot_decision, log_access

router = APIRouter(prefix="/decisions", tags=["Decisions"])


class SortField(str, Enum):
    created_at = "created_at"
    updated_at = "updated_at"
    title = "title"


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


def _decision_query(db: Session, keyword: Optional[str], category, decision_status, tag: Optional[str]):
    query = db.query(Decision).options(selectinload(Decision.tags))
    if keyword:
        pattern = f"%{keyword}%"
        query = query.filter(or_(
            Decision.title.ilike(pattern),
            Decision.problem_statement.ilike(pattern),
            Decision.rationale.ilike(pattern),
        ))
    if category:
        query = query.filter(Decision.category == category.value)
    if decision_status:
        query = query.filter(Decision.status == decision_status.value)
    if tag:
        query = query.join(Decision.tags).filter(Tag.name.ilike(tag))
    return query.distinct()


def _paged_decisions(db, keyword, category, decision_status, tag, page, page_size, sort, order):
    query = _decision_query(db, keyword, category, decision_status, tag)
    sort_column = getattr(Decision, sort.value)
    query = query.order_by(sort_column.asc() if order == SortOrder.asc else sort_column.desc())
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {"items": items, "page": page, "page_size": page_size, "total": total}


@router.post("", response_model=DecisionResponse, status_code=status.HTTP_201_CREATED)
def create_decision(decision: DecisionCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    new_decision = Decision(
        title=decision.title, problem_statement=decision.problem_statement,
        rationale=decision.rationale, category=decision.category,
        status=DecisionStatus.Draft.value, created_by=int(current_user["sub"]),
    )
    db.add(new_decision)
    db.flush()
    log_activity(db, int(current_user["sub"]), "decision_created", "Decision", new_decision.id, f"Decision {new_decision.id} created")
    snapshot_decision(db, new_decision, int(current_user["sub"]))
    log_audit(db, int(current_user["sub"]), "CREATE", "Decision", new_decision.id, f"Decision {new_decision.id} created", new_value={"title": new_decision.title, "category": new_decision.category, "status": new_decision.status})
    db.commit()
    db.refresh(new_decision)
    return new_decision


@router.get("", response_model=PaginatedDecisionResponse)
def get_decisions(
    status_filter: Optional[DecisionStatus] = Query(None, alias="status"),
    category: Optional[DecisionCategory] = None, tag: Optional[str] = None,
    page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100),
    sort: SortField = SortField.created_at, order: SortOrder = SortOrder.desc,
    db: Session = Depends(get_db), current_user=Depends(get_current_user),
):
    return _paged_decisions(db, None, category, status_filter, tag, page, page_size, sort, order)


@router.get("/search", response_model=PaginatedDecisionResponse)
def search_decisions(
    q: str = Query(..., min_length=1),
    status_filter: Optional[DecisionStatus] = Query(None, alias="status"),
    category: Optional[DecisionCategory] = None, tag: Optional[str] = None,
    page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100),
    sort: SortField = SortField.created_at, order: SortOrder = SortOrder.desc,
    db: Session = Depends(get_db), current_user=Depends(get_current_user),
):
    return _paged_decisions(db, q, category, status_filter, tag, page, page_size, sort, order)


def _find_decision(decision_id, db):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    return decision


@router.get("/{decision_id}/tags", response_model=list[TagResponse])
def get_decision_tags(decision_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return _find_decision(decision_id, db).tags


@router.post("/{decision_id}/tags", response_model=list[TagResponse])
def assign_decision_tags(decision_id: int, tag_data: DecisionTagsUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    decision = _find_decision(decision_id, db)
    tags = db.query(Tag).filter(Tag.id.in_(tag_data.tag_ids)).all()
    if len(tags) != len(set(tag_data.tag_ids)):
        raise HTTPException(status_code=404, detail="One or more tags not found")
    existing_ids = {tag.id for tag in decision.tags}
    decision.tags.extend(tag for tag in tags if tag.id not in existing_ids)
    db.commit()
    db.refresh(decision)
    return decision.tags


@router.delete("/{decision_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_decision_tag(decision_id: int, tag_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    decision = _find_decision(decision_id, db)
    tag = next((item for item in decision.tags if item.id == tag_id), None)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag association not found")
    decision.tags.remove(tag)
    db.commit()


@router.get("/{decision_id}/timeline", response_model=list[TimelineEvent])
def get_decision_timeline(decision_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    decision = _find_decision(decision_id, db)
    events = [TimelineEvent(event_type="decision_created", description="Decision created", occurred_at=decision.created_at)]
    for model, event_type, description in (
        (Alternative, "alternative_created", "Alternative added"),
        (DiscussionThread, "discussion_started", "Discussion thread created"),
        (Comment, "comment_added", "Comment added"),
    ):
        records = db.query(model).filter(model.decision_id == decision_id).all()
        events.extend(TimelineEvent(event_type=event_type, description=description, occurred_at=record.created_at) for record in records)
    if decision.status != DecisionStatus.Draft.value:
        events.append(TimelineEvent(
            event_type=f"decision_{decision.status.lower().replace(' ', '_')}",
            description=f"Decision {decision.status.lower()}", occurred_at=decision.updated_at,
        ))
    return sorted(events, key=lambda event: event.occurred_at)


@router.get("/{decision_id}", response_model=DecisionResponse)
def get_decision(decision_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    decision = _find_decision(decision_id, db)
    log_access(db, int(current_user["sub"]), "Decision", decision.id, "VIEW")
    db.commit()
    return decision


@router.put("/{decision_id}", response_model=DecisionResponse)
def update_decision(decision_id: int, decision_data: DecisionUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    decision = _find_decision(decision_id, db)
    if decision.status == DecisionStatus.Archived.value:
        raise HTTPException(status_code=403, detail="Archived decisions cannot be modified")
    old_value = {"title": decision.title, "problem_statement": decision.problem_statement, "category": decision.category, "rationale": decision.rationale}
    decision.title = decision_data.title
    decision.problem_statement = decision_data.problem_statement
    decision.category = decision_data.category
    decision.rationale = decision_data.rationale
    log_activity(db, int(current_user["sub"]), "decision_updated", "Decision", decision.id, f"Decision {decision.id} updated")
    snapshot_decision(db, decision, int(current_user["sub"]))
    log_audit(db, int(current_user["sub"]), "UPDATE", "Decision", decision.id, f"Decision {decision.id} updated", old_value=old_value, new_value={"title": decision.title, "problem_statement": decision.problem_statement, "category": decision.category, "rationale": decision.rationale})
    db.commit()
    db.refresh(decision)
    return decision


@router.patch("/{decision_id}/status", response_model=DecisionResponse)
def update_decision_status(decision_id: int, status_data: DecisionStatusUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    decision = _find_decision(decision_id, db)
    old_status = decision.status
    new_status = status_data.status.value
    role = current_user.get("role")
    allowed_transitions = {
        "Draft": {"Under Review"},
        "Under Review": {"Approved", "Rejected"},
        "Approved": {"Archived"},
        "Rejected": {"Archived"},
        "Archived": set(),
    }
    if new_status not in allowed_transitions.get(old_status, set()):
        raise HTTPException(status_code=409, detail=f"Invalid status transition from {old_status} to {new_status}")
    if new_status == "Under Review" and role not in ("Employee", "Manager", "Administrator"):
        raise HTTPException(status_code=403, detail="Only decision owners, managers, or administrators can submit decisions")
    if new_status in ("Approved", "Rejected") and role not in ("Reviewer", "Manager", "Administrator"):
        raise HTTPException(status_code=403, detail="Only reviewers, managers, or administrators can decide outcomes")
    if new_status == "Archived" and role != "Administrator":
        raise HTTPException(status_code=403, detail="Only administrators can archive decisions")
    decision.status = new_status
    log_activity(db, int(current_user["sub"]), "decision_status_changed", "Decision", decision.id, f"Decision {decision.id} status changed to {decision.status}")
    snapshot_decision(db, decision, int(current_user["sub"]))
    action = "APPROVE" if decision.status == "Approved" else "REJECT" if decision.status == "Rejected" else "UPDATE"
    log_audit(db, int(current_user["sub"]), action, "Decision", decision.id, f"Decision status changed to {decision.status}", old_value={"status": old_status}, new_value={"status": decision.status})
    db.commit()
    db.refresh(decision)
    return decision