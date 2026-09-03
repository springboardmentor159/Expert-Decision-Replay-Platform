from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy import case, func
from sqlalchemy.orm import Session, joinedload

from app.models.alternative import Alternative
from app.models.approval import Approval
from app.models.audit_log import AuditLog
from app.models.decision import Decision
from app.models.tag import Tag
from app.models.user import User
from app.schemas.audit import AuditAction
from app.schemas.decision import DecisionCategory, DecisionStatus
from app.schemas.report import (
    ApprovalReportItem,
    ApprovalReportSummary,
    AuditReportItem,
    AuditReportSummary,
    DecisionReportItem,
    DecisionReportSummary,
    TeamApprovalStats,
    TeamReportItem,
    TeamReportSummary,
)

VALID_DECISION_CATEGORIES = {c.value.lower(): c.value for c in DecisionCategory}
VALID_DECISION_STATUSES = {s.value.lower(): s.value for s in DecisionStatus}
VALID_APPROVAL_STATUSES = {"pending": "Pending", "approved": "Approved", "rejected": "Rejected"}
VALID_AUDIT_ACTIONS = {a.value.upper() for a in AuditAction}
VALID_AUDIT_ENTITIES = {
    "decision",
    "alternative",
    "comment",
    "discussionthread",
    "meetingnote",
    "approval",
    "user",
    "tag",
    "auditlog",
    "securitylog",
    "accesslog",
}


# =============================================================================
# VALIDATION HELPERS
# =============================================================================

def parse_date(date_str: Optional[str], param_name: str, is_end_date: bool = False) -> Optional[datetime]:
    if not date_str or not str(date_str).strip():
        return None
    cleaned = str(date_str).strip()
    dt = None
    try:
        dt = datetime.fromisoformat(cleaned.replace("Z", "+00:00"))
    except ValueError:
        try:
            dt = datetime.strptime(cleaned, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid date format for '{param_name}': '{date_str}'. Expected YYYY-MM-DD or ISO 8601"
            )
    if is_end_date and dt.hour == 0 and dt.minute == 0 and dt.second == 0 and dt.microsecond == 0 and len(cleaned) <= 10:
        dt = dt.replace(hour=23, minute=59, second=59, microsecond=999999)
    return dt



def validate_date_range(start_date: Optional[str], end_date: Optional[str]) -> Tuple[Optional[datetime], Optional[datetime]]:
    start_dt = parse_date(start_date, "start_date", is_end_date=False)
    end_dt = parse_date(end_date, "end_date", is_end_date=True)
    if start_dt and end_dt and start_dt > end_dt:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date cannot be after end_date"
        )
    return start_dt, end_dt


def validate_sort(sort_by: str, sort_order: str, allowed_fields: Dict[str, Any]) -> Tuple[Any, str]:
    clean_field = sort_by.strip().lower()
    if clean_field not in allowed_fields:
        allowed_names = sorted(list(allowed_fields.keys()))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid sorting field '{sort_by}'. Allowed fields: {', '.join(allowed_names)}"
        )
    
    clean_order = sort_order.strip().lower()
    if clean_order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid sort order '{sort_order}'. Allowed: 'asc', 'desc'"
        )
    
    col = allowed_fields[clean_field]
    return col, clean_order


# =============================================================================
# 1. DECISION REPORTS SERVICE
# =============================================================================

ALLOWED_DECISION_SORT_FIELDS = {
    "created_at": Decision.created_at,
    "created_date": Decision.created_at,
    "updated_at": Decision.updated_at,
    "updated_date": Decision.updated_at,
    "title": func.lower(Decision.title),
    "category": Decision.category,
    "status": Decision.status,
    "id": Decision.id,
    "decision_id": Decision.id,
}



