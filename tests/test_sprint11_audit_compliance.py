import uuid
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def get_token(email: str = "admin@example.com", role: str = "Administrator", full_name: str = "Admin User"):
    # Create user if doesn't exist
    emp_id = f"EMP-{uuid.uuid4().hex[:6]}"
    client.post(
        "/users",
        json={
            "email": email,
            "password": "Password123!",
            "full_name": full_name,
            "role": role,
            "employee_id": emp_id
        }
    )
    # Login to get JWT
    resp = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "Password123!"
        }
    )
    if resp.status_code != 200:
        raise Exception(f"Login failed: {resp.text}")
    return resp.json()["access_token"]


def test_audit_logs_unauthenticated_and_forbidden():
    # 1. Without JWT -> 401
    resp = client.get("/audit-logs")
    assert resp.status_code == 401

    resp = client.get("/security-logs")
    assert resp.status_code == 401

    resp = client.get("/access-logs")
    assert resp.status_code == 401

    # 2. As Employee -> 403 Forbidden
    emp_token = get_token("employee@example.com", "Employee", "Emp User")
    headers = {"Authorization": f"Bearer {emp_token}"}

    resp = client.get("/audit-logs", headers=headers)
    assert resp.status_code == 403
    assert "administrators" in resp.json()["detail"].lower()

    resp = client.get("/security-logs", headers=headers)
    assert resp.status_code == 403

    resp = client.get("/access-logs", headers=headers)
    assert resp.status_code == 403


def test_audit_log_protection_immutability():
    admin_token = get_token("admin_sec@example.com", "Administrator", "Sec Admin")
    headers = {"Authorization": f"Bearer {admin_token}"}

    # PUT or DELETE on /audit-logs should not be supported (404/405)
    resp = client.put("/audit-logs/1", headers=headers, json={"action": "HACKED"})
    assert resp.status_code in [404, 405]

    resp = client.delete("/audit-logs/1", headers=headers)
    assert resp.status_code in [404, 405]



def test_security_logging_on_login():
    admin_token = get_token("admin_login_test@example.com", "Administrator", "Login Test Admin")
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Failed login attempt
    bad_login_resp = client.post(
        "/auth/login",
        json={"email": "nonexistent@example.com", "password": "WrongPassword!"}
    )
    assert bad_login_resp.status_code == 401

    # 2. Check security logs for LOGIN_FAILED
    sec_logs_resp = client.get("/security-logs?event_type=LOGIN_FAILED", headers=headers)
    assert sec_logs_resp.status_code == 200
    sec_data = sec_logs_resp.json()
    assert sec_data["total"] >= 1
    # Verify passwords are never logged
    for item in sec_data["items"]:
        assert "WrongPassword!" not in item["description"]

    # 3. Check security logs for LOGIN_SUCCESS
    sec_logs_success = client.get("/security-logs?event_type=LOGIN_SUCCESS", headers=headers)
    assert sec_logs_success.status_code == 200
    assert sec_logs_success.json()["total"] >= 1


