import io
import uuid
import openpyxl
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def create_and_login_user(email: str, role: str, full_name: str, department: str = "Engineering"):
    emp_id = f"EMP-{uuid.uuid4().hex[:6]}"
    client.post(
        "/users",
        json={
            "email": email,
            "password": "Password123!",
            "full_name": full_name,
            "role": role,
            "employee_id": emp_id,
            "department": department
        }
    )
    resp = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "Password123!"
        }
    )
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    token = resp.json()["access_token"]
    user_info = client.get("/users/me", headers={"Authorization": f"Bearer {token}"}).json()
    return token, user_info


# =============================================================================
# 1. COMPLETE END-TO-END DECISION LIFECYCLE INTEGRATION TEST
# =============================================================================

def test_full_decision_lifecycle_integration():
    """
    Validates complete end-to-end flow:
    Register & Login -> Create Decision -> Add 3 Alternatives -> Compare Alternatives ->
    Add Comment, Thread, Note, Rationale -> Submit for Approval -> Multi-level Review ->
    Approval -> Audit Trail -> Versions -> Dashboard -> Reports -> PDF/Excel Exports
    """
    # Step 1 & 2: Register & Authenticate users for all roles
    emp_token, emp_user = create_and_login_user("s13_emp@example.com", "Employee", "Alice Employee", "Engineering")
    rev_token, rev_user = create_and_login_user("s13_rev@example.com", "Reviewer", "Bob Reviewer", "Engineering")
    mgr_token, mgr_user = create_and_login_user("s13_mgr@example.com", "Manager", "Carol Manager", "Engineering")
    adm_token, adm_user = create_and_login_user("s13_adm@example.com", "Administrator", "Dave Admin", "Executive")

    emp_hdr = {"Authorization": f"Bearer {emp_token}"}
    rev_hdr = {"Authorization": f"Bearer {rev_token}"}
    mgr_hdr = {"Authorization": f"Bearer {mgr_token}"}
    adm_hdr = {"Authorization": f"Bearer {adm_token}"}

    # Step 3: Create Decision as Employee
    dec_resp = client.post(
        "/decisions",
        headers=emp_hdr,
        json={
            "title": "Select Core Database Engine for 2026",
            "problem_statement": "Evaluate SQL vs NoSQL for high throughput and ACID compliance",
            "category": "Architecture"
        }
    )
    assert dec_resp.status_code == 201
    decision = dec_resp.json()
    dec_id = decision["id"]
    assert decision["status"] == "Draft"
    assert decision["created_by"] == emp_user["id"]

    # Step 4: Add at least 3 Alternatives (PostgreSQL, MySQL, MongoDB)
    alt1 = client.post(
        f"/decisions/{dec_id}/alternatives",
        headers=emp_hdr,
        json={
            "name": "PostgreSQL 16",
            "description": "Enterprise-grade relational database with JSONB support",
            "pros": "ACID compliance, rich indexing, active ecosystem",
            "cons": "Requires vertical scaling tuning",
            "estimated_cost": 450.0,
            "feasibility_score": 5,
            "risk_level": "Low"
        }
    )
    assert alt1.status_code == 201

    alt2 = client.post(
        f"/decisions/{dec_id}/alternatives",
        headers=emp_hdr,
        json={
            "name": "MySQL 8.4",
            "description": "Standard relational DBMS",
            "pros": "High read performance, wide familiarity",
            "cons": "Less extensive JSON query operators",
            "estimated_cost": 300.0,
            "feasibility_score": 4,
            "risk_level": "Medium"
        }
    )
    assert alt2.status_code == 201

    alt3 = client.post(
        f"/decisions/{dec_id}/alternatives",
        headers=emp_hdr,
        json={
            "name": "MongoDB 7.0",
            "description": "Document-oriented database",
            "pros": "Flexible schema, native sharding",
            "cons": "Complex multi-document transaction overhead",
            "estimated_cost": 600.0,
            "feasibility_score": 3,
            "risk_level": "High"
        }
    )
    assert alt3.status_code == 201

    # Step 5: Compare Alternatives
    cmp_resp = client.get(f"/decisions/{dec_id}/alternatives/compare", headers=emp_hdr)
    assert cmp_resp.status_code == 200
    cmp_data = cmp_resp.json()
    assert cmp_data["decision_id"] == dec_id
    assert len(cmp_data["alternatives"]) == 3
    alt_names = [a["name"] for a in cmp_data["alternatives"]]
    assert "PostgreSQL 16" in alt_names
    assert "MySQL 8.4" in alt_names
    assert "MongoDB 7.0" in alt_names

    # Step 6: Add Discussion (Comment, Discussion Thread, Meeting Note, Rationale)
    # 6a. Comment
    com_resp = client.post(
        f"/decisions/{dec_id}/comments",
        headers=rev_hdr,
        json={"content": "PostgreSQL appears to best satisfy our analytical and transactional needs."}
    )
    assert com_resp.status_code == 201

    # 6b. Thread
    thr_resp = client.post(
        f"/decisions/{dec_id}/threads",
        headers=emp_hdr,
        json={"title": "Partitioning Strategy", "content": "How should we partition time-series logs?"}
    )
    assert thr_resp.status_code == 201

    # 6c. Meeting Note
    note_resp = client.post(
        f"/decisions/{dec_id}/meeting-notes",
        headers=mgr_hdr,
        json={
            "title": "Architecture Review Board Sync",
            "content": "Reviewed benchmarks for all 3 alternatives; consensus favors Postgres."
        }
    )
    assert note_resp.status_code == 201

    # 6d. Decision Rationale
    rat_resp = client.put(
        f"/decisions/{dec_id}/rationale",
        headers=emp_hdr,
        json={"rationale": "PostgreSQL provides the optimal blend of ACID reliability and JSON versatility."}
    )
    assert rat_resp.status_code == 200
    assert rat_resp.json()["rationale"] is not None

    # Step 7 & 8: Submit for Multi-Level Approval
    # Level 1: Assigned to Reviewer
    app1_resp = client.post(
        "/approvals",
        headers=emp_hdr,
        json={
            "decision_id": dec_id,
            "reviewer_id": rev_user["id"],
            "approval_level": 1,
            "comments": "Level 1 Technical Peer Review"
        }
    )
    assert app1_resp.status_code == 201
    app1_id = app1_resp.json()["id"]

    # Level 2: Assigned to Manager
    app2_resp = client.post(
        "/approvals",
        headers=emp_hdr,
        json={
            "decision_id": dec_id,
            "reviewer_id": mgr_user["id"],
            "approval_level": 2,
            "comments": "Level 2 Managerial & Budget Review"
        }
    )
    assert app2_resp.status_code == 201
    app2_id = app2_resp.json()["id"]

    # Verify decision status changed to "Under Review"
    dec_check1 = client.get(f"/decisions/{dec_id}", headers=emp_hdr).json()
    assert dec_check1["status"] == "Under Review"

    # Step 9: Reviewer Action & Authorization Verification
    # 9a. Unauthorized user (Employee) cannot approve
    unauth_app = client.post(f"/approvals/{app1_id}/approve", headers=emp_hdr)
    assert unauth_app.status_code == 403

    # 9b. Reviewer approves Level 1
    rev_app = client.post(
        f"/approvals/{app1_id}/approve",
        headers=rev_hdr,
        json={"comments": "Technical benchmarks approved."}
    )
    assert rev_app.status_code == 200

    # Verify decision status REMAINS "Under Review" because Level 2 is still Pending
    dec_check2 = client.get(f"/decisions/{dec_id}", headers=emp_hdr).json()
    assert dec_check2["status"] == "Under Review"

    # Step 10: Manager Action (Level 2 Approval)
    mgr_app = client.post(
        f"/approvals/{app2_id}/approve",
        headers=mgr_hdr,
        json={"comments": "Budget and architecture approved."}
    )
    assert mgr_app.status_code == 200

    # Step 11: Final Decision Status is "Approved"
    final_dec = client.get(f"/decisions/{dec_id}", headers=emp_hdr).json()
    assert final_dec["status"] == "Approved"

    # Verify Version History (Multiple sequential versions)
    ver_resp = client.get(f"/decisions/{dec_id}/versions", headers=adm_hdr)
    assert ver_resp.status_code == 200
    versions = ver_resp.json()
    assert len(versions) >= 2
    assert versions[0]["version_number"] == 1

    # Verify Audit History
    hist_resp = client.get(f"/decisions/{dec_id}/history", headers=adm_hdr)
    assert hist_resp.status_code == 200
    hist = hist_resp.json()
    assert hist["total_events"] >= 3

    # Verify Dashboards
    emp_dash = client.get("/dashboard/employee", headers=emp_hdr).json()
    assert emp_dash["total_decisions"] >= 1
    assert emp_dash["approved_decisions"] >= 1

    mgr_dash = client.get("/dashboard/manager", headers=mgr_hdr).json()
    assert mgr_dash["team_decisions"] >= 1
    assert mgr_dash["approved_decisions"] >= 1

    adm_dash = client.get("/dashboard/admin", headers=adm_hdr).json()
    assert adm_dash["total_decisions"] >= 1
    assert adm_dash["approved_decisions"] >= 1

    # Verify Centralized Reports
    rep_dec = client.get(f"/reports/decisions?status=Approved", headers=adm_hdr).json()
    assert rep_dec["total"] >= 1

    rep_app = client.get(f"/reports/approvals?decision_id={dec_id}", headers=adm_hdr).json()
    assert rep_app["total"] == 2
    assert rep_app["summary"]["approved_approvals"] == 2
    assert rep_app["summary"]["approval_completion_rate"] == 100.0

    # Verify PDF and Excel Export
    pdf_resp = client.get(f"/reports/decisions/export/pdf?status=Approved", headers=adm_hdr)
    assert pdf_resp.status_code == 200
    assert pdf_resp.content.startswith(b"%PDF-")

    xlsx_resp = client.get(f"/reports/decisions/export/excel?status=Approved", headers=adm_hdr)
    assert xlsx_resp.status_code == 200
    wb = openpyxl.load_workbook(io.BytesIO(xlsx_resp.content))
    assert "Decisions" in wb.sheetnames


