from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.approval import Approval
from app.models.decision import Decision
from app.models.team import Team
from app.models.team_member import TeamMember
from app.models.user import User


VALID_SORT_FIELDS = {
    "team_name": Team.name,
}

VALID_SORT_ORDERS = {
    "asc",
    "desc",
}

ALLOWED_ROLES = {
    "Manager",
    "Administrator",
}


def validate_access(current_user: Optional[User]) -> None:
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    if current_user.role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager or Administrator access required",
        )


def validate_sorting(
    sort_by: str,
    sort_order: str,
) -> None:
    if sort_by not in VALID_SORT_FIELDS:
        allowed_values = ", ".join(
            sorted(VALID_SORT_FIELDS)
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Invalid team report sort_by. "
                f"Allowed values: {allowed_values}"
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


def validate_date_range(
    date_from: Optional[datetime],
    date_to: Optional[datetime],
) -> None:
    if date_from and date_to and date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "date_from must be earlier than "
                "or equal to date_to"
            ),
        )


def get_manager_member_ids(
    db: Session,
    current_user: User,
) -> set[int]:
    rows = (
        db.query(TeamMember.user_id)
        .join(
            User,
            User.id == TeamMember.user_id,
        )
        .filter(
            User.department == current_user.department
        )
        .all()
    )

    return {
        row[0]
        for row in rows
    }


def get_team_report(
    db: Session,
    team_id: Optional[int] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    decision_status: Optional[str] = None,
    category: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "team_name",
    sort_order: str = "asc",
    current_user: Optional[User] = None,
):
    validate_access(current_user)

    validate_sorting(
        sort_by,
        sort_order,
    )

    validate_date_range(
        date_from,
        date_to,
    )

    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="page must be greater than or equal to 1",
        )

    if page_size < 1 or page_size > 10000:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="page_size must be between 1 and 10000",
        )

    # Administrator can see every team.
    #
    # Manager access is restricted to teams that contain
    # at least one member from the manager's department.
    team_query = db.query(Team)

    if team_id is not None:
        team_query = team_query.filter(
            Team.id == team_id
        )

    manager_member_ids: Optional[set[int]] = None

    if current_user.role == "Manager":
        manager_member_ids = get_manager_member_ids(
            db,
            current_user,
        )

        if not manager_member_ids:
            return {
                "data": [],
                "page": page,
                "page_size": page_size,
                "total_records": 0,
            }

        team_query = (
            team_query
            .join(
                TeamMember,
                TeamMember.team_id == Team.id,
            )
            .filter(
                TeamMember.user_id.in_(
                    manager_member_ids
                )
            )
            .distinct()
        )

    total_records = team_query.count()

    sort_column = VALID_SORT_FIELDS[sort_by]

    if sort_order == "asc":
        team_query = team_query.order_by(
            sort_column.asc()
        )
    else:
        team_query = team_query.order_by(
            sort_column.desc()
        )

    offset = (page - 1) * page_size

    teams = (
        team_query
        .offset(offset)
        .limit(page_size)
        .all()
    )

    data = []

    for team in teams:

        member_query = (
            db.query(TeamMember.user_id)
            .join(
                User,
                User.id == TeamMember.user_id,
            )
            .filter(
                TeamMember.team_id == team.id
            )
        )

        # Manager statistics are restricted to the manager's
        # department. Administrator sees all team members.
        if current_user.role == "Manager":
            member_query = member_query.filter(
                User.department == current_user.department
            )

        member_rows = member_query.all()

        member_ids = {
            row[0]
            for row in member_rows
        }

        number_of_members = len(member_ids)

        # No visible members means no visible team decisions.
        if not member_ids:
            data.append(
                {
                    "team_name": team.name,
                    "number_of_members": 0,
                    "total_decisions": 0,
                    "approved_decisions": 0,
                    "rejected_decisions": 0,
                    "pending_decisions": 0,
                    "approval_rate": 0.0,
                }
            )
            continue

        # Decisions created by visible team members.
        decision_query = (
            db.query(Decision)
            .filter(
                Decision.created_by.in_(member_ids)
            )
        )

        if date_from:
            decision_query = decision_query.filter(
                Decision.created_at >= date_from
            )

        if date_to:
            decision_query = decision_query.filter(
                Decision.created_at <= date_to
            )

        if decision_status:
            decision_query = decision_query.filter(
                Decision.status == decision_status
            )

        if category:
            decision_query = decision_query.filter(
                Decision.category == category
            )

        decisions = decision_query.all()

        total_decisions = len(decisions)

        approved_decisions = sum(
            1
            for decision in decisions
            if (
                decision.status
                and decision.status.lower() == "approved"
            )
        )

        rejected_decisions = sum(
            1
            for decision in decisions
            if (
                decision.status
                and decision.status.lower() == "rejected"
            )
        )

        pending_decisions = sum(
            1
            for decision in decisions
            if (
                decision.status
                and decision.status.lower()
                in {
                    "draft",
                    "under review",
                    "under_review",
                    "pending",
                }
            )
        )

        if total_decisions > 0:
            approval_rate = round(
                (
                    approved_decisions
                    / total_decisions
                ) * 100,
                2,
            )
        else:
            approval_rate = 0.0

        data.append(
            {
                "team_name": team.name,
                "number_of_members": number_of_members,
                "total_decisions": total_decisions,
                "approved_decisions": approved_decisions,
                "rejected_decisions": rejected_decisions,
                "pending_decisions": pending_decisions,
                "approval_rate": approval_rate,
            }
        )

    return {
        "data": data,
        "page": page,
        "page_size": page_size,
        "total_records": total_records,
    }