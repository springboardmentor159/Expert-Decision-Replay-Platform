from datetime import datetime
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User

from app.schemas.reports.approval_report import (
    ApprovalReportResponse,
)
from app.schemas.reports.audit_report import (
    AuditReportResponse,
)
from app.schemas.reports.decision_report import (
    DecisionReportResponse,
)
from app.schemas.reports.team_report import (
    TeamReportResponse,
)

from app.services.reports.approval_report_service import (
    get_approval_report,
)
from app.services.reports.audit_report_service import (
    get_audit_report,
)
from app.services.reports.decision_report_service import (
    get_decision_report,
)
from app.services.reports.export_service import (
    generate_excel,
    generate_pdf,
)
from app.services.reports.team_report_service import (
    get_team_report,
)


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


VALID_SORT_FIELDS = {
    "created_date",
    "updated_date",
    "title",
    "approval_date",
    "team_name",
}


VALID_SORT_ORDERS = {
    "asc",
    "desc",
}


VALID_DECISION_STATUSES = {
    "Draft",
    "Under Review",
    "Approved",
    "Rejected",
    "Archived",
}


VALID_APPROVAL_STATUSES = {
    "Pending",
    "Approved",
    "Rejected",
}


def validate_date_range(
    date_from: Optional[datetime],
    date_to: Optional[datetime],
):
    if date_from and date_to and date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "date_from must be earlier than "
                "or equal to date_to"
            ),
        )


def validate_sorting(
    sort_by: str,
    sort_order: str,
):
    if sort_by not in VALID_SORT_FIELDS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Invalid sort_by. Allowed values: "
                "created_date, updated_date, title, "
                "approval_date, team_name"
            ),
        )

    if sort_order not in VALID_SORT_ORDERS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "sort_order must be either "
                "'asc' or 'desc'"
            ),
        )


def validate_report_access(
    current_user: User,
):
    allowed_roles = {
        "Employee",
        "Reviewer",
        "Manager",
        "Administrator",
    }

    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )


def validate_decision_status(
    decision_status: Optional[str],
):
    if (
        decision_status is not None
        and decision_status
        not in VALID_DECISION_STATUSES
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Invalid decision status. Allowed values: "
                "Draft, Under Review, Approved, "
                "Rejected, Archived"
            ),
        )


def validate_approval_status(
    approval_status: Optional[str],
):
    if (
        approval_status is not None
        and approval_status
        not in VALID_APPROVAL_STATUSES
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Invalid approval status. Allowed values: "
                "Pending, Approved, Rejected"
            ),
        )


def build_filters(
    **kwargs,
):
    return {
        key: value
        for key, value in kwargs.items()
        if value is not None
    }


# ============================================================
# DECISION REPORT
# ============================================================

