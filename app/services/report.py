from datetime import datetime
from math import ceil
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.decision import Decision
from app.models.approval import Approval
from app.models.user import User
from app.models.audit_log import AuditLog
from app.models.tag import Tag

from app.schemas.report import (
    DecisionReportResponse,
    DecisionReportRow,
    DecisionReportSummary,
    ApprovalReportResponse,
    ApprovalReportRow,
    ApprovalReportStats,
    TeamReportResponse,
    TeamReportRow,
    AuditReportResponse,
    AuditReportRow,
    ReportPagination,
)


# =========================================================
# COMMON HELPERS
# =========================================================

def _pagination(
    page: int,
    page_size: int,
    total: int,
):
    return ReportPagination(
        page=page,
        page_size=page_size,
        total=total,
        total_pages=ceil(total / page_size)
        if total
        else 0,
    )


def _validate_date_range(
    start_date: Optional[datetime],
    end_date: Optional[datetime],
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date cannot be later than end_date",
        )


def _validate_sort(
    sort_by: str,
    allowed_fields: set[str],
):
    if sort_by not in allowed_fields:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Invalid sort field. Allowed values: "
                + ", ".join(sorted(allowed_fields))
            ),
        )


def _validate_order(order: str):
    if order.lower() not in {"asc", "desc"}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="order must be 'asc' or 'desc'",
        )


def _validate_page(
    page: int,
    page_size: int,
):
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="page must be at least 1",
        )

    if page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="page_size must be between 1 and 100",
        )


# =========================================================
# DECISION REPORT
# =========================================================

def get_decision_report(
    db: Session,
    current_user,
    category: Optional[str] = None,
    status_filter: Optional[str] = None,
    created_by: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    tag: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "created_date",
    order: str = "desc",
):
    _validate_date_range(start_date, end_date)

    _validate_page(page, page_size)

    _validate_sort(
        sort_by,
        {
            "created_date",
            "updated_date",
            "title",
        },
    )

    _validate_order(order)

    query = db.query(Decision)

    role = current_user.role

    # -----------------------------------------------------
    # Existing decision visibility / RBAC
    # -----------------------------------------------------

    if role in {"Admin", "Administrator"}:
        pass

    elif role == "Employee":
        query = query.filter(
            Decision.created_by == current_user.id
        )

    elif role == "Reviewer":
        query = query.filter(
            or_(
                Decision.created_by == current_user.id,
                Decision.status != "Draft",
            )
        )

    elif role == "Manager":
        query = (
            query
            .join(
                User,
                Decision.created_by == User.id,
            )
            .filter(
                or_(
                    User.department
                    == current_user.department,
                    Decision.created_by
                    == current_user.id,
                )
            )
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access reports",
        )

    # -----------------------------------------------------
    # Filters
    # -----------------------------------------------------

    if category:
        query = query.filter(
            Decision.category == category
        )

    if status_filter:
        allowed_statuses = {
            "Draft",
            "Under Review",
            "Approved",
            "Rejected",
            "Archived",
        }

        if status_filter not in allowed_statuses:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid decision status",
            )

        query = query.filter(
            Decision.status == status_filter
        )

    if created_by is not None:
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
        query = (
            query
            .join(Decision.tags)
            .filter(
                Tag.name.ilike(f"%{tag}%")
            )
            .distinct()
        )

    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------

    filtered_decisions = query.all()

    total = len(filtered_decisions)

    summary = DecisionReportSummary(
        total_decisions=total,
        draft=sum(
            1
            for decision in filtered_decisions
            if decision.status == "Draft"
        ),
        under_review=sum(
            1
            for decision in filtered_decisions
            if decision.status == "Under Review"
        ),
        approved=sum(
            1
            for decision in filtered_decisions
            if decision.status == "Approved"
        ),
        rejected=sum(
            1
            for decision in filtered_decisions
            if decision.status == "Rejected"
        ),
        archived=sum(
            1
            for decision in filtered_decisions
            if decision.status == "Archived"
        ),
    )

    # -----------------------------------------------------
    # Controlled sorting
    # -----------------------------------------------------

    sort_columns = {
        "created_date": Decision.created_at,
        "updated_date": Decision.updated_at,
        "title": Decision.title,
    }

    sort_column = sort_columns[sort_by]

    if order.lower() == "asc":
        query = query.order_by(
            sort_column.asc()
        )
    else:
        query = query.order_by(
            sort_column.desc()
        )

    # -----------------------------------------------------
    # Pagination
    # -----------------------------------------------------

    offset = (page - 1) * page_size

    decisions = (
        query
        .offset(offset)
        .limit(page_size)
        .all()
    )

    rows = []

    for decision in decisions:
        approval_count = (
            db.query(Approval)
            .filter(
                Approval.decision_id
                == decision.id
            )
            .count()
        )

        rows.append(
            DecisionReportRow(
                decision_id=decision.id,
                title=decision.title,
                category=decision.category,
                status=decision.status,
                created_by=(
                    decision.user.full_name
                    if decision.user
                    else None
                ),
                created_date=decision.created_at,
                updated_date=decision.updated_at,
                number_of_alternatives=len(
                    decision.alternatives
                ),
                number_of_approvals=approval_count,
                tags=[
                    current_tag.name
                    for current_tag in decision.tags
                ],
            )
        )

    return DecisionReportResponse(
        summary=summary,
        data=rows,
        pagination=_pagination(
            page,
            page_size,
            total,
        ),
    )


