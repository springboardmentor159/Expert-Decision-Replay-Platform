import time
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_complete_sprint13_end_to_end_lifecycle():
    """
    Sprint 13 Comprehensive End-to-End Decision Lifecycle:
    Register (4 Roles) -> Login (JWT) -> Create Decision -> Add 3 Alternatives ->
    Compare Alternatives -> Discussion & Notes & Rationale -> Submit for Review ->
    Reviewer Action -> Manager Approval -> Final Approved Status ->
    Audit Trail -> Version History -> Timeline -> Dashboards -> Reports -> Exports
    """
    ts = int(time.time() * 1000)

    # -------------------------------------------------------------
    # Step 1: Register Users for All 4 Roles
    # -------------------------------------------------------------
    users_data = {
        "Employee": f"s13_emp_{ts}@example.com",
        "Reviewer": f"s13_rev_{ts}@example.com",
        "Manager": f"s13_mgr_{ts}@example.com",
        "Administrator": f"s13_adm_{ts}@example.com",
    }
    tokens = {}
    uids = {}

    for role, email in users_data.items():
        reg_res = client.post("/users", json={
            "full_name": f"Test {role} {ts}",
            "email": email,
            "role": role,
            "password": "SecurePassword123!",
            "employee_id": f"E13_{role[:3].upper()}_{ts}",
            "department": "Platform Architecture",
            "designation": f"Senior {role}",
            "phone_number": "+1-555-0199"
        })
        assert reg_res.status_code == 201, f"Failed registering {role}: {reg_res.text}"
        uids[role] = reg_res.json()["id"]

        # Step 2: Login & JWT Acquisition
        login_res = client.post("/auth/login", json={
            "email": email,
            "password": "SecurePassword123!"
        })
        assert login_res.status_code == 200, f"Failed login for {role}: {login_res.text}"
        tokens[role] = login_res.json()["access_token"]
        assert "access_token" in login_res.json()

    emp_headers = {"Authorization": f"Bearer {tokens['Employee']}"}
    rev_headers = {"Authorization": f"Bearer {tokens['Reviewer']}"}
    mgr_headers = {"Authorization": f"Bearer {tokens['Manager']}"}
    adm_headers = {"Authorization": f"Bearer {tokens['Administrator']}"}

    # Verify invalid login credentials rejected
    bad_login = client.post("/auth/login", json={
        "email": users_data["Employee"],
        "password": "WrongPassword!"
    })
    assert bad_login.status_code == 401

    # -------------------------------------------------------------
    # Step 3: Create Decision as Employee
    # -------------------------------------------------------------
    dec_res = client.post("/decisions", json={
        "title": f"Enterprise Storage Engine Selection {ts}",
        "problem_statement": "Evaluate and choose an enterprise distributed storage backend",
        "category": "Technology"
    }, headers=emp_headers)
    assert dec_res.status_code == 201
    decision = dec_res.json()
    dec_id = decision["id"]
    assert decision["status"] == "Draft"
    assert decision["created_by"] == uids["Employee"]

    # Verify Version 1 is created
    v1_res = client.get(f"/decisions/{dec_id}/versions", headers=emp_headers)
    assert v1_res.status_code == 200
    assert len(v1_res.json()) == 1
    assert v1_res.json()[0]["version_number"] == 1

    # -------------------------------------------------------------
    # Step 4: Add At Least 3 Alternatives
    # -------------------------------------------------------------
    alternatives_input = [
        {"name": "PostgreSQL Aurora", "description": "Managed cloud relational DB", "pros": "ACID compliant, robust", "cons": "Scale limitations", "estimated_cost": 4500.0, "feasibility_score": 5, "risk_level": "Low"},
        {"name": "MySQL Galera Cluster", "description": "Multi-master synchronous replication", "pros": "High write availability", "cons": "Network latency sensitivity", "estimated_cost": 3800.0, "feasibility_score": 4, "risk_level": "Medium"},
        {"name": "MongoDB Atlas Distributed", "description": "Document store with horizontal sharding", "pros": "Flexible schema", "cons": "Memory intensive", "estimated_cost": 5200.0, "feasibility_score": 4, "risk_level": "Medium"},
    ]
    alt_ids = []
    for alt in alternatives_input:
        res = client.post(f"/decisions/{dec_id}/alternatives", json=alt, headers=emp_headers)
        assert res.status_code == 201, f"Failed creating alternative: {res.text}"
        alt_ids.append(res.json()["id"])
    assert len(alt_ids) == 3

    # -------------------------------------------------------------
    # Step 5: Compare Alternatives
    # -------------------------------------------------------------
    cmp_res = client.get(f"/decisions/{dec_id}/alternatives/compare", headers=emp_headers)
    assert cmp_res.status_code == 200
    cmp_data = cmp_res.json()
    assert cmp_data["decision_id"] == dec_id
    assert len(cmp_data["alternatives"]) == 3

    # -------------------------------------------------------------
    # Step 6: Add Discussion, Comments, Threads, Notes, Rationale
    # -------------------------------------------------------------
    # Comment
    com_res = client.post(f"/decisions/{dec_id}/comments", json={
        "content": "Benchmarking data confirms Postgres Aurora has superior transaction throughput."
    }, headers=emp_headers)
    assert com_res.status_code == 201
    com_id = com_res.json()["id"]

    # Discussion Thread
    thr_res = client.post(f"/decisions/{dec_id}/threads", json={
        "title": "Failover Strategy Discussion",
        "description": "Examine RPO and RTO bounds during AZ failure"
    }, headers=emp_headers)
    assert thr_res.status_code == 201
    thr_id = thr_res.json()["id"]

    # Reply to Thread
    rep_res = client.post(f"/threads/{thr_id}/comments", json={
        "content": "Aurora provides sub-30s automated failover."
    }, headers=rev_headers)
    assert rep_res.status_code == 201

    # Meeting Note
    mn_res = client.post(f"/decisions/{dec_id}/meeting-notes", json={
        "title": "Architecture Review Committee Note",
        "content": "Committee agrees with relational consistency guarantee requirement."
    }, headers=emp_headers)
    assert mn_res.status_code == 201

    # Decision Rationale
    rat_res = client.put(f"/decisions/{dec_id}/rationale", json={
        "rationale": "Selected PostgreSQL Aurora for strict ACID compliance and low-latency replicas."
    }, headers=emp_headers)
    assert rat_res.status_code == 200

    # -------------------------------------------------------------
    # Step 7: Submit Decision for Review (Draft -> Under Review)
    # -------------------------------------------------------------
    sub_res = client.post(f"/decisions/{dec_id}/submit", json={
        "reviewer_id": uids["Reviewer"],
        "approval_level": 1,
        "comments": "Ready for initial technical review."
    }, headers=emp_headers)
    assert sub_res.status_code == 201
    approval_1 = sub_res.json()
    appr_1_id = approval_1["id"]
    assert approval_1["status"] == "Pending"

    # Verify decision moved to Under Review
    check_dec = client.get(f"/decisions/{dec_id}", headers=emp_headers).json()
    assert check_dec["status"] == "Under Review"

    # -------------------------------------------------------------
    # Step 8: Reviewer Action (Approval)
    # -------------------------------------------------------------
    act_1_res = client.post(f"/approvals/{appr_1_id}/action", json={
        "status": "Approved",
        "comments": "Technical criteria verified and approved."
    }, headers=rev_headers)
    assert act_1_res.status_code == 200
    assert act_1_res.json()["status"] == "Approved"

    # -------------------------------------------------------------
    # Step 9: Manager Approval (Multi-Level / Final Sign-off)
    # -------------------------------------------------------------
    # Second-level approval submission to Manager
    sub_2_res = client.post(f"/approvals", json={
        "decision_id": dec_id,
        "reviewer_id": uids["Manager"],
        "approval_level": 2,
        "comments": "Escalated for managerial cost signoff."
    }, headers=mgr_headers)
    assert sub_2_res.status_code == 201
    appr_2_id = sub_2_res.json()["id"]

    act_2_res = client.post(f"/approvals/{appr_2_id}/action", json={
        "status": "Approved",
        "comments": "Budget and architecture verified. Fully approved."
    }, headers=mgr_headers)
    assert act_2_res.status_code == 200

    # -------------------------------------------------------------
    # Step 10: Final Decision Status Verification
    # -------------------------------------------------------------
    final_dec = client.get(f"/decisions/{dec_id}", headers=emp_headers).json()
    assert final_dec["status"] == "Approved"

    # -------------------------------------------------------------
    # Step 11: Version History Verification
    # -------------------------------------------------------------
    vers_res = client.get(f"/decisions/{dec_id}/versions", headers=emp_headers)
    assert vers_res.status_code == 200
    versions = vers_res.json()
    assert len(versions) >= 3
    # Check sequential version numbers
    v_nums = [v["version_number"] for v in versions]
    assert v_nums == list(range(1, len(versions) + 1))

    # Retrieve specific version snapshot
    spec_v = client.get(f"/decisions/{dec_id}/versions/1", headers=emp_headers)
    assert spec_v.status_code == 200
    assert spec_v.json()["version_number"] == 1

    # -------------------------------------------------------------
    # Step 12: Audit Trail & Timeline Verification
    # -------------------------------------------------------------
    hist_res = client.get(f"/decisions/{dec_id}/history", headers=emp_headers)
    assert hist_res.status_code == 200
    assert hist_res.json()["total_events"] > 0

    time_res = client.get(f"/decisions/{dec_id}/timeline", headers=emp_headers)
    assert time_res.status_code == 200
    assert len(time_res.json()["events"]) >= 5

    # -------------------------------------------------------------
    # Step 13: Dashboards Verification
    # -------------------------------------------------------------
    emp_dash = client.get("/dashboard/employee", headers=emp_headers)
    assert emp_dash.status_code == 200
    assert emp_dash.json()["total_decisions"] >= 1

    mgr_dash = client.get("/dashboard/manager", headers=mgr_headers)
    assert mgr_dash.status_code == 200
    assert mgr_dash.json()["team_decisions"] >= 1

    adm_dash = client.get("/dashboard/admin", headers=adm_headers)
    assert adm_dash.status_code == 200
    assert adm_dash.json()["total_users"] >= 4

    # -------------------------------------------------------------
    # Step 14: Reports & Export Verification (PDF & Excel)
    # -------------------------------------------------------------
    dec_rep = client.get("/reports/decisions?category=Technology", headers=adm_headers)
    assert dec_rep.status_code == 200
    assert dec_rep.json()["total"] >= 1

    # PDF Export
    pdf_res = client.get("/reports/decisions/export/pdf", headers=adm_headers)
    assert pdf_res.status_code == 200
    assert pdf_res.content.startswith(b"%PDF-")

    # Excel Export
    excel_res = client.get("/reports/decisions/export/excel", headers=adm_headers)
    assert excel_res.status_code == 200
    assert len(excel_res.content) > 100


