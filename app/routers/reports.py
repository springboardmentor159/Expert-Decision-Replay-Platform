from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
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
from app.services.export_excel import (
    generate_approvals_excel,
    generate_audit_excel,
    generate_decisions_excel,
    generate_teams_excel,
)
from app.services.export_pdf import (
    generate_approvals_pdf,
    generate_audit_pdf,
    generate_decisions_pdf,
    generate_teams_pdf,
)
from app.services.report_service import (
    get_approval_report_data,
    get_audit_report_data,
    get_decision_report_data,
    get_team_report_data,
)

router = APIRouter(
    prefix="/reports",
    tags=["Reports & Exports"]
)


def _validate_pagination(page: int, page_size: int):
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Page number must be greater than or equal to 1"
        )
    if page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Page size must be between 1 and 100"
        )


# =============================================================================
# 1. DECISION REPORTS & EXPORTS
# =============================================================================

@router.get(
    "/decisions",
    response_model=DecisionReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate paginated Decision Report with summary statistics and filters"
)
def get_decision_report(
    category: Optional[str] = Query(None, description="Filter by decision category"),
    status: Optional[str] = Query(None, description="Filter by decision status (Draft, Under Review, Approved, Rejected, Archived)"),
    created_by: Optional[int] = Query(None, description="Filter by creator user ID"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD or ISO 8601)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD or ISO 8601)"),
    tag: Optional[str] = Query(None, description="Filter by tag name"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("created_at", description="Sort field (created_at, updated_at, title, category, status)"),
    sort_order: str = Query("desc", description="Sort direction (asc, desc)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _validate_pagination(page, page_size)
    items, summary, total, _ = get_decision_report_data(
        db=db,
        category=category,
        status_filter=status,
        created_by=created_by,
        start_date=start_date,
        end_date=end_date,
        tag=tag,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )
    return DecisionReportResponse(
        items=items,
        summary=summary,
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get(
    "/decisions/export/pdf",
    status_code=status.HTTP_200_OK,
    summary="Export Decision Report as a formatted PDF document"
)
def export_decisions_pdf(
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status"),
    created_by: Optional[int] = Query(None, description="Filter by creator user ID"),
    start_date: Optional[str] = Query(None, description="Start date"),
    end_date: Optional[str] = Query(None, description="End date"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort direction"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, summary, _, filters_applied = get_decision_report_data(
        db=db,
        category=category,
        status_filter=status,
        created_by=created_by,
        start_date=start_date,
        end_date=end_date,
        tag=tag,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    pdf_bytes = generate_decisions_pdf(items, summary, filters_applied)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"decision_report_{timestamp}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get(
    "/decisions/export/excel",
    status_code=status.HTTP_200_OK,
    summary="Export Decision Report as an Excel spreadsheet (.xlsx)"
)
def export_decisions_excel(
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status"),
    created_by: Optional[int] = Query(None, description="Filter by creator user ID"),
    start_date: Optional[str] = Query(None, description="Start date"),
    end_date: Optional[str] = Query(None, description="End date"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort direction"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, summary, _, filters_applied = get_decision_report_data(
        db=db,
        category=category,
        status_filter=status,
        created_by=created_by,
        start_date=start_date,
        end_date=end_date,
        tag=tag,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    excel_bytes = generate_decisions_excel(items, summary, filters_applied)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"decision_report_{timestamp}.xlsx"

    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# =============================================================================
# 2. APPROVAL REPORTS & EXPORTS
# =============================================================================

@router.get(
    "/approvals",
    response_model=ApprovalReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate paginated Approval Report with performance metrics and turnaround times"
)
def get_approval_report(
    status: Optional[str] = Query(None, description="Filter by approval status (Pending, Approved, Rejected)"),
    reviewer_id: Optional[int] = Query(None, description="Filter by reviewer user ID"),
    decision_id: Optional[int] = Query(None, description="Filter by decision ID"),
    approval_level: Optional[int] = Query(None, description="Filter by approval level"),
    start_date: Optional[str] = Query(None, description="Start date"),
    end_date: Optional[str] = Query(None, description="End date"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("created_at", description="Sort field (created_at, completed_at, approval_level, status)"),
    sort_order: str = Query("desc", description="Sort direction (asc, desc)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _validate_pagination(page, page_size)
    items, summary, total, _ = get_approval_report_data(
        db=db,
        status_filter=status,
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
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get(
    "/approvals/export/pdf",
    status_code=status.HTTP_200_OK,
    summary="Export Approval Report as a formatted PDF document"
)
def export_approvals_pdf(
    status: Optional[str] = Query(None, description="Filter by status"),
    reviewer_id: Optional[int] = Query(None, description="Filter by reviewer ID"),
    decision_id: Optional[int] = Query(None, description="Filter by decision ID"),
    approval_level: Optional[int] = Query(None, description="Filter by approval level"),
    start_date: Optional[str] = Query(None, description="Start date"),
    end_date: Optional[str] = Query(None, description="End date"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort direction"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, summary, _, filters_applied = get_approval_report_data(
        db=db,
        status_filter=status,
        reviewer_id=reviewer_id,
        decision_id=decision_id,
        approval_level=approval_level,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    pdf_bytes = generate_approvals_pdf(items, summary, filters_applied)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"approval_report_{timestamp}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get(
    "/approvals/export/excel",
    status_code=status.HTTP_200_OK,
    summary="Export Approval Report as an Excel spreadsheet (.xlsx)"
)
def export_approvals_excel(
    status: Optional[str] = Query(None, description="Filter by status"),
    reviewer_id: Optional[int] = Query(None, description="Filter by reviewer ID"),
    decision_id: Optional[int] = Query(None, description="Filter by decision ID"),
    approval_level: Optional[int] = Query(None, description="Filter by approval level"),
    start_date: Optional[str] = Query(None, description="Start date"),
    end_date: Optional[str] = Query(None, description="End date"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort direction"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, summary, _, filters_applied = get_approval_report_data(
        db=db,
        status_filter=status,
        reviewer_id=reviewer_id,
        decision_id=decision_id,
        approval_level=approval_level,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    excel_bytes = generate_approvals_excel(items, summary, filters_applied)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"approval_report_{timestamp}.xlsx"

    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# =============================================================================
# 3. TEAM REPORTS & EXPORTS
# =============================================================================

@router.get(
    "/teams",
    response_model=TeamReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Team Report with departmental decision metrics and approval stats"
)
def get_team_report(
    team: Optional[str] = Query(None, description="Filter by team / department name"),
    start_date: Optional[str] = Query(None, description="Start date"),
    end_date: Optional[str] = Query(None, description="End date"),
    status: Optional[str] = Query(None, description="Filter decisions by status"),
    category: Optional[str] = Query(None, description="Filter decisions by category"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("team_name", description="Sort field (team_name, member_count, total_decisions, approved_decisions)"),
    sort_order: str = Query("asc", description="Sort direction (asc, desc)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _validate_pagination(page, page_size)
    items, summary, total, _ = get_team_report_data(
        db=db,
        current_user=current_user,
        team=team,
        start_date=start_date,
        end_date=end_date,
        status_filter=status,
        category=category,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )
    return TeamReportResponse(
        items=items,
        summary=summary,
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get(
    "/teams/export/pdf",
    status_code=status.HTTP_200_OK,
    summary="Export Team Report as a formatted PDF document"
)
def export_teams_pdf(
    team: Optional[str] = Query(None, description="Filter by team name"),
    start_date: Optional[str] = Query(None, description="Start date"),
    end_date: Optional[str] = Query(None, description="End date"),
    status: Optional[str] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    sort_by: str = Query("team_name", description="Sort field"),
    sort_order: str = Query("asc", description="Sort direction"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, summary, _, filters_applied = get_team_report_data(
        db=db,
        current_user=current_user,
        team=team,
        start_date=start_date,
        end_date=end_date,
        status_filter=status,
        category=category,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    pdf_bytes = generate_teams_pdf(items, summary, filters_applied)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"team_report_{timestamp}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get(
    "/teams/export/excel",
    status_code=status.HTTP_200_OK,
    summary="Export Team Report as an Excel spreadsheet (.xlsx)"
)
def export_teams_excel(
    team: Optional[str] = Query(None, description="Filter by team name"),
    start_date: Optional[str] = Query(None, description="Start date"),
    end_date: Optional[str] = Query(None, description="End date"),
    status: Optional[str] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    sort_by: str = Query("team_name", description="Sort field"),
    sort_order: str = Query("asc", description="Sort direction"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, summary, _, filters_applied = get_team_report_data(
        db=db,
        current_user=current_user,
        team=team,
        start_date=start_date,
        end_date=end_date,
        status_filter=status,
        category=category,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    excel_bytes = generate_teams_excel(items, summary, filters_applied)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"team_report_{timestamp}.xlsx"

    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# =============================================================================
# 4. AUDIT REPORTS & EXPORTS (ADMINISTRATOR ONLY)
# =============================================================================

@router.get(
    "/audit",
    response_model=AuditReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate system-wide Audit Report with activity breakdowns (Administrator Only)"
)
def get_audit_report(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    action: Optional[str] = Query(None, description="Filter by action (CREATE, UPDATE, DELETE, etc.)"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type (Decision, Alternative, etc.)"),
    entity_id: Optional[int] = Query(None, description="Filter by entity ID"),
    start_date: Optional[str] = Query(None, description="Start date"),
    end_date: Optional[str] = Query(None, description="End date"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("created_at", description="Sort field (created_at, action, entity_type, user_id)"),
    sort_order: str = Query("desc", description="Sort direction (asc, desc)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _validate_pagination(page, page_size)
    items, summary, total, _ = get_audit_report_data(
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
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get(
    "/audit/export/pdf",
    status_code=status.HTTP_200_OK,
    summary="Export Audit Report as a formatted PDF document (Administrator Only)"
)
def export_audit_pdf(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    action: Optional[str] = Query(None, description="Filter by action"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    entity_id: Optional[int] = Query(None, description="Filter by entity ID"),
    start_date: Optional[str] = Query(None, description="Start date"),
    end_date: Optional[str] = Query(None, description="End date"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort direction"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, summary, _, filters_applied = get_audit_report_data(
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
    )
    pdf_bytes = generate_audit_pdf(items, summary, filters_applied)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"audit_report_{timestamp}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get(
    "/audit/export/excel",
    status_code=status.HTTP_200_OK,
    summary="Export Audit Report as an Excel spreadsheet (.xlsx) (Administrator Only)"
)
def export_audit_excel(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    action: Optional[str] = Query(None, description="Filter by action"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    entity_id: Optional[int] = Query(None, description="Filter by entity ID"),
    start_date: Optional[str] = Query(None, description="Start date"),
    end_date: Optional[str] = Query(None, description="End date"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort direction"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, summary, _, filters_applied = get_audit_report_data(
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
    )
    excel_bytes = generate_audit_excel(items, summary, filters_applied)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"audit_report_{timestamp}.xlsx"

    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
