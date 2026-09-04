from datetime import datetime
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query
)

from fastapi.responses import StreamingResponse

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user

from app.models.user import User
from app.models.decision import Decision
from app.models.alternative import Alternative
from app.models.approval import Approval
from app.models.audit_log import AuditLog
from app.models.team import Team

from app.services.report_export import (
    generate_excel,
    generate_pdf
)


router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


# =========================================================
# COMMON FUNCTIONS
# =========================================================

def validate_date_range(
    start_date: Optional[datetime],
    end_date: Optional[datetime]
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date cannot be greater than end_date"
        )


def validate_pagination(
    page: int,
    page_size: int
):
    if page < 1:
        raise HTTPException(
            status_code=422,
            detail="page must be greater than or equal to 1"
        )

    if page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=422,
            detail="page_size must be between 1 and 100"
        )


def validate_sort(
    sort_by: str,
    sort_order: str,
    allowed_fields: dict
):
    if sort_by not in allowed_fields:
        raise HTTPException(
            status_code=422,
            detail="Invalid sorting field"
        )

    if sort_order.lower() not in ["asc", "desc"]:
        raise HTTPException(
            status_code=422,
            detail="sort_order must be 'asc' or 'desc'"
        )


def check_admin(current_user):
    role = str(
        current_user.get("role", "")
    ).lower()

    if role not in [
        "admin",
        "administrator"
    ]:
        raise HTTPException(
            status_code=403,
            detail="Administrator access required"
        )


# =========================================================
# 1. DECISION REPORT
# =========================================================

