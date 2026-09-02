from datetime import date, datetime
from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.report import (
    ApprovalReportResponse,
    AuditReportResponse,
    DecisionReportResponse,
    TeamReportResponse,
)
from app.services.auth import get_current_user
from app.services.excel_export import (
    generate_approvals_excel,
    generate_audit_excel,
    generate_decisions_excel,
    generate_teams_excel,
)
from app.services.pdf_export import (
    generate_approvals_pdf,
    generate_audit_pdf,
    generate_decisions_pdf,
    generate_teams_pdf,
)
from app.services.report_service import (
    get_approvals_report_data,
    get_audit_report_data,
    get_decisions_report_data,
    get_teams_report_data,
)

router = APIRouter(
    prefix="/reports",
    tags=["Reports & Exports"],
)


# ============================================================
# 1. DECISION REPORTS
# ============================================================

@router.get(
    "/decisions",
    response_model=DecisionReportResponse,
    summary="Generate Decision Management Report",
)
def get_decisions_report(
    category: str | None = Query(default=None, description="Filter by decision category"),
    status: str | None = Query(default=None, description="Filter by decision status (Draft, Under Review, Approved, Rejected, Archived)"),
    created_by: int | None = Query(default=None, description="Filter by creator user ID"),
    start_date: date | None = Query(default=None, description="Start date for decision creation"),
    end_date: date | None = Query(default=None, description="End date for decision creation"),
    tag: str | None = Query(default=None, description="Filter by tag name"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query(default="created_at", description="Sort by field (created_at, updated_at, title, status, category)"),
    sort_order: str = Query(default="desc", description="Sort direction (asc, desc)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, summary, total, total_pages = get_decisions_report_data(
        db=db,
        current_user=current_user,
        category=category,
        decision_status=status,
        created_by=created_by,
        start_date=start_date,
        end_date=end_date,
        tag=tag,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
        paginate=True,
    )
    return DecisionReportResponse(
        summary=summary,
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/decisions/export/pdf",
    summary="Export Decision Report as PDF",
)
def export_decisions_pdf(
    category: str | None = Query(default=None),
    status: str | None = Query(default=None),
    created_by: int | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    tag: str | None = Query(default=None),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, summary, _, _ = get_decisions_report_data(
        db=db,
        current_user=current_user,
        category=category,
        decision_status=status,
        created_by=created_by,
        start_date=start_date,
        end_date=end_date,
        tag=tag,
        sort_by=sort_by,
        sort_order=sort_order,
        paginate=False,
    )
    filters = {
        "Category": category,
        "Status": status,
        "Created By (User ID)": created_by,
        "Start Date": start_date.strftime("%Y-%m-%d") if start_date else None,
        "End Date": end_date.strftime("%Y-%m-%d") if end_date else None,
        "Tag": tag,
    }
    pdf_bytes = generate_decisions_pdf(
        items=items,
        summary=summary,
        filters=filters,
        user_name=current_user.full_name,
    )
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"decisions_report_{timestamp}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get(
    "/decisions/export/excel",
    summary="Export Decision Report as Excel (.xlsx)",
)
def export_decisions_excel(
    category: str | None = Query(default=None),
    status: str | None = Query(default=None),
    created_by: int | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    tag: str | None = Query(default=None),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, summary, _, _ = get_decisions_report_data(
        db=db,
        current_user=current_user,
        category=category,
        decision_status=status,
        created_by=created_by,
        start_date=start_date,
        end_date=end_date,
        tag=tag,
        sort_by=sort_by,
        sort_order=sort_order,
        paginate=False,
    )
    filters = {
        "Category": category,
        "Status": status,
        "Created By (User ID)": created_by,
        "Start Date": start_date.strftime("%Y-%m-%d") if start_date else None,
        "End Date": end_date.strftime("%Y-%m-%d") if end_date else None,
        "Tag": tag,
    }
    excel_bytes = generate_decisions_excel(
        items=items,
        summary=summary,
        filters=filters,
        user_name=current_user.full_name,
    )
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"decisions_report_{timestamp}.xlsx"

    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# ============================================================
# 2. APPROVAL REPORTS
# ============================================================

@router.get(
    "/approvals",
    response_model=ApprovalReportResponse,
    summary="Generate Approval Workflow & Compliance Report",
)
def get_approvals_report(
    status: str | None = Query(default=None, description="Filter by approval status (Pending, Approved, Rejected)"),
    reviewer_id: int | None = Query(default=None, description="Filter by reviewer user ID"),
    decision_id: int | None = Query(default=None, description="Filter by decision ID"),
    approval_level: int | None = Query(default=None, description="Filter by approval level sequence (e.g. 1, 2)"),
    start_date: date | None = Query(default=None, description="Start date for approval assignment"),
    end_date: date | None = Query(default=None, description="End date for approval assignment"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query(default="created_at", description="Sort by field (created_at, completed_at, status, id)"),
    sort_order: str = Query(default="desc", description="Sort direction (asc, desc)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, summary, total, total_pages = get_approvals_report_data(
        db=db,
        current_user=current_user,
        approval_status=status,
        reviewer_id=reviewer_id,
        decision_id=decision_id,
        approval_level=approval_level,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
        paginate=True,
    )
    return ApprovalReportResponse(
        summary=summary,
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/approvals/export/pdf",
    summary="Export Approval Report as PDF",
)
def export_approvals_pdf(
    status: str | None = Query(default=None),
    reviewer_id: int | None = Query(default=None),
    decision_id: int | None = Query(default=None),
    approval_level: int | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, summary, _, _ = get_approvals_report_data(
        db=db,
        current_user=current_user,
        approval_status=status,
        reviewer_id=reviewer_id,
        decision_id=decision_id,
        approval_level=approval_level,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
        sort_order=sort_order,
        paginate=False,
    )
    filters = {
        "Status": status,
        "Reviewer ID": reviewer_id,
        "Decision ID": decision_id,
        "Approval Level": approval_level,
        "Start Date": start_date.strftime("%Y-%m-%d") if start_date else None,
        "End Date": end_date.strftime("%Y-%m-%d") if end_date else None,
    }
    pdf_bytes = generate_approvals_pdf(
        items=items,
        summary=summary,
        filters=filters,
        user_name=current_user.full_name,
    )
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"approvals_report_{timestamp}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get(
    "/approvals/export/excel",
    summary="Export Approval Report as Excel (.xlsx)",
)
def export_approvals_excel(
    status: str | None = Query(default=None),
    reviewer_id: int | None = Query(default=None),
    decision_id: int | None = Query(default=None),
    approval_level: int | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, summary, _, _ = get_approvals_report_data(
        db=db,
        current_user=current_user,
        approval_status=status,
        reviewer_id=reviewer_id,
        decision_id=decision_id,
        approval_level=approval_level,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
        sort_order=sort_order,
        paginate=False,
    )
    filters = {
        "Status": status,
        "Reviewer ID": reviewer_id,
        "Decision ID": decision_id,
        "Approval Level": approval_level,
        "Start Date": start_date.strftime("%Y-%m-%d") if start_date else None,
        "End Date": end_date.strftime("%Y-%m-%d") if end_date else None,
    }
    excel_bytes = generate_approvals_excel(
        items=items,
        summary=summary,
        filters=filters,
        user_name=current_user.full_name,
    )
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"approvals_report_{timestamp}.xlsx"

    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# ============================================================
# 3. TEAM REPORTS
# ============================================================

@router.get(
    "/teams",
    response_model=TeamReportResponse,
    summary="Generate Team Decision & Performance Report",
)
def get_teams_report(
    team: str | None = Query(default=None, description="Filter by team/department name"),
    start_date: date | None = Query(default=None, description="Start date filter"),
    end_date: date | None = Query(default=None, description="End date filter"),
    decision_status: str | None = Query(default=None, description="Filter by decision status"),
    category: str | None = Query(default=None, description="Filter by decision category"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query(default="team_name", description="Sort by field (team_name, number_of_members, total_decisions)"),
    sort_order: str = Query(default="asc", description="Sort direction (asc, desc)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, summary, total, total_pages = get_teams_report_data(
        db=db,
        current_user=current_user,
        team=team,
        start_date=start_date,
        end_date=end_date,
        decision_status=decision_status,
        category=category,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
        paginate=True,
    )
    return TeamReportResponse(
        summary=summary,
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/teams/export/pdf",
    summary="Export Team Report as PDF",
)
def export_teams_pdf(
    team: str | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    decision_status: str | None = Query(default=None),
    category: str | None = Query(default=None),
    sort_by: str = Query(default="team_name"),
    sort_order: str = Query(default="asc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, summary, _, _ = get_teams_report_data(
        db=db,
        current_user=current_user,
        team=team,
        start_date=start_date,
        end_date=end_date,
        decision_status=decision_status,
        category=category,
        sort_by=sort_by,
        sort_order=sort_order,
        paginate=False,
    )
    filters = {
        "Team": team,
        "Decision Status": decision_status,
        "Category": category,
        "Start Date": start_date.strftime("%Y-%m-%d") if start_date else None,
        "End Date": end_date.strftime("%Y-%m-%d") if end_date else None,
    }
    pdf_bytes = generate_teams_pdf(
        items=items,
        summary=summary,
        filters=filters,
        user_name=current_user.full_name,
    )
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"teams_report_{timestamp}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get(
    "/teams/export/excel",
    summary="Export Team Report as Excel (.xlsx)",
)
def export_teams_excel(
    team: str | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    decision_status: str | None = Query(default=None),
    category: str | None = Query(default=None),
    sort_by: str = Query(default="team_name"),
    sort_order: str = Query(default="asc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, summary, _, _ = get_teams_report_data(
        db=db,
        current_user=current_user,
        team=team,
        start_date=start_date,
        end_date=end_date,
        decision_status=decision_status,
        category=category,
        sort_by=sort_by,
        sort_order=sort_order,
        paginate=False,
    )
    filters = {
        "Team": team,
        "Decision Status": decision_status,
        "Category": category,
        "Start Date": start_date.strftime("%Y-%m-%d") if start_date else None,
        "End Date": end_date.strftime("%Y-%m-%d") if end_date else None,
    }
    excel_bytes = generate_teams_excel(
        items=items,
        summary=summary,
        filters=filters,
        user_name=current_user.full_name,
    )
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"teams_report_{timestamp}.xlsx"

    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# ============================================================
# 4. AUDIT REPORTS
# ============================================================

@router.get(
    "/audit",
    response_model=AuditReportResponse,
    summary="Generate System Audit Activity Report (Administrator only)",
)
def get_audit_report(
    user_id: int | None = Query(default=None, description="Filter by user ID"),
    action: str | None = Query(default=None, description="Filter by action type (CREATE, UPDATE, DELETE, STATUS_CHANGE, etc.)"),
    entity_type: str | None = Query(default=None, description="Filter by entity type (Decision, Approval, Comment, etc.)"),
    entity_id: int | None = Query(default=None, description="Filter by entity ID"),
    start_date: date | None = Query(default=None, description="Start date for audit activity"),
    end_date: date | None = Query(default=None, description="End date for audit activity"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query(default="created_at", description="Sort by field (created_at, action, entity_type, user_id, id)"),
    sort_order: str = Query(default="desc", description="Sort direction (asc, desc)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, summary, total, total_pages = get_audit_report_data(
        db=db,
        current_user=current_user,
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
        paginate=True,
    )
    return AuditReportResponse(
        summary=summary,
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/audit/export/pdf",
    summary="Export Audit Activity Report as PDF (Administrator only)",
)
def export_audit_pdf(
    user_id: int | None = Query(default=None),
    action: str | None = Query(default=None),
    entity_type: str | None = Query(default=None),
    entity_id: int | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, summary, _, _ = get_audit_report_data(
        db=db,
        current_user=current_user,
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
        sort_order=sort_order,
        paginate=False,
    )
    filters = {
        "User ID": user_id,
        "Action": action,
        "Entity Type": entity_type,
        "Entity ID": entity_id,
        "Start Date": start_date.strftime("%Y-%m-%d") if start_date else None,
        "End Date": end_date.strftime("%Y-%m-%d") if end_date else None,
    }
    pdf_bytes = generate_audit_pdf(
        items=items,
        summary=summary,
        filters=filters,
        user_name=current_user.full_name,
    )
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"audit_report_{timestamp}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get(
    "/audit/export/excel",
    summary="Export Audit Activity Report as Excel (.xlsx) (Administrator only)",
)
def export_audit_excel(
    user_id: int | None = Query(default=None),
    action: str | None = Query(default=None),
    entity_type: str | None = Query(default=None),
    entity_id: int | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, summary, _, _ = get_audit_report_data(
        db=db,
        current_user=current_user,
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
        sort_order=sort_order,
        paginate=False,
    )
    filters = {
        "User ID": user_id,
        "Action": action,
        "Entity Type": entity_type,
        "Entity ID": entity_id,
        "Start Date": start_date.strftime("%Y-%m-%d") if start_date else None,
        "End Date": end_date.strftime("%Y-%m-%d") if end_date else None,
    }
    excel_bytes = generate_audit_excel(
        items=items,
        summary=summary,
        filters=filters,
        user_name=current_user.full_name,
    )
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"audit_report_{timestamp}.xlsx"

    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