def test_decision_lifecycle_automatic_audit_and_versioning():
    admin_token = get_token("admin_lifecycle@example.com", "Administrator", "Lifecycle Admin")
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Create Decision -> Version 1 created & CREATE AuditLog
    create_resp = client.post(
        "/decisions",
        headers=headers,
        json={
            "title": "Select Database Engine",
            "problem_statement": "Need a scalable database for analytics and transactions",
            "category": "Architecture"
        }
    )
    assert create_resp.status_code == 201
    decision_id = create_resp.json()["id"]

    # Check Version 1 exists
    ver_resp = client.get(f"/decisions/{decision_id}/versions", headers=headers)
    assert ver_resp.status_code == 200
    versions = ver_resp.json()
    assert len(versions) == 1
    assert versions[0]["version_number"] == 1

    # Check specific version
    ver_1_resp = client.get(f"/decisions/{decision_id}/versions/1", headers=headers)
    assert ver_1_resp.status_code == 200
    assert ver_1_resp.json()["title"] == "Select Database Engine"
    assert ver_1_resp.json()["status"] == "Draft"

    # 2. Update Decision -> Version 2 created & UPDATE AuditLog with old/new diff
    update_resp = client.put(
        f"/decisions/{decision_id}",
        headers=headers,
        json={
            "title": "Select PostgreSQL Database Engine",
            "problem_statement": "PostgreSQL provides robust JSONB support and ACID guarantees",
            "category": "Data Layer"
        }
    )
    assert update_resp.status_code == 200

    ver_resp2 = client.get(f"/decisions/{decision_id}/versions", headers=headers)
    assert ver_resp2.status_code == 200
    versions2 = ver_resp2.json()
    assert len(versions2) == 2
    assert versions2[1]["version_number"] == 2

    # Check Version 2 details
    ver_2_resp = client.get(f"/decisions/{decision_id}/versions/2", headers=headers)
    assert ver_2_resp.status_code == 200
    assert ver_2_resp.json()["title"] == "Select PostgreSQL Database Engine"

    # Verify Version 1 was preserved immutably
    ver_1_again = client.get(f"/decisions/{decision_id}/versions/1", headers=headers)
    assert ver_1_again.json()["title"] == "Select Database Engine"

    # 3. Add Alternative
    alt_resp = client.post(
        f"/decisions/{decision_id}/alternatives",
        headers=headers,
        json={
            "name": "PostgreSQL 16",
            "description": "Enterprise standard relational database",
            "pros": "Reliable, open-source",
            "cons": "Requires scaling setup",
            "estimated_cost": 500.0,
            "feasibility_score": 5,
            "risk_level": "Low"
        }
    )
    assert alt_resp.status_code == 201
    alt_id = alt_resp.json()["id"]

    # 4. Add Comment
    comment_resp = client.post(
        f"/decisions/{decision_id}/comments",
        headers=headers,
        json={"content": "Strongly support PostgreSQL for this architecture"}
    )
    assert comment_resp.status_code == 201

    # 5. Create Reviewer and Submit for Approval
    rev_token = get_token("reviewer_test@example.com", "Reviewer", "Rev User")
    rev_info = client.get("/users/me", headers={"Authorization": f"Bearer {rev_token}"}).json()
    rev_id = rev_info["id"]

    app_resp = client.post(
        "/approvals",
        headers=headers,
        json={
            "decision_id": decision_id,
            "reviewer_id": rev_id,
            "approval_level": 1,
            "comments": "Please review"
        }
    )
    assert app_resp.status_code == 201
    approval_id = app_resp.json()["id"]

    # 6. Approve Decision
    approve_resp = client.post(
        f"/approvals/{approval_id}/approve",
        headers={"Authorization": f"Bearer {rev_token}"},
        json={"comments": "Approved after technical review"}
    )
    assert approve_resp.status_code == 200

    # 7. Check Decision History API
    history_resp = client.get(f"/decisions/{decision_id}/history", headers=headers)
    assert history_resp.status_code == 200
    hist = history_resp.json()
    assert hist["decision_id"] == decision_id
    assert hist["total_events"] >= 5
    actions = [h["action"] for h in hist["history"]]
    assert "CREATE" in actions
    assert "UPDATE" in actions
    assert "SUBMIT" in actions
    assert "APPROVE" in actions


def test_audit_filtering_and_pagination():
    admin_token = get_token("admin_filter@example.com", "Administrator", "Filter Admin")
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Query audit logs with pagination and filters
    resp = client.get("/audit-logs?page=1&page_size=10", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert data["page"] == 1
    assert data["page_size"] == 10

    # Filter by action
    resp_action = client.get("/audit-logs?action=CREATE", headers=headers)
    assert resp_action.status_code == 200
    for item in resp_action.json()["items"]:
        assert item["action"] == "CREATE"

    # Filter by entity_type
    resp_entity = client.get("/audit-logs?entity_type=Decision", headers=headers)
    assert resp_entity.status_code == 200
    for item in resp_entity.json()["items"]:
        assert item["entity_type"].lower() == "decision"


def test_validation_errors():
    admin_token = get_token("admin_validation@example.com", "Administrator", "Val Admin")
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Invalid date range (start > end) -> 422
    resp = client.get("/audit-logs?start_date=2026-12-31&end_date=2026-01-01", headers=headers)
    assert resp.status_code == 422

    # 2. Invalid date format -> 422
    resp = client.get("/audit-logs?start_date=invalid-date", headers=headers)
    assert resp.status_code == 422

    # 3. Invalid action -> 422
    resp = client.get("/audit-logs?action=NON_EXISTENT_ACTION", headers=headers)
    assert resp.status_code == 422

    # 4. Invalid entity_type -> 422
    resp = client.get("/audit-logs?entity_type=InvalidEntity", headers=headers)
    assert resp.status_code == 422

    # 5. Non-existing decision for versions -> 404
    resp = client.get("/decisions/999999/versions", headers=headers)
    assert resp.status_code == 404

    # 6. Non-existing version number -> 404
    # Create decision
    d = client.post("/decisions", headers=headers, json={"title": "T", "problem_statement": "P", "category": "C"}).json()
    resp = client.get(f"/decisions/{d['id']}/versions/9999", headers=headers)
    assert resp.status_code == 404


def test_access_logging():
    admin_token = get_token("admin_access_user@example.com", "Administrator", "Access Admin")
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Create a decision
    d_resp = client.post("/decisions", headers=headers, json={"title": "Access Test", "problem_statement": "P", "category": "C"})
    d_id = d_resp.json()["id"]

    # View decision -> triggers VIEW access log
    client.get(f"/decisions/{d_id}", headers=headers)

    # Check access logs
    acc_resp = client.get(f"/access-logs?resource_type=Decision&resource_id={d_id}", headers=headers)
    assert acc_resp.status_code == 200
    acc_data = acc_resp.json()
    assert acc_data["total"] >= 1
    assert acc_data["items"][0]["action"] == "VIEW"
