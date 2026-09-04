from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.decision import Decision
from app.models.user import User


def test_employee_dashboard(
    client: TestClient,
    employee_headers: dict,
    employee_user: User,
    db_session: Session,
):
    """Verify Employee Dashboard matches database metrics."""
    res = client.get("/dashboard/employee", headers=employee_headers)
    assert res.status_code == 200
    data = res.json()

    # Query DB directly to verify accuracy
    db_count = db_session.query(Decision).filter(Decision.created_by == employee_user.id).count()
    assert data["total_decisions"] == db_count
    assert "draft_decisions" in data
    assert "pending_reviews" in data
    assert "recent_activities" in data


def test_manager_dashboard(
    client: TestClient,
    manager_headers: dict,
    manager_user: User,
    db_session: Session,
):
    """Verify Manager Dashboard metrics."""
    res = client.get("/dashboard/manager", headers=manager_headers)
    assert res.status_code == 200
    data = res.json()

    org_count = (
        db_session.query(Decision)
        .filter(Decision.organization_id == manager_user.organization_id)
        .count()
    )
    assert data["total_decisions"] == org_count
    assert "pending_approvals" in data


def test_admin_dashboard_and_analytics(
    client: TestClient,
    admin_headers: dict,
    admin_user: User,
    db_session: Session,
):
    """Verify Admin Dashboard and System Analytics."""
    res = client.get("/dashboard/admin", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()

    total_users = (
        db_session.query(User)
        .filter(User.organization_id == admin_user.organization_id)
        .count()
    )
    assert data["total_users"] == total_users

    # System Analytics
    res_analytics = client.get("/dashboard/admin/analytics", headers=admin_headers)
    assert res_analytics.status_code == 200
    analytics = res_analytics.json()
    assert "decision_statistics" in analytics
    assert "user_statistics" in analytics
