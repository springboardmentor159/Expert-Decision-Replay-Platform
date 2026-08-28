import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db.database import SessionLocal
from app.models.decision import Decision
from app.models.user import User

client = TestClient(app)


def get_token(email: str, role: str = "Employee", password: str = "Password123!", department: str = "Engineering"):
    user_in = {
        "full_name": email.split("@")[0].capitalize(),
        "email": email,
        "role": role,
        "password": password,
        "employee_id": f"EMP_{email[:8]}",
        "department": department
    }
    client.post("/users", json=user_in)

    res = client.post("/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200
    return res.json()["access_token"]


def test_sprint10_employee_dashboard():
    token = get_token("emp_dash_user@example.com", role="Employee", department="Engineering")
    headers = {"Authorization": f"Bearer {token}"}

    # Create a decision
    client.post("/decisions", json={"title": "Dashboard Decision", "problem_statement": "Track dashboard metrics", "category": "Product"}, headers=headers)

    # 1. GET /dashboard/employee
    res_dash = client.get("/dashboard/employee", headers=headers)
    assert res_dash.status_code == 200
    data = res_dash.json()
    assert "total_decisions" in data
    assert "draft_decisions" in data
    assert "under_review" in data
    assert "approved_decisions" in data
    assert "rejected_decisions" in data
    assert "pending_reviews" in data
    assert "recent_activities" in data
    assert data["total_decisions"] >= 1

    # 2. GET /dashboard/employee/decisions
    res_decs = client.get("/dashboard/employee/decisions", headers=headers)
    assert res_decs.status_code == 200
    assert len(res_decs.json()) >= 1

    # 3. GET /dashboard/employee/pending-reviews
    res_pending = client.get("/dashboard/employee/pending-reviews", headers=headers)
    assert res_pending.status_code == 200
    assert isinstance(res_pending.json(), list)

    # 4. GET /dashboard/employee/recent-activities
    res_acts = client.get("/dashboard/employee/recent-activities", headers=headers)
    assert res_acts.status_code == 200
    assert len(res_acts.json()) >= 1


def test_sprint10_manager_dashboard():
    mgr_token = get_token("mgr_dash_user@example.com", role="Manager", department="Engineering")
    mgr_headers = {"Authorization": f"Bearer {mgr_token}"}

    emp_token = get_token("emp_team_member@example.com", role="Employee", department="Engineering")
    emp_headers = {"Authorization": f"Bearer {emp_token}"}

    # Employee creates decision in same department
    client.post("/decisions", json={"title": "Team Feature Decision", "problem_statement": "Engineering plan", "category": "Technology"}, headers=emp_headers)

    # 1. GET /dashboard/manager
    res_mgr = client.get("/dashboard/manager", headers=mgr_headers)
    assert res_mgr.status_code == 200
    m_data = res_mgr.json()
    assert "team_decisions" in m_data
    assert "pending_approvals" in m_data
    assert "approved_decisions" in m_data
    assert "rejected_decisions" in m_data
    assert "under_review" in m_data
    assert "team_members_count" in m_data
    assert m_data["team_decisions"] >= 1

    # 2. GET /dashboard/manager/team-decisions
    res_team = client.get("/dashboard/manager/team-decisions", headers=mgr_headers)
    assert res_team.status_code == 200
    assert len(res_team.json()) >= 1

    # 3. GET /dashboard/manager/pending-approvals
    res_p_apprv = client.get("/dashboard/manager/pending-approvals", headers=mgr_headers)
    assert res_p_apprv.status_code == 200
    assert isinstance(res_p_apprv.json(), list)

    # 4. GET /dashboard/manager/statistics
    res_stats = client.get("/dashboard/manager/statistics", headers=mgr_headers)
    assert res_stats.status_code == 200
    assert "total_decisions" in res_stats.json()


def test_sprint10_admin_dashboard_and_analytics():
    adm_token = get_token("adm_dash_user@example.com", role="Administrator", department="Executive")
    adm_headers = {"Authorization": f"Bearer {adm_token}"}

    # 1. GET /dashboard/admin
    res_admin = client.get("/dashboard/admin", headers=adm_headers)
    assert res_admin.status_code == 200
    a_data = res_admin.json()
    assert "total_users" in a_data
    assert "total_decisions" in a_data
    assert "total_approvals" in a_data
    assert "pending_approvals" in a_data
    assert a_data["total_users"] >= 1

    # 2. GET /dashboard/admin/analytics
    res_analytics = client.get("/dashboard/admin/analytics", headers=adm_headers)
    assert res_analytics.status_code == 200
    an_data = res_analytics.json()
    assert "decision_statistics" in an_data
    assert "user_statistics" in an_data
    assert "approval_statistics" in an_data

    # 3. GET /dashboard/admin/decision-activity
    res_act = client.get("/dashboard/admin/decision-activity", headers=adm_headers)
    assert res_act.status_code == 200
    assert isinstance(res_act.json(), dict)

    # 4. GET /dashboard/admin/approval-statistics
    res_app_stats = client.get("/dashboard/admin/approval-statistics", headers=adm_headers)
    assert res_app_stats.status_code == 200
    as_data = res_app_stats.json()
    assert "completion_rate" in as_data
    assert "total_approvals" in as_data

    # 5. GET /dashboard/admin/user-activity
    res_u_act = client.get("/dashboard/admin/user-activity", headers=adm_headers)
    assert res_u_act.status_code == 200
    assert "active_users_count" in res_u_act.json()


def test_sprint10_role_based_authorization_and_errors():
    emp_token = get_token("emp_auth_check@example.com", role="Employee")
    emp_headers = {"Authorization": f"Bearer {emp_token}"}

    mgr_token = get_token("mgr_auth_check@example.com", role="Manager")
    mgr_headers = {"Authorization": f"Bearer {mgr_token}"}

    adm_token = get_token("adm_auth_check@example.com", role="Administrator")
    adm_headers = {"Authorization": f"Bearer {adm_token}"}

    # 1. Unauthenticated requests -> 401
    assert client.get("/dashboard/employee").status_code == 401
    assert client.get("/dashboard/manager").status_code == 401
    assert client.get("/dashboard/admin").status_code == 401
    assert client.get("/activities").status_code == 401

    # 2. Employee accessing Manager dashboard -> 403
    assert client.get("/dashboard/manager", headers=emp_headers).status_code == 403
    assert client.get("/dashboard/manager/team-decisions", headers=emp_headers).status_code == 403

    # 3. Employee accessing Admin dashboard -> 403
    assert client.get("/dashboard/admin", headers=emp_headers).status_code == 403
    assert client.get("/dashboard/admin/analytics", headers=emp_headers).status_code == 403

    # 4. Manager accessing Admin dashboard -> 403
    assert client.get("/dashboard/admin", headers=mgr_headers).status_code == 403
    assert client.get("/dashboard/admin/analytics", headers=mgr_headers).status_code == 403

    # 5. Invalid date filter format -> 422
    assert client.get("/dashboard/admin/analytics?start_date=invalid-date", headers=adm_headers).status_code == 422

    # 6. start_date > end_date -> 422
    assert client.get("/dashboard/admin/analytics?start_date=2026-12-31&end_date=2026-01-01", headers=adm_headers).status_code == 422


def test_sprint10_approval_workflow_and_activities():
    emp_token = get_token("emp_workflow@example.com", role="Employee")
    emp_headers = {"Authorization": f"Bearer {emp_token}"}

    mgr_token = get_token("mgr_workflow@example.com", role="Manager")
    mgr_headers = {"Authorization": f"Bearer {mgr_token}"}

    # Get manager's user ID
    mgr_info = client.get("/users/me", headers=mgr_headers).json()
    mgr_id = mgr_info["id"]

    # 1. Employee creates decision
    dec = client.post("/decisions", json={"title": "Workflow Approval Test", "problem_statement": "Testing approval pipeline", "category": "Operations"}, headers=emp_headers).json()
    dec_id = dec["id"]
    assert dec["status"] == "Draft"

    # 2. Submit decision for approval to manager
    submit_res = client.post(
        f"/decisions/{dec_id}/submit",
        json={"decision_id": dec_id, "reviewer_id": mgr_id, "comments": "Please review for operations"},
        headers=emp_headers
    )
    assert submit_res.status_code == 201
    approval_data = submit_res.json()
    assert approval_data["status"] == "Pending"
    apprv_id = approval_data["id"]

    # Decision should now be Under Review
    dec_check = client.get(f"/decisions/{dec_id}", headers=emp_headers).json()
    assert dec_check["status"] == "Under Review"

    # 3. Manager approves
    action_res = client.post(
        f"/approvals/{apprv_id}/action",
        json={"status": "Approved", "comments": "Approved after operations check"},
        headers=mgr_headers
    )
    assert action_res.status_code == 200
    assert action_res.json()["status"] == "Approved"

    # Decision should now be Approved
    dec_approved = client.get(f"/decisions/{dec_id}", headers=emp_headers).json()
    assert dec_approved["status"] == "Approved"

    # 4. Check activities log
    acts_res = client.get("/activities", headers=mgr_headers)
    assert acts_res.status_code == 200
    acts_data = acts_res.json()
    assert acts_data["total"] >= 1
    actions = [a["action"] for a in acts_data["items"]]
    assert any("approve" in a or "submit" in a or "decision" in a for a in actions)