def get_decision_report_data(
    db: Session,
    category: Optional[str] = None,
    status_filter: Optional[str] = None,
    created_by: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    tag: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    page: Optional[int] = None,
    page_size: Optional[int] = None,
) -> Tuple[List[DecisionReportItem], DecisionReportSummary, int, Dict[str, Any]]:
    # Validate date range
    start_dt, end_dt = validate_date_range(start_date, end_date)

    # Validate category if provided
    canonical_category = None
    if category and str(category).strip():
        cat_clean = str(category).strip().lower()
        if cat_clean not in VALID_DECISION_CATEGORIES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid category '{category}'. Allowed: {', '.join(VALID_DECISION_CATEGORIES.values())}"
            )
        canonical_category = VALID_DECISION_CATEGORIES[cat_clean]

    # Validate status if provided
    canonical_status = None
    if status_filter and str(status_filter).strip():
        st_clean = str(status_filter).strip().lower()
        if st_clean not in VALID_DECISION_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid status '{status_filter}'. Allowed: {', '.join(VALID_DECISION_STATUSES.values())}"
            )
        canonical_status = VALID_DECISION_STATUSES[st_clean]

    # Validate sorting
    sort_col, order_direction = validate_sort(sort_by, sort_order, ALLOWED_DECISION_SORT_FIELDS)

    # Build query
    query = db.query(Decision).options(
        joinedload(Decision.creator),
        joinedload(Decision.tags),
        joinedload(Decision.alternatives),
        joinedload(Decision.approvals),
    )

    if canonical_category:
        query = query.filter(Decision.category == canonical_category)
    if canonical_status:
        query = query.filter(Decision.status == canonical_status)
    if created_by is not None:
        query = query.filter(Decision.created_by == created_by)
    if start_dt:
        query = query.filter(Decision.created_at >= start_dt)
    if end_dt:
        query = query.filter(Decision.created_at <= end_dt)
    if tag and str(tag).strip():
        clean_tag = str(tag).strip()
        query = query.filter(Decision.tags.any(Tag.name.ilike(f"%{clean_tag}%")))

    # Calculate Summary Statistics over filtered dataset
    all_matching = query.all()
    total_count = len(all_matching)

    draft_count = sum(1 for d in all_matching if d.status == "Draft")
    under_review_count = sum(1 for d in all_matching if d.status == "Under Review")
    approved_count = sum(1 for d in all_matching if d.status == "Approved")
    rejected_count = sum(1 for d in all_matching if d.status == "Rejected")
    archived_count = sum(1 for d in all_matching if d.status == "Archived")

    summary = DecisionReportSummary(
        total_decisions=total_count,
        draft_decisions=draft_count,
        under_review_decisions=under_review_count,
        approved_decisions=approved_count,
        rejected_decisions=rejected_count,
        archived_decisions=archived_count,
    )

    # Apply Sorting
    order_clause = sort_col.asc() if order_direction == "asc" else sort_col.desc()
    sorted_query = query.order_by(order_clause)

    # Apply Pagination if requested
    if page is not None and page_size is not None:
        paged_decisions = sorted_query.offset((page - 1) * page_size).limit(page_size).all()
    else:
        paged_decisions = sorted_query.all()

    items = []
    for d in paged_decisions:
        tag_names = [t.name for t in d.tags] if d.tags else []
        alts_count = len(d.alternatives) if d.alternatives else 0
        apprvs_count = len(d.approvals) if d.approvals else 0
        creator_name = d.creator.full_name if d.creator else None
        creator_email = d.creator.email if d.creator else None

        items.append(
            DecisionReportItem(
                id=d.id,
                title=d.title,
                category=d.category,
                status=d.status,
                created_by=d.created_by,
                creator_name=creator_name,
                creator_email=creator_email,
                created_at=d.created_at,
                updated_at=d.updated_at,
                alternatives_count=alts_count,
                approvals_count=apprvs_count,
                tags=tag_names,
            )
        )

    filters_applied = {
        "category": canonical_category,
        "status": canonical_status,
        "created_by": created_by,
        "start_date": start_date,
        "end_date": end_date,
        "tag": tag,
    }

    return items, summary, total_count, filters_applied


# =============================================================================
# 2. APPROVAL REPORTS SERVICE
# =============================================================================

