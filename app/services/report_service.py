from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import Optional

from app.models.decision import Decision
from app.models.alternative import Alternative
from app.models.comment import Comment
from app.models.user import User
from app.models.audit_log import AuditLog



def get_decision_report(
    db: Session,
    category: Optional[str] = None,
    status: Optional[str] = None,
    created_by: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 20,
    sort: str = "created_at",
    order: str = "desc",
):
    query = db.query(Decision)

    if category:
        query = query.filter(Decision.category == category)
    if status:
        query = query.filter(Decision.status == status)
    if created_by:
        query = query.filter(Decision.created_by == created_by)
    if start_date:
        query = query.filter(Decision.created_at >= start_date)
    if end_date:
        query = query.filter(Decision.created_at <= end_date)

    allowed_sort = {
        "created_at": Decision.created_at,
        "updated_at": Decision.updated_at,
        "title": Decision.title,
    }
    sort_col = allowed_sort.get(sort, Decision.created_at)
    query = query.order_by(sort_col.asc() if order == "asc" else sort_col.desc())

    total = query.count()
    decisions = query.offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for d in decisions:
        alt_count = db.query(func.count(Alternative.id)).filter(
            Alternative.decision_id == d.id
        ).scalar()
        items.append({
            "id": d.id,
            "title": d.title,
            "category": d.category,
            "status": d.status,
            "created_by": d.created_by,
            "created_at": str(d.created_at),
            "updated_at": str(d.updated_at),
            "alternatives_count": alt_count,
        })

    # Summary statistics
    base = db.query(Decision)
    if start_date:
        base = base.filter(Decision.created_at >= start_date)
    if end_date:
        base = base.filter(Decision.created_at <= end_date)

    summary = {
        "total": base.count(),
        "draft": base.filter(Decision.status == "Draft").count(),
        "under_review": base.filter(Decision.status == "Under Review").count(),
        "approved": base.filter(Decision.status == "Approved").count(),
        "rejected": base.filter(Decision.status == "Rejected").count(),
        "archived": base.filter(Decision.status == "Archived").count(),
    }

    return {
        "summary": summary,
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items,
    }


def get_approval_report(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 20,
):
    # Since no Approval model exists, use Decision status as proxy
    query = db.query(Decision)

    if start_date:
        query = query.filter(Decision.created_at >= start_date)
    if end_date:
        query = query.filter(Decision.created_at <= end_date)

    total = query.count()
    decisions = query.offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for d in decisions:
        items.append({
            "decision_id": d.id,
            "decision_title": d.title,
            "status": d.status,
            "created_by": d.created_by,
            "created_at": str(d.created_at),
            "updated_at": str(d.updated_at),
        })

    base = db.query(Decision)
    total_decisions = base.count()
    approved = base.filter(Decision.status == "Approved").count()
    rejected = base.filter(Decision.status == "Rejected").count()
    under_review = base.filter(Decision.status == "Under Review").count()

    completion_rate = round(
        (approved + rejected) / total_decisions * 100, 2
    ) if total_decisions > 0 else 0.0

    summary = {
        "total_decisions": total_decisions,
        "approved": approved,
        "rejected": rejected,
        "under_review": under_review,
        "completion_rate": completion_rate,
    }

    return {
        "summary": summary,
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items,
    }




def get_team_report(
    db: Session,
    department: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 20,
):
    # Group by department
    dept_query = db.query(User.department).distinct()
    if department:
        dept_query = dept_query.filter(User.department == department)

    departments = [r.department for r in dept_query.all() if r.department]

    items = []
    for dept in departments:
        members = db.query(User).filter(User.department == dept).all()
        member_ids = [m.id for m in members]

        d_query = db.query(Decision).filter(Decision.created_by.in_(member_ids))
        if start_date:
            d_query = d_query.filter(Decision.created_at >= start_date)
        if end_date:
            d_query = d_query.filter(Decision.created_at <= end_date)

        total_d = d_query.count()
        approved = d_query.filter(Decision.status == "Approved").count()
        rejected = d_query.filter(Decision.status == "Rejected").count()
        pending = d_query.filter(Decision.status == "Under Review").count()
        draft = d_query.filter(Decision.status == "Draft").count()

        items.append({
            "department": dept,
            "member_count": len(members),
            "total_decisions": total_d,
            "approved_decisions": approved,
            "rejected_decisions": rejected,
            "pending_decisions": pending,
            "draft_decisions": draft,
        })

    # Paginate
    total = len(items)
    start = (page - 1) * page_size
    paginated = items[start:start + page_size]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": paginated,
    }




def get_audit_report(
    db: Session,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 20,
):
    query = db.query(AuditLog)

    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if entity_id:
        query = query.filter(AuditLog.entity_id == entity_id)
    if start_date:
        query = query.filter(AuditLog.created_at >= start_date)
    if end_date:
        query = query.filter(AuditLog.created_at <= end_date)

    total = query.count()
    items = (
        query
        .order_by(AuditLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": a.id,
                "user_id": a.user_id,
                "action": a.action,
                "entity_type": a.entity_type,
                "entity_id": a.entity_id,
                "description": a.description,
                "old_value": a.old_value,
                "new_value": a.new_value,
                "created_at": str(a.created_at),
            }
            for a in items
        ],
    }