from datetime import datetime, timezone
from typing import Optional, List
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import and_, or_, func, desc, asc

from app.db.database import get_db
from app.models.decision import Decision
from app.models.approval import Approval
from app.models.user import User
from app.models.audit_log import AuditLog
from app.models.alternative import Alternative
from app.models.tag import Tag
from app.routers.users import get_current_user
from app.schemas.reports import (
    DecisionReportResponse, DecisionReportRow, DecisionReportSummary,
    DecisionReportFilters,
    ApprovalReportResponse, ApprovalReportRow, ApprovalReportSummary,
    ApprovalReportFilters,
    TeamReportResponse, TeamReportRow, TeamDecisionStats, TeamApprovalStats,
    TeamReportFilters,
    AuditReportResponse, AuditReportRow,
    AuditReportFilters,
    ReportSortField, SortOrder
)
from app.utils.report_generator import (
    generate_decisions_pdf, generate_decisions_excel,
    generate_approvals_pdf, generate_approvals_excel,
    generate_teams_pdf, generate_teams_excel,
    generate_audit_pdf, generate_audit_excel
)
from app.utils.authorization import check_authorization

router = APIRouter(prefix="/reports", tags=["Reports"])


# ============ DECISION REPORTS ============

@router.get("/decisions", response_model=DecisionReportResponse)
def get_decision_reports(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    created_by: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    tags: Optional[str] = Query(None),  # Comma-separated tags
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """
    Get decision reports with filtering, sorting, and pagination.
    """
    # Build query
    query = db.query(Decision).options(
        selectinload(Decision.user),
        selectinload(Decision.alternatives),
        selectinload(Decision.approvals),
        selectinload(Decision.tags)
    )

    # Apply filters
    if category:
        query = query.filter(Decision.category == category)
    
    if status:
        query = query.filter(Decision.status == status)
    
    if created_by:
        query = query.filter(Decision.created_by == created_by)
    
    if start_date:
        start_date_utc = start_date.replace(tzinfo=timezone.utc) if start_date.tzinfo is None else start_date
        query = query.filter(Decision.created_at >= start_date_utc)
    
    if end_date:
        end_date_utc = end_date.replace(tzinfo=timezone.utc) if end_date.tzinfo is None else end_date
        query = query.filter(Decision.created_at <= end_date_utc)
    
    if tags:
        tag_list = [t.strip() for t in tags.split(",")]
        query = query.join(Decision.tags).filter(Tag.name.in_(tag_list)).distinct()

    # Calculate summary before pagination
    total_decisions = query.count()
    
    draft = db.query(Decision).filter(Decision.status == "Draft").count()
    under_review = db.query(Decision).filter(Decision.status == "Under Review").count()
    approved = db.query(Decision).filter(Decision.status == "Approved").count()
    rejected = db.query(Decision).filter(Decision.status == "Rejected").count()
    archived = db.query(Decision).filter(Decision.status == "Archived").count()

    summary = DecisionReportSummary(
        total_decisions=total_decisions,
        draft_decisions=draft,
        decisions_under_review=under_review,
        approved_decisions=approved,
        rejected_decisions=rejected,
        archived_decisions=archived
    )

    # Apply sorting
    if sort_by == "created_at":
        sort_column = Decision.created_at
    elif sort_by == "updated_at":
        sort_column = Decision.updated_at
    elif sort_by == "title":
        sort_column = Decision.title
    else:
        sort_column = Decision.created_at

    if sort_order == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    # Apply pagination
    total_records = query.count()
    total_pages = (total_records + page_size - 1) // page_size
    
    decisions = query.offset((page - 1) * page_size).limit(page_size).all()

    # Build response rows
    rows = []
    for decision in decisions:
        row = DecisionReportRow(
            decision_id=decision.id,
            decision_title=decision.title,
            category=decision.category,
            status=decision.status,
            created_by=decision.user.full_name if decision.user else "Unknown",
            created_date=decision.created_at,
            updated_date=decision.updated_at,
            number_of_alternatives=len(decision.alternatives),
            number_of_approvals=len(decision.approvals),
            tags=[tag.name for tag in decision.tags]
        )
        rows.append(row)

    return DecisionReportResponse(
        summary=summary,
        data=rows,
        page=page,
        page_size=page_size,
        total_records=total_records,
        total_pages=total_pages
    )


@router.get("/decisions/export/pdf")
def export_decision_reports_pdf(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    created_by: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    tags: Optional[str] = Query(None)
):
    """
    Export decision reports as PDF.
    """
    # Get the report data
    report = get_decision_reports(
        db=db,
        current_user=current_user,
        category=category,
        status=status,
        created_by=created_by,
        start_date=start_date,
        end_date=end_date,
        tags=tags,
        page=1,
        page_size=10000  # Get all records
    )

    # Generate PDF
    pdf_bytes = generate_decisions_pdf(report, category, status, start_date, end_date)
    
    return StreamingResponse(
        iter([pdf_bytes.getvalue()]),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment;filename=decisions_report.pdf"}
    )


@router.get("/decisions/export/excel")
def export_decision_reports_excel(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    created_by: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    tags: Optional[str] = Query(None)
):
    """
    Export decision reports as Excel.
    """
    # Get the report data
    report = get_decision_reports(
        db=db,
        current_user=current_user,
        category=category,
        status=status,
        created_by=created_by,
        start_date=start_date,
        end_date=end_date,
        tags=tags,
        page=1,
        page_size=10000  # Get all records
    )

    # Generate Excel
    excel_bytes = generate_decisions_excel(report)
    
    return StreamingResponse(
        iter([excel_bytes.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment;filename=decisions_report.xlsx"}
    )


# ============ APPROVAL REPORTS ============

@router.get("/approvals", response_model=ApprovalReportResponse)
def get_approval_reports(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    approval_status: Optional[str] = Query(None),
    reviewer_id: Optional[int] = Query(None),
    decision_id: Optional[int] = Query(None),
    approval_level: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """
    Get approval reports with filtering, sorting, and pagination.
    """
    # Build query
    query = db.query(Approval).options(
        selectinload(Approval.reviewer),
        selectinload(Approval.decision)
    )

    # Apply filters
    if approval_status:
        query = query.filter(Approval.status == approval_status)
    
    if reviewer_id:
        query = query.filter(Approval.reviewer_id == reviewer_id)
    
    if decision_id:
        query = query.filter(Approval.decision_id == decision_id)
    
    if approval_level:
        query = query.filter(Approval.approval_level == approval_level)
    
    if start_date:
        start_date_utc = start_date.replace(tzinfo=timezone.utc) if start_date.tzinfo is None else start_date
        query = query.filter(Approval.created_at >= start_date_utc)
    
    if end_date:
        end_date_utc = end_date.replace(tzinfo=timezone.utc) if end_date.tzinfo is None else end_date
        query = query.filter(Approval.created_at <= end_date_utc)

    # Calculate summary before pagination
    total_approvals = query.count()
    pending = db.query(Approval).filter(Approval.status == "Pending").count()
    approved_count = db.query(Approval).filter(Approval.status == "Approved").count()
    rejected_count = db.query(Approval).filter(Approval.status == "Rejected").count()

    # Calculate average turnaround time (for completed approvals)
    completed_approvals = db.query(Approval).filter(
        Approval.completed_at.isnot(None)
    ).all()
    
    avg_turnaround = 0.0
    if completed_approvals:
        total_hours = 0
        for approval in completed_approvals:
            if approval.completed_at and approval.created_at:
                time_diff = approval.completed_at - approval.created_at
                total_hours += time_diff.total_seconds() / 3600
        avg_turnaround = total_hours / len(completed_approvals)

    # Calculate completion rate
    completion_rate = (approved_count + rejected_count) / total_approvals * 100 if total_approvals > 0 else 0

    summary = ApprovalReportSummary(
        total_approvals=total_approvals,
        pending_approvals=pending,
        approved_approvals=approved_count,
        rejected_approvals=rejected_count,
        average_approval_turnaround_time_hours=avg_turnaround,
        approval_completion_rate=completion_rate
    )

    # Apply sorting
    if sort_by == "created_at":
        sort_column = Approval.created_at
    elif sort_by == "approval_date":
        sort_column = Approval.completed_at
    else:
        sort_column = Approval.created_at

    if sort_order == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    # Apply pagination
    total_records = query.count()
    total_pages = (total_records + page_size - 1) // page_size
    
    approvals = query.offset((page - 1) * page_size).limit(page_size).all()

    # Build response rows
    rows = []
    for approval in approvals:
        turnaround_time = None
        if approval.completed_at and approval.created_at:
            time_diff = approval.completed_at - approval.created_at
            turnaround_time = time_diff.total_seconds() / 3600

        row = ApprovalReportRow(
            approval_id=approval.id,
            decision_id=approval.decision_id,
            decision_title=approval.decision.title if approval.decision else "Unknown",
            reviewer=approval.reviewer.full_name if approval.reviewer else "Unknown",
            approval_level=approval.approval_level,
            approval_status=approval.status,
            assigned_date=approval.created_at,
            completed_date=approval.completed_at,
            approval_turnaround_time_hours=turnaround_time
        )
        rows.append(row)

    return ApprovalReportResponse(
        summary=summary,
        data=rows,
        page=page,
        page_size=page_size,
        total_records=total_records,
        total_pages=total_pages
    )


@router.get("/approvals/export/pdf")
def export_approval_reports_pdf(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    approval_status: Optional[str] = Query(None),
    reviewer_id: Optional[int] = Query(None),
    decision_id: Optional[int] = Query(None),
    approval_level: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    """
    Export approval reports as PDF.
    """
    # Get the report data
    report = get_approval_reports(
        db=db,
        current_user=current_user,
        approval_status=approval_status,
        reviewer_id=reviewer_id,
        decision_id=decision_id,
        approval_level=approval_level,
        start_date=start_date,
        end_date=end_date,
        page=1,
        page_size=10000
    )

    # Generate PDF
    pdf_bytes = generate_approvals_pdf(report, approval_status, start_date, end_date)
    
    return StreamingResponse(
        iter([pdf_bytes.getvalue()]),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment;filename=approvals_report.pdf"}
    )


@router.get("/approvals/export/excel")
def export_approval_reports_excel(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    approval_status: Optional[str] = Query(None),
    reviewer_id: Optional[int] = Query(None),
    decision_id: Optional[int] = Query(None),
    approval_level: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    """
    Export approval reports as Excel.
    """
    # Get the report data
    report = get_approval_reports(
        db=db,
        current_user=current_user,
        approval_status=approval_status,
        reviewer_id=reviewer_id,
        decision_id=decision_id,
        approval_level=approval_level,
        start_date=start_date,
        end_date=end_date,
        page=1,
        page_size=10000
    )

    # Generate Excel
    excel_bytes = generate_approvals_excel(report)
    
    return StreamingResponse(
        iter([excel_bytes.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment;filename=approvals_report.xlsx"}
    )


# ============ TEAM REPORTS ============

@router.get("/teams", response_model=TeamReportResponse)
def get_team_reports(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    team_name: Optional[str] = Query(None),
    decision_status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    sort_by: str = Query("team_name"),
    sort_order: str = Query("asc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """
    Get team reports with filtering, sorting, and pagination.
    """
    # Get all unique departments (teams)
    all_users = db.query(User).all()
    teams_dict = {}
    
    for user in all_users:
        dept = user.department
        if dept not in teams_dict:
            teams_dict[dept] = {
                "members": [],
                "decisions": [],
                "approvals": []
            }
        teams_dict[dept]["members"].append(user)

    # Get decisions and approvals for each team
    decisions = db.query(Decision).options(
        selectinload(Decision.user),
        selectinload(Decision.approvals)
    ).all()

    for decision in decisions:
        if decision.user and decision.user.department in teams_dict:
            teams_dict[decision.user.department]["decisions"].append(decision)

    approvals = db.query(Approval).options(
        selectinload(Approval.reviewer),
        selectinload(Approval.decision)
    ).all()

    for approval in approvals:
        if approval.reviewer and approval.reviewer.department in teams_dict:
            teams_dict[approval.reviewer.department]["approvals"].append(approval)

    # Build report rows
    rows = []
    for team_name_key, team_data in teams_dict.items():
        # Filter by team_name if provided
        if team_name and team_name.lower() not in team_name_key.lower():
            continue

        # Filter decisions by status and category
        filtered_decisions = team_data["decisions"]
        if decision_status:
            filtered_decisions = [d for d in filtered_decisions if d.status == decision_status]
        if category:
            filtered_decisions = [d for d in filtered_decisions if d.category == category]
        if start_date:
            start_date_utc = start_date.replace(tzinfo=timezone.utc) if start_date.tzinfo is None else start_date
            filtered_decisions = [d for d in filtered_decisions if d.created_at >= start_date_utc]
        if end_date:
            end_date_utc = end_date.replace(tzinfo=timezone.utc) if end_date.tzinfo is None else end_date
            filtered_decisions = [d for d in filtered_decisions if d.created_at <= end_date_utc]

        # Calculate decision stats
        decision_stats = TeamDecisionStats(
            total_decisions=len(filtered_decisions),
            approved_decisions=len([d for d in filtered_decisions if d.status == "Approved"]),
            rejected_decisions=len([d for d in filtered_decisions if d.status == "Rejected"]),
            pending_decisions=len([d for d in filtered_decisions if d.status == "Under Review"]),
            draft_decisions=len([d for d in filtered_decisions if d.status == "Draft"])
        )

        # Calculate approval stats
        filtered_approvals = team_data["approvals"]
        if start_date:
            filtered_approvals = [a for a in filtered_approvals if a.created_at >= start_date_utc]
        if end_date:
            filtered_approvals = [a for a in filtered_approvals if a.created_at <= end_date_utc]

        approved_count = len([a for a in filtered_approvals if a.status == "Approved"])
        rejected_count = len([a for a in filtered_approvals if a.status == "Rejected"])
        pending_count = len([a for a in filtered_approvals if a.status == "Pending"])

        avg_turnaround = 0.0
        completed_approvals = [a for a in filtered_approvals if a.completed_at is not None]
        if completed_approvals:
            total_hours = 0
            for approval in completed_approvals:
                if approval.completed_at and approval.created_at:
                    time_diff = approval.completed_at - approval.created_at
                    total_hours += time_diff.total_seconds() / 3600
            avg_turnaround = total_hours / len(completed_approvals)

        approval_stats = TeamApprovalStats(
            total_approvals=len(filtered_approvals),
            pending_approvals=pending_count,
            approved_approvals=approved_count,
            rejected_approvals=rejected_count,
            average_turnaround_time_hours=avg_turnaround
        )

        row = TeamReportRow(
            team_name=team_name_key,
            number_of_members=len(team_data["members"]),
            decision_stats=decision_stats,
            approval_stats=approval_stats
        )
        rows.append(row)

    # Apply sorting
    if sort_by == "team_name":
        rows.sort(key=lambda x: x.team_name, reverse=(sort_order == "desc"))

    # Apply pagination
    total_records = len(rows)
    total_pages = (total_records + page_size - 1) // page_size
    
    paginated_rows = rows[(page - 1) * page_size : page * page_size]

    return TeamReportResponse(
        data=paginated_rows,
        page=page,
        page_size=page_size,
        total_records=total_records,
        total_pages=total_pages
    )


@router.get("/teams/export/pdf")
def export_team_reports_pdf(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    team_name: Optional[str] = Query(None),
    decision_status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    """
    Export team reports as PDF.
    """
    # Get the report data
    report = get_team_reports(
        db=db,
        current_user=current_user,
        team_name=team_name,
        decision_status=decision_status,
        category=category,
        start_date=start_date,
        end_date=end_date,
        page=1,
        page_size=10000
    )

    # Generate PDF
    pdf_bytes = generate_teams_pdf(report, team_name, decision_status, category, start_date, end_date)
    
    return StreamingResponse(
        iter([pdf_bytes.getvalue()]),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment;filename=teams_report.pdf"}
    )


@router.get("/teams/export/excel")
def export_team_reports_excel(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    team_name: Optional[str] = Query(None),
    decision_status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    """
    Export team reports as Excel.
    """
    # Get the report data
    report = get_team_reports(
        db=db,
        current_user=current_user,
        team_name=team_name,
        decision_status=decision_status,
        category=category,
        start_date=start_date,
        end_date=end_date,
        page=1,
        page_size=10000
    )

    # Generate Excel
    excel_bytes = generate_teams_excel(report)
    
    return StreamingResponse(
        iter([excel_bytes.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment;filename=teams_report.xlsx"}
    )


# ============ AUDIT REPORTS ============

@router.get("/audit", response_model=AuditReportResponse)
def get_audit_reports(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """
    Get audit reports with filtering, sorting, and pagination.
    Only administrators can access this endpoint.
    """
    # Check authorization - only administrators can view audit reports
    if current_user.get("role") != "Administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can access audit reports"
        )

    # Build query
    query = db.query(AuditLog).options(
        selectinload(AuditLog.user)
    )

    # Apply filters
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    
    if action:
        query = query.filter(AuditLog.action == action)
    
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    
    if entity_id:
        query = query.filter(AuditLog.entity_id == entity_id)
    
    if start_date:
        start_date_utc = start_date.replace(tzinfo=timezone.utc) if start_date.tzinfo is None else start_date
        query = query.filter(AuditLog.created_at >= start_date_utc)
    
    if end_date:
        end_date_utc = end_date.replace(tzinfo=timezone.utc) if end_date.tzinfo is None else end_date
        query = query.filter(AuditLog.created_at <= end_date_utc)

    # Apply sorting
    if sort_by == "created_at":
        sort_column = AuditLog.created_at
    else:
        sort_column = AuditLog.created_at

    if sort_order == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    # Apply pagination
    total_records = query.count()
    total_pages = (total_records + page_size - 1) // page_size
    
    audit_logs = query.offset((page - 1) * page_size).limit(page_size).all()

    # Build response rows
    rows = []
    for audit_log in audit_logs:
        row = AuditReportRow(
            audit_id=audit_log.id,
            user=audit_log.user.full_name if audit_log.user else "System",
            action=audit_log.action,
            entity_type=audit_log.entity_type,
            entity_id=audit_log.entity_id,
            description=audit_log.description,
            timestamp=audit_log.created_at,
            ip_address=None  # IP address not stored in AuditLog model, but we can add it later
        )
        rows.append(row)

    return AuditReportResponse(
        data=rows,
        page=page,
        page_size=page_size,
        total_records=total_records,
        total_pages=total_pages
    )


@router.get("/audit/export/pdf")
def export_audit_reports_pdf(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    """
    Export audit reports as PDF.
    Only administrators can access this endpoint.
    """
    # Get the report data
    report = get_audit_reports(
        db=db,
        current_user=current_user,
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        start_date=start_date,
        end_date=end_date,
        page=1,
        page_size=10000
    )

    # Generate PDF
    pdf_bytes = generate_audit_pdf(report, user_id, action, entity_type, start_date, end_date)
    
    return StreamingResponse(
        iter([pdf_bytes.getvalue()]),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment;filename=audit_report.pdf"}
    )


@router.get("/audit/export/excel")
def export_audit_reports_excel(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    """
    Export audit reports as Excel.
    Only administrators can access this endpoint.
    """
    # Get the report data
    report = get_audit_reports(
        db=db,
        current_user=current_user,
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        start_date=start_date,
        end_date=end_date,
        page=1,
        page_size=10000
    )

    # Generate Excel
    excel_bytes = generate_audit_excel(report)
    
    return StreamingResponse(
        iter([excel_bytes.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment;filename=audit_report.xlsx"}
    )