# =============================================================================
# 2. DECISION STATE MACHINE & TRANSITION RULES
# =============================================================================

def test_decision_state_machine_enforcement():
    adm_token, _ = create_and_login_user("s13_state_adm@example.com", "Administrator", "State Admin")
    headers = {"Authorization": f"Bearer {adm_token}"}

    # 1. Create Decision in Draft
    d = client.post(
        "/decisions",
        headers=headers,
        json={"title": "State Test Decision", "problem_statement": "Test state transitions", "category": "Testing"}
    ).json()
    d_id = d["id"]
    assert d["status"] == "Draft"

    # 2. Valid transition: Draft -> Under Review
    resp = client.patch(f"/decisions/{d_id}/status", headers=headers, json={"status": "Under Review"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "Under Review"

    # 3. Valid transition: Under Review -> Approved
    resp = client.patch(f"/decisions/{d_id}/status", headers=headers, json={"status": "Approved"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "Approved"

    # 4. Invalid transition: Approved -> Draft (Must fail with 400 Bad Request)
    resp = client.patch(f"/decisions/{d_id}/status", headers=headers, json={"status": "Draft"})
    assert resp.status_code == 400
    assert "invalid state transition" in resp.json()["detail"].lower()

    # 5. Valid transition: Approved -> Archived
    resp = client.patch(f"/decisions/{d_id}/status", headers=headers, json={"status": "Archived"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "Archived"

    # 6. Invalid transition: Archived -> Draft (Terminal state, must fail with 400 Bad Request)
    resp = client.patch(f"/decisions/{d_id}/status", headers=headers, json={"status": "Draft"})
    assert resp.status_code == 400
    assert "archived" in resp.json()["detail"].lower()


# =============================================================================
# 3. AUTHENTICATION & AUTHORIZATION (401 & 403)
# =============================================================================

def test_authentication_and_authorization_matrix():
    # 1. Missing JWT -> 401 Unauthorized
    assert client.get("/decisions").status_code == 401
    assert client.get("/dashboard/employee").status_code == 401
    assert client.get("/reports/decisions").status_code == 401

    # 2. Invalid JWT -> 401 Unauthorized
    bad_hdr = {"Authorization": "Bearer invalid.jwt.token"}
    assert client.get("/decisions", headers=bad_hdr).status_code == 401

    # 3. Role Access Matrix
    emp_token, _ = create_and_login_user("s13_perm_emp@example.com", "Employee", "Perm Emp", "Engineering")
    mgr_token, _ = create_and_login_user("s13_perm_mgr@example.com", "Manager", "Perm Mgr", "Engineering")
    adm_token, _ = create_and_login_user("s13_perm_adm@example.com", "Administrator", "Perm Adm", "Executive")

    emp_hdr = {"Authorization": f"Bearer {emp_token}"}
    mgr_hdr = {"Authorization": f"Bearer {mgr_token}"}
    adm_hdr = {"Authorization": f"Bearer {adm_token}"}

    # Employee cannot access Manager Dashboard (403)
    assert client.get("/dashboard/manager", headers=emp_hdr).status_code == 403
    # Manager can access Manager Dashboard (200)
    assert client.get("/dashboard/manager", headers=mgr_hdr).status_code == 200

    # Employee and Manager cannot access Admin Dashboard (403)
    assert client.get("/dashboard/admin", headers=emp_hdr).status_code == 403
    assert client.get("/dashboard/admin", headers=mgr_hdr).status_code == 403
    # Administrator can access Admin Dashboard (200)
    assert client.get("/dashboard/admin", headers=adm_hdr).status_code == 200

    # Audit reports: Forbidden for Employee and Manager, Allowed for Admin
    assert client.get("/reports/audit", headers=emp_hdr).status_code == 403
    assert client.get("/reports/audit", headers=mgr_hdr).status_code == 403
    assert client.get("/reports/audit", headers=adm_hdr).status_code == 200


# =============================================================================
# 4. INPUT VALIDATION & ERROR HANDLING (404 & 422)
# =============================================================================

def test_validation_and_error_handling():
    adm_token, _ = create_and_login_user("s13_err_adm@example.com", "Administrator", "Err Admin")
    headers = {"Authorization": f"Bearer {adm_token}"}

    # 1. 404 Not Found for non-existing entities
    assert client.get("/decisions/999999", headers=headers).status_code == 404
    assert client.get("/approvals/999999", headers=headers).status_code == 404

    # 2. 422 for invalid non-integer IDs
    assert client.get("/decisions/not-an-int", headers=headers).status_code == 422

    # 3. 422 for missing required fields in Decision
    bad_dec = client.post("/decisions", headers=headers, json={"title": "Missing Fields"})
    assert bad_dec.status_code == 422

    # 4. 422 for invalid feasibility score (0 and 6)
    d = client.post(
        "/decisions",
        headers=headers,
        json={"title": "Alt Val Test", "problem_statement": "Validate alternatives", "category": "Testing"}
    ).json()

    # Feasibility = 0 -> 422
    alt_low = client.post(
        f"/decisions/{d['id']}/alternatives",
        headers=headers,
        json={"name": "A", "description": "D", "pros": "P", "cons": "C", "estimated_cost": 100, "feasibility_score": 0, "risk_level": "Low"}
    )
    assert alt_low.status_code == 422

    # Feasibility = 6 -> 422
    alt_high = client.post(
        f"/decisions/{d['id']}/alternatives",
        headers=headers,
        json={"name": "A", "description": "D", "pros": "P", "cons": "C", "estimated_cost": 100, "feasibility_score": 6, "risk_level": "Low"}
    )
    assert alt_high.status_code == 422

    # 5. 422 for invalid Risk Level
    alt_risk = client.post(
        f"/decisions/{d['id']}/alternatives",
        headers=headers,
        json={"name": "A", "description": "D", "pros": "P", "cons": "C", "estimated_cost": 100, "feasibility_score": 3, "risk_level": "Very Dangerous"}
    )
    assert alt_risk.status_code == 422

    # 6. 422 for invalid date range in reports
    rep_date = client.get("/reports/decisions?start_date=2026-12-31&end_date=2026-01-01", headers=headers)
    assert rep_date.status_code == 422
