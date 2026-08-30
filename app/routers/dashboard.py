from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services import dashboard_service as svc

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])




def require_manager(current_user: User):
    if current_user.role not in ("Manager", "Administrator"):
        raise HTTPException(status_code=403, detail="Manager access required")
    return current_user


def require_admin(current_user: User):
    if current_user.role != "Administrator":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


def parse_dates(start_date: Optional[str], end_date: Optional[str]):
    start, end = None, None
    try:
        if start_date:
            start = datetime.fromisoformat(start_date)
        if end_date:
            end = datetime.fromisoformat(end_date)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid date format. Use YYYY-MM-DD.")
    if start and end and start > end:
        raise HTTPException(status_code=422, detail="start_date must be before end_date.")
    return start, end



@router.get("/employee")
def employee_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return svc.get_employee_dashboard(db, current_user.id)


@router.get("/employee/decisions")
def employee_decisions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return svc.get_employee_decisions(db, current_user.id)


@router.get("/employee/recent-activities")
def employee_recent_activities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return svc.get_employee_recent_activities(db, current_user.id)




@router.get("/manager")
def manager_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_manager(current_user)
    return svc.get_manager_dashboard(db, current_user)


@router.get("/manager/team-decisions")
def manager_team_decisions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_manager(current_user)
    return svc.get_manager_team_decisions(db, current_user)


@router.get("/manager/statistics")
def manager_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_manager(current_user)
    return svc.get_manager_statistics(db, current_user)




@router.get("/admin")
def admin_dashboard(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_admin(current_user)
    start, end = parse_dates(start_date, end_date)
    return svc.get_admin_dashboard(db, start, end)


@router.get("/admin/analytics")
def admin_analytics(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_admin(current_user)
    start, end = parse_dates(start_date, end_date)
    return svc.get_admin_analytics(db, start, end)


@router.get("/admin/decision-activity")
def admin_decision_activity(
    group_by: str = Query("day", pattern="^(day|week|month)$"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_admin(current_user)
    start, end = parse_dates(start_date, end_date)
    return svc.get_decision_activity(db, group_by, start, end)


@router.get("/admin/user-activity")
def admin_user_activity(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_admin(current_user)
    return svc.get_user_activity(db)