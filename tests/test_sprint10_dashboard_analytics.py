import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_auth_headers(user_email: str, password: str = "Password123!"):
    login_res = client.post("/auth/login", json={"email": user_email, "password": password})
    assert login_res.status_code == 200, f"Login failed for {user_email}: {login_res.text}"
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def setup_sprint10_environment():
    # 1. Create Employee User
    emp = {
        "full_name": "Edward Employee",
        "email": "edward@example.com",
        "role": "Employee",
        "password": "Password123!",
        "employee_id": "EMP_ED_10",
        "department": "Engineering"
    }
    r_emp = client.post("/users", json=emp)
    assert r_emp.status_code == 201

    # 2. Create Reviewer User
    rev = {
        "full_name": "Rachel Reviewer",
        "email": "rachel@example.com",
        "role": "Reviewer",
        "password": "Password123!",
        "employee_id": "REV_RACHEL_10",
        "department": "Engineering"
    }
    r_rev = client.post("/users", json=rev)
    assert r_rev.status_code == 201

    # 3. Create Manager User
    mgr = {
        "full_name": "Michael Manager",
        "email": "michael@example.com",
        "role": "Manager",
        "password": "Password123!",
        "employee_id": "MGR_MIKE_10",
        "department": "Engineering"
    }
    r_mgr = client.post("/users", json=mgr)
    assert r_mgr.status_code == 201

    # 4. Create Admin User
    adm = {
        "full_name": "Adam Admin",
        "email": "adam@example.com",
        "role": "Administrator",
        "password": "Password123!",
        "employee_id": "ADM_ADAM_10",
        "department": "Executive"
    }
    r_adm = client.post("/users", json=adm)
    assert r_adm.status_code == 201

    h_emp = get_auth_headers("edward@example.com")
    h_rev = get_auth_headers("rachel@example.com")
    h_mgr = get_auth_headers("michael@example.com")
    h_adm = get_auth_headers("adam@example.com")

    # 5. Create Decisions as Employee
    d1 = client.post(
        "/decisions",
        json={
            "title": "Adopt GraphQL Gateway",
            "problem_statement": "Need flexible query layer for frontend clients.",
            "category": "Technology"
        },
        headers=h_emp
    ).json()

    d2 = client.post(
        "/decisions",
        json={
            "title": "Implement Zero Trust Network",
            "problem_statement": "Enhance security perimeters.",
            "category": "Security"
        },
        headers=h_emp
    ).json()

    # 6. Add Alternatives, Comments, Threads
    client.post(
        f"/decisions/{d1['id']}/alternatives",
        json={
            "name": "Apollo GraphQL",
            "description": "Enterprise GraphQL federation platform.",
            "pros": "Rich ecosystem",
            "cons": "Licensing fees",
            "estimated_cost": 5000.0,
            "feasibility_score": 4,
            "risk_level": "Medium"
        },
        headers=h_emp
    )

    client.post(
        f"/decisions/{d1['id']}/comments",
        json={"content": "Looks good from an engineering standpoint."},
        headers=h_emp
    )

    client.post(
        f"/decisions/{d1['id']}/threads",
        json={"title": "Security review for GraphQL", "description": "Discuss rate limiting."},
        headers=h_emp
    )

    # 7. Submit Decision for Approval
    app_res = client.post(
        "/approvals",
        json={
            "decision_id": d1["id"],
            "reviewer_id": r_rev.json()["id"],
            "approval_level": 1,
            "comments": "Please review GraphQL architecture."
        },
        headers=h_emp
    ).json()

    return {
        "h_emp": h_emp,
        "h_rev": h_rev,
        "h_mgr": h_mgr,
        "h_adm": h_adm,
        "d1": d1,
        "d2": d2,
        "approval": app_res,
        "rev_id": r_rev.json()["id"],
        "emp_id": r_emp.json()["id"]
    }


def test_employee_dashboard(setup_sprint10_environment):
    h_emp = setup_sprint10_environment["h_emp"]

    # 1. Main employee dashboard
    res = client.get("/dashboard/employee", headers=h_emp)
    assert res.status_code == 200
    data = res.json()
    assert data["total_decisions"] >= 2
    assert data["under_review"] >= 1  # d1 is submitted
    assert data["draft_decisions"] >= 1  # d2 is Draft
    assert len(data["recent_activities"]) >= 1

    # 2. My decisions
    my_decisions = client.get("/dashboard/employee/decisions", headers=h_emp)
    assert my_decisions.status_code == 200
    assert len(my_decisions.json()) >= 2

    # 3. Pending reviews for reviewer
    h_rev = setup_sprint10_environment["h_rev"]
    rev_pending = client.get("/dashboard/employee/pending-reviews", headers=h_rev)
    assert rev_pending.status_code == 200
    assert len(rev_pending.json()) >= 1
    assert rev_pending.json()[0]["decision_id"] == setup_sprint10_environment["d1"]["id"]

    # 4. Recent activities
    activities = client.get("/dashboard/employee/recent-activities", headers=h_emp)
    assert activities.status_code == 200
    assert len(activities.json()) >= 1


