import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from app.main import app
from app.models.user import User

client = TestClient(app)


def create_user_and_token(email: str, role: str, full_name: str = "Test User"):
    register_payload = {
        "full_name": full_name,
        "email": email,
        "role": role,
        "password": "Password123!",
        "employee_id": f"EMP_{email[:8]}",
        "department": "Engineering",
        "designation": role,
        "phone_number": "+1-555-0199"
    }
    client.post("/users", json=register_payload)
    login_res = client.post("/auth/login", json={"email": email, "password": "Password123!"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    user_id = login_res.json()["user"]["id"]
    return token, user_id


# --- 1. AUDIT & VERSIONING ON DECISION WORKFLOW ---

def test_decision_create_generates_version_and_audit():
    emp_token, emp_id = create_user_and_token("emp_s11_1@example.com", "Employee")
    headers = {"Authorization": f"Bearer {emp_token}"}

    create_res = client.post("/decisions", json={
        "title": "Migrate to Microservices",
        "problem_statement": "Monolith scalability bottleneck",
        "category": "Technology"
    }, headers=headers)
    assert create_res.status_code == 201
    decision = create_res.json()
    decision_id = decision["id"]

    # 1. Verify Version 1 created
    ver_res = client.get(f"/decisions/{decision_id}/versions", headers=headers)
    assert ver_res.status_code == 200
    versions = ver_res.json()
    assert len(versions) == 1
    assert versions[0]["version_number"] == 1
    assert versions[0]["title"] == "Migrate to Microservices"
    assert versions[0]["status"] == "Draft"

    # 2. Verify specific version retrieval
    ver1_res = client.get(f"/decisions/{decision_id}/versions/1", headers=headers)
    assert ver1_res.status_code == 200
    assert ver1_res.json()["version_number"] == 1


def test_decision_update_creates_sequential_versions_and_diffs():
    emp_token, emp_id = create_user_and_token("emp_s11_2@example.com", "Employee")
    headers = {"Authorization": f"Bearer {emp_token}"}

    # Step 1: Create Decision (v1)
    res = client.post("/decisions", json={
        "title": "Select Database",
        "problem_statement": "Evaluate RDBMS",
        "category": "Technology"
    }, headers=headers)
    dec_id = res.json()["id"]

    # Step 2: Update Decision (v2)
    update_res = client.put(f"/decisions/{dec_id}", json={
        "title": "Select PostgreSQL Database",
        "problem_statement": "Evaluate PostgreSQL RDBMS cluster",
        "category": "Technology"
    }, headers=headers)
    assert update_res.status_code == 200

    # Step 3: Patch Status (v3)
    status_res = client.patch(f"/decisions/{dec_id}/status", json={"status": "Under Review"}, headers=headers)
    assert status_res.status_code == 200

    # Step 4: Update Rationale (v4)
    rat_res = client.put(f"/decisions/{dec_id}/rationale", json={"rationale": "PostgreSQL has ACID compliance and JSON support"}, headers=headers)
    assert rat_res.status_code == 200

    # Verify sequential versioning: 1, 2, 3, 4
    vers_res = client.get(f"/decisions/{dec_id}/versions", headers=headers)
    assert vers_res.status_code == 200
    versions = vers_res.json()
    assert len(versions) == 4
    assert [v["version_number"] for v in versions] == [1, 2, 3, 4]
    assert versions[0]["title"] == "Select Database"
    assert versions[1]["title"] == "Select PostgreSQL Database"
    assert versions[2]["status"] == "Under Review"

    # Specific version checks
    v2 = client.get(f"/decisions/{dec_id}/versions/2", headers=headers).json()
    assert v2["title"] == "Select PostgreSQL Database"

    # 404 for non-existing version
    v999 = client.get(f"/decisions/{dec_id}/versions/999", headers=headers)
    assert v999.status_code == 404


def test_decision_change_history_endpoint():
    emp_token, emp_id = create_user_and_token("emp_s11_3@example.com", "Employee")
    headers = {"Authorization": f"Bearer {emp_token}"}

    # Create Decision
    dec = client.post("/decisions", json={
        "title": "Adopt Event-Driven Architecture",
        "problem_statement": "Decouple services",
        "category": "Architecture"
    }, headers=headers).json()
    dec_id = dec["id"]

    # Add Alternative
    client.post(f"/decisions/{dec_id}/alternatives", json={
        "name": "Apache Kafka",
        "description": "High-throughput message streaming",
        "pros": "Durable, high throughput",
        "cons": "Operational complexity",
        "estimated_cost": 1200.0,
        "feasibility_score": 5,
        "risk_level": "Medium"
    }, headers=headers)

    # Add Comment
    client.post(f"/decisions/{dec_id}/comments", json={"content": "Benchmarking Kafka throughput."}, headers=headers)

    # Get History
    hist_res = client.get(f"/decisions/{dec_id}/history", headers=headers)
    assert hist_res.status_code == 200
    hist_data = hist_res.json()
    assert hist_data["decision_id"] == dec_id
    assert hist_data["total_events"] >= 3
    actions = [h["action"] for h in hist_data["history"]]
    assert "CREATE" in actions


# --- 2. AUDIT LOGS RBAC & FILTERING ---

def test_audit_logs_access_control():
    emp_token, _ = create_user_and_token("emp_s11_4@example.com", "Employee")
    adm_token, _ = create_user_and_token("admin_s11_4@example.com", "Administrator")

    # 1. No JWT -> 401
    res_no_jwt = client.get("/audit-logs")
    assert res_no_jwt.status_code == 401

    # 2. Employee -> 403 Forbidden
    res_emp = client.get("/audit-logs", headers={"Authorization": f"Bearer {emp_token}"})
    assert res_emp.status_code == 403

    # 3. Administrator -> 200 OK
    res_adm = client.get("/audit-logs", headers={"Authorization": f"Bearer {adm_token}"})
    assert res_adm.status_code == 200
    data = res_adm.json()
    assert "items" in data
    assert "page" in data
    assert "page_size" in data
    assert "total" in data


def test_audit_logs_filters_and_validations():
    adm_token, adm_id = create_user_and_token("admin_s11_5@example.com", "Administrator")
    adm_headers = {"Authorization": f"Bearer {adm_token}"}

    # Filter by action=CREATE
    res_act = client.get("/audit-logs?action=CREATE", headers=adm_headers)
    assert res_act.status_code == 200
    for item in res_act.json()["items"]:
        assert item["action"] == "CREATE"

    # Filter by entity_type=Decision
    res_ent = client.get("/audit-logs?entity_type=Decision", headers=adm_headers)
    assert res_ent.status_code == 200
    for item in res_ent.json()["items"]:
        assert item["entity_type"] == "Decision"

    # Invalid Action -> 422
    res_bad_act = client.get("/audit-logs?action=INVALID_ACTION", headers=adm_headers)
    assert res_bad_act.status_code == 422

    # Invalid Entity Type -> 422
    res_bad_ent = client.get("/audit-logs?entity_type=InvalidType", headers=adm_headers)
    assert res_bad_ent.status_code == 422

    # Invalid Date Format -> 422
    res_bad_date = client.get("/audit-logs?start_date=2026/08/31", headers=adm_headers)
    assert res_bad_date.status_code == 422

    # start_date > end_date -> 422
    res_bad_range = client.get("/audit-logs?start_date=2026-12-31&end_date=2026-01-01", headers=adm_headers)
    assert res_bad_range.status_code == 422

    # Non-existent user -> 404
    res_no_user = client.get("/audit-logs?user_id=99999", headers=adm_headers)
    assert res_no_user.status_code == 404


# --- 3. SECURITY LOGS & ACCESS LOGS ---

def test_security_logs_login_events():
    adm_token, _ = create_user_and_token("admin_s11_6@example.com", "Administrator")
    adm_headers = {"Authorization": f"Bearer {adm_token}"}

    # Failed login attempt
    bad_login = client.post("/auth/login", json={"email": "non_existent@example.com", "password": "WrongPassword!"})
    assert bad_login.status_code == 401

    # Check security logs as admin
    sec_res = client.get("/security-logs", headers=adm_headers)
    assert sec_res.status_code == 200
    sec_data = sec_res.json()
    event_types = [item["event_type"] for item in sec_data["items"]]
    assert "LOGIN_FAILED" in event_types
    assert "LOGIN_SUCCESS" in event_types

    # Ensure passwords are NOT in the descriptions
    for item in sec_data["items"]:
        assert "WrongPassword!" not in item["description"]
        assert "Password123!" not in item["description"]


def test_access_logs_resource_tracking():
    emp_token, _ = create_user_and_token("emp_s11_7@example.com", "Employee")
    adm_token, _ = create_user_and_token("admin_s11_7@example.com", "Administrator")

    # Employee creates and views a decision
    dec = client.post("/decisions", json={
        "title": "Access Log Test Decision",
        "problem_statement": "Testing access logs",
        "category": "Security"
    }, headers={"Authorization": f"Bearer {emp_token}"}).json()

    # View decision
    client.get(f"/decisions/{dec['id']}", headers={"Authorization": f"Bearer {emp_token}"})

    # Admin checks access logs
    acc_res = client.get("/access-logs", headers={"Authorization": f"Bearer {adm_token}"})
    assert acc_res.status_code == 200
    acc_data = acc_res.json()
    resource_types = [item["resource_type"] for item in acc_data["items"]]
    assert "Decision" in resource_types
