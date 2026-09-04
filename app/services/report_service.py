from datetime import date, datetime, time
from math import ceil
from typing import Any
from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.approval import Approval, ApprovalStatus
from app.models.audit import AuditLog
from app.models.decision import Decision, DecisionStatus
from app.models.tag import Tag
from app.models.user import User, UserRole
from app.schemas.report import (
    ApprovalReportItem,
    ApprovalReportResponse,
    ApprovalReportSummary,
    AuditReportItem,
    AuditReportResponse,
    AuditReportSummary,
    DecisionReportItem,
    DecisionReportResponse,
    DecisionReportSummary,
    TeamApprovalStatistics,
    TeamReportItem,
    TeamReportResponse,
    TeamReportSummary,
)


def _validate_date_range(start_date: date | None, end_date: date | None):
    if start_date is not None and end_date is not None and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date cannot be after end_date",
        )


def _validate_sort(sort_by: str, allowed_sort_fields: dict[str, Any], sort_order: str):
    if sort_by.lower() not in allowed_sort_fields:
        allowed_list = ", ".join(sorted(allowed_sort_fields.keys()))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid sorting field '{sort_by}'. Allowed fields: {allowed_list}",
        )
    if sort_order.lower() not in ("asc", "desc"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="sort_order must be 'asc' or 'desc'",
        )


# 1. DECISION REPORT SERVICE
def get_decisions_report_data(
    db: Session,
    current_user: User,
    category: str | None = None,
    decision_status: str | None = None,
    created_by: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    tag: str | None = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    paginate: bool = True,
) -> tuple[list[DecisionReportItem], DecisionReportSummary, int, int]:
    """
    Query, filter, aggregate summary stats, and format decision reports.
    """
    _validate_date_range(start_date, end_date)

    if page < 1:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="page must be >= 1")
    if page_size < 1:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="page_size must be >= 1")

    allowed_sort_fields = {
        "created_at": Decision.created_at,
        "created_date": Decision.created_at,
        "updated_at": Decision.updated_at,
        "updated_date": Decision.updated_at,
        "title": Decision.title,
        "status": Decision.status,
        "category": Decision.category,
        "id": Decision.id,
    }
    _validate_sort(sort_by, allowed_sort_fields, sort_order)

    # Base query scoped to organization
    base_query = (
        db.query(Decision)
        .options(
            joinedload(Decision.user),
            joinedload(Decision.tags),
            joinedload(Decision.alternatives),
            joinedload(Decision.approvals),
        )
        .filter(Decision.organization_id == current_user.organization_id)
    )

    # Apply filters
    if category:
        base_query = base_query.filter(Decision.category == category)

    if decision_status:
        try:
            # Validate status against enum values
            status_enum = DecisionStatus(decision_status)
            base_query = base_query.filter(Decision.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid decision status '{decision_status}'",
            )

    if created_by is not None:
        base_query = base_query.filter(Decision.created_by == created_by)

    if start_date is not None:
        base_query = base_query.filter(
            Decision.created_at >= datetime.combine(start_date, time.min)
        )

    if end_date is not None:
        base_query = base_query.filter(
            Decision.created_at <= datetime.combine(end_date, time.max)
        )

    if tag:
        base_query = base_query.filter(Decision.tags.any(Tag.name == tag))

    # Calculate summary statistics over filtered decisions
    # We do counts using subqueries or filtered queries
    total_decisions = base_query.count()

    draft_count = (
        base_query
        .filter(Decision.status == DecisionStatus.DRAFT)
        .count()
    )
    under_review_count = (
        base_query
        .filter(Decision.status == DecisionStatus.UNDER_REVIEW)
        .count()
    )
    approved_count = (
        base_query
        .filter(Decision.status == DecisionStatus.APPROVED)
        .count()
    )
    rejected_count = (
        base_query
        .filter(Decision.status == DecisionStatus.REJECTED)
        .count()
    )
    archived_count = (
        base_query
        .filter(Decision.status == DecisionStatus.ARCHIVED)
        .count()
    )

    summary = DecisionReportSummary(
        total_decisions=total_decisions,
        draft_decisions=draft_count,
        decisions_under_review=under_review_count,
        approved_decisions=approved_count,
        rejected_decisions=rejected_count,
        archived_decisions=archived_count,
    )

    # Sorting
    sort_column = allowed_sort_fields[sort_by.lower()]
    order_clause = sort_column.desc() if sort_order.lower() == "desc" else sort_column.asc()
    ordered_query = base_query.order_by(order_clause)

    # Pagination
    if paginate:
        offset = (page - 1) * page_size
        decisions = ordered_query.offset(offset).limit(page_size).all()
        total_pages = ceil(total_decisions / page_size) if total_decisions > 0 else 0
    else:
        decisions = ordered_query.all()
        total_pages = 1 if total_decisions > 0 else 0

    items: list[DecisionReportItem] = []
    for d in decisions:
        creator_name = d.user.full_name if d.user else None
        tag_names = [t.name for t in d.tags] if d.tags else []
        items.append(
            DecisionReportItem(
                decision_id=d.id,
                decision_title=d.title,
                category=d.category,
                status=d.status.value if hasattr(d.status, "value") else str(d.status),
                created_by=d.created_by,
                creator_name=creator_name,
                created_date=d.created_at,
                updated_date=d.updated_at,
                number_of_alternatives=len(d.alternatives),
                number_of_approvals=len(d.approvals),
                tags=tag_names,
            )
        )

    return items, summary, total_decisions, total_pages


