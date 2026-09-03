from datetime import date
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user
from app.core.enums import UserRole

from app.services.reports import (
    get_decision_report,
    get_approval_report,
    get_team_report,
    get_audit_report,
)

from app.services.report_pdf import (
    generate_decision_pdf,
    generate_approval_pdf,
    generate_team_pdf,
    generate_audit_pdf,
)

from app.services.report_excel import (
    generate_decision_excel,
    generate_approval_excel,
    generate_team_excel,
    generate_audit_excel,
)

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


# =========================================================
# AUTHORIZATION
# =========================================================

def require_report_access(current_user):
    allowed_roles = {
        UserRole.EMPLOYEE,
        UserRole.REVIEWER,
        UserRole.MANAGER,
        UserRole.ADMINISTRATOR,
    }

    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access reports",
        )


def require_audit_access(current_user):
    allowed_roles = {
        UserRole.MANAGER,
        UserRole.ADMINISTRATOR,
    }

    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access audit reports",
        )


# =========================================================
# DECISION REPORT
# =========================================================

@router.get("/decisions")
def decision_report(
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    created_by: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    tag: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
    order: str = Query("desc"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_report_access(current_user)

    allowed_sort_fields = {
        "id",
        "title",
        "category",
        "status",
        "created_at",
        "updated_at",
    }

    if sort_by not in allowed_sort_fields:
        raise HTTPException(
            status_code=422,
            detail="Invalid sort_by value",
        )

    if order not in {"asc", "desc"}:
        raise HTTPException(
            status_code=422,
            detail="order must be asc or desc",
        )

    allowed_statuses = {
        "Draft",
        "Under Review",
        "Approved",
        "Rejected",
        "Archived",
    }

    if status and status not in allowed_statuses:
        raise HTTPException(
            status_code=422,
            detail="Invalid decision status",
        )

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date cannot be after end_date",
        )

    return get_decision_report(
        db=db,
        category=category,
        status=status,
        created_by=created_by,
        start_date=start_date,
        end_date=end_date,
        tag=tag,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        order=order,
    )


# =========================================================
# APPROVAL REPORT
# =========================================================

@router.get("/approvals")
def approval_report(
    status: Optional[str] = Query(None),
    reviewer: Optional[int] = Query(None),
    decision: Optional[int] = Query(None),
    approval_level: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("assigned_at"),
    order: str = Query("desc"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_report_access(current_user)

    allowed_statuses = {
        "Pending",
        "Approved",
        "Rejected",
    }

    if status and status not in allowed_statuses:
        raise HTTPException(
            status_code=422,
            detail="Invalid approval status",
        )

    allowed_roles = {
        "Employee",
        "Reviewer",
        "Manager",
        "Administrator",
    }

    if approval_level and approval_level not in allowed_roles:
        raise HTTPException(
            status_code=422,
            detail="Invalid approval level",
        )

    allowed_sort_fields = {
        "id",
        "decision_id",
        "assigned_at",
        "reviewed_at",
        "status",
    }

    if sort_by not in allowed_sort_fields:
        raise HTTPException(
            status_code=422,
            detail="Invalid sort_by value",
        )

    if order not in {"asc", "desc"}:
        raise HTTPException(
            status_code=422,
            detail="order must be asc or desc",
        )

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date cannot be after end_date",
        )

    return get_approval_report(
        db=db,
        status=status,
        reviewer=reviewer,
        decision=decision,
        approval_level=approval_level,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        order=order,
    )


# =========================================================
# TEAM REPORT
# =========================================================

@router.get("/teams")
def team_report(
    team: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    decision_status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("team"),
    order: str = Query("asc"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_report_access(current_user)

    allowed_statuses = {
        "Draft",
        "Under Review",
        "Approved",
        "Rejected",
        "Archived",
    }

    if (
        decision_status
        and decision_status not in allowed_statuses
    ):
        raise HTTPException(
            status_code=422,
            detail="Invalid decision status",
        )

    allowed_sort_fields = {
        "team",
        "member_count",
        "total_decisions",
        "approved",
        "rejected",
    }

    if sort_by not in allowed_sort_fields:
        raise HTTPException(
            status_code=422,
            detail="Invalid sort_by value",
        )

    if order not in {"asc", "desc"}:
        raise HTTPException(
            status_code=422,
            detail="order must be asc or desc",
        )

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date cannot be after end_date",
        )

    return get_team_report(
        db=db,
        team=team,
        start_date=start_date,
        end_date=end_date,
        decision_status=decision_status,
        category=category,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        order=order,
    )


# =========================================================
# AUDIT REPORT
# =========================================================

@router.get("/audit")
def audit_report(
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
    order: str = Query("desc"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_audit_access(current_user)

    allowed_sort_fields = {
        "id",
        "action",
        "entity_type",
        "entity_id",
        "created_at",
    }

    if sort_by not in allowed_sort_fields:
        raise HTTPException(
            status_code=422,
            detail="Invalid sort_by value",
        )

    if order not in {"asc", "desc"}:
        raise HTTPException(
            status_code=422,
            detail="order must be asc or desc",
        )

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date cannot be after end_date",
        )

    return get_audit_report(
        db=db,
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        order=order,
    )


# =========================================================
# DECISION PDF EXPORT
# =========================================================

@router.get("/decisions/export/pdf")
def export_decisions_pdf(
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    created_by: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    tag: Optional[str] = Query(None),
    page_size: int = Query(100, ge=1, le=1000),
    sort_by: str = Query("created_at"),
    order: str = Query("desc"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_report_access(current_user)

    allowed_sort_fields = {
        "id",
        "title",
        "category",
        "status",
        "created_at",
        "updated_at",
    }

    if sort_by not in allowed_sort_fields:
        raise HTTPException(
            status_code=422,
            detail="Invalid sort_by value",
        )

    if order not in {"asc", "desc"}:
        raise HTTPException(
            status_code=422,
            detail="order must be asc or desc",
        )

    allowed_statuses = {
        "Draft",
        "Under Review",
        "Approved",
        "Rejected",
        "Archived",
    }

    if status and status not in allowed_statuses:
        raise HTTPException(
            status_code=422,
            detail="Invalid decision status",
        )

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date cannot be after end_date",
        )

    report = get_decision_report(
        db=db,
        category=category,
        status=status,
        created_by=created_by,
        start_date=start_date,
        end_date=end_date,
        tag=tag,
        page=1,
        page_size=page_size,
        sort_by=sort_by,
        order=order,
    )

    filters = {
        "category": category,
        "status": status,
        "created_by": created_by,
        "start_date": start_date,
        "end_date": end_date,
        "tag": tag,
    }

    pdf = generate_decision_pdf(
        report,
        filters,
    )

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                'attachment; filename="decision_report.pdf"'
        },
    )


# =========================================================
# APPROVAL PDF EXPORT
# =========================================================

@router.get("/approvals/export/pdf")
def export_approvals_pdf(
    status: Optional[str] = Query(None),
    reviewer: Optional[int] = Query(None),
    decision: Optional[int] = Query(None),
    approval_level: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    page_size: int = Query(100, ge=1, le=1000),
    sort_by: str = Query("assigned_at"),
    order: str = Query("desc"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_report_access(current_user)

    allowed_statuses = {
        "Pending",
        "Approved",
        "Rejected",
    }

    if status and status not in allowed_statuses:
        raise HTTPException(
            status_code=422,
            detail="Invalid approval status",
        )

    allowed_roles = {
        "Employee",
        "Reviewer",
        "Manager",
        "Administrator",
    }

    if approval_level and approval_level not in allowed_roles:
        raise HTTPException(
            status_code=422,
            detail="Invalid approval level",
        )

    allowed_sort_fields = {
        "id",
        "decision_id",
        "assigned_at",
        "reviewed_at",
        "status",
    }

    if sort_by not in allowed_sort_fields:
        raise HTTPException(
            status_code=422,
            detail="Invalid sort_by value",
        )

    if order not in {"asc", "desc"}:
        raise HTTPException(
            status_code=422,
            detail="order must be asc or desc",
        )

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date cannot be after end_date",
        )

    report = get_approval_report(
        db=db,
        status=status,
        reviewer=reviewer,
        decision=decision,
        approval_level=approval_level,
        start_date=start_date,
        end_date=end_date,
        page=1,
        page_size=page_size,
        sort_by=sort_by,
        order=order,
    )

    filters = {
        "status": status,
        "reviewer": reviewer,
        "decision": decision,
        "approval_level": approval_level,
        "start_date": start_date,
        "end_date": end_date,
    }

    pdf = generate_approval_pdf(
        report,
        filters,
    )

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                'attachment; filename="approval_report.pdf"'
        },
    )


# =========================================================
# TEAM PDF EXPORT
# =========================================================

@router.get("/teams/export/pdf")
def export_teams_pdf(
    team: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    decision_status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    page_size: int = Query(100, ge=1, le=1000),
    sort_by: str = Query("team"),
    order: str = Query("asc"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_report_access(current_user)

    allowed_statuses = {
        "Draft",
        "Under Review",
        "Approved",
        "Rejected",
        "Archived",
    }

    if (
        decision_status
        and decision_status not in allowed_statuses
    ):
        raise HTTPException(
            status_code=422,
            detail="Invalid decision status",
        )

    allowed_sort_fields = {
        "team",
        "member_count",
        "total_decisions",
        "approved",
        "rejected",
    }

    if sort_by not in allowed_sort_fields:
        raise HTTPException(
            status_code=422,
            detail="Invalid sort_by value",
        )

    if order not in {"asc", "desc"}:
        raise HTTPException(
            status_code=422,
            detail="order must be asc or desc",
        )

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date cannot be after end_date",
        )

    report = get_team_report(
        db=db,
        team=team,
        start_date=start_date,
        end_date=end_date,
        decision_status=decision_status,
        category=category,
        page=1,
        page_size=page_size,
        sort_by=sort_by,
        order=order,
    )

    filters = {
        "team": team,
        "start_date": start_date,
        "end_date": end_date,
        "decision_status": decision_status,
        "category": category,
    }

    pdf = generate_team_pdf(
        report,
        filters,
    )

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                'attachment; filename="team_report.pdf"'
        },
    )


# =========================================================
# AUDIT PDF EXPORT
# =========================================================

@router.get("/audit/export/pdf")
def export_audit_pdf(
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    page_size: int = Query(100, ge=1, le=1000),
    sort_by: str = Query("created_at"),
    order: str = Query("desc"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_audit_access(current_user)

    allowed_sort_fields = {
        "id",
        "action",
        "entity_type",
        "entity_id",
        "created_at",
    }

    if sort_by not in allowed_sort_fields:
        raise HTTPException(
            status_code=422,
            detail="Invalid sort_by value",
        )

    if order not in {"asc", "desc"}:
        raise HTTPException(
            status_code=422,
            detail="order must be asc or desc",
        )

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date cannot be after end_date",
        )

    report = get_audit_report(
        db=db,
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        start_date=start_date,
        end_date=end_date,
        page=1,
        page_size=page_size,
        sort_by=sort_by,
        order=order,
    )

    filters = {
        "user_id": user_id,
        "action": action,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "start_date": start_date,
        "end_date": end_date,
    }

    pdf = generate_audit_pdf(
        report,
        filters,
    )

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                'attachment; filename="audit_report.pdf"'
        },
    )