# =========================================================
# APPROVAL REPORT
# =========================================================

def get_approval_report(
    db: Session,
    current_user,
    approval_status: Optional[str] = None,
    reviewer: Optional[int] = None,
    decision_id: Optional[int] = None,
    approval_level: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "approval_date",
    order: str = "desc",
):
    _validate_date_range(start_date, end_date)

    _validate_page(page, page_size)

    _validate_sort(
        sort_by,
        {"approval_date"},
    )

    _validate_order(order)

    query = (
        db.query(Approval)
        .join(
            Decision,
            Approval.decision_id
            == Decision.id,
        )
    )

    role = current_user.role

    # -----------------------------------------------------
    # RBAC
    # -----------------------------------------------------

    if role in {"Admin", "Administrator"}:
        pass

    elif role == "Reviewer":
        query = query.filter(
            Approval.assigned_reviewer_id
            == current_user.id
        )

    elif role == "Employee":
        query = query.filter(
            Decision.created_by
            == current_user.id
        )

    elif role == "Manager":
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

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access reports",
        )

    # -----------------------------------------------------
    # Filters
    # -----------------------------------------------------

    if approval_status:
        allowed_statuses = {
            "Pending",
            "Approved",
            "Rejected",
        }

        if approval_status not in allowed_statuses:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid approval status",
            )

        query = query.filter(
            Approval.status
            == approval_status
        )

    if reviewer is not None:
        query = query.filter(
            Approval.assigned_reviewer_id
            == reviewer
        )

    if decision_id is not None:
        query = query.filter(
            Approval.decision_id
            == decision_id
        )

    if approval_level is not None:
        if approval_level < 1:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="approval_level must be at least 1",
            )

        query = query.filter(
            Approval.approval_level
            == approval_level
        )

    if start_date:
        query = query.filter(
            Approval.created_at
            >= start_date
        )

    if end_date:
        query = query.filter(
            Approval.created_at
            <= end_date
        )

    # -----------------------------------------------------
    # Statistics
    # -----------------------------------------------------

    all_approvals = query.all()

    total = len(all_approvals)

    pending = sum(
        1
        for approval in all_approvals
        if approval.status == "Pending"
    )

    approved = sum(
        1
        for approval in all_approvals
        if approval.status == "Approved"
    )

    rejected = sum(
        1
        for approval in all_approvals
        if approval.status == "Rejected"
    )

    completed = approved + rejected

    completion_rate = (
        (completed / total) * 100
        if total
        else 0.0
    )

    # -----------------------------------------------------
    # Turnaround time
    # -----------------------------------------------------

    turnaround_seconds = []

    for approval in all_approvals:
        if (
            approval.created_at
            and approval.completed_at
        ):
            seconds = (
                approval.completed_at
                - approval.created_at
            ).total_seconds()

            turnaround_seconds.append(
                seconds
            )

    average_turnaround = None

    if turnaround_seconds:
        average_seconds = (
            sum(turnaround_seconds)
            / len(turnaround_seconds)
        )

        average_turnaround = (
            f"{average_seconds / 3600:.2f} hours"
        )

    # -----------------------------------------------------
    # Sorting
    # -----------------------------------------------------

    if order.lower() == "asc":
        query = query.order_by(
            Approval.created_at.asc()
        )
    else:
        query = query.order_by(
            Approval.created_at.desc()
        )

    # -----------------------------------------------------
    # Pagination
    # -----------------------------------------------------

    offset = (page - 1) * page_size

    approvals = (
        query
        .offset(offset)
        .limit(page_size)
        .all()
    )

    rows = []

    for approval in approvals:
        reviewer_user = (
            db.query(User)
            .filter(
                User.id
                == approval.assigned_reviewer_id
            )
            .first()
        )

        turnaround = None

        if (
            approval.created_at
            and approval.completed_at
        ):
            seconds = (
                approval.completed_at
                - approval.created_at
            ).total_seconds()

            turnaround = (
                f"{seconds / 3600:.2f} hours"
            )

        rows.append(
            ApprovalReportRow(
                approval_id=approval.id,
                decision_id=approval.decision_id,
                decision_title=(
                    approval.decision.title
                    if approval.decision
                    else ""
                ),
                reviewer=(
                    reviewer_user.full_name
                    if reviewer_user
                    else None
                ),
                approval_level=approval.approval_level,
                approval_status=approval.status,
                assigned_date=approval.created_at,
                completed_date=approval.completed_at,
                approval_turnaround_time=turnaround,
            )
        )

    return ApprovalReportResponse(
        stats=ApprovalReportStats(
            total_approvals=total,
            pending=pending,
            approved=approved,
            rejected=rejected,
            average_approval_turnaround=(
                average_turnaround
            ),
            completion_rate=round(
                completion_rate,
                2,
            ),
        ),
        data=rows,
        pagination=_pagination(
            page,
            page_size,
            total,
        ),
    )