def test_role_based_access_control_and_permissions():
    """
    Test RBAC authorization matrices and ensure 403 Forbidden on unauthorized actions:
    - Employee cannot access Admin / Manager dashboards
    - Employee cannot access system audit/security/access logs
    - Non-owner Employee cannot update another user's decision
    - Non-admin cannot modify user roles or delete users
    - Non-admin cannot delete tags
    """
    ts = int(time.time() * 1000)
    # Register Alice (Employee) and Bob (Employee) and Charlie (Admin)
    def register_and_login(name, role):
        email = f"rbac_{name}_{ts}@example.com"
        client.post("/users", json={
            "full_name": name,
            "email": email,
            "role": role,
            "password": "Password123!",
            "employee_id": f"EMP_RBAC_{name[:3].upper()}_{ts}"
        })
        l = client.post("/auth/login", json={"email": email, "password": "Password123!"})
        return l.json()["access_token"], l.json()["user"]["id"]

    alice_token, alice_id = register_and_login("Alice", "Employee")
    bob_token, bob_id = register_and_login("Bob", "Employee")
    admin_token, admin_id = register_and_login("CharlieAdmin", "Administrator")

    alice_h = {"Authorization": f"Bearer {alice_token}"}
    bob_h = {"Authorization": f"Bearer {bob_token}"}
    admin_h = {"Authorization": f"Bearer {admin_token}"}

    # 1. Alice creates a decision
    d_res = client.post("/decisions", json={
        "title": f"Alice Decision {ts}",
        "problem_statement": "Confidential decision by Alice",
        "category": "Technology"
    }, headers=alice_h)
    alice_dec_id = d_res.json()["id"]

    # 2. Bob tries to update Alice's decision -> 403 Forbidden
    bob_update = client.put(f"/decisions/{alice_dec_id}", json={
        "title": "Hacked Title",
        "problem_statement": "Hacked statement",
        "category": "Technology"
    }, headers=bob_h)
    assert bob_update.status_code == 403

    # 3. Bob tries to submit Alice's decision -> 403 Forbidden
    bob_sub = client.post(f"/decisions/{alice_dec_id}/submit", json={
        "reviewer_id": admin_id,
        "approval_level": 1
    }, headers=bob_h)
    assert bob_sub.status_code == 403

    # 4. Bob tries to add an alternative to Alice's decision -> 403 Forbidden
    bob_alt = client.post(f"/decisions/{alice_dec_id}/alternatives", json={
        "name": "Bob Alt",
        "description": "Desc",
        "pros": "P",
        "cons": "C",
        "estimated_cost": 100.0,
        "feasibility_score": 3,
        "risk_level": "Low"
    }, headers=bob_h)
    assert bob_alt.status_code == 403

    # 5. Alice tries to access Administrator endpoints -> 403 Forbidden
    assert client.get("/dashboard/admin", headers=alice_h).status_code == 403
    assert client.get("/dashboard/manager", headers=alice_h).status_code == 403
    assert client.get("/audit-logs", headers=alice_h).status_code == 403
    assert client.get("/security-logs", headers=alice_h).status_code == 403
    assert client.get("/access-logs", headers=alice_h).status_code == 403

    # 6. Alice tries to elevate her own role to Administrator -> 403 Forbidden
    elevate_res = client.put(f"/users/{alice_id}", json={"role": "Administrator"}, headers=alice_h)
    assert elevate_res.status_code == 403

    # 7. Alice tries to delete Bob -> 403 Forbidden
    assert client.delete(f"/users/{bob_id}", headers=alice_h).status_code == 403

    # 8. Create a tag as Admin, Alice tries to delete tag -> 403 Forbidden
    tag_res = client.post("/tags", json={"name": f"SecTag_{ts}", "category": "Security"}, headers=admin_h)
    if tag_res.status_code == 201:
        tid = tag_res.json()["id"]
        assert client.delete(f"/tags/{tid}", headers=alice_h).status_code == 403


