import math
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from fastapi import HTTPException, status as http_status
from sqlalchemy import func, desc, asc
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.approval import Approval
from app.models.audit_log import AuditLog
from app.models.decision import Decision
from app.models.tag import Tag
from app.models.user import User
from app.services.audit_service import VALID_AUDIT_ACTIONS, VALID_ENTITY_TYPES

VALID_DECISION_STATUSES = {"Draft", "Under Review", "Approved", "Rejected", "Archived"}
VALID_APPROVAL_STATUSES = {"Pending", "Approved", "Rejected"}

ALLOWED_DECISION_SORT_FIELDS = {
    "created_at": Decision.created_at,
    "created_date": Decision.created_at,
    "updated_at": Decision.updated_at,
    "updated_date": Decision.updated_at,
    "title": Decision.title,
    "status": Decision.status,
    "category": Decision.category,
    "id": Decision.id,
    "decision_id": Decision.id,
}

ALLOWED_APPROVAL_SORT_FIELDS = {
    "created_at": Approval.created_at,
    "assigned_date": Approval.created_at,
    "completed_at": Approval.completed_at,
    "completed_date": Approval.completed_at,
    "approval_level": Approval.approval_level,
    "status": Approval.status,
    "approval_status": Approval.status,
    "decision_id": Approval.decision_id,
    "id": Approval.id,
    "approval_id": Approval.id,
}

ALLOWED_TEAM_SORT_FIELDS = {
    "team_name",
    "department",
    "number_of_members",
    "total_decisions",
    "approved_decisions",
    "rejected_decisions",
    "pending_decisions",
}

ALLOWED_AUDIT_SORT_FIELDS = {
    "created_at": AuditLog.created_at,
    "timestamp": AuditLog.created_at,
    "action": AuditLog.action,
    "entity_type": AuditLog.entity_type,
    "user_id": AuditLog.user_id,
    "id": AuditLog.id,
}


def parse_and_validate_dates(
    start_date: Optional[str],
    end_date: Optional[str]
) -> Tuple[Optional[datetime], Optional[datetime]]:
    parsed_start = None
    parsed_end = None

    if start_date:
        try:
            parsed_start = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid start_date format. Expected YYYY-MM-DD"
            )

    if end_date:
        try:
            parsed_end = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        except ValueError:
            raise HTTPException(
                status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid end_date format. Expected YYYY-MM-DD"
            )

    if parsed_start and parsed_end and parsed_start > parsed_end:
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date cannot be after end_date"
        )

    return parsed_start, parsed_end


# =============================================================================
# 1. DECISION REPORT SERVICE
# =============================================================================

