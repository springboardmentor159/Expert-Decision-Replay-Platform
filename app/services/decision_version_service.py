from sqlalchemy.orm import Session

from app.models.decision import Decision
from app.models.decision_version import DecisionVersion


def create_decision_version(
    db: Session,
    decision: Decision,
    user_id: int,
):
    """
    Create a new immutable version of a decision.
    Version numbers are assigned by the backend.
    """

    latest_version = (
        db.query(DecisionVersion)
        .filter(
            DecisionVersion.decision_id == decision.id
        )
        .order_by(
            DecisionVersion.version_number.desc()
        )
        .first()
    )

    next_version = (
        latest_version.version_number + 1
        if latest_version
        else 1
    )

    version = DecisionVersion(
        decision_id=decision.id,
        version_number=next_version,
        title=decision.title,
        problem_statement=decision.problem_statement,
        description=None,
        category=decision.category,
        status=decision.status,
        created_by=user_id,
    )

    db.add(version)
    db.flush()

    return version