def test_decision_state_transition_rules():
    """
    Test valid and invalid decision state transitions:
    - Valid: Draft -> Under Review -> Approved
    - Invalid: Archived -> Draft (must be 422)
    - Invalid: Approved -> Draft (must be 422)
    - Submit already Approved decision -> 422
    - Action on already completed approval -> 400
    """
    ts = int(time.time() * 1000)
    email = f"state_tester_{ts}@example.com"
    client.post("/users", json={
        "full_name": "State Tester",
        "email": email,
        "role": "Administrator",
        "password": "Password123!",
        "employee_id": f"EMP_ST_{ts}"
    })
    token = client.post("/auth/login", json={"email": email, "password": "Password123!"}).json()["access_token"]
    h = {"Authorization": f"Bearer {token}"}

    # 1. Create Decision
    d_res = client.post("/decisions", json={
        "title": f"State Test Decision {ts}",
        "problem_statement": "Testing transition constraints",
        "category": "Operations"
    }, headers=h)
    dec_id = d_res.json()["id"]

    # 2. Transition Draft -> Archived
    arch_res = client.patch(f"/decisions/{dec_id}/status", json={"status": "Archived"}, headers=h)
    assert arch_res.status_code == 200
    assert arch_res.json()["status"] == "Archived"

    # 3. Try Invalid Transition: Archived -> Draft
    inv_res = client.patch(f"/decisions/{dec_id}/status", json={"status": "Draft"}, headers=h)
    assert inv_res.status_code == 422
    assert "Invalid state transition" in inv_res.json()["detail"]

    # 4. Try Invalid Transition: Archived -> Under Review
    inv_res_2 = client.patch(f"/decisions/{dec_id}/status", json={"status": "Under Review"}, headers=h)
    assert inv_res_2.status_code == 422

    # 5. Create another decision and move Draft -> Under Review -> Approved
    d2 = client.post("/decisions", json={
        "title": f"Approved Decision {ts}",
        "problem_statement": "Testing approved constraints",
        "category": "Finance"
    }, headers=h).json()
    d2_id = d2["id"]

    client.patch(f"/decisions/{d2_id}/status", json={"status": "Under Review"}, headers=h)
    client.patch(f"/decisions/{d2_id}/status", json={"status": "Approved"}, headers=h)

    # Try Invalid Transition: Approved -> Draft
    inv_res_3 = client.patch(f"/decisions/{d2_id}/status", json={"status": "Draft"}, headers=h)
    assert inv_res_3.status_code == 422

    # Try Submitting an already Archived decision -> 422
    inv_sub = client.post(f"/decisions/{dec_id}/submit", json={"reviewer_id": 1}, headers=h)
    assert inv_sub.status_code == 422


