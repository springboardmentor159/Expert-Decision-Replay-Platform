from datetime import date, datetime, time, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import exists, func
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db

from app.models.user import User
from app.models.role import UserRole
from app.models.decision import Decision
from app.models.decision_status import DecisionStatus
from app.models.alternative import Alternative
from app.models.approval import Approval
from app.models.approval_status import ApprovalStatus
from app.models.tag import Tag
from app.models.audit_log import AuditLog

from app.schemas.reports import (
    DecisionReportItem,
    DecisionReportResponse,
    DecisionReportSummary,
    ApprovalReportItem,
    ApprovalReportResponse,
    ApprovalReportSummary,
    TeamReportItem,
    TeamReportResponse,
    TeamReportSummary,
    AuditReportItem,
    AuditReportResponse,
    AuditReportSummary,
)

from app.services.report_export import (
    build_pdf,
    create_excel_workbook,
)


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


# ============================================================
# COMMON HELPERS
# ============================================================

def validate_date_range(
    start_date: Optional[date],
    end_date: Optional[date],
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date cannot be later than end_date",
        )


def get_start_datetime(
    value: Optional[date],
) -> Optional[datetime]:
    if value is None:
        return None

    return datetime.combine(
        value,
        time.min,
    )


def get_end_datetime(
    value: Optional[date],
) -> Optional[datetime]:
    if value is None:
        return None

    return datetime.combine(
        value + timedelta(days=1),
        time.min,
    )


def excel_response(
    workbook,
    filename: str,
):
    return Response(
        content=workbook.getvalue(),
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition": (
                f'attachment; filename="{filename}"'
            )
        },
    )


def pdf_response(
    pdf,
    filename: str,
):
    return Response(
        content=pdf.getvalue(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f'attachment; filename="{filename}"'
            )
        },
    )


def get_all_decision_report_items(
    category,
    status,
    created_by,
    start_date,
    end_date,
    tag,
    sort_by,
    sort_order,
    current_user,
    db,
):
    first_page = decision_report(
        category=category,
        status=status,
        created_by=created_by,
        start_date=start_date,
        end_date=end_date,
        tag=tag,
        page=1,
        page_size=100,
        sort_by=sort_by,
        sort_order=sort_order,
        current_user=current_user,
        db=db,
    )

    items = list(first_page.items)
    total = first_page.total

    page = 2

    while len(items) < total:
        result = decision_report(
            category=category,
            status=status,
            created_by=created_by,
            start_date=start_date,
            end_date=end_date,
            tag=tag,
            page=page,
            page_size=100,
            sort_by=sort_by,
            sort_order=sort_order,
            current_user=current_user,
            db=db,
        )

        if not result.items:
            break

        items.extend(result.items)
        page += 1

    return items, first_page.summary


def get_all_approval_report_items(
    status,
    reviewer_id,
    decision_id,
    approval_level,
    start_date,
    end_date,
    sort_by,
    sort_order,
    current_user,
    db,
):
    first_page = approval_report(
        status=status,
        reviewer_id=reviewer_id,
        decision_id=decision_id,
        approval_level=approval_level,
        start_date=start_date,
        end_date=end_date,
        page=1,
        page_size=100,
        sort_by=sort_by,
        sort_order=sort_order,
        current_user=current_user,
        db=db,
    )

    items = list(first_page.items)
    total = first_page.total

    page = 2

    while len(items) < total:
        result = approval_report(
            status=status,
            reviewer_id=reviewer_id,
            decision_id=decision_id,
            approval_level=approval_level,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=100,
            sort_by=sort_by,
            sort_order=sort_order,
            current_user=current_user,
            db=db,
        )

        if not result.items:
            break

        items.extend(result.items)
        page += 1

    return items, first_page.summary


def get_all_team_report_items(
    team,
    status,
    category,
    start_date,
    end_date,
    sort_by,
    sort_order,
    current_user,
    db,
):
    first_page = team_report(
        team=team,
        status=status,
        category=category,
        start_date=start_date,
        end_date=end_date,
        page=1,
        page_size=100,
        sort_by=sort_by,
        sort_order=sort_order,
        current_user=current_user,
        db=db,
    )

    items = list(first_page.items)
    total = first_page.total

    page = 2

    while len(items) < total:
        result = team_report(
            team=team,
            status=status,
            category=category,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=100,
            sort_by=sort_by,
            sort_order=sort_order,
            current_user=current_user,
            db=db,
        )

        if not result.items:
            break

        items.extend(result.items)
        page += 1

    return items, first_page.summary