# =========================================================
# DECISION EXCEL EXPORT
# =========================================================

@router.get("/decisions/export/excel")
def export_decisions_excel(
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    created_by: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    tag: Optional[str] = Query(None),
    page_size: int = Query(1000, ge=1, le=1000),
    sort_by: str = Query("created_at"),
    order: str = Query("desc"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_report_access(current_user)

    allowed_sort_fields = {
        "id",
        "title",
        "category",
        "status",
        "created_at",
        "updated_at",
    }

    if sort_by not in allowed_sort_fields:
        raise HTTPException(
            status_code=422,
            detail="Invalid sort_by value",
        )

    if order not in {"asc", "desc"}:
        raise HTTPException(
            status_code=422,
            detail="order must be asc or desc",
        )

    allowed_statuses = {
        "Draft",
        "Under Review",
        "Approved",
        "Rejected",
        "Archived",
    }

    if status and status not in allowed_statuses:
        raise HTTPException(
            status_code=422,
            detail="Invalid decision status",
        )

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date cannot be after end_date",
        )

    report = get_decision_report(
        db=db,
        category=category,
        status=status,
        created_by=created_by,
        start_date=start_date,
        end_date=end_date,
        tag=tag,
        page=1,
        page_size=page_size,
        sort_by=sort_by,
        order=order,
    )

    filters = {
        "category": category,
        "status": status,
        "created_by": created_by,
        "start_date": start_date,
        "end_date": end_date,
        "tag": tag,
    }

    excel = generate_decision_excel(
        report,
        filters,
    )

    return StreamingResponse(
        excel,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
                'attachment; filename="decision_report.xlsx"'
        },
    )