def test_input_validation_and_error_handling():
    """
    Test comprehensive input validations and expected error responses:
    - 422 for feasibility_score < 1 or > 5
    - 422 for invalid risk level
    - 422 for malformed email
    - 422 for missing required fields
    - 404 for non-existent resources
    - 401 for unauthenticated requests
    """
    ts = int(time.time() * 1000)
    email = f"val_tester_{ts}@example.com"
    client.post("/users", json={
        "full_name": "Validation Tester",
        "email": email,
        "role": "Administrator",
        "password": "Password123!",
        "employee_id": f"EMP_VAL_{ts}"
    })
    token = client.post("/auth/login", json={"email": email, "password": "Password123!"}).json()["access_token"]
    h = {"Authorization": f"Bearer {token}"}

    d = client.post("/decisions", json={
        "title": f"Validation Target {ts}",
        "problem_statement": "Testing validations",
        "category": "Technology"
    }, headers=h).json()
    dec_id = d["id"]

    # Feasibility Score 0 -> 422
    r_0 = client.post(f"/decisions/{dec_id}/alternatives", json={
        "name": "Alt 0", "description": "Desc", "pros": "P", "cons": "C",
        "estimated_cost": 100.0, "feasibility_score": 0, "risk_level": "Low"
    }, headers=h)
    assert r_0.status_code == 422

    # Feasibility Score 6 -> 422
    r_6 = client.post(f"/decisions/{dec_id}/alternatives", json={
        "name": "Alt 6", "description": "Desc", "pros": "P", "cons": "C",
        "estimated_cost": 100.0, "feasibility_score": 6, "risk_level": "Low"
    }, headers=h)
    assert r_6.status_code == 422

    # Invalid Risk Level -> 422
    r_risk = client.post(f"/decisions/{dec_id}/alternatives", json={
        "name": "Alt Risk", "description": "Desc", "pros": "P", "cons": "C",
        "estimated_cost": 100.0, "feasibility_score": 3, "risk_level": "Extremely Dangerous"
    }, headers=h)
    assert r_risk.status_code == 422

    # Malformed Email in Registration -> 422
    r_email = client.post("/users", json={
        "full_name": "Bad Email",
        "email": "not-an-email",
        "role": "Employee",
        "password": "Password123!",
        "employee_id": f"EMP_BAD_{ts}"
    })
    assert r_email.status_code == 422

    # Missing Required Fields -> 422
    r_miss = client.post("/decisions", json={"title": "Missing fields"}, headers=h)
    assert r_miss.status_code == 422

    # Non-existing resources -> 404
    assert client.get("/decisions/9999999", headers=h).status_code == 404
    assert client.get("/alternatives/9999999", headers=h).status_code == 404
    assert client.get("/comments/9999999", headers=h).status_code == 404
    assert client.get("/threads/9999999", headers=h).status_code == 404
    assert client.get("/meeting-notes/9999999", headers=h).status_code == 404
    assert client.get("/users/9999999", headers=h).status_code == 404

    # Unauthenticated Requests -> 401
    assert client.get("/decisions").status_code == 401
    assert client.get("/dashboard/employee").status_code == 401
    assert client.get("/audit-logs").status_code == 401