# 2. APPROVAL REPORT SERVICE
def get_approvals_report_data(
    db: Session,
    current_user: User,
    approval_status: str | None = None,
    reviewer_id: int | None = None,
    decision_id: int | None = None,
    approval_level: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    paginate: bool = True,
) -> tuple[list[ApprovalReportItem], ApprovalReportSummary, int, int]:
    """
    Query, filter, aggregate summary stats, and format approval reports.
    """
    _validate_date_range(start_date, end_date)

    if page < 1:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="page must be >= 1")
    if page_size < 1:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="page_size must be >= 1")

    allowed_sort_fields = {
        "created_at": Approval.created_at,
        "assigned_date": Approval.created_at,
        "completed_at": Approval.completed_at,
        "completed_date": Approval.completed_at,
        "status": Approval.status,
        "approval_id": Approval.id,
        "id": Approval.id,
    }
    _validate_sort(sort_by, allowed_sort_fields, sort_order)

    base_query = (
        db.query(Approval)
        .join(Decision, Approval.decision_id == Decision.id)
        .options(
            joinedload(Approval.decision),
            joinedload(Approval.reviewer),
        )
        .filter(Decision.organization_id == current_user.organization_id)
    )

    if approval_status:
        try:
            st_enum = ApprovalStatus(approval_status)
            base_query = base_query.filter(Approval.status == st_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid approval status '{approval_status}'",
            )

    if reviewer_id is not None:
        base_query = base_query.filter(Approval.reviewer_id == reviewer_id)

    if decision_id is not None:
        base_query = base_query.filter(Approval.decision_id == decision_id)

    if start_date is not None:
        base_query = base_query.filter(
            Approval.created_at >= datetime.combine(start_date, time.min)
        )

    if end_date is not None:
        base_query = base_query.filter(
            Approval.created_at <= datetime.combine(end_date, time.max)
        )

    # Summary Statistics Calculation
    total_approvals = base_query.count()
    pending_count = base_query.filter(Approval.status == ApprovalStatus.PENDING).count()
    approved_count = base_query.filter(Approval.status == ApprovalStatus.APPROVED).count()
    rejected_count = base_query.filter(Approval.status == ApprovalStatus.REJECTED).count()

    completed_approvals = (
        base_query
        .filter(
            Approval.status.in_([ApprovalStatus.APPROVED, ApprovalStatus.REJECTED]),
            Approval.completed_at.isnot(None),
        )
        .all()
    )

    turnaround_times = [
        (a.completed_at - a.created_at).total_seconds() / 3600.0
        for a in completed_approvals
        if a.completed_at and a.created_at
    ]

    avg_turnaround = (sum(turnaround_times) / len(turnaround_times)) if turnaround_times else None
    completed_count = approved_count + rejected_count
    completion_rate = (completed_count / total_approvals * 100.0) if total_approvals > 0 else 0.0

    summary = ApprovalReportSummary(
        total_approvals=total_approvals,
        pending_approvals=pending_count,
        approved_approvals=approved_count,
        rejected_approvals=rejected_count,
        average_approval_turnaround_time_hours=avg_turnaround,
        approval_completion_rate=round(completion_rate, 2),
    )

    # Ordering
    sort_column = allowed_sort_fields[sort_by.lower()]
    order_clause = sort_column.desc() if sort_order.lower() == "desc" else sort_column.asc()
    ordered_query = base_query.order_by(order_clause)

    all_matched = ordered_query.all()

    # Calculate sequential approval level per decision
    # Build a lookup of approval levels for each decision
    decision_ids = list({a.decision_id for a in all_matched})
    level_map: dict[int, int] = {}
    if decision_ids:
        all_decision_approvals = (
            db.query(Approval.id, Approval.decision_id)
            .filter(Approval.decision_id.in_(decision_ids))
            .order_by(Approval.decision_id, Approval.created_at.asc(), Approval.id.asc())
            .all()
        )
        current_dec = None
        seq = 1
        for appr_id, dec_id in all_decision_approvals:
            if dec_id != current_dec:
                current_dec = dec_id
                seq = 1
            else:
                seq += 1
            level_map[appr_id] = seq

    items: list[ApprovalReportItem] = []
    for a in all_matched:
        appr_level = level_map.get(a.id, 1)
        if approval_level is not None and appr_level != approval_level:
            continue

        turnaround_val = None
        if a.completed_at and a.created_at:
            turnaround_val = round((a.completed_at - a.created_at).total_seconds() / 3600.0, 2)

        items.append(
            ApprovalReportItem(
                approval_id=a.id,
                decision_id=a.decision_id,
                decision_title=a.decision.title if a.decision else f"Decision #{a.decision_id}",
                reviewer_id=a.reviewer_id,
                reviewer_name=a.reviewer.full_name if a.reviewer else None,
                approval_level=appr_level,
                approval_status=a.status.value if hasattr(a.status, "value") else str(a.status),
                assigned_date=a.created_at,
                completed_date=a.completed_at,
                approval_turnaround_time_hours=turnaround_val,
            )
        )

    # Apply pagination on items after level filtering
    total_matched = len(items)
    if paginate:
        offset = (page - 1) * page_size
        paginated_items = items[offset : offset + page_size]
        total_pages = ceil(total_matched / page_size) if total_matched > 0 else 0
        return paginated_items, summary, total_matched, total_pages
    else:
        total_pages = 1 if total_matched > 0 else 0
        return items, summary, total_matched, total_pages


