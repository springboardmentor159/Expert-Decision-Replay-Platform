from typing import Optional

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.report import (
    ApprovalReportResponse,
    AuditReportResponse,
    DecisionReportResponse,
    TeamReportResponse,
)
from app.services.excel_export_service import (
    generate_approval_report_excel,
    generate_audit_report_excel,
    generate_decision_report_excel,
    generate_team_report_excel,
)
from app.services.pdf_export_service import (
    generate_approval_report_pdf,
    generate_audit_report_pdf,
    generate_decision_report_pdf,
    generate_team_report_pdf,
)
from app.services.report_service import (
    get_approval_report_data,
    get_audit_report_data,
    get_decision_report_data,
    get_team_report_data,
)

router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)

EXCEL_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
PDF_MIME = "application/pdf"


# =============================================================================
# 1. DECISION REPORTS & EXPORTS
# =============================================================================

@router.get(
    "/decisions",
    response_model=DecisionReportResponse,
    summary="Generate comprehensive Decision Report",
    description="Generate a detailed report of decisions with status summaries, tag associations, and filtering."
)
def get_decisions_report(
    category: Optional[str] = Query(None, description="Filter by decision category"),
    status: Optional[str] = Query(None, description="Filter by status (Draft, Under Review, Approved, Rejected, Archived)"),
    created_by: Optional[int] = Query(None, description="Filter by creator user ID"),
    start_date: Optional[str] = Query(None, description="Start date range filter (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date range filter (YYYY-MM-DD)"),
    tags: Optional[str] = Query(None, description="Filter by associated tag name"),
    sort_by: str = Query("created_at", description="Controlled sort field (created_at, updated_at, title, status, category)"),
    sort_order: str = Query("desc", description="Sort direction (asc, desc)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, summary, total, total_pages = get_decision_report_data(
        db=db,
        category=category,
        status=status,
        created_by=created_by,
        start_date=start_date,
        end_date=end_date,
        tag=tags,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )
    return DecisionReportResponse(
        items=items,
        summary=summary,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/decisions/export/pdf",
    summary="Export Decision Report as PDF",
    description="Download professional PDF document of the filtered decisions report."
)
def export_decisions_pdf(
    category: Optional[str] = Query(None, description="Filter by decision category"),
    status: Optional[str] = Query(None, description="Filter by status (Draft, Under Review, Approved, Rejected, Archived)"),
    created_by: Optional[int] = Query(None, description="Filter by creator user ID"),
    start_date: Optional[str] = Query(None, description="Start date range filter (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date range filter (YYYY-MM-DD)"),
    tags: Optional[str] = Query(None, description="Filter by associated tag name"),
    sort_by: str = Query("created_at", description="Controlled sort field"),
    sort_order: str = Query("desc", description="Sort direction"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, summary, _, _ = get_decision_report_data(
        db=db,
        category=category,
        status=status,
        created_by=created_by,
        start_date=start_date,
        end_date=end_date,
        tag=tags,
        sort_by=sort_by,
        sort_order=sort_order,
        page=None,
        page_size=None,
    )
    filters = {
        "category": category,
        "status": status,
        "created_by": created_by,
        "date_range": f"{start_date} to {end_date}" if (start_date or end_date) else None,
        "tags": tags,
    }
    pdf_bytes = generate_decision_report_pdf(items, summary, filters)
    return Response(
        content=pdf_bytes,
        media_type=PDF_MIME,
        headers={"Content-Disposition": 'attachment; filename="decisions_report.pdf"'}
    )


@router.get(
    "/decisions/export/excel",
    summary="Export Decision Report as Excel",
    description="Download structured Excel (.xlsx) workbook of the filtered decisions report."
)
def export_decisions_excel(
    category: Optional[str] = Query(None, description="Filter by decision category"),
    status: Optional[str] = Query(None, description="Filter by status (Draft, Under Review, Approved, Rejected, Archived)"),
    created_by: Optional[int] = Query(None, description="Filter by creator user ID"),
    start_date: Optional[str] = Query(None, description="Start date range filter (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date range filter (YYYY-MM-DD)"),
    tags: Optional[str] = Query(None, description="Filter by associated tag name"),
    sort_by: str = Query("created_at", description="Controlled sort field"),
    sort_order: str = Query("desc", description="Sort direction"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, summary, _, _ = get_decision_report_data(
        db=db,
        category=category,
        status=status,
        created_by=created_by,
        start_date=start_date,
        end_date=end_date,
        tag=tags,
        sort_by=sort_by,
        sort_order=sort_order,
        page=None,
        page_size=None,
    )
    filters = {
        "category": category,
        "status": status,
        "created_by": created_by,
        "date_range": f"{start_date} to {end_date}" if (start_date or end_date) else None,
        "tags": tags,
    }
    excel_bytes = generate_decision_report_excel(items, summary, filters)
    return Response(
        content=excel_bytes,
        media_type=EXCEL_MIME,
        headers={"Content-Disposition": 'attachment; filename="decisions_report.xlsx"'}
    )


# =============================================================================
# 2. APPROVAL REPORTS & EXPORTS
# =============================================================================

@router.get(
    "/approvals",
    response_model=ApprovalReportResponse,
    summary="Generate comprehensive Approval Report",
    description="Generate a detailed report of approval workflows with turnaround times and completion rate metrics."
)
def get_approvals_report(
    status: Optional[str] = Query(None, description="Filter by approval status (Pending, Approved, Rejected)"),
    reviewer_id: Optional[int] = Query(None, description="Filter by reviewer user ID"),
    decision_id: Optional[int] = Query(None, description="Filter by decision ID"),
    approval_level: Optional[int] = Query(None, description="Filter by approval level hierarchy (1, 2, etc.)"),
    start_date: Optional[str] = Query(None, description="Start date range filter (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date range filter (YYYY-MM-DD)"),
    sort_by: str = Query("created_at", description="Controlled sort field (created_at, completed_at, approval_level, status)"),
    sort_order: str = Query("desc", description="Sort direction (asc, desc)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, summary, total, total_pages = get_approval_report_data(
        db=db,
        status=status,
        reviewer_id=reviewer_id,
        decision_id=decision_id,
        approval_level=approval_level,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )
    return ApprovalReportResponse(
        items=items,
        summary=summary,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/approvals/export/pdf",
    summary="Export Approval Report as PDF",
    description="Download professional PDF document of the filtered approvals report."
)
def export_approvals_pdf(
    status: Optional[str] = Query(None, description="Filter by approval status (Pending, Approved, Rejected)"),
    reviewer_id: Optional[int] = Query(None, description="Filter by reviewer user ID"),
    decision_id: Optional[int] = Query(None, description="Filter by decision ID"),
    approval_level: Optional[int] = Query(None, description="Filter by approval level"),
    start_date: Optional[str] = Query(None, description="Start date range filter (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date range filter (YYYY-MM-DD)"),
    sort_by: str = Query("created_at", description="Controlled sort field"),
    sort_order: str = Query("desc", description="Sort direction"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, summary, _, _ = get_approval_report_data(
        db=db,
        status=status,
        reviewer_id=reviewer_id,
        decision_id=decision_id,
        approval_level=approval_level,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
        sort_order=sort_order,
        page=None,
        page_size=None,
    )
    filters = {
        "status": status,
        "reviewer_id": reviewer_id,
        "decision_id": decision_id,
        "approval_level": approval_level,
        "date_range": f"{start_date} to {end_date}" if (start_date or end_date) else None,
    }
    pdf_bytes = generate_approval_report_pdf(items, summary, filters)
    return Response(
        content=pdf_bytes,
        media_type=PDF_MIME,
        headers={"Content-Disposition": 'attachment; filename="approvals_report.pdf"'}
    )


@router.get(
    "/approvals/export/excel",
    summary="Export Approval Report as Excel",
    description="Download structured Excel (.xlsx) workbook of the filtered approvals report."
)
def export_approvals_excel(
    status: Optional[str] = Query(None, description="Filter by approval status (Pending, Approved, Rejected)"),
    reviewer_id: Optional[int] = Query(None, description="Filter by reviewer user ID"),
    decision_id: Optional[int] = Query(None, description="Filter by decision ID"),
    approval_level: Optional[int] = Query(None, description="Filter by approval level"),
    start_date: Optional[str] = Query(None, description="Start date range filter (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date range filter (YYYY-MM-DD)"),
    sort_by: str = Query("created_at", description="Controlled sort field"),
    sort_order: str = Query("desc", description="Sort direction"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, summary, _, _ = get_approval_report_data(
        db=db,
        status=status,
        reviewer_id=reviewer_id,
        decision_id=decision_id,
        approval_level=approval_level,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
        sort_order=sort_order,
        page=None,
        page_size=None,
    )
    filters = {
        "status": status,
        "reviewer_id": reviewer_id,
        "decision_id": decision_id,
        "approval_level": approval_level,
        "date_range": f"{start_date} to {end_date}" if (start_date or end_date) else None,
    }
    excel_bytes = generate_approval_report_excel(items, summary, filters)
    return Response(
        content=excel_bytes,
        media_type=EXCEL_MIME,
        headers={"Content-Disposition": 'attachment; filename="approvals_report.xlsx"'}
    )


# =============================================================================
# 3. TEAM REPORTS & EXPORTS
# =============================================================================

@router.get(
    "/teams",
    response_model=TeamReportResponse,
    summary="Generate Team Activity & Approval Report",
    description="Generate a team-based report with membership counts, decision statuses, and approval turnaround statistics."
)
def get_teams_report(
    team: Optional[str] = Query(None, description="Filter by team or department name"),
    start_date: Optional[str] = Query(None, description="Start date range filter (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date range filter (YYYY-MM-DD)"),
    status: Optional[str] = Query(None, description="Filter by decision status (Draft, Under Review, Approved, Rejected, Archived)"),
    category: Optional[str] = Query(None, description="Filter by decision category"),
    sort_by: str = Query("team_name", description="Controlled sort field (team_name, number_of_members, total_decisions)"),
    sort_order: str = Query("asc", description="Sort direction (asc, desc)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, summary, total, total_pages = get_team_report_data(
        db=db,
        current_user=current_user,
        team=team,
        start_date=start_date,
        end_date=end_date,
        status=status,
        category=category,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )
    return TeamReportResponse(
        items=items,
        summary=summary,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/teams/export/pdf",
    summary="Export Team Report as PDF",
    description="Download professional PDF document of the team activity report."
)
def export_teams_pdf(
    team: Optional[str] = Query(None, description="Filter by team or department name"),
    start_date: Optional[str] = Query(None, description="Start date range filter (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date range filter (YYYY-MM-DD)"),
    status: Optional[str] = Query(None, description="Filter by decision status"),
    category: Optional[str] = Query(None, description="Filter by decision category"),
    sort_by: str = Query("team_name", description="Controlled sort field"),
    sort_order: str = Query("asc", description="Sort direction"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, summary, _, _ = get_team_report_data(
        db=db,
        current_user=current_user,
        team=team,
        start_date=start_date,
        end_date=end_date,
        status=status,
        category=category,
        sort_by=sort_by,
        sort_order=sort_order,
        page=None,
        page_size=None,
    )
    filters = {
        "team": team,
        "category": category,
        "status": status,
        "date_range": f"{start_date} to {end_date}" if (start_date or end_date) else None,
    }
    pdf_bytes = generate_team_report_pdf(items, summary, filters)
    return Response(
        content=pdf_bytes,
        media_type=PDF_MIME,
        headers={"Content-Disposition": 'attachment; filename="teams_report.pdf"'}
    )


@router.get(
    "/teams/export/excel",
    summary="Export Team Report as Excel",
    description="Download structured Excel (.xlsx) workbook of the team activity report."
)
def export_teams_excel(
    team: Optional[str] = Query(None, description="Filter by team or department name"),
    start_date: Optional[str] = Query(None, description="Start date range filter (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date range filter (YYYY-MM-DD)"),
    status: Optional[str] = Query(None, description="Filter by decision status"),
    category: Optional[str] = Query(None, description="Filter by decision category"),
    sort_by: str = Query("team_name", description="Controlled sort field"),
    sort_order: str = Query("asc", description="Sort direction"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, summary, _, _ = get_team_report_data(
        db=db,
        current_user=current_user,
        team=team,
        start_date=start_date,
        end_date=end_date,
        status=status,
        category=category,
        sort_by=sort_by,
        sort_order=sort_order,
        page=None,
        page_size=None,
    )
    filters = {
        "team": team,
        "category": category,
        "status": status,
        "date_range": f"{start_date} to {end_date}" if (start_date or end_date) else None,
    }
    excel_bytes = generate_team_report_excel(items, summary, filters)
    return Response(
        content=excel_bytes,
        media_type=EXCEL_MIME,
        headers={"Content-Disposition": 'attachment; filename="teams_report.xlsx"'}
    )


# =============================================================================
# 4. AUDIT REPORTS & EXPORTS
# =============================================================================

@router.get(
    "/audit",
    response_model=AuditReportResponse,
    summary="Generate System Audit Activity Report",
    description="Generate audit trail and compliance report for administrators with action and entity breakdowns."
)
def get_audit_report(
    user_id: Optional[int] = Query(None, description="Filter by actor user ID"),
    action: Optional[str] = Query(None, description="Filter by audit action (CREATE, UPDATE, DELETE, APPROVE, REJECT, etc.)"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type (Decision, Alternative, Comment, etc.)"),
    entity_id: Optional[int] = Query(None, description="Filter by target entity ID"),
    start_date: Optional[str] = Query(None, description="Start date range filter (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date range filter (YYYY-MM-DD)"),
    sort_by: str = Query("created_at", description="Controlled sort field (created_at, action, entity_type, user_id)"),
    sort_order: str = Query("desc", description="Sort direction (asc, desc)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
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
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )
    return AuditReportResponse(
        items=items,
        summary=summary,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/audit/export/pdf",
    summary="Export Audit Report as PDF",
    description="Download professional PDF document of the system audit report (Administrator only)."
)
def export_audit_pdf(
    user_id: Optional[int] = Query(None, description="Filter by actor user ID"),
    action: Optional[str] = Query(None, description="Filter by audit action"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    entity_id: Optional[int] = Query(None, description="Filter by target entity ID"),
    start_date: Optional[str] = Query(None, description="Start date range filter (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date range filter (YYYY-MM-DD)"),
    sort_by: str = Query("created_at", description="Controlled sort field"),
    sort_order: str = Query("desc", description="Sort direction"),
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
        page=None,
        page_size=None,
    )
    filters = {
        "user_id": user_id,
        "action": action,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "date_range": f"{start_date} to {end_date}" if (start_date or end_date) else None,
    }
    pdf_bytes = generate_audit_report_pdf(items, summary, filters)
    return Response(
        content=pdf_bytes,
        media_type=PDF_MIME,
        headers={"Content-Disposition": 'attachment; filename="audit_report.pdf"'}
    )


@router.get(
    "/audit/export/excel",
    summary="Export Audit Report as Excel",
    description="Download structured Excel (.xlsx) workbook of the system audit report (Administrator only)."
)
def export_audit_excel(
    user_id: Optional[int] = Query(None, description="Filter by actor user ID"),
    action: Optional[str] = Query(None, description="Filter by audit action"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    entity_id: Optional[int] = Query(None, description="Filter by target entity ID"),
    start_date: Optional[str] = Query(None, description="Start date range filter (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date range filter (YYYY-MM-DD)"),
    sort_by: str = Query("created_at", description="Controlled sort field"),
    sort_order: str = Query("desc", description="Sort direction"),
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
        page=None,
        page_size=None,
    )
    filters = {
        "user_id": user_id,
        "action": action,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "date_range": f"{start_date} to {end_date}" if (start_date or end_date) else None,
    }
    excel_bytes = generate_audit_report_excel(items, summary, filters)
    return Response(
        content=excel_bytes,
        media_type=EXCEL_MIME,
        headers={"Content-Disposition": 'attachment; filename="audit_report.xlsx"'}
    )