def test_manager_dashboard_and_permissions(setup_sprint10_environment):
    h_mgr = setup_sprint10_environment["h_mgr"]
    h_emp = setup_sprint10_environment["h_emp"]

    # Employee attempting to access manager dashboard -> 403
    emp_forbidden = client.get("/dashboard/manager", headers=h_emp)
    assert emp_forbidden.status_code == 403

    # Manager dashboard
    mgr_res = client.get("/dashboard/manager", headers=h_mgr)
    assert mgr_res.status_code == 200
    mgr_data = mgr_res.json()
    assert mgr_data["team_decisions"] >= 2
    assert mgr_data["under_review"] >= 1
    assert mgr_data["pending_approvals"] >= 1

    # Team decisions
    team_dec = client.get("/dashboard/manager/team-decisions", headers=h_mgr)
    assert team_dec.status_code == 200
    assert len(team_dec.json()) >= 2

    # Manager statistics
    stats = client.get("/dashboard/manager/statistics", headers=h_mgr)
    assert stats.status_code == 200
    assert stats.json()["total_decisions"] >= 2


def test_admin_dashboard_and_analytics(setup_sprint10_environment):
    h_adm = setup_sprint10_environment["h_adm"]
    h_emp = setup_sprint10_environment["h_emp"]
    h_mgr = setup_sprint10_environment["h_mgr"]

    # Non-admin access forbidden -> 403
    assert client.get("/dashboard/admin", headers=h_emp).status_code == 403
    assert client.get("/dashboard/admin", headers=h_mgr).status_code == 403
    assert client.get("/dashboard/admin/analytics", headers=h_emp).status_code == 403

    # Admin dashboard overview
    adm_res = client.get("/dashboard/admin", headers=h_adm)
    assert adm_res.status_code == 200
    adm_data = adm_res.json()
    assert adm_data["total_users"] >= 4
    assert adm_data["total_decisions"] >= 2
    assert adm_data["total_approvals"] >= 1

    # Analytics API with valid date filters
    analytics = client.get("/dashboard/admin/analytics?start_date=2020-01-01&end_date=2030-12-31", headers=h_adm)
    assert analytics.status_code == 200
    adata = analytics.json()
    assert adata["decision_statistics"]["total_decisions"] >= 2
    assert adata["user_statistics"]["total_users"] >= 4
    assert adata["approval_statistics"]["total_approvals"] >= 1

    # Date range error handling
    invalid_date = client.get("/dashboard/admin/analytics?start_date=invalid-date", headers=h_adm)
    assert invalid_date.status_code == 422

    inverted_dates = client.get("/dashboard/admin/analytics?start_date=2026-08-30&end_date=2026-08-01", headers=h_adm)
    assert inverted_dates.status_code == 422

    # Decision creation activity breakdown by date
    act_breakdown = client.get("/dashboard/admin/decision-activity", headers=h_adm)
    assert act_breakdown.status_code == 200
    assert len(act_breakdown.json()) >= 1

    # User activity metrics
    user_act = client.get("/dashboard/admin/user-activity", headers=h_adm)
    assert user_act.status_code == 200
    assert user_act.json()["active_users_count"] >= 1


def test_approval_workflow_and_performance_stats(setup_sprint10_environment):
    h_rev = setup_sprint10_environment["h_rev"]
    h_adm = setup_sprint10_environment["h_adm"]
    app_id = setup_sprint10_environment["approval"]["id"]

    # Reviewer approves decision
    approve_res = client.post(
        f"/approvals/{app_id}/approve",
        json={"comments": "Architectural review passed."},
        headers=h_rev
    )
    assert approve_res.status_code == 200
    assert approve_res.json()["status"] == "Approved"

    # Verify decision status changed to Approved
    d1_id = setup_sprint10_environment["d1"]["id"]
    dec_check = client.get(f"/decisions/{d1_id}", headers=h_rev)
    assert dec_check.status_code == 200
    assert dec_check.json()["status"] == "Approved"

    # Verify approval turnaround metrics
    perf = client.get("/dashboard/admin/approval-statistics", headers=h_adm)
    assert perf.status_code == 200
    pdata = perf.json()
    assert pdata["total_approvals"] >= 1
    assert pdata["completed_approvals"] >= 1
    assert pdata["completion_rate"] == 100.0
    assert pdata["average_approval_time_hours"] is not None


def test_activity_logging_and_filtering(setup_sprint10_environment):
    h_adm = setup_sprint10_environment["h_adm"]

    # Get all activities as admin
    acts = client.get("/activities", headers=h_adm)
    assert acts.status_code == 200
    assert acts.json()["total"] >= 5

    # Filter by entity_type
    dec_acts = client.get("/activities?entity_type=Decision", headers=h_adm)
    assert dec_acts.status_code == 200
    assert all(a["entity_type"] == "Decision" for a in dec_acts.json()["items"])

    # Filter by action
    create_acts = client.get("/activities?action=create", headers=h_adm)
    assert create_acts.status_code == 200
    assert all(a["action"] == "create" for a in create_acts.json()["items"])


def test_unauthenticated_dashboard_access():
    assert client.get("/dashboard/employee").status_code == 401
    assert client.get("/dashboard/manager").status_code == 401
    assert client.get("/dashboard/admin").status_code == 401
    assert client.get("/activities").status_code == 401