ALLOWED_APPROVAL_SORT_FIELDS = {
    "created_at": Approval.created_at,
    "assigned_date": Approval.created_at,
    "completed_at": Approval.completed_at,
    "approval_date": Approval.completed_at,
    "approval_level": Approval.approval_level,
    "status": Approval.status,
    "id": Approval.id,
    "approval_id": Approval.id,
    "decision_id": Approval.decision_id,
    "reviewer_id": Approval.reviewer_id,
}


def get_approval_report_data(
    db: Session,
    status_filter: Optional[str] = None,
    reviewer_id: Optional[int] = None,
    decision_id: Optional[int] = None,
    approval_level: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    page: Optional[int] = None,
    page_size: Optional[int] = None,
) -> Tuple[List[ApprovalReportItem], ApprovalReportSummary, int, Dict[str, Any]]:
    # Validate date range
    start_dt, end_dt = validate_date_range(start_date, end_date)

    # Validate status if provided
    canonical_status = None
    if status_filter and str(status_filter).strip():
        st_clean = str(status_filter).strip().lower()
        if st_clean not in VALID_APPROVAL_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid approval status '{status_filter}'. Allowed: Pending, Approved, Rejected"
            )
        canonical_status = VALID_APPROVAL_STATUSES[st_clean]

    # Validate sorting
    sort_col, order_direction = validate_sort(sort_by, sort_order, ALLOWED_APPROVAL_SORT_FIELDS)

    query = db.query(Approval).options(
        joinedload(Approval.decision),
        joinedload(Approval.reviewer),
    )

    if canonical_status:
        query = query.filter(Approval.status == canonical_status)
    if reviewer_id is not None:
        query = query.filter(Approval.reviewer_id == reviewer_id)
    if decision_id is not None:
        query = query.filter(Approval.decision_id == decision_id)
    if approval_level is not None:
        query = query.filter(Approval.approval_level == approval_level)
    if start_dt:
        query = query.filter(Approval.created_at >= start_dt)
    if end_dt:
        query = query.filter(Approval.created_at <= end_dt)

    all_matching = query.all()
    total_count = len(all_matching)

    pending_count = sum(1 for a in all_matching if a.status == "Pending")
    approved_count = sum(1 for a in all_matching if a.status == "Approved")
    rejected_count = sum(1 for a in all_matching if a.status == "Rejected")
    completed_items = [a for a in all_matching if a.completed_at is not None]
    completed_count = len(completed_items)

    completion_rate = round((completed_count / total_count * 100.0), 2) if total_count > 0 else 0.0

    durations = [
        (a.completed_at - a.created_at).total_seconds() / 3600.0
        for a in completed_items
        if a.completed_at >= a.created_at
    ]
    avg_turnaround = round(sum(durations) / len(durations), 2) if durations else None

    summary = ApprovalReportSummary(
        total_approvals=total_count,
        pending_approvals=pending_count,
        approved_approvals=approved_count,
        rejected_approvals=rejected_count,
        average_turnaround_time_hours=avg_turnaround,
        completion_rate=completion_rate,
    )

    # Sorting & Pagination
    order_clause = sort_col.asc() if order_direction == "asc" else sort_col.desc()
    sorted_query = query.order_by(order_clause)

    if page is not None and page_size is not None:
        paged_approvals = sorted_query.offset((page - 1) * page_size).limit(page_size).all()
    else:
        paged_approvals = sorted_query.all()

    items = []
    for a in paged_approvals:
        turnaround = None
        if a.completed_at and a.created_at and a.completed_at >= a.created_at:
            turnaround = round((a.completed_at - a.created_at).total_seconds() / 3600.0, 2)

        items.append(
            ApprovalReportItem(
                id=a.id,
                decision_id=a.decision_id,
                decision_title=a.decision.title if a.decision else None,
                reviewer_id=a.reviewer_id,
                reviewer_name=a.reviewer.full_name if a.reviewer else None,
                reviewer_email=a.reviewer.email if a.reviewer else None,
                approval_level=a.approval_level,
                status=a.status,
                comments=a.comments,
                created_at=a.created_at,
                completed_at=a.completed_at,
                turnaround_time_hours=turnaround,
            )
        )

    filters_applied = {
        "status": canonical_status,
        "reviewer_id": reviewer_id,
        "decision_id": decision_id,
        "approval_level": approval_level,
        "start_date": start_date,
        "end_date": end_date,
    }

    return items, summary, total_count, filters_applied