@router.get(
    "/decisions",
    response_model=DecisionReportResponse,
)
def decision_report(
    category: Optional[str] = Query(default=None),
    decision_status: Optional[str] = Query(
        default=None,
        alias="status",
    ),
    created_by: Optional[int] = Query(
        default=None,
        ge=1,
    ),
    date_from: Optional[datetime] = Query(
        default=None,
    ),
    date_to: Optional[datetime] = Query(
        default=None,
    ),
    tags: Optional[str] = Query(default=None),
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    sort_by: str = Query(
        default="created_date",
    ),
    sort_order: str = Query(
        default="desc",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    validate_report_access(current_user)

    validate_date_range(
        date_from,
        date_to,
    )

    validate_sorting(
        sort_by,
        sort_order,
    )

    validate_decision_status(
        decision_status,
    )

    return get_decision_report(
        db=db,
        category=category,
        status=decision_status,
        created_by=created_by,
        date_from=date_from,
        date_to=date_to,
        tags=tags,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )


# ============================================================
# APPROVAL REPORT
# ============================================================

@router.get(
    "/approvals",
    response_model=ApprovalReportResponse,
)
def approval_report(
    approval_status: Optional[str] = Query(
        default=None,
    ),
    reviewer_id: Optional[int] = Query(
        default=None,
        ge=1,
    ),
    decision_id: Optional[int] = Query(
        default=None,
        ge=1,
    ),
    approval_level: Optional[int] = Query(
        default=None,
        ge=1,
    ),
    date_from: Optional[datetime] = Query(
        default=None,
    ),
    date_to: Optional[datetime] = Query(
        default=None,
    ),
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    sort_by: str = Query(
        default="approval_date",
    ),
    sort_order: str = Query(
        default="desc",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    validate_report_access(current_user)

    validate_date_range(
        date_from,
        date_to,
    )

    validate_sorting(
        sort_by,
        sort_order,
    )

    validate_approval_status(
        approval_status,
    )

    return get_approval_report(
        db=db,
        approval_status=approval_status,
        reviewer_id=reviewer_id,
        decision_id=decision_id,
        approval_level=approval_level,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )


# ============================================================
# TEAM REPORT
# ============================================================

@router.get(
    "/teams",
    response_model=TeamReportResponse,
)
def team_report(
    team_id: Optional[int] = Query(
        default=None,
        ge=1,
    ),
    date_from: Optional[datetime] = Query(
        default=None,
    ),
    date_to: Optional[datetime] = Query(
        default=None,
    ),
    decision_status: Optional[str] = Query(
        default=None,
        alias="status",
    ),
    category: Optional[str] = Query(default=None),
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    sort_by: str = Query(
        default="team_name",
    ),
    sort_order: str = Query(
        default="asc",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    validate_report_access(current_user)

    validate_date_range(
        date_from,
        date_to,
    )

    validate_sorting(
        sort_by,
        sort_order,
    )

    validate_decision_status(
        decision_status,
    )

    return get_team_report(
        db=db,
        team_id=team_id,
        date_from=date_from,
        date_to=date_to,
        decision_status=decision_status,
        category=category,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )


# ============================================================
# AUDIT REPORT
# ============================================================

@router.get(
    "/audit",
    response_model=AuditReportResponse,
)
def audit_report(
    user_id: Optional[int] = Query(
        default=None,
        ge=1,
    ),
    action: Optional[str] = Query(default=None),
    entity_type: Optional[str] = Query(
        default=None,
    ),
    entity_id: Optional[int] = Query(
        default=None,
        ge=1,
    ),
    date_from: Optional[datetime] = Query(
        default=None,
    ),
    date_to: Optional[datetime] = Query(
        default=None,
    ),
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    sort_by: str = Query(
        default="created_date",
    ),
    sort_order: str = Query(
        default="desc",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "Administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required",
        )

    validate_date_range(
        date_from,
        date_to,
    )

    if sort_by != "created_date":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Invalid sort_by. "
                "Allowed value: created_date"
            ),
        )

    if sort_order not in VALID_SORT_ORDERS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "sort_order must be either "
                "'asc' or 'desc'"
            ),
        )

    return get_audit_report(
        db=db,
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )


# ============================================================
# DECISION EXPORTS
# ============================================================

@router.get(
    "/decisions/export/excel"
)
def export_decisions_excel(
    category: Optional[str] = Query(default=None),
    decision_status: Optional[str] = Query(
        default=None,
        alias="status",
    ),
    created_by: Optional[int] = Query(
        default=None,
        ge=1,
    ),
    date_from: Optional[datetime] = Query(default=None),
    date_to: Optional[datetime] = Query(default=None),
    tags: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    validate_report_access(current_user)
    validate_date_range(date_from, date_to)
    validate_decision_status(decision_status)

    report = get_decision_report(
        db=db,
        category=category,
        status=decision_status,
        created_by=created_by,
        date_from=date_from,
        date_to=date_to,
        tags=tags,
        page=1,
        page_size=10000,
        sort_by="created_date",
        sort_order="desc",
    )

    columns = [
        "decision_id",
        "title",
        "category",
        "status",
        "created_by",
        "created_date",
        "updated_date",
        "number_of_alternatives",
        "number_of_approvals",
        "tags",
    ]

    output = generate_excel(
        title="Decision Report",
        columns=columns,
        rows=report["data"],
        filters=build_filters(
            category=category,
            status=decision_status,
            created_by=created_by,
            date_from=date_from,
            date_to=date_to,
            tags=tags,
        ),
        summary=report["summary"],
    )

    return StreamingResponse(
        output,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition": (
                'attachment; filename="decision_report.xlsx"'
            )
        },
    )


@router.get(
    "/decisions/export/pdf"
)
def export_decisions_pdf(
    category: Optional[str] = Query(default=None),
    decision_status: Optional[str] = Query(
        default=None,
        alias="status",
    ),
    created_by: Optional[int] = Query(
        default=None,
        ge=1,
    ),
    date_from: Optional[datetime] = Query(default=None),
    date_to: Optional[datetime] = Query(default=None),
    tags: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    validate_report_access(current_user)
    validate_date_range(date_from, date_to)
    validate_decision_status(decision_status)

    report = get_decision_report(
        db=db,
        category=category,
        status=decision_status,
        created_by=created_by,
        date_from=date_from,
        date_to=date_to,
        tags=tags,
        page=1,
        page_size=10000,
        sort_by="created_date",
        sort_order="desc",
    )

    columns = [
        "decision_id",
        "title",
        "category",
        "status",
        "created_by",
        "created_date",
        "updated_date",
        "number_of_alternatives",
        "number_of_approvals",
        "tags",
    ]

    output = generate_pdf(
        title="Decision Report",
        columns=columns,
        rows=report["data"],
        filters=build_filters(
            category=category,
            status=decision_status,
            created_by=created_by,
            date_from=date_from,
            date_to=date_to,
            tags=tags,
        ),
        summary=report["summary"],
    )

    return StreamingResponse(
        output,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                'attachment; filename="decision_report.pdf"'
            )
        },
    )


# ============================================================
# APPROVAL EXPORTS
# ============================================================

@router.get(
    "/approvals/export/excel"
)
def export_approvals_excel(
    approval_status: Optional[str] = Query(default=None),
    reviewer_id: Optional[int] = Query(
        default=None,
        ge=1,
    ),
    decision_id: Optional[int] = Query(
        default=None,
        ge=1,
    ),
    approval_level: Optional[int] = Query(
        default=None,
        ge=1,
    ),
    date_from: Optional[datetime] = Query(default=None),
    date_to: Optional[datetime] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    validate_report_access(current_user)
    validate_date_range(date_from, date_to)
    validate_approval_status(approval_status)

    report = get_approval_report(
        db=db,
        approval_status=approval_status,
        reviewer_id=reviewer_id,
        decision_id=decision_id,
        approval_level=approval_level,
        date_from=date_from,
        date_to=date_to,
        page=1,
        page_size=10000,
        sort_by="approval_date",
        sort_order="desc",
    )

    columns = [
        "approval_id",
        "decision_id",
        "decision_title",
        "reviewer",
        "approval_level",
        "approval_status",
        "assigned_date",
        "completed_date",
        "approval_turnaround_time",
    ]

    output = generate_excel(
        title="Approval Report",
        columns=columns,
        rows=report["data"],
        filters=build_filters(
            approval_status=approval_status,
            reviewer_id=reviewer_id,
            decision_id=decision_id,
            approval_level=approval_level,
            date_from=date_from,
            date_to=date_to,
        ),
        summary=report["stats"],
    )

    return StreamingResponse(
        output,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition": (
                'attachment; filename="approval_report.xlsx"'
            )
        },
    )