@router.get("/decisions")
def get_decision_report(
    category: Optional[str] = None,
    decision_status: Optional[str] = Query(
        default=None,
        alias="status"
    ),
    created_by: Optional[int] = None,
    tag: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,

    page: int = 1,
    page_size: int = 20,

    sort_by: str = "created_at",
    sort_order: str = "desc",

    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    validate_date_range(start_date, end_date)
    validate_pagination(page, page_size)

    allowed_sort_fields = {
        "created_at": Decision.created_at,
        "updated_at": Decision.updated_at,
        "title": Decision.title,
        "status": Decision.status,
        "category": Decision.category
    }

    validate_sort(
        sort_by,
        sort_order,
        allowed_sort_fields
    )

    query = (
        db.query(
            Decision,
            User.full_name.label("creator_name")
        )
        .join(
            User,
            User.id == Decision.created_by
        )
    )

    if category:
        query = query.filter(
            Decision.category == category
        )

    if decision_status:
        allowed_statuses = [
            "Draft",
            "Under Review",
            "Approved",
            "Rejected",
            "Archived"
        ]

        if decision_status not in allowed_statuses:
            raise HTTPException(
                status_code=422,
                detail="Invalid decision status"
            )

        query = query.filter(
            Decision.status == decision_status
        )

    if created_by:
        query = query.filter(
            Decision.created_by == created_by
        )

    if start_date:
        query = query.filter(
            Decision.created_at >= start_date
        )

    if end_date:
        query = query.filter(
            Decision.created_at <= end_date
        )

    if tag:
        query = query.filter(
            Decision.tags.any(
                name=tag
            )
        )

    sort_column = allowed_sort_fields[sort_by]

    if sort_order.lower() == "asc":
        query = query.order_by(
            sort_column.asc()
        )
    else:
        query = query.order_by(
            sort_column.desc()
        )

    total = query.count()

    offset = (
        page - 1
    ) * page_size

    decisions = (
        query
        .offset(offset)
        .limit(page_size)
        .all()
    )

    data = []

    for decision, creator_name in decisions:

        alternative_count = (
            db.query(
                func.count(Alternative.id)
            )
            .filter(
                Alternative.decision_id == decision.id
            )
            .scalar()
        )

        approval_count = (
            db.query(
                func.count(Approval.id)
            )
            .filter(
                Approval.decision_id == decision.id
            )
            .scalar()
        )

        tag_names = [
            tag.name
            for tag in decision.tags
        ]

        data.append({
            "decision_id": decision.id,
            "title": decision.title,
            "category": decision.category,
            "status": decision.status,
            "created_by": creator_name,
            "created_at": decision.created_at,
            "updated_at": decision.updated_at,
            "number_alternatives": alternative_count,
            "number_approvals": approval_count,
            "tags": tag_names
        })

    summary_query = db.query(Decision)

    if category:
        summary_query = summary_query.filter(
            Decision.category == category
        )

    if created_by:
        summary_query = summary_query.filter(
            Decision.created_by == created_by
        )

    if start_date:
        summary_query = summary_query.filter(
            Decision.created_at >= start_date
        )

    if end_date:
        summary_query = summary_query.filter(
            Decision.created_at <= end_date
        )

    if tag:
        summary_query = summary_query.filter(
            Decision.tags.any(
                name=tag
            )
        )

    summary = {
        "total": summary_query.count(),
        "Draft": summary_query.filter(
            Decision.status == "Draft"
        ).count(),
        "Under Review": summary_query.filter(
            Decision.status == "Under Review"
        ).count(),
        "Approved": summary_query.filter(
            Decision.status == "Approved"
        ).count(),
        "Rejected": summary_query.filter(
            Decision.status == "Rejected"
        ).count(),
        "Archived": summary_query.filter(
            Decision.status == "Archived"
        ).count()
    }

    return {
        "report": "Decision Report",
        "page": page,
        "page_size": page_size,
        "total": total,
        "summary": summary,
        "data": data
    }


# =========================================================
# 2. APPROVAL REPORT
# =========================================================

@router.get("/approvals")
def get_approval_report(
    approval_status: Optional[str] = Query(
        default=None,
        alias="status"
    ),
    reviewer: Optional[int] = None,
    decision_id: Optional[int] = None,
    level: Optional[int] = None,

    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,

    page: int = 1,
    page_size: int = 20,

    sort_by: str = "created_at",
    sort_order: str = "desc",

    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    validate_date_range(start_date, end_date)
    validate_pagination(page, page_size)

    allowed_sort_fields = {
        "created_at": Approval.created_at,
        "completed_at": Approval.completed_at,
        "approval_level": Approval.approval_level,
        "status": Approval.status
    }

    validate_sort(
        sort_by,
        sort_order,
        allowed_sort_fields
    )

    query = (
        db.query(
            Approval,
            Decision.title.label("decision_title"),
            User.full_name.label("reviewer_name")
        )
        .join(
            Decision,
            Decision.id == Approval.decision_id
        )
        .join(
            User,
            User.id == Approval.assigned_to
        )
    )

    if approval_status:
        allowed_statuses = [
            "Pending",
            "Approved",
            "Rejected"
        ]

        if approval_status not in allowed_statuses:
            raise HTTPException(
                status_code=422,
                detail="Invalid approval status"
            )

        query = query.filter(
            Approval.status == approval_status
        )

    if reviewer:
        query = query.filter(
            Approval.assigned_to == reviewer
        )

    if decision_id:
        query = query.filter(
            Approval.decision_id == decision_id
        )

    if level:
        query = query.filter(
            Approval.approval_level == level
        )

    if start_date:
        query = query.filter(
            Approval.created_at >= start_date
        )

    if end_date:
        query = query.filter(
            Approval.created_at <= end_date
        )

    sort_column = allowed_sort_fields[sort_by]

    if sort_order.lower() == "asc":
        query = query.order_by(
            sort_column.asc()
        )
    else:
        query = query.order_by(
            sort_column.desc()
        )

    total = query.count()

    approvals = (
        query
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    data = []

    for approval, decision_title, reviewer_name in approvals:

        turnaround_time = None

        if (
            approval.completed_at
            and approval.created_at
        ):
            turnaround_time = (
                approval.completed_at
                - approval.created_at
            ).total_seconds() / 3600

        data.append({
            "approval_id": approval.id,
            "decision_id": approval.decision_id,
            "decision_title": decision_title,
            "reviewer": reviewer_name,
            "approval_level": approval.approval_level,
            "status": approval.status,
            "assigned_date": approval.created_at,
            "completed_date": approval.completed_at,
            "turnaround_time_hours": turnaround_time
        })

    summary_query = db.query(Approval)

    if approval_status:
        summary_query = summary_query.filter(
            Approval.status == approval_status
        )

    if reviewer:
        summary_query = summary_query.filter(
            Approval.assigned_to == reviewer
        )

    if decision_id:
        summary_query = summary_query.filter(
            Approval.decision_id == decision_id
        )

    if level:
        summary_query = summary_query.filter(
            Approval.approval_level == level
        )

    if start_date:
        summary_query = summary_query.filter(
            Approval.created_at >= start_date
        )

    if end_date:
        summary_query = summary_query.filter(
            Approval.created_at <= end_date
        )

    total_approvals = summary_query.count()

    pending = summary_query.filter(
        Approval.status == "Pending"
    ).count()

    approved = summary_query.filter(
        Approval.status == "Approved"
    ).count()

    rejected = summary_query.filter(
        Approval.status == "Rejected"
    ).count()

    completed = approved + rejected

    completion_rate = (
        (completed / total_approvals) * 100
        if total_approvals
        else 0
    )

    completed_records = (
        summary_query
        .filter(
            Approval.completed_at.isnot(None)
        )
        .all()
    )

    turnaround_values = []

    for approval in completed_records:
        if approval.created_at and approval.completed_at:
            hours = (
                approval.completed_at
                - approval.created_at
            ).total_seconds() / 3600

            turnaround_values.append(hours)

    average_turnaround = (
        sum(turnaround_values)
        / len(turnaround_values)
        if turnaround_values
        else 0
    )

    return {
        "report": "Approval Report",
        "page": page,
        "page_size": page_size,
        "total": total,
        "summary": {
            "total": total_approvals,
            "pending": pending,
            "approved": approved,
            "rejected": rejected,
            "average_turnaround_hours": round(
                average_turnaround,
                2
            ),
            "completion_rate": round(
                completion_rate,
                2
            )
        },
        "data": data
    }


# =========================================================
# 3. TEAM REPORT
# =========================================================

@router.get("/teams")
def get_team_report(
    team_id: Optional[int] = None,
    category: Optional[str] = None,
    decision_status: Optional[str] = Query(
        default=None,
        alias="status"
    ),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,

    page: int = 1,
    page_size: int = 20,

    sort_by: str = "name",
    sort_order: str = "asc",

    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    validate_date_range(start_date, end_date)
    validate_pagination(page, page_size)

    role = str(
        current_user.get("role", "")
    ).lower()

    if role not in [
        "admin",
        "administrator",
        "manager"
    ]:
        raise HTTPException(
            status_code=403,
            detail="Manager or Administrator access required"
        )

    if sort_by not in [
        "name"
    ]:
        raise HTTPException(
            status_code=422,
            detail="Invalid sorting field"
        )

    if sort_order.lower() not in [
        "asc",
        "desc"
    ]:
        raise HTTPException(
            status_code=422,
            detail="sort_order must be 'asc' or 'desc'"
        )

    query = db.query(Team)

    if team_id:
        query = query.filter(
            Team.id == team_id
        )

    if sort_order.lower() == "asc":
        query = query.order_by(
            Team.name.asc()
        )
    else:
        query = query.order_by(
            Team.name.desc()
        )

    total = query.count()

    teams = (
        query
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    data = []

    for team in teams:

        member_ids = [
            member.id
            for member in team.members
        ]

        member_count = len(member_ids)

        decision_query = db.query(
            Decision
        )

        if member_ids:
            decision_query = decision_query.filter(
                Decision.created_by.in_(member_ids)
            )
        else:
            decision_query = decision_query.filter(
                Decision.id == -1
            )

        if category:
            decision_query = decision_query.filter(
                Decision.category == category
            )

        if decision_status:
            allowed_statuses = [
                "Draft",
                "Under Review",
                "Approved",
                "Rejected",
                "Archived"
            ]

            if decision_status not in allowed_statuses:
                raise HTTPException(
                    status_code=422,
                    detail="Invalid decision status"
                )

            decision_query = decision_query.filter(
                Decision.status == decision_status
            )

        if start_date:
            decision_query = decision_query.filter(
                Decision.created_at >= start_date
            )

        if end_date:
            decision_query = decision_query.filter(
                Decision.created_at <= end_date
            )

        total_decisions = decision_query.count()

        approved = decision_query.filter(
            Decision.status == "Approved"
        ).count()

        rejected = decision_query.filter(
            Decision.status == "Rejected"
        ).count()

        pending = decision_query.filter(
            Decision.status.in_([
                "Draft",
                "Under Review"
            ])
        ).count()

        approval_total = 0
        approval_approved = 0
        approval_rejected = 0

        if member_ids:

            approval_base = (
                db.query(Approval)
                .join(
                    Decision,
                    Decision.id == Approval.decision_id
                )
                .filter(
                    Decision.created_by.in_(
                        member_ids
                    )
                )
            )

            if start_date:
                approval_base = approval_base.filter(
                    Approval.created_at >= start_date
                )

            if end_date:
                approval_base = approval_base.filter(
                    Approval.created_at <= end_date
                )

            approval_total = approval_base.count()

            approval_approved = (
                approval_base
                .filter(
                    Approval.status == "Approved"
                )
                .count()
            )

            approval_rejected = (
                approval_base
                .filter(
                    Approval.status == "Rejected"
                )
                .count()
            )

        data.append({
            "team_id": team.id,
            "team_name": team.name,
            "member_count": member_count,
            "total_decisions": total_decisions,
            "approved_decisions": approved,
            "rejected_decisions": rejected,
            "pending_decisions": pending,
            "total_approvals": approval_total,
            "approved_approvals": approval_approved,
            "rejected_approvals": approval_rejected
        })

    return {
        "report": "Team Report",
        "page": page,
        "page_size": page_size,
        "total": total,
        "data": data
    }


# =========================================================
# 4. AUDIT REPORT
# =========================================================

@router.get("/audit")
def get_audit_report(
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,

    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,

    page: int = 1,
    page_size: int = 20,

    sort_by: str = "created_at",
    sort_order: str = "desc",

    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    check_admin(current_user)

    validate_date_range(start_date, end_date)
    validate_pagination(page, page_size)

    allowed_sort_fields = {
        "created_at": AuditLog.created_at,
        "action": AuditLog.action,
        "entity_type": AuditLog.entity_type
    }

    validate_sort(
        sort_by,
        sort_order,
        allowed_sort_fields
    )

    query = (
        db.query(
            AuditLog,
            User.full_name.label("user_name")
        )
        .outerjoin(
            User,
            User.id == AuditLog.user_id
        )
    )

    if user_id:
        query = query.filter(
            AuditLog.user_id == user_id
        )

    if action:
        query = query.filter(
            AuditLog.action == action
        )

    if entity_type:
        query = query.filter(
            AuditLog.entity_type == entity_type
        )

    if entity_id:
        query = query.filter(
            AuditLog.entity_id == entity_id
        )

    if start_date:
        query = query.filter(
            AuditLog.created_at >= start_date
        )

    if end_date:
        query = query.filter(
            AuditLog.created_at <= end_date
        )

    sort_column = allowed_sort_fields[sort_by]

    if sort_order.lower() == "asc":
        query = query.order_by(
            sort_column.asc()
        )
    else:
        query = query.order_by(
            sort_column.desc()
        )

    total = query.count()

    logs = (
        query
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    data = []

    for audit, user_name in logs:
        data.append({
            "id": audit.id,
            "user_id": audit.user_id,
            "user": user_name,
            "action": audit.action,
            "entity_type": audit.entity_type,
            "entity_id": audit.entity_id,
            "description": audit.description,
            "timestamp": audit.created_at,
            "ip_address": getattr(
                audit,
                "ip_address",
                None
            )
        })

    return {
        "report": "Audit Report",
        "page": page,
        "page_size": page_size,
        "total": total,
        "data": data
    }


# =========================================================
# 5. DECISION PDF
# =========================================================

@router.get("/decisions/export/pdf")
def export_decision_pdf(
    category: Optional[str] = None,
    decision_status: Optional[str] = Query(default=None, alias="status"),
    created_by: Optional[int] = None,
    tag: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    result = get_decision_report(
        category=category,
        decision_status=decision_status,
        created_by=created_by,
        tag=tag,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
        db=db,
        current_user=current_user
    )

    columns = [
        "Decision ID",
        "Title",
        "Category",
        "Status",
        "Created By",
        "Created Date",
        "Updated Date",
        "Alternatives",
        "Approvals",
        "Tags"
    ]

    rows = []

    for item in result["data"]:
        rows.append([
            item["decision_id"],
            item["title"],
            item["category"],
            item["status"],
            item["created_by"],
            item["created_at"],
            item["updated_at"],
            item["number_alternatives"],
            item["number_approvals"],
            ", ".join(item["tags"])
        ])

    pdf = generate_pdf(
        "Decision Report",
        columns,
        rows,
        [
            f"Total: {result['summary']['total']}",
            f"Draft: {result['summary']['Draft']}",
            f"Under Review: {result['summary']['Under Review']}",
            f"Approved: {result['summary']['Approved']}",
            f"Rejected: {result['summary']['Rejected']}",
            f"Archived: {result['summary']['Archived']}"
        ]
    )

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                "attachment; filename=decision_report.pdf"
        }
    )


# =========================================================
# 6. DECISION EXCEL
# =========================================================

@router.get("/decisions/export/excel")
def export_decision_excel(
    category: Optional[str] = None,
    decision_status: Optional[str] = Query(default=None, alias="status"),
    created_by: Optional[int] = None,
    tag: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    result = get_decision_report(
        category=category,
        decision_status=decision_status,
        created_by=created_by,
        tag=tag,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
        db=db,
        current_user=current_user
    )

    columns = [
        "Decision ID",
        "Title",
        "Category",
        "Status",
        "Created By",
        "Created Date",
        "Updated Date",
        "Alternatives",
        "Approvals",
        "Tags"
    ]

    rows = []

    for item in result["data"]:
        rows.append([
            item["decision_id"],
            item["title"],
            item["category"],
            item["status"],
            item["created_by"],
            item["created_at"],
            item["updated_at"],
            item["number_alternatives"],
            item["number_approvals"],
            ", ".join(item["tags"])
        ])

    excel = generate_excel(
        "Decision Report",
        columns,
        rows
    )

    return StreamingResponse(
        excel,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
                "attachment; filename=decision_report.xlsx"
        }
    )


# =========================================================
# 7. APPROVAL PDF
# =========================================================

@router.get("/approvals/export/pdf")
def export_approval_pdf(
    approval_status: Optional[str] = Query(default=None, alias="status"),
    reviewer: Optional[int] = None,
    decision_id: Optional[int] = None,
    level: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    result = get_approval_report(
        approval_status=approval_status,
        reviewer=reviewer,
        decision_id=decision_id,
        level=level,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
        db=db,
        current_user=current_user
    )

    columns = [
        "Approval ID",
        "Decision ID",
        "Decision",
        "Reviewer",
        "Level",
        "Status",
        "Assigned",
        "Completed",
        "Turnaround Hours"
    ]

    rows = []

    for item in result["data"]:
        rows.append([
            item["approval_id"],
            item["decision_id"],
            item["decision_title"],
            item["reviewer"],
            item["approval_level"],
            item["status"],
            item["assigned_date"],
            item["completed_date"],
            item["turnaround_time_hours"]
        ])

    pdf = generate_pdf(
        "Approval Report",
        columns,
        rows,
        [
            f"Total: {result['summary']['total']}",
            f"Pending: {result['summary']['pending']}",
            f"Approved: {result['summary']['approved']}",
            f"Rejected: {result['summary']['rejected']}",
            f"Average Turnaround: "
            f"{result['summary']['average_turnaround_hours']} hours",
            f"Completion Rate: "
            f"{result['summary']['completion_rate']}%"
        ]
    )

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                "attachment; filename=approval_report.pdf"
        }
    )


# =========================================================
# 8. APPROVAL EXCEL
# =========================================================

@router.get("/approvals/export/excel")
def export_approval_excel(
    approval_status: Optional[str] = Query(default=None, alias="status"),
    reviewer: Optional[int] = None,
    decision_id: Optional[int] = None,
    level: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    result = get_approval_report(
        approval_status=approval_status,
        reviewer=reviewer,
        decision_id=decision_id,
        level=level,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
        db=db,
        current_user=current_user
    )

    columns = [
        "Approval ID",
        "Decision ID",
        "Decision",
        "Reviewer",
        "Level",
        "Status",
        "Assigned",
        "Completed",
        "Turnaround Hours"
    ]

    rows = []

    for item in result["data"]:
        rows.append([
            item["approval_id"],
            item["decision_id"],
            item["decision_title"],
            item["reviewer"],
            item["approval_level"],
            item["status"],
            item["assigned_date"],
            item["completed_date"],
            item["turnaround_time_hours"]
        ])

    excel = generate_excel(
        "Approval Report",
        columns,
        rows
    )

    return StreamingResponse(
        excel,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
                "attachment; filename=approval_report.xlsx"
        }
    )


# =========================================================
# 9. TEAM PDF
# =========================================================

@router.get("/teams/export/pdf")
def export_team_pdf(
    team_id: Optional[int] = None,
    category: Optional[str] = None,
    decision_status: Optional[str] = Query(default=None, alias="status"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "name",
    sort_order: str = "asc",
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    result = get_team_report(
        team_id=team_id,
        category=category,
        decision_status=decision_status,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
        db=db,
        current_user=current_user
    )

    columns = [
        "Team ID",
        "Team Name",
        "Members",
        "Total Decisions",
        "Approved",
        "Rejected",
        "Pending",
        "Total Approvals",
        "Approved Approvals",
        "Rejected Approvals"
    ]

    rows = []

    for item in result["data"]:
        rows.append([
            item["team_id"],
            item["team_name"],
            item["member_count"],
            item["total_decisions"],
            item["approved_decisions"],
            item["rejected_decisions"],
            item["pending_decisions"],
            item["total_approvals"],
            item["approved_approvals"],
            item["rejected_approvals"]
        ])

    pdf = generate_pdf(
        "Team Report",
        columns,
        rows
    )

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                "attachment; filename=team_report.pdf"
        }
    )


# =========================================================
# 10. TEAM EXCEL
# =========================================================

@router.get("/teams/export/excel")
def export_team_excel(
    team_id: Optional[int] = None,
    category: Optional[str] = None,
    decision_status: Optional[str] = Query(default=None, alias="status"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "name",
    sort_order: str = "asc",
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    result = get_team_report(
        team_id=team_id,
        category=category,
        decision_status=decision_status,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
        db=db,
        current_user=current_user
    )

    columns = [
        "Team ID",
        "Team Name",
        "Members",
        "Total Decisions",
        "Approved",
        "Rejected",
        "Pending",
        "Total Approvals",
        "Approved Approvals",
        "Rejected Approvals"
    ]

    rows = []

    for item in result["data"]:
        rows.append([
            item["team_id"],
            item["team_name"],
            item["member_count"],
            item["total_decisions"],
            item["approved_decisions"],
            item["rejected_decisions"],
            item["pending_decisions"],
            item["total_approvals"],
            item["approved_approvals"],
            item["rejected_approvals"]
        ])

    excel = generate_excel(
        "Team Report",
        columns,
        rows
    )

    return StreamingResponse(
        excel,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
                "attachment; filename=team_report.xlsx"
        }
    )


# =========================================================
# 11. AUDIT PDF
# =========================================================

@router.get("/audit/export/pdf")
def export_audit_pdf(
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    check_admin(current_user)

    result = get_audit_report(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
        db=db,
        current_user=current_user
    )

    columns = [
        "ID",
        "User ID",
        "User",
        "Action",
        "Entity Type",
        "Entity ID",
        "Description",
        "Timestamp",
        "IP Address"
    ]

    rows = []

    for item in result["data"]:
        rows.append([
            item["id"],
            item["user_id"],
            item["user"],
            item["action"],
            item["entity_type"],
            item["entity_id"],
            item["description"],
            item["timestamp"],
            item["ip_address"]
        ])

    pdf = generate_pdf(
        "Audit Report",
        columns,
        rows,
        [
            f"Total Audit Records: {result['total']}"
        ]
    )

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                "attachment; filename=audit_report.pdf"
        }
    )


# =========================================================
# 12. AUDIT EXCEL
# =========================================================

@router.get("/audit/export/excel")
def export_audit_excel(
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    check_admin(current_user)

    result = get_audit_report(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
        db=db,
        current_user=current_user
    )

    columns = [
        "ID",
        "User ID",
        "User",
        "Action",
        "Entity Type",
        "Entity ID",
        "Description",
        "Timestamp",
        "IP Address"
    ]

    rows = []

    for item in result["data"]:
        rows.append([
            item["id"],
            item["user_id"],
            item["user"],
            item["action"],
            item["entity_type"],
            item["entity_id"],
            item["description"],
            item["timestamp"],
            item["ip_address"]
        ])

    excel = generate_excel(
        "Audit Report",
        columns,
        rows
    )

    return StreamingResponse(
        excel,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
                "attachment; filename=audit_report.xlsx"
        }
    )