# =============================================================================
# 3. TEAM REPORTS SERVICE
# =============================================================================

ALLOWED_TEAM_SORT_FIELDS = {
    "team_name": "team_name",
    "member_count": "member_count",
    "total_decisions": "total_decisions",
    "approved_decisions": "approved_decisions",
    "rejected_decisions": "rejected_decisions",
}


def get_team_report_data(
    db: Session,
    current_user: User,
    team: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status_filter: Optional[str] = None,
    category: Optional[str] = None,
    sort_by: str = "team_name",
    sort_order: str = "asc",
    page: Optional[int] = None,
    page_size: Optional[int] = None,
) -> Tuple[List[TeamReportItem], TeamReportSummary, int, Dict[str, Any]]:
    # Validate date range
    start_dt, end_dt = validate_date_range(start_date, end_date)

    # Validate category & status if provided
    canonical_category = None
    if category and str(category).strip():
        cat_clean = str(category).strip().lower()
        if cat_clean not in VALID_DECISION_CATEGORIES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid category '{category}'. Allowed: {', '.join(VALID_DECISION_CATEGORIES.values())}"
            )
        canonical_category = VALID_DECISION_CATEGORIES[cat_clean]

    canonical_status = None
    if status_filter and str(status_filter).strip():
        st_clean = str(status_filter).strip().lower()
        if st_clean not in VALID_DECISION_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid status '{status_filter}'. Allowed: {', '.join(VALID_DECISION_STATUSES.values())}"
            )
        canonical_status = VALID_DECISION_STATUSES[st_clean]

    # Validate sorting field
    clean_sort_field = sort_by.strip().lower()
    if clean_sort_field not in ALLOWED_TEAM_SORT_FIELDS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid sorting field '{sort_by}'. Allowed fields: {', '.join(sorted(ALLOWED_TEAM_SORT_FIELDS.keys()))}"
        )
    clean_order = sort_order.strip().lower()
    if clean_order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid sort order '{sort_order}'. Allowed: 'asc', 'desc'"
        )

    # RBAC Enforcement for Team Data:
    # Non-administrators can only access their own department / team.
    user_dept = current_user.department or "General"
    if current_user.role != "Administrator":
        if team and str(team).strip():
            req_team = str(team).strip()
            if req_team.lower() != user_dept.lower():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access forbidden: You do not have permission to view team reports for '{req_team}'"
                )
            target_department = user_dept
        else:
            target_department = user_dept
    else:
        target_department = str(team).strip() if team and str(team).strip() else None

    # Fetch users grouped by department
    user_query = db.query(User)
    if target_department:
        user_query = user_query.filter(User.department.ilike(f"{target_department}"))
    all_users = user_query.all()

    # Group users by department name
    dept_users_map: Dict[str, List[User]] = {}
    for u in all_users:
        dept = u.department if u.department and u.department.strip() else "General"
        dept_users_map.setdefault(dept, []).append(u)

    team_items: List[TeamReportItem] = []

    for dept_name, members in dept_users_map.items():
        member_ids = [m.id for m in members]
        member_count = len(members)

        # Query decisions created by members of this team
        dec_q = db.query(Decision).filter(Decision.created_by.in_(member_ids))
        if canonical_category:
            dec_q = dec_q.filter(Decision.category == canonical_category)
        if canonical_status:
            dec_q = dec_q.filter(Decision.status == canonical_status)
        if start_dt:
            dec_q = dec_q.filter(Decision.created_at >= start_dt)
        if end_dt:
            dec_q = dec_q.filter(Decision.created_at <= end_dt)
        
        team_decisions = dec_q.all()
        tot_decs = len(team_decisions)
        apprv_decs = sum(1 for d in team_decisions if d.status == "Approved")
        rej_decs = sum(1 for d in team_decisions if d.status == "Rejected")
        draft_decs = sum(1 for d in team_decisions if d.status == "Draft")
        under_review_decs = sum(1 for d in team_decisions if d.status == "Under Review")
        pending_decs = draft_decs + under_review_decs

        # Query approvals for team decisions or assigned to reviewers in this team
        team_dec_ids = [d.id for d in team_decisions]
        apprv_q = db.query(Approval).filter(
            (Approval.reviewer_id.in_(member_ids)) | (Approval.decision_id.in_(team_dec_ids))
        )
        if start_dt:
            apprv_q = apprv_q.filter(Approval.created_at >= start_dt)
        if end_dt:
            apprv_q = apprv_q.filter(Approval.created_at <= end_dt)

        team_approvals = apprv_q.all()
        tot_apprv = len(team_approvals)
        apprv_apprv = sum(1 for a in team_approvals if a.status == "Approved")
        rej_apprv = sum(1 for a in team_approvals if a.status == "Rejected")
        pend_apprv = sum(1 for a in team_approvals if a.status == "Pending")
        comp_apprv = apprv_apprv + rej_apprv
        apprv_comp_rate = round((comp_apprv / tot_apprv * 100.0), 2) if tot_apprv > 0 else 0.0

        durations = [
            (a.completed_at - a.created_at).total_seconds() / 3600.0
            for a in team_approvals
            if a.completed_at and a.created_at and a.completed_at >= a.created_at
        ]
        avg_turn = round(sum(durations) / len(durations), 2) if durations else None

        approval_stats = TeamApprovalStats(
            total_approvals=tot_apprv,
            approved_approvals=apprv_apprv,
            rejected_approvals=rej_apprv,
            pending_approvals=pend_apprv,
            completion_rate=apprv_comp_rate,
            average_turnaround_time_hours=avg_turn,
        )

        team_items.append(
            TeamReportItem(
                team_name=dept_name,
                member_count=member_count,
                total_decisions=tot_decs,
                approved_decisions=apprv_decs,
                rejected_decisions=rej_decs,
                pending_decisions=pending_decs,
                draft_decisions=draft_decs,
                under_review_decisions=under_review_decs,
                team_approval_statistics=approval_stats,
            )
        )

    # Sort team items
    reverse_sort = (clean_order == "desc")
    if clean_sort_field == "team_name":
        team_items.sort(key=lambda x: x.team_name.lower(), reverse=reverse_sort)
    elif clean_sort_field == "member_count":
        team_items.sort(key=lambda x: x.member_count, reverse=reverse_sort)
    elif clean_sort_field == "total_decisions":
        team_items.sort(key=lambda x: x.total_decisions, reverse=reverse_sort)
    elif clean_sort_field == "approved_decisions":
        team_items.sort(key=lambda x: x.approved_decisions, reverse=reverse_sort)
    elif clean_sort_field == "rejected_decisions":
        team_items.sort(key=lambda x: x.rejected_decisions, reverse=reverse_sort)

    total_teams_count = len(team_items)
    tot_members = sum(t.member_count for t in team_items)
    tot_decs_all = sum(t.total_decisions for t in team_items)
    tot_apprv_decs = sum(t.approved_decisions for t in team_items)
    tot_rej_decs = sum(t.rejected_decisions for t in team_items)
    tot_pend_decs = sum(t.pending_decisions for t in team_items)

    summary = TeamReportSummary(
        total_teams=total_teams_count,
        total_members=tot_members,
        total_decisions=tot_decs_all,
        approved_decisions=tot_apprv_decs,
        rejected_decisions=tot_rej_decs,
        pending_decisions=tot_pend_decs,
    )

    if page is not None and page_size is not None:
        paged_items = team_items[(page - 1) * page_size : page * page_size]
    else:
        paged_items = team_items

    filters_applied = {
        "team": target_department,
        "start_date": start_date,
        "end_date": end_date,
        "status": canonical_status,
        "category": canonical_category,
    }

    return paged_items, summary, total_teams_count, filters_applied


