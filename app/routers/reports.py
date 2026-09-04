from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services import report_service as svc
from app.services.export_service import generate_pdf, generate_excel

router = APIRouter(prefix="/reports", tags=["Reports"])

VALID_STATUSES = ["Draft", "Under Review", "Approved", "Rejected", "Archived"]
VALID_SORT_FIELDS = ["created_at", "updated_at", "title"]


def require_admin(current_user: User):
    if current_user.role != "Administrator":
        raise HTTPException(status_code=403, detail="Admin access required")


def parse_date(date_str: str, field_name: str) -> datetime:
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid {field_name} format. Use YYYY-MM-DD."
        )


def get_dates(start_date, end_date):
    start, end = None, None
    if start_date:
        start = parse_date(start_date, "start_date")
    if end_date:
        end = parse_date(end_date, "end_date")
    if start and end and start > end:
        raise HTTPException(
            status_code=422,
            detail="start_date must be before end_date"
        )
    return start, end


@router.get("/decisions")
def decision_report(
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    created_by: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort: str = Query("created_at"),
    order: str = Query("desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if status and status not in VALID_STATUSES:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid status. Valid values: {VALID_STATUSES}"
        )
    if sort not in VALID_SORT_FIELDS:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid sort field. Valid fields: {VALID_SORT_FIELDS}"
        )
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=422, detail="Order must be 'asc' or 'desc'")

    start, end = get_dates(start_date, end_date)

    return svc.get_decision_report(
        db, category, status, created_by,
        start, end, page, page_size, sort, order
    )


@router.get("/decisions/export/pdf")
def decision_report_pdf(
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    created_by: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start, end = get_dates(start_date, end_date)
    data = svc.get_decision_report(db, category, status, created_by, start, end, 1, 1000)

    headers = ["ID", "Title", "Category", "Status", "Created By", "Created At", "Alternatives"]
    rows = [
        [
            str(d["id"]), d["title"], d["category"], d["status"],
            str(d["created_by"]), d["created_at"], str(d["alternatives_count"])
        ]
        for d in data["items"]
    ]

    pdf = generate_pdf("Decision Report", headers, rows, data["summary"])
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=decision_report.pdf"}
    )


@router.get("/decisions/export/excel")
def decision_report_excel(
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    created_by: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start, end = get_dates(start_date, end_date)
    data = svc.get_decision_report(db, category, status, created_by, start, end, 1, 1000)

    headers = ["ID", "Title", "Category", "Status", "Created By", "Created At", "Alternatives"]
    rows = [
        [
            d["id"], d["title"], d["category"], d["status"],
            d["created_by"], d["created_at"], d["alternatives_count"]
        ]
        for d in data["items"]
    ]

    excel = generate_excel("Decision Report", headers, rows, data["summary"])
    return Response(
        content=excel,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=decision_report.xlsx"}
    )



@router.get("/approvals")
def approval_report(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start, end = get_dates(start_date, end_date)
    return svc.get_approval_report(db, start, end, page, page_size)


@router.get("/approvals/export/pdf")
def approval_report_pdf(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start, end = get_dates(start_date, end_date)
    data = svc.get_approval_report(db, start, end, 1, 1000)

    headers = ["Decision ID", "Title", "Status", "Created By", "Created At"]
    rows = [
        [
            str(d["decision_id"]), d["decision_title"], d["status"],
            str(d["created_by"]), d["created_at"]
        ]
        for d in data["items"]
    ]

    pdf = generate_pdf("Approval Report", headers, rows, data["summary"])
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=approval_report.pdf"}
    )


@router.get("/approvals/export/excel")
def approval_report_excel(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start, end = get_dates(start_date, end_date)
    data = svc.get_approval_report(db, start, end, 1, 1000)

    headers = ["Decision ID", "Title", "Status", "Created By", "Created At"]
    rows = [
        [
            d["decision_id"], d["decision_title"], d["status"],
            d["created_by"], d["created_at"]
        ]
        for d in data["items"]
    ]

    excel = generate_excel("Approval Report", headers, rows, data["summary"])
    return Response(
        content=excel,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=approval_report.xlsx"}
    )



@router.get("/teams")
def team_report(
    department: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start, end = get_dates(start_date, end_date)
    return svc.get_team_report(db, department, start, end, page, page_size)


@router.get("/teams/export/pdf")
def team_report_pdf(
    department: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start, end = get_dates(start_date, end_date)
    data = svc.get_team_report(db, department, start, end, 1, 1000)

    headers = ["Department", "Members", "Total", "Approved", "Rejected", "Pending", "Draft"]
    rows = [
        [
            d["department"], str(d["member_count"]), str(d["total_decisions"]),
            str(d["approved_decisions"]), str(d["rejected_decisions"]),
            str(d["pending_decisions"]), str(d["draft_decisions"])
        ]
        for d in data["items"]
    ]

    pdf = generate_pdf("Team Report", headers, rows)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=team_report.pdf"}
    )


@router.get("/teams/export/excel")
def team_report_excel(
    department: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start, end = get_dates(start_date, end_date)
    data = svc.get_team_report(db, department, start, end, 1, 1000)

    headers = ["Department", "Members", "Total", "Approved", "Rejected", "Pending", "Draft"]
    rows = [
        [
            d["department"], d["member_count"], d["total_decisions"],
            d["approved_decisions"], d["rejected_decisions"],
            d["pending_decisions"], d["draft_decisions"]
        ]
        for d in data["items"]
    ]

    excel = generate_excel("Team Report", headers, rows)
    return Response(
        content=excel,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=team_report.xlsx"}
    )



@router.get("/audit")
def audit_report(
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)
    start, end = get_dates(start_date, end_date)
    return svc.get_audit_report(db, user_id, action, entity_type, entity_id, start, end, page, page_size)


@router.get("/audit/export/pdf")
def audit_report_pdf(
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    entity_type: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)
    start, end = get_dates(start_date, end_date)
    data = svc.get_audit_report(db, user_id, action, entity_type, None, start, end, 1, 1000)

    headers = ["ID", "User ID", "Action", "Entity Type", "Entity ID", "Description", "Created At"]
    rows = [
        [
            str(a["id"]), str(a["user_id"]), a["action"],
            str(a["entity_type"]), str(a["entity_id"]),
            str(a["description"]), a["created_at"]
        ]
        for a in data["items"]
    ]

    pdf = generate_pdf("Audit Report", headers, rows)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=audit_report.pdf"}
    )


@router.get("/audit/export/excel")
def audit_report_excel(
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    entity_type: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)
    start, end = get_dates(start_date, end_date)
    data = svc.get_audit_report(db, user_id, action, entity_type, None, start, end, 1, 1000)

    headers = ["ID", "User ID", "Action", "Entity Type", "Entity ID", "Description", "Created At"]
    rows = [
        [
            a["id"], a["user_id"], a["action"],
            a["entity_type"], a["entity_id"],
            a["description"], a["created_at"]
        ]
        for a in data["items"]
    ]

    excel = generate_excel("Audit Report", headers, rows)
    return Response(
        content=excel,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=audit_report.xlsx"}
    )