# =========================================================
# APPROVAL EXCEL EXPORT
# =========================================================

@router.get("/approvals/export/excel")
def export_approvals_excel(
    status: Optional[str] = Query(None),
    reviewer: Optional[int] = Query(None),
    decision: Optional[int] = Query(None),
    approval_level: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    page_size: int = Query(1000, ge=1, le=1000),
    sort_by: str = Query("assigned_at"),
    order: str = Query("desc"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_report_access(current_user)

    allowed_statuses = {
        "Pending",
        "Approved",
        "Rejected",
    }

    if status and status not in allowed_statuses:
        raise HTTPException(
            status_code=422,
            detail="Invalid approval status",
        )

    allowed_roles = {
        "Employee",
        "Reviewer",
        "Manager",
        "Administrator",
    }

    if approval_level and approval_level not in allowed_roles:
        raise HTTPException(
            status_code=422,
            detail="Invalid approval level",
        )

    allowed_sort_fields = {
        "id",
        "decision_id",
        "assigned_at",
        "reviewed_at",
        "status",
    }

    if sort_by not in allowed_sort_fields:
        raise HTTPException(
            status_code=422,
            detail="Invalid sort_by value",
        )

    if order not in {"asc", "desc"}:
        raise HTTPException(
            status_code=422,
            detail="order must be asc or desc",
        )

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date cannot be after end_date",
        )

    report = get_approval_report(
        db=db,
        status=status,
        reviewer=reviewer,
        decision=decision,
        approval_level=approval_level,
        start_date=start_date,
        end_date=end_date,
        page=1,
        page_size=page_size,
        sort_by=sort_by,
        order=order,
    )

    filters = {
        "status": status,
        "reviewer": reviewer,
        "decision": decision,
        "approval_level": approval_level,
        "start_date": start_date,
        "end_date": end_date,
    }

    excel = generate_approval_excel(
        report,
        filters,
    )

    return StreamingResponse(
        excel,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
                'attachment; filename="approval_report.xlsx"'
        },
    )