# =========================================================
# TEAM REPORT
# =========================================================

def get_team_report(
    db: Session,
    current_user,
    team: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    decision_status: Optional[str] = None,
    category: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "team_name",
    order: str = "asc",
):
    _validate_date_range(start_date, end_date)

    _validate_page(page, page_size)

    _validate_sort(
        sort_by,
        {"team_name"},
    )

    _validate_order(order)

    role = current_user.role

    if role not in {
        "Admin",
        "Administrator",
        "Manager",
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only Managers and Administrators "
                "can access team reports"
            ),
        )

    # -----------------------------------------------------
    # Team = existing User.department
    # -----------------------------------------------------

    if role == "Manager":
        departments = [
            current_user.department
        ]

    else:
        departments = [
            row[0]
            for row in (
                db.query(User.department)
                .filter(
                    User.department.isnot(None)
                )
                .distinct()
                .all()
            )
        ]

    if team:
        if (
            role == "Manager"
            and team
            != current_user.department
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You cannot access this team report"
                ),
            )

        departments = [team]

    rows = []

    for department in departments:
        if department is None:
            continue

        # -------------------------------------------------
        # Members
        # -------------------------------------------------

        member_count = (
            db.query(User)
            .filter(
                User.department
                == department
            )
            .count()
        )

        # -------------------------------------------------
        # Decisions
        # -------------------------------------------------

        decision_query = (
            db.query(Decision)
            .join(
                User,
                Decision.created_by
                == User.id,
            )
            .filter(
                User.department
                == department
            )
        )

        if start_date:
            decision_query = (
                decision_query.filter(
                    Decision.created_at
                    >= start_date
                )
            )

        if end_date:
            decision_query = (
                decision_query.filter(
                    Decision.created_at
                    <= end_date
                )
            )

        if decision_status:
            allowed_statuses = {
                "Draft",
                "Under Review",
                "Approved",
                "Rejected",
                "Archived",
            }

            if decision_status not in allowed_statuses:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Invalid decision status",
                )

            decision_query = (
                decision_query.filter(
                    Decision.status
                    == decision_status
                )
            )

        if category:
            decision_query = (
                decision_query.filter(
                    Decision.category
                    == category
                )
            )

        decisions = decision_query.all()

        total_decisions = len(decisions)

        approved_decisions = sum(
            1
            for decision in decisions
            if decision.status == "Approved"
        )

        rejected_decisions = sum(
            1
            for decision in decisions
            if decision.status == "Rejected"
        )

        pending_decisions = sum(
            1
            for decision in decisions
            if decision.status
            in {
                "Draft",
                "Under Review",
            }
        )

        # -------------------------------------------------
        # Team approvals
        # -------------------------------------------------

        decision_ids = [
            decision.id
            for decision in decisions
        ]

        if decision_ids:
            team_approvals = (
                db.query(Approval)
                .filter(
                    Approval.decision_id.in_(
                        decision_ids
                    )
                )
                .all()
            )
        else:
            team_approvals = []

        approval_total = len(
            team_approvals
        )

        approval_pending = sum(
            1
            for approval in team_approvals
            if approval.status == "Pending"
        )

        approval_approved = sum(
            1
            for approval in team_approvals
            if approval.status == "Approved"
        )

        approval_rejected = sum(
            1
            for approval in team_approvals
            if approval.status == "Rejected"
        )

        approval_completed = (
            approval_approved
            + approval_rejected
        )

        approval_completion_rate = (
            (
                approval_completed
                / approval_total
                * 100
            )
            if approval_total
            else 0.0
        )

        rows.append(
            TeamReportRow(
                team_name=department,
                number_of_members=member_count,
                total_decisions=total_decisions,
                approved_decisions=approved_decisions,
                rejected_decisions=rejected_decisions,
                pending_decisions=pending_decisions,
                team_approval_statistics={
                    "total_approvals": approval_total,
                    "pending": approval_pending,
                    "approved": approval_approved,
                    "rejected": approval_rejected,
                    "completion_rate": round(
                        approval_completion_rate,
                        2,
                    ),
                },
            )
        )

    # -----------------------------------------------------
    # Sorting
    # -----------------------------------------------------

    rows.sort(
        key=lambda row: row.team_name.lower(),
        reverse=order.lower() == "desc",
    )

    total = len(rows)

    # -----------------------------------------------------
    # Pagination
    # -----------------------------------------------------

    offset = (page - 1) * page_size

    paginated_rows = rows[
        offset:offset + page_size
    ]

    return TeamReportResponse(
        data=paginated_rows,
        pagination=_pagination(
            page,
            page_size,
            total,
        ),
    )