# =============================================================================
# 4. AUDIT REPORTS SERVICE
# =============================================================================

ALLOWED_AUDIT_SORT_FIELDS = {
    "created_at": AuditLog.created_at,
    "timestamp": AuditLog.created_at,
    "action": AuditLog.action,
    "entity_type": AuditLog.entity_type,
    "id": AuditLog.id,
    "audit_id": AuditLog.id,
    "user_id": AuditLog.user_id,
}


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
) -> Tuple[List[AuditReportItem], AuditReportSummary, int, Dict[str, Any]]:
    # RBAC: Administrator only
    if current_user.role != "Administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Administrator privileges required to access Audit Reports"
        )

    # Validate date range
    start_dt, end_dt = validate_date_range(start_date, end_date)

    # Validate action
    canonical_action = None
    if action and str(action).strip():
        act_clean = str(action).strip().upper()
        if act_clean not in VALID_AUDIT_ACTIONS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid action '{action}'. Allowed: {', '.join(sorted(VALID_AUDIT_ACTIONS))}"
            )
        canonical_action = act_clean

    # Validate entity_type
    canonical_entity = None
    if entity_type and str(entity_type).strip():
        ent_clean = str(entity_type).strip().lower()
        if ent_clean not in VALID_AUDIT_ENTITIES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid entity_type '{entity_type}'. Allowed: Decision, Alternative, Comment, DiscussionThread, MeetingNote, Approval, User, Tag, etc."
            )
        # Find exact case from entities
        matched = next((e for e in ["Decision", "Alternative", "Comment", "DiscussionThread", "MeetingNote", "Approval", "User", "Tag", "AuditLog", "SecurityLog", "AccessLog"] if e.lower() == ent_clean), entity_type)
        canonical_entity = matched

    # Validate sorting
    sort_col, order_direction = validate_sort(sort_by, sort_order, ALLOWED_AUDIT_SORT_FIELDS)

    query = db.query(AuditLog).options(joinedload(AuditLog.user))

    if user_id is not None:
        query = query.filter(AuditLog.user_id == user_id)
    if canonical_action:
        query = query.filter(AuditLog.action == canonical_action)
    if canonical_entity:
        query = query.filter(AuditLog.entity_type == canonical_entity)
    if entity_id is not None:
        query = query.filter(AuditLog.entity_id == entity_id)
    if start_dt:
        query = query.filter(AuditLog.created_at >= start_dt)
    if end_dt:
        query = query.filter(AuditLog.created_at <= end_dt)

    all_matching = query.all()
    total_count = len(all_matching)

    actions_breakdown: Dict[str, int] = {}
    entities_breakdown: Dict[str, int] = {}
    for log in all_matching:
        actions_breakdown[log.action] = actions_breakdown.get(log.action, 0) + 1
        entities_breakdown[log.entity_type] = entities_breakdown.get(log.entity_type, 0) + 1

    summary = AuditReportSummary(
        total_audit_logs=total_count,
        actions_breakdown=actions_breakdown,
        entities_breakdown=entities_breakdown,
    )

    # Sorting & Pagination
    order_clause = sort_col.asc() if order_direction == "asc" else sort_col.desc()
    sorted_query = query.order_by(order_clause)

    if page is not None and page_size is not None:
        paged_logs = sorted_query.offset((page - 1) * page_size).limit(page_size).all()
    else:
        paged_logs = sorted_query.all()

    items = [
        AuditReportItem(
            id=log.id,
            user_id=log.user_id,
            user_name=log.user.full_name if log.user else None,
            user_email=log.user.email if log.user else None,
            action=log.action,
            entity_type=log.entity_type,
            entity_id=log.entity_id,
            description=log.description,
            created_at=log.created_at,
            ip_address=log.ip_address,
            request_method=log.request_method,
            endpoint=log.endpoint,
        )
        for log in paged_logs
    ]

    filters_applied = {
        "user_id": user_id,
        "action": canonical_action,
        "entity_type": canonical_entity,
        "entity_id": entity_id,
        "start_date": start_date,
        "end_date": end_date,
    }

    return items, summary, total_count, filters_applied