# 3. TEAM REPORT SERVICE
def get_teams_report_data(
    db: Session,
    current_user: User,
    team: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    decision_status: str | None = None,
    category: str | None = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "team_name",
    sort_order: str = "asc",
    paginate: bool = True,
) -> tuple[list[TeamReportItem], TeamReportSummary, int, int]:
    """
    Query and aggregate team/department statistics with RBAC authorization.
    """
    _validate_date_range(start_date, end_date)

    if page < 1:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="page must be >= 1")
    if page_size < 1:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="page_size must be >= 1")

    allowed_sort_fields = {
        "team_name": "team_name",
        "number_of_members": "number_of_members",
        "total_decisions": "total_decisions",
        "created_date": "created_date",
        "created_at": "created_date",
    }
    if sort_by.lower() not in allowed_sort_fields:
        allowed_list = ", ".join(sorted(allowed_sort_fields.keys()))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid sorting field '{sort_by}'. Allowed fields: {allowed_list}",
        )
    if sort_order.lower() not in ("asc", "desc"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="sort_order must be 'asc' or 'desc'",
        )

    # RBAC rules for Teams
    # Administrator: can view all departments
    # Manager, Reviewer, Employee: restricted to their own department
    if current_user.role != UserRole.ADMINISTRATOR:
        user_dept = current_user.department or "General"
        if team is not None and team.lower() != user_dept.lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view reports for other teams",
            )
        team = user_dept

    # Validate decision_status enum if provided
    status_enum = None
    if decision_status:
        try:
            status_enum = DecisionStatus(decision_status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid decision status '{decision_status}'",
            )

    # Find distinct departments in the user's organization
    dept_query = (
        db.query(User.department)
        .filter(
            User.organization_id == current_user.organization_id,
            User.department.isnot(None),
            User.department != "",
        )
        .distinct()
    )
    if team:
        dept_query = dept_query.filter(User.department == team)

    departments = [row[0] for row in dept_query.all()]
    if not departments and team:
        departments = [team]

    items: list[TeamReportItem] = []
    total_org_members = 0
    total_org_decisions = 0
    total_org_approvals = 0

    for dept_name in departments:
        # Get users belonging to this department in the org
        team_users = (
            db.query(User)
            .filter(
                User.organization_id == current_user.organization_id,
                User.department == dept_name,
            )
            .all()
        )
        member_count = len(team_users)
        user_ids = [u.id for u in team_users]

        total_org_members += member_count

        if not user_ids:
            items.append(
                TeamReportItem(
                    team_name=dept_name,
                    number_of_members=0,
                    total_decisions=0,
                    approved_decisions=0,
                    rejected_decisions=0,
                    pending_decisions=0,
                    team_approval_statistics=TeamApprovalStatistics(
                        total_approvals=0,
                        approved_approvals=0,
                        rejected_approvals=0,
                        pending_approvals=0,
                        average_turnaround_time_hours=None,
                        completion_rate=0.0,
                    ),
                )
            )
            continue

        # Decisions created by this team
        dec_query = (
            db.query(Decision)
            .filter(
                Decision.organization_id == current_user.organization_id,
                Decision.created_by.in_(user_ids),
            )
        )

        if category:
            dec_query = dec_query.filter(Decision.category == category)

        if status_enum:
            dec_query = dec_query.filter(Decision.status == status_enum)

        if start_date is not None:
            dec_query = dec_query.filter(
                Decision.created_at >= datetime.combine(start_date, time.min)
            )

        if end_date is not None:
            dec_query = dec_query.filter(
                Decision.created_at <= datetime.combine(end_date, time.max)
            )

        t_decisions = dec_query.count()
        t_approved = dec_query.filter(Decision.status == DecisionStatus.APPROVED).count()
        t_rejected = dec_query.filter(Decision.status == DecisionStatus.REJECTED).count()
        t_pending = (
            dec_query
            .filter(Decision.status.in_([DecisionStatus.DRAFT, DecisionStatus.UNDER_REVIEW]))
            .count()
        )

        total_org_decisions += t_decisions

        # Approvals for decisions created by this team
        team_decisions_subquery = (
            db.query(Decision.id)
            .filter(
                Decision.organization_id == current_user.organization_id,
                Decision.created_by.in_(user_ids),
            )
        )
        if start_date is not None:
            team_decisions_subquery = team_decisions_subquery.filter(
                Decision.created_at >= datetime.combine(start_date, time.min)
            )
        if end_date is not None:
            team_decisions_subquery = team_decisions_subquery.filter(
                Decision.created_at <= datetime.combine(end_date, time.max)
            )

        appr_query = db.query(Approval).filter(Approval.decision_id.in_(team_decisions_subquery))
        t_appr_total = appr_query.count()
        t_appr_approved = appr_query.filter(Approval.status == ApprovalStatus.APPROVED).count()
        t_appr_rejected = appr_query.filter(Approval.status == ApprovalStatus.REJECTED).count()
        t_appr_pending = appr_query.filter(Approval.status == ApprovalStatus.PENDING).count()

        total_org_approvals += t_appr_total

        completed_apprs = (
            appr_query
            .filter(
                Approval.status.in_([ApprovalStatus.APPROVED, ApprovalStatus.REJECTED]),
                Approval.completed_at.isnot(None),
            )
            .all()
        )
        t_turnarounds = [
            (a.completed_at - a.created_at).total_seconds() / 3600.0
            for a in completed_apprs
            if a.completed_at and a.created_at
        ]
        t_avg_turnaround = (sum(t_turnarounds) / len(t_turnarounds)) if t_turnarounds else None
        t_completed_count = t_appr_approved + t_appr_rejected
        t_comp_rate = (t_completed_count / t_appr_total * 100.0) if t_appr_total > 0 else 0.0

        items.append(
            TeamReportItem(
                team_name=dept_name,
                number_of_members=member_count,
                total_decisions=t_decisions,
                approved_decisions=t_approved,
                rejected_decisions=t_rejected,
                pending_decisions=t_pending,
                team_approval_statistics=TeamApprovalStatistics(
                    total_approvals=t_appr_total,
                    approved_approvals=t_appr_approved,
                    rejected_approvals=t_appr_rejected,
                    pending_approvals=t_appr_pending,
                    average_turnaround_time_hours=(
                        round(t_avg_turnaround, 2) if t_avg_turnaround is not None else None
                    ),
                    completion_rate=round(t_comp_rate, 2),
                ),
            )
        )

    # In-memory sorting for aggregated team items
    reverse = (sort_order.lower() == "desc")
    if sort_by.lower() == "team_name":
        items.sort(key=lambda x: x.team_name.lower(), reverse=reverse)
    elif sort_by.lower() == "number_of_members":
        items.sort(key=lambda x: x.number_of_members, reverse=reverse)
    elif sort_by.lower() == "total_decisions":
        items.sort(key=lambda x: x.total_decisions, reverse=reverse)

    summary = TeamReportSummary(
        total_teams=len(items),
        total_members=total_org_members,
        total_decisions=total_org_decisions,
        total_approvals=total_org_approvals,
    )

    total_matched = len(items)
    if paginate:
        offset = (page - 1) * page_size
        paginated_items = items[offset : offset + page_size]
        total_pages = ceil(total_matched / page_size) if total_matched > 0 else 0
        return paginated_items, summary, total_matched, total_pages
    else:
        total_pages = 1 if total_matched > 0 else 0
        return items, summary, total_matched, total_pages