@router.get(
    "/approvals/export/pdf"
)
def export_approvals_pdf(
    approval_status: Optional[str] = Query(default=None),
    reviewer_id: Optional[int] = Query(
        default=None,
        ge=1,
    ),
    decision_id: Optional[int] = Query(
        default=None,
        ge=1,
    ),
    approval_level: Optional[int] = Query(
        default=None,
        ge=1,
    ),
    date_from: Optional[datetime] = Query(default=None),
    date_to: Optional[datetime] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    validate_report_access(current_user)
    validate_date_range(date_from, date_to)
    validate_approval_status(approval_status)

    report = get_approval_report(
        db=db,
        approval_status=approval_status,
        reviewer_id=reviewer_id,
        decision_id=decision_id,
        approval_level=approval_level,
        date_from=date_from,
        date_to=date_to,
        page=1,
        page_size=10000,
        sort_by="approval_date",
        sort_order="desc",
    )

    columns = [
        "approval_id",
        "decision_id",
        "decision_title",
        "reviewer",
        "approval_level",
        "approval_status",
        "assigned_date",
        "completed_date",
        "approval_turnaround_time",
    ]

    output = generate_pdf(
        title="Approval Report",
        columns=columns,
        rows=report["data"],
        filters=build_filters(
            approval_status=approval_status,
            reviewer_id=reviewer_id,
            decision_id=decision_id,
            approval_level=approval_level,
            date_from=date_from,
            date_to=date_to,
        ),
        summary=report["stats"],
    )

    return StreamingResponse(
        output,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                'attachment; filename="approval_report.pdf"'
            )
        },
    )


# ============================================================
# TEAM EXPORTS
# ============================================================

