from typing import Optional

from sqlalchemy.orm import Session

from app.models.approval import Approval
from app.models.decision import Decision
from app.models.team import Team
from app.models.team_member import TeamMember


VALID_SORT_FIELDS = {
    "team_name": Team.name,
}


def get_team_report(
    db: Session,
    team_id: Optional[int] = None,
    date_from=None,
    date_to=None,
    decision_status: Optional[str] = None,
    category: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "team_name",
    sort_order: str = "asc",
):
    # Get teams
    team_query = db.query(Team)

    if team_id is not None:
        team_query = team_query.filter(
            Team.id == team_id
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

        # Find users belonging to this team
        member_rows = (
            db.query(TeamMember.user_id)
            .filter(
                TeamMember.team_id == team.id
            )
            .all()
        )

        member_ids = [
            row[0]
            for row in member_rows
        ]

        number_of_members = len(member_ids)

        # No members means no team decisions
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

        # Decisions created by team members
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
            if decision.status.lower() == "approved"
        )

        rejected_decisions = sum(
            1
            for decision in decisions
            if decision.status.lower() == "rejected"
        )

        pending_decisions = sum(
            1
            for decision in decisions
            if decision.status.lower()
            in {
                "draft",
                "under review",
                "under_review",
                "pending",
            }
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