# 4. AUDIT REPORT SERVICE
def get_audit_report_data(
    db: Session,
    current_user: User,
    user_id: int | None = None,
    action: str | None = None,
    entity_type: str | None = None,
    entity_id: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    paginate: bool = True,
) -> tuple[list[AuditReportItem], AuditReportSummary, int, int]:
    """
    Query, filter, and summarize system audit activities.
    RBAC: strictly Administrator only.
    """
    if current_user.role != UserRole.ADMINISTRATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Audit reports are restricted to Administrators only",
        )

    _validate_date_range(start_date, end_date)

    if page < 1:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="page must be >= 1")
    if page_size < 1:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="page_size must be >= 1")

    allowed_sort_fields = {
        "created_at": AuditLog.created_at,
        "timestamp": AuditLog.created_at,
        "action": AuditLog.action,
        "entity_type": AuditLog.entity_type,
        "user_id": AuditLog.user_id,
        "audit_id": AuditLog.id,
        "id": AuditLog.id,
    }
    _validate_sort(sort_by, allowed_sort_fields, sort_order)

    base_query = (
        db.query(AuditLog)
        .join(User, AuditLog.user_id == User.id)
        .options(joinedload(AuditLog.user))
        .filter(User.organization_id == current_user.organization_id)
    )

    if user_id is not None:
        base_query = base_query.filter(AuditLog.user_id == user_id)

    if action:
        base_query = base_query.filter(AuditLog.action == action)

    if entity_type:
        base_query = base_query.filter(AuditLog.entity_type == entity_type)

    if entity_id is not None:
        base_query = base_query.filter(AuditLog.entity_id == entity_id)

    if start_date is not None:
        base_query = base_query.filter(
            AuditLog.created_at >= datetime.combine(start_date, time.min)
        )

    if end_date is not None:
        base_query = base_query.filter(
            AuditLog.created_at <= datetime.combine(end_date, time.max)
        )

    total_records = base_query.count()

    # Action counts breakdown
    actions_data = (
        base_query.with_entities(AuditLog.action, func.count(AuditLog.id))
        .group_by(AuditLog.action)
        .all()
    )
    actions_breakdown = {row[0]: row[1] for row in actions_data}

    # Entity types breakdown
    entities_data = (
        base_query.with_entities(AuditLog.entity_type, func.count(AuditLog.id))
        .group_by(AuditLog.entity_type)
        .all()
    )
    entity_types_breakdown = {row[0]: row[1] for row in entities_data}

    summary = AuditReportSummary(
        total_audit_records=total_records,
        actions_breakdown=actions_breakdown,
        entity_types_breakdown=entity_types_breakdown,
    )

    # Ordering
    sort_column = allowed_sort_fields[sort_by.lower()]
    order_clause = sort_column.desc() if sort_order.lower() == "desc" else sort_column.asc()
    ordered_query = base_query.order_by(order_clause)

    if paginate:
        offset = (page - 1) * page_size
        logs = ordered_query.offset(offset).limit(page_size).all()
        total_pages = ceil(total_records / page_size) if total_records > 0 else 0
    else:
        logs = ordered_query.all()
        total_pages = 1 if total_records > 0 else 0

    items: list[AuditReportItem] = []
    for log in logs:
        items.append(
            AuditReportItem(
                audit_id=log.id,
                user_id=log.user_id,
                user_name=log.user.full_name if log.user else None,
                user_email=log.user.email if log.user else None,
                action=log.action,
                entity_type=log.entity_type,
                entity_id=log.entity_id,
                description=log.description,
                timestamp=log.created_at,
                ip_address=log.ip_address,
            )
        )

    return items, summary, total_records, total_pages
