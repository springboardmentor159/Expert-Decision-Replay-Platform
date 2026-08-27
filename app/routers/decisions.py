from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)

from sqlalchemy.orm import Session

from app.database import get_db
from app.models.decision import Decision
from app.models.user import User

from app.schemas.decision import (
    DecisionCreate,
    DecisionResponse,
    DecisionStatus,
    DecisionStatusUpdate,
    DecisionUpdate
)

from app.routers.auth import get_current_user


router = APIRouter(
    prefix="/decisions",
    tags=["Decisions"]
)


# ============================================================
# 1. CREATE DECISION
# ============================================================

@router.post(
    "",
    response_model=DecisionResponse,
    status_code=status.HTTP_201_CREATED
)
def create_decision(
    decision: DecisionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    new_decision = Decision(
        title=decision.title,
        problem_statement=decision.problem_statement,
        category=decision.category,
        status="Draft",
        created_by=current_user.id
    )

    db.add(new_decision)
    db.commit()
    db.refresh(new_decision)

    return new_decision


# ============================================================
# 2. GET ALL DECISIONS - KNOWLEDGE REPOSITORY
# ============================================================

@router.get(
    "",
    response_model=List[DecisionResponse]
)
def get_all_decisions(
    status_filter: Optional[DecisionStatus] = Query(
        None,
        alias="status"
    ),
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    query = db.query(Decision)

    if status_filter is not None:
        query = query.filter(
            Decision.status == status_filter.value
        )

    if category is not None:
        query = query.filter(
            Decision.category == category
        )

    return query.all()


# ============================================================
# 3. SEARCH DECISIONS
# ============================================================

@router.get(
    "/search",
    response_model=List[DecisionResponse]
)
def search_decisions(
    q: str = Query(
        ...,
        min_length=1,
        description="Search by title, problem statement, or category"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    search_text = f"%{q}%"

    decisions = (
        db.query(Decision)
        .filter(
            (Decision.title.ilike(search_text)) |
            (Decision.problem_statement.ilike(search_text)) |
            (Decision.category.ilike(search_text))
        )
        .all()
    )

    return decisions


# ============================================================
# 4. DECISION DISCOVERY
# ============================================================

@router.get(
    "/discover",
    response_model=List[DecisionResponse]
)
def discover_decisions(
    category: Optional[str] = None,
    status_filter: Optional[DecisionStatus] = Query(
        None,
        alias="status"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    query = db.query(Decision)

    # Filter by category
    if category is not None:
        query = query.filter(
            Decision.category == category
        )

    # Filter by status
    if status_filter is not None:
        query = query.filter(
            Decision.status == status_filter.value
        )

    # Show newest decisions first
    query = query.order_by(
        Decision.created_at.desc()
    )

    return query.all()


# ============================================================
# 5. GET DECISION BY ID
# ============================================================

@router.get(
    "/{decision_id}",
    response_model=DecisionResponse
)
def get_decision_by_id(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if decision is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    return decision


# ============================================================
# 6. UPDATE DECISION
# ============================================================

@router.put(
    "/{decision_id}",
    response_model=DecisionResponse
)
def update_decision(
    decision_id: int,
    decision_data: DecisionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if decision is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    decision.title = decision_data.title

    decision.problem_statement = (
        decision_data.problem_statement
    )

    decision.category = decision_data.category

    db.commit()
    db.refresh(decision)

    return decision


# ============================================================
# 7. UPDATE DECISION STATUS
# ============================================================

@router.patch(
    "/{decision_id}/status",
    response_model=DecisionResponse
)
def update_decision_status(
    decision_id: int,
    status_data: DecisionStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if decision is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    decision.status = status_data.status.value

    db.commit()
    db.refresh(decision)

    return decision