@router.get(
    "/teams/export/excel"
)
def export_teams_excel(
    team_id: Optional[int] = Query(
        default=None,
        ge=1,
    ),
    date_from: Optional[datetime] = Query(default=None),
    date_to: Optional[datetime] = Query(default=None),
    decision_status: Optional[str] = Query(
        default=None,
        alias="status",
    ),
    category: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    validate_report_access(current_user)
    validate_date_range(date_from, date_to)
    validate_decision_status(decision_status)

    report = get_team_report(
        db=db,
        team_id=team_id,
        date_from=date_from,
        date_to=date_to,
        decision_status=decision_status,
        category=category,
        page=1,
        page_size=10000,
        sort_by="team_name",
        sort_order="asc",
    )

    columns = [
        "team_name",
        "number_of_members",
        "total_decisions",
        "approved_decisions",
        "rejected_decisions",
        "pending_decisions",
        "approval_rate",
    ]

    output = generate_excel(
        title="Team Report",
        columns=columns,
        rows=report["data"],
        filters=build_filters(
            team_id=team_id,
            date_from=date_from,
            date_to=date_to,
            status=decision_status,
            category=category,
        ),
    )

    return StreamingResponse(
        output,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition": (
                'attachment; filename="team_report.xlsx"'
            )
        },
    )


@router.get(
    "/teams/export/pdf"
)
def export_teams_pdf(
    team_id: Optional[int] = Query(
        default=None,
        ge=1,
    ),
    date_from: Optional[datetime] = Query(default=None),
    date_to: Optional[datetime] = Query(default=None),
    decision_status: Optional[str] = Query(
        default=None,
        alias="status",
    ),
    category: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    validate_report_access(current_user)
    validate_date_range(date_from, date_to)
    validate_decision_status(decision_status)

    report = get_team_report(
        db=db,
        team_id=team_id,
        date_from=date_from,
        date_to=date_to,
        decision_status=decision_status,
        category=category,
        page=1,
        page_size=10000,
        sort_by="team_name",
        sort_order="asc",
    )

    columns = [
        "team_name",
        "number_of_members",
        "total_decisions",
        "approved_decisions",
        "rejected_decisions",
        "pending_decisions",
        "approval_rate",
    ]

    output = generate_pdf(
        title="Team Report",
        columns=columns,
        rows=report["data"],
        filters=build_filters(
            team_id=team_id,
            date_from=date_from,
            date_to=date_to,
            status=decision_status,
            category=category,
        ),
    )

    return StreamingResponse(
        output,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                'attachment; filename="team_report.pdf"'
            )
        },
    )


# ============================================================
# AUDIT EXPORTS
# ============================================================

@router.get(
    "/audit/export/excel"
)
def export_audit_excel(
    user_id: Optional[int] = Query(
        default=None,
        ge=1,
    ),
    action: Optional[str] = Query(default=None),
    entity_type: Optional[str] = Query(default=None),
    entity_id: Optional[int] = Query(
        default=None,
        ge=1,
    ),
    date_from: Optional[datetime] = Query(default=None),
    date_to: Optional[datetime] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "Administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required",
        )

    validate_date_range(date_from, date_to)

    report = get_audit_report(
        db=db,
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        date_from=date_from,
        date_to=date_to,
        page=1,
        page_size=10000,
        sort_by="created_date",
        sort_order="desc",
    )

    columns = [
        "user",
        "action",
        "entity_type",
        "entity_id",
        "description",
        "timestamp",
        "ip_address",
    ]

    output = generate_excel(
        title="Audit Report",
        columns=columns,
        rows=report["data"],
        filters=build_filters(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            date_from=date_from,
            date_to=date_to,
        ),
    )

    return StreamingResponse(
        output,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition": (
                'attachment; filename="audit_report.xlsx"'
            )
        },
    )


@router.get(
    "/audit/export/pdf"
)
def export_audit_pdf(
    user_id: Optional[int] = Query(
        default=None,
        ge=1,
    ),
    action: Optional[str] = Query(default=None),
    entity_type: Optional[str] = Query(default=None),
    entity_id: Optional[int] = Query(
        default=None,
        ge=1,
    ),
    date_from: Optional[datetime] = Query(default=None),
    date_to: Optional[datetime] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "Administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required",
        )

    validate_date_range(date_from, date_to)

    report = get_audit_report(
        db=db,
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        date_from=date_from,
        date_to=date_to,
        page=1,
        page_size=10000,
        sort_by="created_date",
        sort_order="desc",
    )

    columns = [
        "user",
        "action",
        "entity_type",
        "entity_id",
        "description",
        "timestamp",
        "ip_address",
    ]

    output = generate_pdf(
        title="Audit Report",
        columns=columns,
        rows=report["data"],
        filters=build_filters(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            date_from=date_from,
            date_to=date_to,
        ),
    )

    return StreamingResponse(
        output,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                'attachment; filename="audit_report.pdf"'
            )
        },
    )