from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.models.decision import Decision
from app.routers.auth import get_current_user


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)
@router.get("/")
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total_decisions = db.query(Decision).count()

    return {
        "message": "Dashboard data retrieved successfully",
        "total_decisions": total_decisions
    }