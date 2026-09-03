from datetime import datetime
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy import asc, desc, func
from sqlalchemy.orm import Session, selectinload

from app.core.auth import get_current_user
from app.db.database import get_db
from app.models.approval import Approval
from app.models.audit import AuditLog
from app.models.decision import Decision
from app.models.user import User
from app.schemas.decision import DecisionCategory, DecisionStatus
from app.models.tag import Tag

router = APIRouter(prefix="/reports", tags=["Reports"])


def _role(user: User) -> str:
    return str(user.role).lower()


def _require(user: User, roles: set[str]) -> None:
    if _role(user) not in roles:
        raise HTTPException(status_code=403, detail="Insufficient permission")


def _dates(start_date, end_date):
    if start_date and end_date and end_date < start_date:
        raise HTTPException(status_code=422, detail="end_date must be on or after start_date")


def _page(page, page_size):
    return (page - 1) * page_size


def _decision_query(db, current_user, category, decision_status, created_by, tag, start_date, end_date):
    query = db.query(Decision).options(selectinload(Decision.tags), selectinload(Decision.alternatives)).join(User, Decision.created_by == User.id)
    if _role(current_user) not in {"admin", "administrator", "manager"}:
        query = query.filter(Decision.created_by == current_user.id)
    if category: query = query.filter(Decision.category == category)
    if decision_status: query = query.filter(Decision.status == decision_status)
    if created_by: query = query.filter(Decision.created_by == created_by)
    if tag: query = query.filter(Decision.tags.any(func.lower(Tag.name) == tag.lower()))
    if start_date: query = query.filter(Decision.created_at >= start_date)
    if end_date: query = query.filter(Decision.created_at <= end_date)
    return query


def _decision_rows(query, db):
    decisions = query.all()
    approval_counts = dict(db.query(Approval.decision_id, func.count(Approval.id)).group_by(Approval.decision_id).all())
    return [{"decision_id": d.id, "title": d.title, "category": d.category, "status": d.status, "created_by": d.created_by, "created_date": d.created_at, "updated_date": d.updated_at, "alternatives": len(d.alternatives), "approvals": approval_counts.get(d.id, 0), "tags": [tag.name for tag in d.tags]} for d in decisions]


def _decision_summary(rows):
    counts = {}
    for row in rows: counts[row["status"]] = counts.get(row["status"], 0) + 1
    return {"total_decisions": len(rows), "draft_decisions": counts.get("Draft", 0), "under_review": counts.get("Under Review", 0), "approved_decisions": counts.get("Approved", 0), "rejected_decisions": counts.get("Rejected", 0), "archived_decisions": counts.get("Archived", 0)}