def get_decision_report_data(
    db: Session,
    category: Optional[str] = None,
    status: Optional[str] = None,
    created_by: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    tag: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    page: Optional[int] = None,
    page_size: Optional[int] = None,
) -> Tuple[List[dict], dict, int, int]:
    # Validate date range
    parsed_start, parsed_end = parse_and_validate_dates(start_date, end_date)

    # Validate status if provided
    if status:
        matched_status = [s for s in VALID_DECISION_STATUSES if s.lower() == status.strip().lower()]
        if not matched_status:
            raise HTTPException(
                status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid status '{status}'. Allowed statuses: {sorted(list(VALID_DECISION_STATUSES))}"
            )
        status = matched_status[0]

    # Validate sorting field
    sort_key = sort_by.strip().lower()
    if sort_key not in ALLOWED_DECISION_SORT_FIELDS:
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid sort_by field '{sort_by}'. Allowed fields: {sorted(list(ALLOWED_DECISION_SORT_FIELDS.keys()))}"
        )

    sort_column = ALLOWED_DECISION_SORT_FIELDS[sort_key]
    order_func = desc if sort_order.strip().lower() == "desc" else asc

    # Build query
    query = (
        db.query(Decision)
        .options(
            joinedload(Decision.creator),
            selectinload(Decision.alternatives),
            selectinload(Decision.approvals),
            selectinload(Decision.tags),
        )
    )

    if category:
        query = query.filter(Decision.category.ilike(f"%{category.strip()}%"))
    if status:
        query = query.filter(Decision.status == status)
    if created_by is not None:
        query = query.filter(Decision.created_by == created_by)
    if parsed_start:
        query = query.filter(Decision.created_at >= parsed_start)
    if parsed_end:
        query = query.filter(Decision.created_at <= parsed_end)
    if tag:
        query = query.filter(Decision.tags.any(Tag.name.ilike(f"%{tag.strip()}%")))

    # Summary metrics over the filtered set
    all_filtered_decisions = query.all()
    total_count = len(all_filtered_decisions)

    summary = {
        "total_decisions": total_count,
        "draft_decisions": sum(1 for d in all_filtered_decisions if d.status == "Draft"),
        "decisions_under_review": sum(1 for d in all_filtered_decisions if d.status == "Under Review"),
        "approved_decisions": sum(1 for d in all_filtered_decisions if d.status == "Approved"),
        "rejected_decisions": sum(1 for d in all_filtered_decisions if d.status == "Rejected"),
        "archived_decisions": sum(1 for d in all_filtered_decisions if d.status == "Archived"),
    }

    # Ordering & Pagination
    sorted_query = query.order_by(order_func(sort_column))

    if page is not None and page_size is not None:
        if page < 1 or page_size < 1:
            raise HTTPException(
                status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Page and page_size must be positive integers"
            )
        decisions = sorted_query.offset((page - 1) * page_size).limit(page_size).all()
        total_pages = math.ceil(total_count / page_size) if total_count > 0 else 1
    else:
        decisions = sorted_query.all()
        total_pages = 1

    # Convert to dict items
    items = []
    for d in decisions:
        items.append({
            "decision_id": d.id,
            "title": d.title,
            "category": d.category,
            "status": d.status,
            "created_by": d.created_by,
            "created_by_name": d.creator.full_name if d.creator else None,
            "created_at": d.created_at,
            "updated_at": d.updated_at,
            "number_of_alternatives": len(d.alternatives) if d.alternatives else 0,
            "number_of_approvals": len(d.approvals) if d.approvals else 0,
            "tags": [t.name for t in d.tags] if d.tags else [],
        })

    return items, summary, total_count, total_pages


# =============================================================================
# 2. APPROVAL REPORT SERVICE
# =============================================================================