def get_all_audit_report_items(
    user_id,
    action,
    entity_type,
    entity_id,
    start_date,
    end_date,
    sort_by,
    sort_order,
    current_user,
    db,
):
    first_page = audit_report(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        start_date=start_date,
        end_date=end_date,
        page=1,
        page_size=100,
        sort_by=sort_by,
        sort_order=sort_order,
        current_user=current_user,
        db=db,
    )

    items = list(first_page.items)
    total = first_page.total

    page = 2

    while len(items) < total:
        result = audit_report(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=100,
            sort_by=sort_by,
            sort_order=sort_order,
            current_user=current_user,
            db=db,
        )

        if not result.items:
            break

        items.extend(result.items)
        page += 1

    return items, first_page.summary


# ============================================================
# DECISION REPORT
# ============================================================

@router.get(
    "/decisions",
    response_model=DecisionReportResponse,
)
def decision_report(
    category: Optional[str] = Query(
        default=None,
        description="Filter by decision category",
    ),
    status: Optional[DecisionStatus] = Query(
        default=None,
        description="Filter by decision status",
    ),
    created_by: Optional[int] = Query(
        default=None,
        ge=1,
        description="Filter by decision creator user ID",
    ),
    start_date: Optional[date] = Query(
        default=None,
        description="Filter decisions created on or after this date",
    ),
    end_date: Optional[date] = Query(
        default=None,
        description="Filter decisions created on or before this date",
    ),
    tag: Optional[str] = Query(
        default=None,
        description="Filter by tag name",
    ),
    page: int = Query(
        default=1,
        ge=1,
        description="Page number",
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Number of records per page",
    ),
    sort_by: str = Query(
        default="created_date",
        description="Allowed values: created_date, updated_date, title",
    ),
    sort_order: str = Query(
        default="desc",
        description="Allowed values: asc, desc",
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    validate_date_range(
        start_date,
        end_date,
    )

    allowed_sort_fields = {
        "created_date": Decision.created_at,
        "updated_date": Decision.updated_at,
        "title": Decision.title,
    }

    if sort_by not in allowed_sort_fields:
        raise HTTPException(
            status_code=422,
            detail=(
                "Invalid sort_by. Allowed values: "
                "created_date, updated_date, title"
            ),
        )

    if sort_order.lower() not in {"asc", "desc"}:
        raise HTTPException(
            status_code=422,
            detail="Invalid sort_order. Allowed values: asc, desc",
        )

    query = db.query(Decision)

    if current_user.role == UserRole.ADMINISTRATOR:
        pass

    elif current_user.role == UserRole.MANAGER:
        query = (
            query
            .join(
                User,
                Decision.created_by == User.id,
            )
            .filter(
                User.department == current_user.department
            )
        )

    elif current_user.role == UserRole.EMPLOYEE:
        query = query.filter(
            Decision.created_by == current_user.id
        )

    elif current_user.role == UserRole.REVIEWER:
        reviewer_exists = exists().where(
            (Approval.decision_id == Decision.id)
            & (
                Approval.reviewer_id
                == current_user.id
            )
        )

        query = query.filter(
            reviewer_exists
        )

    else:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access decision reports",
        )

    if category is not None:
        query = query.filter(
            Decision.category == category
        )

    if status is not None:
        query = query.filter(
            Decision.status == status
        )

    if created_by is not None:
        query = query.filter(
            Decision.created_by == created_by
        )

    start_datetime = get_start_datetime(
        start_date
    )

    if start_datetime is not None:
        query = query.filter(
            Decision.created_at >= start_datetime
        )

    end_datetime = get_end_datetime(
        end_date
    )

    if end_datetime is not None:
        query = query.filter(
            Decision.created_at < end_datetime
        )

    if tag is not None:
        query = query.filter(
            Decision.tags.any(
                Tag.name == tag
            )
        )

    total = query.count()

    summary = DecisionReportSummary(
        total_decisions=total,

        draft_decisions=query.filter(
            Decision.status == DecisionStatus.DRAFT
        ).count(),

        under_review_decisions=query.filter(
            Decision.status == DecisionStatus.UNDER_REVIEW
        ).count(),

        approved_decisions=query.filter(
            Decision.status == DecisionStatus.APPROVED
        ).count(),

        rejected_decisions=query.filter(
            Decision.status == DecisionStatus.REJECTED
        ).count(),

        archived_decisions=query.filter(
            Decision.status == DecisionStatus.ARCHIVED
        ).count(),
    )

    sort_column = allowed_sort_fields[
        sort_by
    ]

    if sort_order.lower() == "asc":
        query = query.order_by(
            sort_column.asc()
        )
    else:
        query = query.order_by(
            sort_column.desc()
        )

    offset = (
        page - 1
    ) * page_size

    decisions = (
        query
        .offset(offset)
        .limit(page_size)
        .all()
    )

    items = []

    for decision in decisions:

        alternatives_count = (
            db.query(
                func.count(
                    Alternative.id
                )
            )
            .filter(
                Alternative.decision_id
                == decision.id
            )
            .scalar()
            or 0
        )

        approvals_count = (
            db.query(
                func.count(
                    Approval.id
                )
            )
            .filter(
                Approval.decision_id
                == decision.id
            )
            .scalar()
            or 0
        )

        tags = [
            decision_tag.name
            for decision_tag in decision.tags
        ]

        items.append(
            DecisionReportItem(
                decision_id=decision.id,
                title=decision.title,
                category=decision.category,
                status=decision.status.value,
                created_by=decision.created_by,
                created_date=decision.created_at,
                updated_date=decision.updated_at,
                alternatives_count=alternatives_count,
                approvals_count=approvals_count,
                tags=tags,
            )
        )

    return DecisionReportResponse(
        items=items,
        summary=summary,
        page=page,
        page_size=page_size,
        total=total,
    )


# ============================================================
# APPROVAL REPORT
# ============================================================

@router.get(
    "/approvals",
    response_model=ApprovalReportResponse,
)
def approval_report(
    status: Optional[ApprovalStatus] = Query(
        default=None,
        description="Filter by approval status",
    ),
    reviewer_id: Optional[int] = Query(
        default=None,
        ge=1,
        description="Filter by reviewer user ID",
    ),
    decision_id: Optional[int] = Query(
        default=None,
        ge=1,
        description="Filter by decision ID",
    ),
    approval_level: Optional[int] = Query(
        default=None,
        ge=1,
        description="Filter by approval level",
    ),
    start_date: Optional[date] = Query(
        default=None,
        description="Filter approvals assigned on or after this date",
    ),
    end_date: Optional[date] = Query(
        default=None,
        description="Filter approvals assigned on or before this date",
    ),
    page: int = Query(
        default=1,
        ge=1,
        description="Page number",
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Number of records per page",
    ),
    sort_by: str = Query(
        default="approval_date",
        description="Allowed value: approval_date",
    ),
    sort_order: str = Query(
        default="desc",
        description="Allowed values: asc, desc",
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    validate_date_range(
        start_date,
        end_date,
    )

    if sort_by != "approval_date":
        raise HTTPException(
            status_code=422,
            detail="Invalid sort_by. Allowed value: approval_date",
        )

    if sort_order.lower() not in {
        "asc",
        "desc",
    }:
        raise HTTPException(
            status_code=422,
            detail="Invalid sort_order. Allowed values: asc, desc",
        )

    query = (
        db.query(Approval)
        .join(
            Decision,
            Approval.decision_id
            == Decision.id,
        )
    )

    if current_user.role == UserRole.ADMINISTRATOR:
        pass

    elif current_user.role == UserRole.MANAGER:
        query = (
            query
            .join(
                User,
                Decision.created_by
                == User.id,
            )
            .filter(
                User.department
                == current_user.department
            )
        )

    elif current_user.role == UserRole.EMPLOYEE:
        query = query.filter(
            Decision.created_by
            == current_user.id
        )

    elif current_user.role == UserRole.REVIEWER:
        query = query.filter(
            Approval.reviewer_id
            == current_user.id
        )

    else:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access approval reports",
        )

    if status is not None:
        query = query.filter(
            Approval.status == status
        )

    if reviewer_id is not None:
        query = query.filter(
            Approval.reviewer_id
            == reviewer_id
        )

    if decision_id is not None:
        query = query.filter(
            Approval.decision_id
            == decision_id
        )

    if approval_level is not None:
        query = query.filter(
            Approval.approval_level
            == approval_level
        )

    start_datetime = get_start_datetime(
        start_date
    )

    if start_datetime is not None:
        query = query.filter(
            Approval.created_at
            >= start_datetime
        )

    end_datetime = get_end_datetime(
        end_date
    )

    if end_datetime is not None:
        query = query.filter(
            Approval.created_at
            < end_datetime
        )

    total = query.count()

    pending_count = query.filter(
        Approval.status
        == ApprovalStatus.PENDING
    ).count()

    approved_count = query.filter(
        Approval.status
        == ApprovalStatus.APPROVED
    ).count()

    rejected_count = query.filter(
        Approval.status
        == ApprovalStatus.REJECTED
    ).count()

    completed_count = (
        approved_count
        + rejected_count
    )

    completion_rate = (
        (
            completed_count
            / total
        ) * 100
        if total > 0
        else 0.0
    )

    completed_records = (
        query
        .filter(
            Approval.status.in_(
                [
                    ApprovalStatus.APPROVED,
                    ApprovalStatus.REJECTED,
                ]
            )
        )
        .all()
    )

    turnaround_values = []

    for approval in completed_records:

        if (
            approval.created_at
            and approval.updated_at
        ):
            turnaround = (
                approval.updated_at
                - approval.created_at
            ).total_seconds() / 86400

            turnaround_values.append(
                turnaround
            )

    average_turnaround = (
        sum(turnaround_values)
        / len(turnaround_values)
        if turnaround_values
        else None
    )

    if sort_order.lower() == "asc":
        query = query.order_by(
            Approval.created_at.asc()
        )
    else:
        query = query.order_by(
            Approval.created_at.desc()
        )

    offset = (
        page - 1
    ) * page_size

    approvals = (
        query
        .offset(offset)
        .limit(page_size)
        .all()
    )

    items = []

    for approval in approvals:

        completed_date = None
        turnaround_days = None

        if approval.status in {
            ApprovalStatus.APPROVED,
            ApprovalStatus.REJECTED,
        }:

            completed_date = (
                approval.updated_at
            )

            if (
                approval.created_at
                and approval.updated_at
            ):
                turnaround_days = (
                    approval.updated_at
                    - approval.created_at
                ).total_seconds() / 86400

        items.append(
            ApprovalReportItem(
                approval_id=approval.id,
                decision_id=approval.decision_id,
                decision_title=approval.decision.title,
                reviewer_id=approval.reviewer_id,
                approval_level=approval.approval_level,
                status=approval.status.value,
                assigned_date=approval.created_at,
                completed_date=completed_date,
                turnaround_days=(
                    round(
                        turnaround_days,
                        2,
                    )
                    if turnaround_days
                    is not None
                    else None
                ),
            )
        )

    return ApprovalReportResponse(
        items=items,
        summary=ApprovalReportSummary(
            total_approvals=total,
            pending_approvals=pending_count,
            approved_approvals=approved_count,
            rejected_approvals=rejected_count,
            average_turnaround_days=(
                round(
                    average_turnaround,
                    2,
                )
                if average_turnaround
                is not None
                else None
            ),
            completion_rate=round(
                completion_rate,
                2,
            ),
        ),
        page=page,
        page_size=page_size,
        total=total,
    )


# ============================================================
# TEAM REPORT
# ============================================================

@router.get(
    "/teams",
    response_model=TeamReportResponse,
)
def team_report(
    team: Optional[str] = Query(
        default=None,
        description="Filter by team/department name",
    ),
    status: Optional[DecisionStatus] = Query(
        default=None,
        description="Filter by decision status",
    ),
    category: Optional[str] = Query(
        default=None,
        description="Filter by decision category",
    ),
    start_date: Optional[date] = Query(
        default=None,
        description="Filter decisions created on or after this date",
    ),
    end_date: Optional[date] = Query(
        default=None,
        description="Filter decisions created on or before this date",
    ),
    page: int = Query(
        default=1,
        ge=1,
        description="Page number",
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Number of teams per page",
    ),
    sort_by: str = Query(
        default="team_name",
        description="Allowed value: team_name",
    ),
    sort_order: str = Query(
        default="asc",
        description="Allowed values: asc, desc",
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    validate_date_range(
        start_date,
        end_date,
    )

    if sort_by != "team_name":
        raise HTTPException(
            status_code=422,
            detail="Invalid sort_by. Allowed value: team_name",
        )

    if sort_order.lower() not in {
        "asc",
        "desc",
    }:
        raise HTTPException(
            status_code=422,
            detail="Invalid sort_order. Allowed values: asc, desc",
        )

    if current_user.role == UserRole.ADMINISTRATOR:

        accessible_teams_query = (
            db.query(User.department)
            .filter(
                User.department.isnot(None)
            )
            .distinct()
        )

    elif current_user.role in {
        UserRole.MANAGER,
        UserRole.EMPLOYEE,
        UserRole.REVIEWER,
    }:

        accessible_teams_query = (
            db.query(User.department)
            .filter(
                User.department
                == current_user.department,
                User.department.isnot(None),
            )
            .distinct()
        )

    else:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access team reports",
        )

    accessible_teams = [
        row[0]
        for row in accessible_teams_query.all()
    ]

    if team is not None:

        if team not in accessible_teams:
            accessible_teams = []

        else:
            accessible_teams = [
                team
            ]

    team_items = []

    for team_name in accessible_teams:

        member_count = (
            db.query(
                func.count(User.id)
            )
            .filter(
                User.department
                == team_name
            )
            .scalar()
            or 0
        )

        decision_query = (
            db.query(Decision)
            .join(
                User,
                Decision.created_by
                == User.id,
            )
            .filter(
                User.department
                == team_name
            )
        )

        start_datetime = get_start_datetime(
            start_date
        )

        if start_datetime is not None:
            decision_query = decision_query.filter(
                Decision.created_at
                >= start_datetime
            )

        end_datetime = get_end_datetime(
            end_date
        )

        if end_datetime is not None:
            decision_query = decision_query.filter(
                Decision.created_at
                < end_datetime
            )

        if category is not None:
            decision_query = decision_query.filter(
                Decision.category
                == category
            )

        if status is not None:
            decision_query = decision_query.filter(
                Decision.status
                == status
            )

        decisions = decision_query.all()

        total_decisions = len(
            decisions
        )

        approved_decisions = sum(
            1
            for decision in decisions
            if decision.status
            == DecisionStatus.APPROVED
        )

        rejected_decisions = sum(
            1
            for decision in decisions
            if decision.status
            == DecisionStatus.REJECTED
        )

        pending_decisions = sum(
            1
            for decision in decisions
            if decision.status
            == DecisionStatus.UNDER_REVIEW
        )

        completed_decisions = (
            approved_decisions
            + rejected_decisions
        )

        approval_rate = (
            (
                approved_decisions
                / completed_decisions
            ) * 100
            if completed_decisions > 0
            else 0.0
        )

        team_items.append(
            TeamReportItem(
                team_name=team_name,
                members=member_count,
                total_decisions=total_decisions,
                approved_decisions=approved_decisions,
                rejected_decisions=rejected_decisions,
                pending_decisions=pending_decisions,
                approval_rate=round(
                    approval_rate,
                    2,
                ),
            )
        )

    team_items.sort(
        key=lambda item:
        item.team_name.lower(),
        reverse=(
            sort_order.lower()
            == "desc"
        ),
    )

    total_teams = len(
        team_items
    )

    total_members = sum(
        item.members
        for item in team_items
    )

    total_decisions = sum(
        item.total_decisions
        for item in team_items
    )

    total_approved = sum(
        item.approved_decisions
        for item in team_items
    )

    total_rejected = sum(
        item.rejected_decisions
        for item in team_items
    )

    total_pending = sum(
        item.pending_decisions
        for item in team_items
    )

    summary = TeamReportSummary(
        total_teams=total_teams,
        total_members=total_members,
        total_decisions=total_decisions,
        total_approved=total_approved,
        total_rejected=total_rejected,
        total_pending=total_pending,
    )

    total = len(
        team_items
    )

    offset = (
        page - 1
    ) * page_size

    paginated_items = team_items[
        offset:
        offset + page_size
    ]

    return TeamReportResponse(
        items=paginated_items,
        summary=summary,
        page=page,
        page_size=page_size,
        total=total,
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
        description="Filter by user ID",
    ),
    action: Optional[str] = Query(
        default=None,
        description="Filter by audit action",
    ),
    entity_type: Optional[str] = Query(
        default=None,
        description="Filter by entity type",
    ),
    entity_id: Optional[int] = Query(
        default=None,
        ge=1,
        description="Filter by entity ID",
    ),
    start_date: Optional[date] = Query(
        default=None,
        description="Filter logs created on or after this date",
    ),
    end_date: Optional[date] = Query(
        default=None,
        description="Filter logs created on or before this date",
    ),
    page: int = Query(
        default=1,
        ge=1,
        description="Page number",
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Number of records per page",
    ),
    sort_by: str = Query(
        default="timestamp",
        description="Allowed value: timestamp",
    ),
    sort_order: str = Query(
        default="desc",
        description="Allowed values: asc, desc",
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != UserRole.ADMINISTRATOR:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access audit reports",
        )

    validate_date_range(
        start_date,
        end_date,
    )

    if sort_by != "timestamp":
        raise HTTPException(
            status_code=422,
            detail="Invalid sort_by. Allowed value: timestamp",
        )

    if sort_order.lower() not in {
        "asc",
        "desc",
    }:
        raise HTTPException(
            status_code=422,
            detail="Invalid sort_order. Allowed values: asc, desc",
        )

    query = db.query(
        AuditLog
    )

    if user_id is not None:
        query = query.filter(
            AuditLog.user_id
            == user_id
        )

    if action is not None:
        query = query.filter(
            AuditLog.action
            == action
        )

    if entity_type is not None:
        query = query.filter(
            AuditLog.entity_type
            == entity_type
        )

    if entity_id is not None:
        query = query.filter(
            AuditLog.entity_id
            == entity_id
        )

    start_datetime = get_start_datetime(
        start_date
    )

    if start_datetime is not None:
        query = query.filter(
            AuditLog.created_at
            >= start_datetime
        )

    end_datetime = get_end_datetime(
        end_date
    )

    if end_datetime is not None:
        query = query.filter(
            AuditLog.created_at
            < end_datetime
        )

    total = query.count()

    summary = AuditReportSummary(
        total_audit_logs=total,

        create_actions=query.filter(
            AuditLog.action == "CREATE"
        ).count(),

        update_actions=query.filter(
            AuditLog.action == "UPDATE"
        ).count(),

        delete_actions=query.filter(
            AuditLog.action == "DELETE"
        ).count(),

        approve_actions=query.filter(
            AuditLog.action == "APPROVE"
        ).count(),

        reject_actions=query.filter(
            AuditLog.action == "REJECT"
        ).count(),

        access_actions=query.filter(
            AuditLog.action == "ACCESS"
        ).count(),

        login_actions=query.filter(
            AuditLog.action == "LOGIN"
        ).count(),

        logout_actions=query.filter(
            AuditLog.action == "LOGOUT"
        ).count(),

        submit_actions=query.filter(
            AuditLog.action == "SUBMIT"
        ).count(),

        archive_actions=query.filter(
            AuditLog.action == "ARCHIVE"
        ).count(),
    )

    if sort_order.lower() == "asc":
        query = query.order_by(
            AuditLog.created_at.asc()
        )
    else:
        query = query.order_by(
            AuditLog.created_at.desc()
        )

    offset = (
        page - 1
    ) * page_size

    audit_logs = (
        query
        .offset(offset)
        .limit(page_size)
        .all()
    )

    items = []

    for audit_log in audit_logs:

        action_value = (
            audit_log.action.value
            if hasattr(
                audit_log.action,
                "value",
            )
            else str(
                audit_log.action
            )
        )

        items.append(
            AuditReportItem(
                audit_id=audit_log.id,
                user_id=audit_log.user_id,
                action=action_value,
                entity_type=audit_log.entity_type,
                entity_id=audit_log.entity_id,
                description=audit_log.description,
                timestamp=audit_log.created_at,
                ip_address=audit_log.ip_address,
            )
        )

    return AuditReportResponse(
        items=items,
        summary=summary,
        page=page,
        page_size=page_size,
        total=total,
    )


# ============================================================
# DECISION PDF EXPORT
# ============================================================

@router.get(
    "/decisions/export/pdf",
)
def export_decisions_pdf(
    category: Optional[str] = Query(default=None),
    status: Optional[DecisionStatus] = Query(default=None),
    created_by: Optional[int] = Query(default=None, ge=1),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    tag: Optional[str] = Query(default=None),
    sort_by: str = Query(default="created_date"),
    sort_order: str = Query(default="desc"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items, summary = get_all_decision_report_items(
        category,
        status,
        created_by,
        start_date,
        end_date,
        tag,
        sort_by,
        sort_order,
        current_user,
        db,
    )

    headers = [
        "Decision ID",
        "Title",
        "Category",
        "Status",
        "Created By",
        "Created Date",
        "Updated Date",
        "Alternatives",
        "Approvals",
        "Tags",
    ]

    rows = [
        [
            item.decision_id,
            item.title,
            item.category,
            item.status,
            item.created_by,
            item.created_date,
            item.updated_date,
            item.alternatives_count,
            item.approvals_count,
            ", ".join(item.tags),
        ]
        for item in items
    ]

    summary_data = {
        "Total Decisions": summary.total_decisions,
        "Draft": summary.draft_decisions,
        "Under Review": summary.under_review_decisions,
        "Approved": summary.approved_decisions,
        "Rejected": summary.rejected_decisions,
        "Archived": summary.archived_decisions,
    }

    filters = {
        "Category": category,
        "Status": status,
        "Created By": created_by,
        "Start Date": start_date,
        "End Date": end_date,
        "Tag": tag,
        "Sort By": sort_by,
        "Sort Order": sort_order,
    }

    pdf = build_pdf(
        "Decision Report",
        headers,
        rows,
        summary=summary_data,
        filters=filters,
    )

    return pdf_response(
        pdf,
        "decision_report.pdf",
    )


# ============================================================
# DECISION EXCEL EXPORT
# ============================================================

@router.get(
    "/decisions/export/excel",
)
def export_decisions_excel(
    category: Optional[str] = Query(default=None),
    status: Optional[DecisionStatus] = Query(default=None),
    created_by: Optional[int] = Query(default=None, ge=1),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    tag: Optional[str] = Query(default=None),
    sort_by: str = Query(default="created_date"),
    sort_order: str = Query(default="desc"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items, summary = get_all_decision_report_items(
        category,
        status,
        created_by,
        start_date,
        end_date,
        tag,
        sort_by,
        sort_order,
        current_user,
        db,
    )

    headers = [
        "Decision ID",
        "Title",
        "Category",
        "Status",
        "Created By",
        "Created Date",
        "Updated Date",
        "Alternatives",
        "Approvals",
        "Tags",
    ]

    rows = [
        [
            item.decision_id,
            item.title,
            item.category,
            item.status,
            item.created_by,
            item.created_date,
            item.updated_date,
            item.alternatives_count,
            item.approvals_count,
            ", ".join(item.tags),
        ]
        for item in items
    ]

    workbook = create_excel_workbook(
        "Decision Report",
        headers,
        rows,
    )

    return excel_response(
        workbook,
        "decision_report.xlsx",
    )


# ============================================================
# APPROVAL PDF EXPORT
# ============================================================

@router.get(
    "/approvals/export/pdf",
)
def export_approvals_pdf(
    status: Optional[ApprovalStatus] = Query(default=None),
    reviewer_id: Optional[int] = Query(default=None, ge=1),
    decision_id: Optional[int] = Query(default=None, ge=1),
    approval_level: Optional[int] = Query(default=None, ge=1),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    sort_by: str = Query(default="approval_date"),
    sort_order: str = Query(default="desc"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items, summary = get_all_approval_report_items(
        status,
        reviewer_id,
        decision_id,
        approval_level,
        start_date,
        end_date,
        sort_by,
        sort_order,
        current_user,
        db,
    )

    headers = [
        "Approval ID",
        "Decision ID",
        "Decision Title",
        "Reviewer",
        "Approval Level",
        "Status",
        "Assigned Date",
        "Completed Date",
        "Turnaround Days",
    ]

    rows = [
        [
            item.approval_id,
            item.decision_id,
            item.decision_title,
            item.reviewer_id,
            item.approval_level,
            item.status,
            item.assigned_date,
            item.completed_date,
            item.turnaround_days,
        ]
        for item in items
    ]

    summary_data = {
        "Total Approvals": summary.total_approvals,
        "Pending": summary.pending_approvals,
        "Approved": summary.approved_approvals,
        "Rejected": summary.rejected_approvals,
        "Average Turnaround Days": (
            summary.average_turnaround_days
        ),
        "Completion Rate": (
            f"{summary.completion_rate}%"
        ),
    }

    filters = {
        "Status": status,
        "Reviewer ID": reviewer_id,
        "Decision ID": decision_id,
        "Approval Level": approval_level,
        "Start Date": start_date,
        "End Date": end_date,
        "Sort By": sort_by,
        "Sort Order": sort_order,
    }

    pdf = build_pdf(
        "Approval Report",
        headers,
        rows,
        summary=summary_data,
        filters=filters,
    )

    return pdf_response(
        pdf,
        "approval_report.pdf",
    )


# ============================================================
# APPROVAL EXCEL EXPORT
# ============================================================

@router.get(
    "/approvals/export/excel",
)
def export_approvals_excel(
    status: Optional[ApprovalStatus] = Query(default=None),
    reviewer_id: Optional[int] = Query(default=None, ge=1),
    decision_id: Optional[int] = Query(default=None, ge=1),
    approval_level: Optional[int] = Query(default=None, ge=1),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    sort_by: str = Query(default="approval_date"),
    sort_order: str = Query(default="desc"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items, summary = get_all_approval_report_items(
        status,
        reviewer_id,
        decision_id,
        approval_level,
        start_date,
        end_date,
        sort_by,
        sort_order,
        current_user,
        db,
    )

    headers = [
        "Approval ID",
        "Decision ID",
        "Decision Title",
        "Reviewer",
        "Approval Level",
        "Status",
        "Assigned Date",
        "Completed Date",
        "Turnaround Days",
    ]

    rows = [
        [
            item.approval_id,
            item.decision_id,
            item.decision_title,
            item.reviewer_id,
            item.approval_level,
            item.status,
            item.assigned_date,
            item.completed_date,
            item.turnaround_days,
        ]
        for item in items
    ]

    workbook = create_excel_workbook(
        "Approval Report",
        headers,
        rows,
    )

    return excel_response(
        workbook,
        "approval_report.xlsx",
    )


# ============================================================
# TEAM PDF EXPORT
# ============================================================

@router.get(
    "/teams/export/pdf",
)
def export_teams_pdf(
    team: Optional[str] = Query(default=None),
    status: Optional[DecisionStatus] = Query(default=None),
    category: Optional[str] = Query(default=None),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    sort_by: str = Query(default="team_name"),
    sort_order: str = Query(default="asc"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items, summary = get_all_team_report_items(
        team,
        status,
        category,
        start_date,
        end_date,
        sort_by,
        sort_order,
        current_user,
        db,
    )

    headers = [
        "Team Name",
        "Members",
        "Total Decisions",
        "Approved",
        "Rejected",
        "Pending",
        "Approval Rate",
    ]

    rows = [
        [
            item.team_name,
            item.members,
            item.total_decisions,
            item.approved_decisions,
            item.rejected_decisions,
            item.pending_decisions,
            f"{item.approval_rate}%",
        ]
        for item in items
    ]

    summary_data = {
        "Total Teams": summary.total_teams,
        "Total Members": summary.total_members,
        "Total Decisions": summary.total_decisions,
        "Total Approved": summary.total_approved,
        "Total Rejected": summary.total_rejected,
        "Total Pending": summary.total_pending,
    }

    filters = {
        "Team": team,
        "Status": status,
        "Category": category,
        "Start Date": start_date,
        "End Date": end_date,
        "Sort By": sort_by,
        "Sort Order": sort_order,
    }

    pdf = build_pdf(
        "Team Report",
        headers,
        rows,
        summary=summary_data,
        filters=filters,
    )

    return pdf_response(
        pdf,
        "team_report.pdf",
    )


# ============================================================
# TEAM EXCEL EXPORT
# ============================================================

@router.get(
    "/teams/export/excel",
)
def export_teams_excel(
    team: Optional[str] = Query(default=None),
    status: Optional[DecisionStatus] = Query(default=None),
    category: Optional[str] = Query(default=None),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    sort_by: str = Query(default="team_name"),
    sort_order: str = Query(default="asc"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items, summary = get_all_team_report_items(
        team,
        status,
        category,
        start_date,
        end_date,
        sort_by,
        sort_order,
        current_user,
        db,
    )

    headers = [
        "Team Name",
        "Members",
        "Total Decisions",
        "Approved",
        "Rejected",
        "Pending",
        "Approval Rate",
    ]

    rows = [
        [
            item.team_name,
            item.members,
            item.total_decisions,
            item.approved_decisions,
            item.rejected_decisions,
            item.pending_decisions,
            f"{item.approval_rate}%",
        ]
        for item in items
    ]

    workbook = create_excel_workbook(
        "Team Report",
        headers,
        rows,
    )

    return excel_response(
        workbook,
        "team_report.xlsx",
    )


# ============================================================
# AUDIT PDF EXPORT
# ============================================================

@router.get(
    "/audit/export/pdf",
)
def export_audit_pdf(
    user_id: Optional[int] = Query(default=None, ge=1),
    action: Optional[str] = Query(default=None),
    entity_type: Optional[str] = Query(default=None),
    entity_id: Optional[int] = Query(default=None, ge=1),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    sort_by: str = Query(default="timestamp"),
    sort_order: str = Query(default="desc"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items, summary = get_all_audit_report_items(
        user_id,
        action,
        entity_type,
        entity_id,
        start_date,
        end_date,
        sort_by,
        sort_order,
        current_user,
        db,
    )

    headers = [
        "Audit ID",
        "User ID",
        "Action",
        "Entity Type",
        "Entity ID",
        "Description",
        "Timestamp",
        "IP Address",
    ]

    rows = [
        [
            item.audit_id,
            item.user_id,
            item.action,
            item.entity_type,
            item.entity_id,
            item.description,
            item.timestamp,
            item.ip_address,
        ]
        for item in items
    ]

    summary_data = {
        "Total Audit Logs": summary.total_audit_logs,
        "CREATE": summary.create_actions,
        "UPDATE": summary.update_actions,
        "DELETE": summary.delete_actions,
        "APPROVE": summary.approve_actions,
        "REJECT": summary.reject_actions,
        "ACCESS": summary.access_actions,
        "LOGIN": summary.login_actions,
        "LOGOUT": summary.logout_actions,
        "SUBMIT": summary.submit_actions,
        "ARCHIVE": summary.archive_actions,
    }

    filters = {
        "User ID": user_id,
        "Action": action,
        "Entity Type": entity_type,
        "Entity ID": entity_id,
        "Start Date": start_date,
        "End Date": end_date,
        "Sort By": sort_by,
        "Sort Order": sort_order,
    }

    pdf = build_pdf(
        "Audit Report",
        headers,
        rows,
        summary=summary_data,
        filters=filters,
    )

    return pdf_response(
        pdf,
        "audit_report.pdf",
    )


# ============================================================
# AUDIT EXCEL EXPORT
# ============================================================

@router.get(
    "/audit/export/excel",
)
def export_audit_excel(
    user_id: Optional[int] = Query(default=None, ge=1),
    action: Optional[str] = Query(default=None),
    entity_type: Optional[str] = Query(default=None),
    entity_id: Optional[int] = Query(default=None, ge=1),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    sort_by: str = Query(default="timestamp"),
    sort_order: str = Query(default="desc"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items, summary = get_all_audit_report_items(
        user_id,
        action,
        entity_type,
        entity_id,
        start_date,
        end_date,
        sort_by,
        sort_order,
        current_user,
        db,
    )

    headers = [
        "Audit ID",
        "User ID",
        "Action",
        "Entity Type",
        "Entity ID",
        "Description",
        "Timestamp",
        "IP Address",
    ]

    rows = [
        [
            item.audit_id,
            item.user_id,
            item.action,
            item.entity_type,
            item.entity_id,
            item.description,
            item.timestamp,
            item.ip_address,
        ]
        for item in items
    ]

    workbook = create_excel_workbook(
        "Audit Report",
        headers,
        rows,
    )

    return excel_response(
        workbook,
        "audit_report.xlsx",
    )


# ============================================================
# END OF REPORT ROUTES
# ============================================================