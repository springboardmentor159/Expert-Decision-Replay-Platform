from datetime import datetime
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.alternative import Alternative
from app.models.approval import Approval
from app.models.decision import Decision
from app.models.user import User


VALID_SORT_FIELDS = {
    "created_date": Decision.created_at,
    "updated_date": Decision.updated_at,
    "title": Decision.title,
}


def get_decision_report(
    db: Session,
    category: Optional[str] = None,
    status: Optional[str] = None,
    created_by: Optional[int] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    tags: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "created_date",
    sort_order: str = "desc",
):
    query = (
        db.query(
            Decision,
            User.full_name.label("creator_name"),
            func.count(
                func.distinct(Alternative.id)
            ).label("alternative_count"),
            func.count(
                func.distinct(Approval.id)
            ).label("approval_count"),
        )
        .join(
            User,
            Decision.created_by == User.id
        )
        .outerjoin(
            Alternative,
            Alternative.decision_id == Decision.id
        )
        .outerjoin(
            Approval,
            Approval.decision_id == Decision.id
        )
        .group_by(
            Decision.id,
            User.full_name
        )
    )

    # Filters
    if category:
        query = query.filter(
            Decision.category == category
        )

    if status:
        query = query.filter(
            Decision.status == status
        )

    if created_by is not None:
        query = query.filter(
            Decision.created_by == created_by
        )

    if date_from:
        query = query.filter(
            Decision.created_at >= date_from
        )

    if date_to:
        query = query.filter(
            Decision.created_at <= date_to
        )

    if tags:
        query = query.filter(
            Decision.tags.ilike(f"%{tags}%")
        )

    total_records = query.count()

    # Controlled sorting
    sort_column = VALID_SORT_FIELDS[sort_by]

    if sort_order == "asc":
        query = query.order_by(
            sort_column.asc()
        )
    else:
        query = query.order_by(
            sort_column.desc()
        )

    offset = (page - 1) * page_size

    rows = (
        query
        .offset(offset)
        .limit(page_size)
        .all()
    )

    data = []

    for (
        decision,
        creator_name,
        alternative_count,
        approval_count,
    ) in rows:

        data.append(
            {
                "decision_id": decision.id,
                "title": decision.title,
                "category": decision.category,
                "status": decision.status,
                "created_by": creator_name,
                "created_date": decision.created_at,
                "updated_date": decision.updated_at,
                "number_of_alternatives": alternative_count,
                "number_of_approvals": approval_count,
                "tags": decision.tags,
            }
        )

    # Summary
    summary_query = db.query(Decision)

    if category:
        summary_query = summary_query.filter(
            Decision.category == category
        )

    if created_by is not None:
        summary_query = summary_query.filter(
            Decision.created_by == created_by
        )

    if date_from:
        summary_query = summary_query.filter(
            Decision.created_at >= date_from
        )

    if date_to:
        summary_query = summary_query.filter(
            Decision.created_at <= date_to
        )

    if tags:
        summary_query = summary_query.filter(
            Decision.tags.ilike(f"%{tags}%")
        )

    summary_decisions = summary_query.all()

    summary = {
        "total": len(summary_decisions),
        "draft": sum(
            1
            for decision in summary_decisions
            if decision.status.lower() == "draft"
        ),
        "under_review": sum(
            1
            for decision in summary_decisions
            if decision.status.lower().replace(
                " ",
                "_"
            ) == "under_review"
        ),
        "approved": sum(
            1
            for decision in summary_decisions
            if decision.status.lower() == "approved"
        ),
        "rejected": sum(
            1
            for decision in summary_decisions
            if decision.status.lower() == "rejected"
        ),
        "archived": sum(
            1
            for decision in summary_decisions
            if decision.status.lower() == "archived"
        ),
    }

    return {
        "data": data,
        "summary": summary,
        "page": page,
        "page_size": page_size,
        "total_records": total_records,
    }