# =========================================================
# AUDIT REPORT
# =========================================================

def get_audit_report(
    db: Session,
    current_user,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "timestamp",
    order: str = "desc",
):
    _validate_date_range(start_date, end_date)

    _validate_page(page, page_size)

    _validate_sort(
        sort_by,
        {"timestamp"},
    )

    _validate_order(order)

    # -----------------------------------------------------
    # Sprint 11 audit authorization
    # -----------------------------------------------------

    if current_user.role not in {
        "Admin",
        "Administrator",
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only Administrators can access "
                "audit reports"
            ),
        )

    query = db.query(AuditLog)

    # -----------------------------------------------------
    # Filters
    # -----------------------------------------------------

    if user_id is not None:
        query = query.filter(
            AuditLog.user_id == user_id
        )

    if action:
        allowed_actions = {
            "CREATE",
            "UPDATE",
            "DELETE",
            "APPROVE",
            "REJECT",
            "SUBMIT",
        }

        if action not in allowed_actions:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid audit action",
            )

        query = query.filter(
            AuditLog.action == action
        )

    if entity_type:
        query = query.filter(
            AuditLog.entity_type
            == entity_type
        )

    if entity_id is not None:
        query = query.filter(
            AuditLog.entity_id
            == entity_id
        )

    if start_date:
        query = query.filter(
            AuditLog.created_at
            >= start_date
        )

    if end_date:
        query = query.filter(
            AuditLog.created_at
            <= end_date
        )

    # -----------------------------------------------------
    # Sorting
    # -----------------------------------------------------

    if order.lower() == "asc":
        query = query.order_by(
            AuditLog.created_at.asc()
        )
    else:
        query = query.order_by(
            AuditLog.created_at.desc()
        )

    # -----------------------------------------------------
    # Total
    # -----------------------------------------------------

    total = query.count()

    # -----------------------------------------------------
    # Pagination
    # -----------------------------------------------------

    offset = (page - 1) * page_size

    logs = (
        query
        .offset(offset)
        .limit(page_size)
        .all()
    )

    rows = []

    for log in logs:
        rows.append(
            AuditReportRow(
                user=(
                    log.user.full_name
                    if log.user
                    else None
                ),
                action=log.action,
                entity_type=log.entity_type,
                entity_id=log.entity_id,
                description=log.description,
                timestamp=log.created_at,
                ip_address=log.ip_address,
            )
        )

    return AuditReportResponse(
        data=rows,
        pagination=_pagination(
            page,
            page_size,
            total,
        ),
    )