def get_approval_report_data(
    db: Session,
    status: Optional[str] = None,
    reviewer_id: Optional[int] = None,
    decision_id: Optional[int] = None,
    approval_level: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    page: Optional[int] = None,
    page_size: Optional[int] = None,
) -> Tuple[List[dict], dict, int, int]:
    # Validate date range
    parsed_start, parsed_end = parse_and_validate_dates(start_date, end_date)

    # Validate status
    if status:
        matched_status = [s for s in VALID_APPROVAL_STATUSES if s.lower() == status.strip().lower()]
        if not matched_status:
            raise HTTPException(
                status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid status '{status}'. Allowed statuses: {sorted(list(VALID_APPROVAL_STATUSES))}"
            )
        status = matched_status[0]

    # Validate sorting field
    sort_key = sort_by.strip().lower()
    if sort_key not in ALLOWED_APPROVAL_SORT_FIELDS:
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid sort_by field '{sort_by}'. Allowed fields: {sorted(list(ALLOWED_APPROVAL_SORT_FIELDS.keys()))}"
        )

    sort_column = ALLOWED_APPROVAL_SORT_FIELDS[sort_key]
    order_func = desc if sort_order.strip().lower() == "desc" else asc

    # Build query
    query = (
        db.query(Approval)
        .options(
            joinedload(Approval.decision),
            joinedload(Approval.reviewer),
        )
    )

    if status:
        query = query.filter(Approval.status == status)
    if reviewer_id is not None:
        query = query.filter(Approval.reviewer_id == reviewer_id)
    if decision_id is not None:
        query = query.filter(Approval.decision_id == decision_id)
    if approval_level is not None:
        query = query.filter(Approval.approval_level == approval_level)
    if parsed_start:
        query = query.filter(Approval.created_at >= parsed_start)
    if parsed_end:
        query = query.filter(Approval.created_at <= parsed_end)

    all_filtered = query.all()
    total_count = len(all_filtered)

    # Compute summaries & turnaround metrics
    pending_count = 0
    approved_count = 0
    rejected_count = 0
    turnaround_times = []

    for a in all_filtered:
        if a.status == "Pending":
            pending_count += 1
        elif a.status == "Approved":
            approved_count += 1
        elif a.status == "Rejected":
            rejected_count += 1

        if a.completed_at and a.created_at:
            diff_hours = max(0.0, (a.completed_at - a.created_at).total_seconds() / 3600.0)
            turnaround_times.append(diff_hours)

    avg_tt = round(sum(turnaround_times) / len(turnaround_times), 2) if turnaround_times else None
    completed_count = approved_count + rejected_count
    comp_rate = round((completed_count / total_count) * 100.0, 2) if total_count > 0 else 0.0

    summary = {
        "total_approvals": total_count,
        "pending_approvals": pending_count,
        "approved_approvals": approved_count,
        "rejected_approvals": rejected_count,
        "average_turnaround_time_hours": avg_tt,
        "approval_completion_rate": comp_rate,
    }

    # Ordering & Pagination
    sorted_query = query.order_by(order_func(sort_column))

    if page is not None and page_size is not None:
        if page < 1 or page_size < 1:
            raise HTTPException(
                status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Page and page_size must be positive integers"
            )
        approvals = sorted_query.offset((page - 1) * page_size).limit(page_size).all()
        total_pages = math.ceil(total_count / page_size) if total_count > 0 else 1
    else:
        approvals = sorted_query.all()
        total_pages = 1

    items = []
    for a in approvals:
        tt = None
        if a.completed_at and a.created_at:
            tt = round(max(0.0, (a.completed_at - a.created_at).total_seconds() / 3600.0), 2)

        items.append({
            "approval_id": a.id,
            "decision_id": a.decision_id,
            "decision_title": a.decision.title if a.decision else f"Decision #{a.decision_id}",
            "reviewer_id": a.reviewer_id,
            "reviewer_name": a.reviewer.full_name if a.reviewer else None,
            "reviewer_email": a.reviewer.email if a.reviewer else None,
            "approval_level": a.approval_level,
            "approval_status": a.status,
            "assigned_date": a.created_at,
            "completed_date": a.completed_at,
            "turnaround_time_hours": tt,
        })

    return items, summary, total_count, total_pages


# =============================================================================
# 3. TEAM REPORT SERVICE
# =============================================================================