# =========================================================
# TEAM EXCEL EXPORT
# =========================================================

@router.get("/teams/export/excel")
def export_teams_excel(
    team: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    decision_status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    page_size: int = Query(1000, ge=1, le=1000),
    sort_by: str = Query("team"),
    order: str = Query("asc"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_report_access(current_user)

    allowed_statuses = {
        "Draft",
        "Under Review",
        "Approved",
        "Rejected",
        "Archived",
    }

    if (
        decision_status
        and decision_status not in allowed_statuses
    ):
        raise HTTPException(
            status_code=422,
            detail="Invalid decision status",
        )

    allowed_sort_fields = {
        "team",
        "member_count",
        "total_decisions",
        "approved",
        "rejected",
    }

    if sort_by not in allowed_sort_fields:
        raise HTTPException(
            status_code=422,
            detail="Invalid sort_by value",
        )

    if order not in {"asc", "desc"}:
        raise HTTPException(
            status_code=422,
            detail="order must be asc or desc",
        )

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date cannot be after end_date",
        )

    report = get_team_report(
        db=db,
        team=team,
        start_date=start_date,
        end_date=end_date,
        decision_status=decision_status,
        category=category,
        page=1,
        page_size=page_size,
        sort_by=sort_by,
        order=order,
    )

    filters = {
        "team": team,
        "start_date": start_date,
        "end_date": end_date,
        "decision_status": decision_status,
        "category": category,
    }

    excel = generate_team_excel(
        report,
        filters,
    )

    return StreamingResponse(
        excel,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
                'attachment; filename="team_report.xlsx"'
        },
    )


# =========================================================
# AUDIT EXCEL EXPORT
# =========================================================

@router.get("/audit/export/excel")
def export_audit_excel(
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    page_size: int = Query(1000, ge=1, le=1000),
    sort_by: str = Query("created_at"),
    order: str = Query("desc"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_audit_access(current_user)

    allowed_sort_fields = {
        "id",
        "action",
        "entity_type",
        "entity_id",
        "created_at",
    }

    if sort_by not in allowed_sort_fields:
        raise HTTPException(
            status_code=422,
            detail="Invalid sort_by value",
        )

    if order not in {"asc", "desc"}:
        raise HTTPException(
            status_code=422,
            detail="order must be asc or desc",
        )

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date cannot be after end_date",
        )

    report = get_audit_report(
        db=db,
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        start_date=start_date,
        end_date=end_date,
        page=1,
        page_size=page_size,
        sort_by=sort_by,
        order=order,
    )

    filters = {
        "user_id": user_id,
        "action": action,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "start_date": start_date,
        "end_date": end_date,
    }

    excel = generate_audit_excel(
        report,
        filters,
    )

    return StreamingResponse(
        excel,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
                'attachment; filename="audit_report.xlsx"'
        },
    )