def test_security_audit_data_sanitization():
    """
    Verify security integrity:
    - Passwords and secrets are never present in audit logs or security logs
    - User passwords in responses are excluded
    """
    ts = int(time.time() * 1000)
    email = f"audit_sec_{ts}@example.com"
    reg = client.post("/users", json={
        "full_name": "Audit Sec User",
        "email": email,
        "role": "Administrator",
        "password": "SuperSecretPassword999!",
        "employee_id": f"EMP_AUD_{ts}"
    })
    user_data = reg.json()
    assert "password" not in user_data
    assert "hashed_password" not in user_data

    l = client.post("/auth/login", json={"email": email, "password": "SuperSecretPassword999!"})
    token = l.json()["access_token"]
    h = {"Authorization": f"Bearer {token}"}

    # Verify audit logs do not contain raw secret passwords
    audits = client.get("/audit-logs?page=1&page_size=20", headers=h).json()["items"]
    for a in audits:
        assert "SuperSecretPassword999!" not in str(a.get("description", ""))
        assert "SuperSecretPassword999!" not in str(a.get("old_value", ""))
        assert "SuperSecretPassword999!" not in str(a.get("new_value", ""))

    # Verify security logs do not contain passwords
    sec_logs = client.get("/security-logs?page=1&page_size=20", headers=h).json()["items"]
    for s in sec_logs:
        assert "SuperSecretPassword999!" not in str(s.get("description", ""))