@router.get("/decisions")
def decision_report(category: DecisionCategory | None = None, status: DecisionStatus | None = None, created_by: int | None = Query(None, ge=1), tag: str | None = None, start_date: datetime | None = None, end_date: datetime | None = None, sort: str = Query("created_date", pattern="^(created_date|updated_date|title)$"), order: str = Query("desc", pattern="^(asc|desc)$"), page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _dates(start_date, end_date)
    query = _decision_query(db, current_user, category, status, created_by, tag, start_date, end_date)
    sort_column = {"created_date": Decision.created_at, "updated_date": Decision.updated_at, "title": Decision.title}[sort]
    query = query.order_by((asc if order == "asc" else desc)(sort_column))
    total = query.order_by(None).count()
    all_rows = _decision_rows(query, db)
    return {"items": all_rows[_page(page, page_size):_page(page, page_size) + page_size], "page": page, "page_size": page_size, "total": total, "summary": _decision_summary(all_rows)}


def _approval_rows(db, current_user, approval_status, reviewer_id, decision_id, start_date, end_date):
    query = db.query(Approval, Decision, User).join(Decision, Approval.decision_id == Decision.id).join(User, Approval.reviewer_id == User.id)
    if _role(current_user) not in {"admin", "administrator", "manager"}: query = query.filter(Approval.reviewer_id == current_user.id)
    if approval_status: query = query.filter(Approval.status == approval_status)
    if reviewer_id: query = query.filter(Approval.reviewer_id == reviewer_id)
    if decision_id: query = query.filter(Approval.decision_id == decision_id)
    if start_date: query = query.filter(Approval.created_at >= start_date)
    if end_date: query = query.filter(Approval.created_at <= end_date)
    rows = []
    for approval, decision, reviewer in query.all():
        seconds = (approval.completed_at - approval.created_at).total_seconds() if approval.completed_at else None
        rows.append({"approval_id": approval.id, "decision_id": decision.id, "decision_title": decision.title, "reviewer": reviewer.full_name, "reviewer_id": reviewer.id, "approval_status": approval.status, "assigned_date": approval.created_at, "completed_date": approval.completed_at, "turnaround_seconds": seconds})
    return rows


@router.get("/approvals")
def approval_report(status: str | None = Query(None, pattern="^(Pending|Approved|Rejected)$"), reviewer_id: int | None = Query(None, ge=1), decision_id: int | None = Query(None, ge=1), start_date: datetime | None = None, end_date: datetime | None = None, sort: str = Query("assigned_date", pattern="^(assigned_date|completed_date)$"), order: str = Query("desc", pattern="^(asc|desc)$"), page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _dates(start_date, end_date)
    rows = _approval_rows(db, current_user, status, reviewer_id, decision_id, start_date, end_date)
    rows.sort(key=lambda row: row[sort] or datetime.min, reverse=order == "desc")
    total = len(rows); items = rows[_page(page, page_size):_page(page, page_size) + page_size]
    completed = sum(row["approval_status"] != "Pending" for row in rows); durations = [row["turnaround_seconds"] for row in rows if row["turnaround_seconds"] is not None]
    return {"items": items, "page": page, "page_size": page_size, "total": total, "summary": {"total_approvals": total, "pending_approvals": total - completed, "approved_approvals": sum(row["approval_status"] == "Approved" for row in rows), "rejected_approvals": sum(row["approval_status"] == "Rejected" for row in rows), "average_turnaround_seconds": sum(durations) / len(durations) if durations else None, "completion_rate": round(completed * 100 / total, 2) if total else 0}}


@router.get("/teams")
def team_report(team: str | None = None, category: str | None = None, status: str | None = Query(None, pattern="^(Draft|Under Review|Approved|Rejected|Archived)$"), start_date: datetime | None = None, end_date: datetime | None = None, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require(current_user, {"manager", "admin", "administrator"}); _dates(start_date, end_date)
    query = db.query(User.department, func.count(func.distinct(User.id)).label("members"), func.count(Decision.id).label("decisions")).outerjoin(Decision, Decision.created_by == User.id)
    if team: query = query.filter(User.department == team)
    if category: query = query.filter(Decision.category == category)
    if status: query = query.filter(Decision.status == status)
    if start_date: query = query.filter(Decision.created_at >= start_date)
    if end_date: query = query.filter(Decision.created_at <= end_date)
    departments = [row[0] for row in query.group_by(User.department).all()]
    items = []
    for department in departments:
        decisions = db.query(Decision).join(User, Decision.created_by == User.id).filter(User.department == department)
        if category: decisions = decisions.filter(Decision.category == category)
        if status: decisions = decisions.filter(Decision.status == status)
        if start_date: decisions = decisions.filter(Decision.created_at >= start_date)
        if end_date: decisions = decisions.filter(Decision.created_at <= end_date)
        counts = {value: count for value, count in decisions.with_entities(Decision.status, func.count(Decision.id)).group_by(Decision.status).all()}
        items.append({"team": department, "members": db.query(func.count(User.id)).filter(User.department == department).scalar(), "total_decisions": sum(counts.values()), "approved_decisions": counts.get("Approved", 0), "rejected_decisions": counts.get("Rejected", 0), "pending_decisions": counts.get("Pending", 0) + counts.get("Draft", 0) + counts.get("Under Review", 0)})
    total = len(items); return {"items": items[_page(page, page_size):_page(page, page_size) + page_size], "page": page, "page_size": page_size, "total": total}


@router.get("/audit")
def audit_report(user_id: int | None = Query(None, ge=1), action: str | None = Query(None, pattern="^(CREATE|UPDATE|DELETE|APPROVE|REJECT|SUBMIT|LOGIN|LOGOUT|ACCESS)$"), entity_type: str | None = Query(None, pattern="^(Decision|Alternative|Comment|DiscussionThread|MeetingNote|Approval|User)$"), entity_id: int | None = Query(None, ge=1), start_date: datetime | None = None, end_date: datetime | None = None, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require(current_user, {"admin", "administrator"}); _dates(start_date, end_date)
    query = db.query(AuditLog)
    for field, value in ((AuditLog.user_id, user_id), (AuditLog.action, action), (AuditLog.entity_type, entity_type), (AuditLog.entity_id, entity_id)):
        if value: query = query.filter(field == value)
    if start_date: query = query.filter(AuditLog.created_at >= start_date)
    if end_date: query = query.filter(AuditLog.created_at <= end_date)
    total = query.count(); items = query.order_by(AuditLog.created_at.desc()).offset(_page(page, page_size)).limit(page_size).all()
    return {"items": items, "page": page, "page_size": page_size, "total": total}


def _export_response(title, headers, rows, excel):
    if excel:
        workbook = Workbook(); sheet = workbook.active; sheet.title = "Report"; sheet.append(headers)
        for row in rows: sheet.append([str(row.get(header, "")) for header in headers])
        stream = BytesIO(); workbook.save(stream); media = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"; filename = f"{title.lower().replace(' ', '_')}.xlsx"
    else:
        stream = BytesIO(); document = SimpleDocTemplate(stream, pagesize=landscape(letter)); styles = getSampleStyleSheet(); elements = [Paragraph(title, styles["Title"]), Spacer(1, 12), Paragraph(f"Generated: {datetime.utcnow().isoformat()} UTC", styles["Normal"])]
        data = [headers] + [[str(row.get(header, "")) for header in headers] for row in rows]; table = Table(data, repeatRows=1); table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e79")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), 0.25, colors.grey), ("FONTSIZE", (0, 0), (-1, -1), 7)])); elements.append(table); document.build(elements); media = "application/pdf"; filename = f"{title.lower().replace(' ', '_')}.pdf"
    stream.seek(0); return StreamingResponse(stream, media_type=media, headers={"Content-Disposition": f"attachment; filename={filename}"})


@router.get("/decisions/export/{format}")
def export_decisions(format: str, category: DecisionCategory | None = None, status: DecisionStatus | None = None, created_by: int | None = Query(None, ge=1), tag: str | None = None, start_date: datetime | None = None, end_date: datetime | None = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if format not in {"pdf", "excel"}: raise HTTPException(status_code=422, detail="Unsupported export format")
    _dates(start_date, end_date); rows = _decision_rows(_decision_query(db, current_user, category, status, created_by, tag, start_date, end_date), db); headers = ["decision_id", "title", "category", "status", "created_by", "created_date", "updated_date", "alternatives", "approvals", "tags"]
    return _export_response("Decision Report", headers, rows, format == "excel")


@router.get("/approvals/export/{format}")
def export_approvals(format: str, status: str | None = Query(None, pattern="^(Pending|Approved|Rejected)$"), reviewer_id: int | None = Query(None, ge=1), decision_id: int | None = Query(None, ge=1), start_date: datetime | None = None, end_date: datetime | None = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if format not in {"pdf", "excel"}: raise HTTPException(status_code=422, detail="Unsupported export format")
    _dates(start_date, end_date); rows = _approval_rows(db, current_user, status, reviewer_id, decision_id, start_date, end_date); headers = ["approval_id", "decision_id", "decision_title", "reviewer", "reviewer_id", "approval_status", "assigned_date", "completed_date", "turnaround_seconds"]
    return _export_response("Approval Report", headers, rows, format == "excel")


@router.get("/teams/export/{format}")
def export_teams(format: str, team: str | None = None, category: DecisionCategory | None = None, status: DecisionStatus | None = None, start_date: datetime | None = None, end_date: datetime | None = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if format not in {"pdf", "excel"}: raise HTTPException(status_code=422, detail="Unsupported export format")
    report = team_report(team, category, status, start_date, end_date, 1, 100, current_user, db); headers = ["team", "members", "total_decisions", "approved_decisions", "rejected_decisions", "pending_decisions"]
    return _export_response("Team Report", headers, report["items"], format == "excel")


@router.get("/audit/export/{format}")
def export_audit(format: str, user_id: int | None = Query(None, ge=1), action: str | None = Query(None, pattern="^(CREATE|UPDATE|DELETE|APPROVE|REJECT|SUBMIT|LOGIN|LOGOUT|ACCESS)$"), entity_type: str | None = Query(None, pattern="^(Decision|Alternative|Comment|DiscussionThread|MeetingNote|Approval|User)$"), entity_id: int | None = Query(None, ge=1), start_date: datetime | None = None, end_date: datetime | None = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require(current_user, {"admin", "administrator"})
    if format not in {"pdf", "excel"}: raise HTTPException(status_code=422, detail="Unsupported export format")
    _dates(start_date, end_date); query = db.query(AuditLog)
    for field, value in ((AuditLog.user_id, user_id), (AuditLog.action, action), (AuditLog.entity_type, entity_type), (AuditLog.entity_id, entity_id)):
        if value: query = query.filter(field == value)
    if start_date: query = query.filter(AuditLog.created_at >= start_date)
    if end_date: query = query.filter(AuditLog.created_at <= end_date)
    rows = [row.__dict__ for row in query.order_by(AuditLog.created_at.desc()).limit(1000).all()]; headers = ["user_id", "action", "entity_type", "entity_id", "description", "created_at", "ip_address"]
    return _export_response("Audit Report", headers, rows, format == "excel")