def get_team_report_data(
    db: Session,
    current_user: User,
    team: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    sort_by: str = "team_name",
    sort_order: str = "asc",
    page: Optional[int] = None,
    page_size: Optional[int] = None,
) -> Tuple[List[dict], dict, int, int]:
    # RBAC Authorization: Managers can only view their own department/team
    if current_user.role not in ["Manager", "Administrator"]:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Access restricted to Managers and Administrators"
        )

    if current_user.role == "Manager":
        manager_dept = current_user.department or "General"
        if team and team.strip().lower() != manager_dept.lower():
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Managers can only access reports for their own team ('{manager_dept}')"
            )
        team = manager_dept

    # Validate date range
    parsed_start, parsed_end = parse_and_validate_dates(start_date, end_date)

    # Validate status if provided
    if status:
        matched_status = [s for s in VALID_DECISION_STATUSES if s.lower() == status.strip().lower()]
        if not matched_status:
            raise HTTPException(
                status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid status '{status}'. Allowed statuses: {sorted(list(VALID_DECISION_STATUSES))}"
            )
        status = matched_status[0]

    # Validate sorting
    sort_key = sort_by.strip().lower()
    if sort_key not in ALLOWED_TEAM_SORT_FIELDS:
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid sort_by field '{sort_by}'. Allowed fields: {sorted(list(ALLOWED_TEAM_SORT_FIELDS))}"
        )

    # Fetch all users or filtered by team
    user_query = db.query(User)
    if team:
        user_query = user_query.filter(User.department.ilike(f"%{team.strip()}%"))
    all_users = user_query.all()

    # Group users by department/team
    teams_dict: Dict[str, List[User]] = {}
    for u in all_users:
        dept = u.department if (u.department and u.department.strip()) else "General"
        if dept not in teams_dict:
            teams_dict[dept] = []
        teams_dict[dept].append(u)

    # If specific team filter was given and no users matched, handle gracefully
    if team and not teams_dict:
        teams_dict[team.strip()] = []

    # Fetch decisions with filters
    decision_query = db.query(Decision)
    if category:
        decision_query = decision_query.filter(Decision.category.ilike(f"%{category.strip()}%"))
    if status:
        decision_query = decision_query.filter(Decision.status == status)
    if parsed_start:
        decision_query = decision_query.filter(Decision.created_at >= parsed_start)
    if parsed_end:
        decision_query = decision_query.filter(Decision.created_at <= parsed_end)
    all_filtered_decisions = decision_query.all()

    # Group decisions by creator ID
    decisions_by_user: Dict[int, List[Decision]] = {}
    for d in all_filtered_decisions:
        if d.created_by not in decisions_by_user:
            decisions_by_user[d.created_by] = []
        decisions_by_user[d.created_by].append(d)

    # Fetch approvals with date filters
    approval_query = db.query(Approval)
    if parsed_start:
        approval_query = approval_query.filter(Approval.created_at >= parsed_start)
    if parsed_end:
        approval_query = approval_query.filter(Approval.created_at <= parsed_end)
    all_filtered_approvals = approval_query.all()

    # Build report items per team
    items = []
    total_all_members = 0
    total_all_decisions = 0
    total_all_approvals = 0

    for team_name, members in teams_dict.items():
        member_ids = [m.id for m in members]
        total_all_members += len(member_ids)

        # Team decisions
        team_decisions = []
        for mid in member_ids:
            team_decisions.extend(decisions_by_user.get(mid, []))

        total_dec = len(team_decisions)
        total_all_decisions += total_dec
        approved_dec = sum(1 for d in team_decisions if d.status == "Approved")
        rejected_dec = sum(1 for d in team_decisions if d.status == "Rejected")
        pending_dec = sum(1 for d in team_decisions if d.status in ["Draft", "Under Review"])

        # Team approvals (approvals where reviewer is a team member OR decision created by team)
        team_decision_ids = {d.id for d in team_decisions}
        team_approvals = [
            a for a in all_filtered_approvals
            if (a.reviewer_id in member_ids or a.decision_id in team_decision_ids)
        ]

        total_app = len(team_approvals)
        total_all_approvals += total_app
        approved_app = sum(1 for a in team_approvals if a.status == "Approved")
        rejected_app = sum(1 for a in team_approvals if a.status == "Rejected")
        pending_app = sum(1 for a in team_approvals if a.status == "Pending")

        turnaround_times = [
            max(0.0, (a.completed_at - a.created_at).total_seconds() / 3600.0)
            for a in team_approvals if (a.completed_at and a.created_at)
        ]
        avg_tt = round(sum(turnaround_times) / len(turnaround_times), 2) if turnaround_times else None

        items.append({
            "team_name": team_name,
            "number_of_members": len(member_ids),
            "total_decisions": total_dec,
            "approved_decisions": approved_dec,
            "rejected_decisions": rejected_dec,
            "pending_decisions": pending_dec,
            "team_approval_statistics": {
                "total_approvals": total_app,
                "approved_approvals": approved_app,
                "rejected_approvals": rejected_app,
                "pending_approvals": pending_app,
                "average_turnaround_time_hours": avg_tt,
            }
        })

    # Sort items in memory
    reverse_sort = (sort_order.strip().lower() == "desc")
    if sort_key in ["team_name", "department"]:
        items.sort(key=lambda x: str(x["team_name"]).lower(), reverse=reverse_sort)
    elif sort_key == "number_of_members":
        items.sort(key=lambda x: x["number_of_members"], reverse=reverse_sort)
    elif sort_key == "total_decisions":
        items.sort(key=lambda x: x["total_decisions"], reverse=reverse_sort)
    elif sort_key == "approved_decisions":
        items.sort(key=lambda x: x["approved_decisions"], reverse=reverse_sort)
    elif sort_key == "rejected_decisions":
        items.sort(key=lambda x: x["rejected_decisions"], reverse=reverse_sort)
    elif sort_key == "pending_decisions":
        items.sort(key=lambda x: x["pending_decisions"], reverse=reverse_sort)

    total_count = len(items)
    summary = {
        "total_teams": total_count,
        "total_members": total_all_members,
        "total_decisions": total_all_decisions,
        "total_approvals": total_all_approvals,
    }

    # Pagination
    if page is not None and page_size is not None:
        if page < 1 or page_size < 1:
            raise HTTPException(
                status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Page and page_size must be positive integers"
            )
        start_idx = (page - 1) * page_size
        paged_items = items[start_idx : start_idx + page_size]
        total_pages = math.ceil(total_count / page_size) if total_count > 0 else 1
    else:
        paged_items = items
        total_pages = 1

    return paged_items, summary, total_count, total_pages


# =============================================================================
# 4. AUDIT REPORT SERVICE
# =============================================================================

def get_audit_report_data(
    db: Session,
    current_user: User,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    page: Optional[int] = None,
    page_size: Optional[int] = None,
) -> Tuple[List[dict], dict, int, int]:
    # RBAC: Only Administrators can access Audit reports
    if current_user.role != "Administrator":
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Only administrators can view audit reports"
        )

    # Validate date range
    parsed_start, parsed_end = parse_and_validate_dates(start_date, end_date)

    # Validate action
    if action:
        normalized_action = action.upper().strip()
        if normalized_action not in VALID_AUDIT_ACTIONS:
            raise HTTPException(
                status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid action '{action}'. Allowed actions: {sorted(list(VALID_AUDIT_ACTIONS))}"
            )
        action = normalized_action

    # Validate entity_type
    if entity_type:
        normalized_entity = entity_type.strip()
        matched = [e for e in VALID_ENTITY_TYPES if e.lower() == normalized_entity.lower()]
        if not matched:
            raise HTTPException(
                status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid entity_type '{entity_type}'. Allowed types: {sorted(list(VALID_ENTITY_TYPES))}"
            )
        entity_type = matched[0]

    # Validate sorting
    sort_key = sort_by.strip().lower()
    if sort_key not in ALLOWED_AUDIT_SORT_FIELDS:
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid sort_by field '{sort_by}'. Allowed fields: {sorted(list(ALLOWED_AUDIT_SORT_FIELDS.keys()))}"
        )

    sort_column = ALLOWED_AUDIT_SORT_FIELDS[sort_key]
    order_func = desc if sort_order.strip().lower() == "desc" else asc

    # Build query
    query = db.query(AuditLog).options(joinedload(AuditLog.user))

    if user_id is not None:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if entity_type:
        query = query.filter(AuditLog.entity_type.ilike(entity_type))
    if entity_id is not None:
        query = query.filter(AuditLog.entity_id == entity_id)
    if parsed_start:
        query = query.filter(AuditLog.created_at >= parsed_start)
    if parsed_end:
        query = query.filter(AuditLog.created_at <= parsed_end)

    all_filtered = query.all()
    total_count = len(all_filtered)

    # Summary statistics breakdown
    action_breakdown: Dict[str, int] = {}
    entity_breakdown: Dict[str, int] = {}
    for log in all_filtered:
        action_breakdown[log.action] = action_breakdown.get(log.action, 0) + 1
        entity_breakdown[log.entity_type] = entity_breakdown.get(log.entity_type, 0) + 1

    summary = {
        "total_events": total_count,
        "action_breakdown": action_breakdown,
        "entity_breakdown": entity_breakdown,
    }

    # Ordering & Pagination
    sorted_query = query.order_by(order_func(sort_column))

    if page is not None and page_size is not None:
        if page < 1 or page_size < 1:
            raise HTTPException(
                status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Page and page_size must be positive integers"
            )
        logs = sorted_query.offset((page - 1) * page_size).limit(page_size).all()
        total_pages = math.ceil(total_count / page_size) if total_count > 0 else 1
    else:
        logs = sorted_query.all()
        total_pages = 1

    items = []
    for log in logs:
        items.append({
            "id": log.id,
            "user_id": log.user_id,
            "user_name": log.user.full_name if log.user else None,
            "user_email": log.user.email if log.user else None,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "description": log.description,
            "timestamp": log.created_at,
            "ip_address": log.ip_address,
            "request_method": log.request_method,
            "endpoint": log.endpoint,
        })

    return items, summary, total_count, total_pages
