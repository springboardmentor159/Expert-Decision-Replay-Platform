import sys
from fastapi.testclient import TestClient
from sqlalchemy import inspect

from app.db.database import engine
from app.main import app

client = TestClient(app)


def run_sprint11_verification():
    print("=" * 85)
    print(" SPRINT 11: AUDIT & COMPLIANCE MODULE COMPREHENSIVE VERIFICATION")
    print("=" * 85)

    passed_count = 0
    total_count = 0

    def record_check(condition: bool, test_name: str, details: str = ""):
        nonlocal passed_count, total_count
        total_count += 1
        if condition:
            passed_count += 1
            print(f" [PASS] {test_name}")
        else:
            print(f" [FAIL] {test_name} -> {details}")

    def setup_user(email: str, role: str, department: str = "Enterprise Architecture"):
        u_data = {
            "full_name": email.split("@")[0].replace("_", " ").title(),
            "email": email,
            "role": role,
            "password": "Password123!",
            "employee_id": f"EMP_S11_{email[:6]}",
            "department": department,
            "designation": f"Lead {role}",
            "phone_number": "+1-555-1100"
        }
        client.post("/users", json=u_data)
        login_res = client.post("/auth/login", json={"email": email, "password": "Password123!"})
        assert login_res.status_code == 200, f"Login failed for {email}"
        return login_res.json()["access_token"], login_res.json()["user"]["id"]

    # =========================================================================
    # Step 1: User Roles Setup & JWT Acquisition
    # =========================================================================
    print("\n--- Step 1: Setup Roles & Login (Swagger Step 1) ---")
    emp_token, emp_id = setup_user("s11_employee@example.com", "Employee", "Architecture")
    emp_headers = {"Authorization": f"Bearer {emp_token}"}
    record_check(bool(emp_token), "1.1 Login as Employee & Acquire JWT Token (200 OK)")

    rev_token, rev_id = setup_user("s11_reviewer@example.com", "Reviewer", "Architecture")
    rev_headers = {"Authorization": f"Bearer {rev_token}"}
    record_check(bool(rev_token), "1.2 Login as Reviewer & Acquire JWT Token (200 OK)")

    adm_token, adm_id = setup_user("s11_admin@example.com", "Administrator", "Compliance")
    adm_headers = {"Authorization": f"Bearer {adm_token}"}
    record_check(bool(adm_token), "1.3 Login as Admin & Acquire JWT Token (200 OK)")

    # =========================================================================
    # Step 2: Create Decision -> Auto CREATE Audit Log & Version 1
    # =========================================================================
    print("\n--- Step 2: Create Decision & Verify Auto Audit / Version 1 (Swagger Step 2) ---")
    dec_payload = {
        "title": "Select PostgreSQL Database",
        "problem_statement": "Need robust transactional RDBMS with JSON support",
        "category": "Technology"
    }
    create_res = client.post("/decisions", json=dec_payload, headers=emp_headers)
    record_check(create_res.status_code == 201, "2.1 POST /decisions creates Decision (201 Created)")
    dec_id = create_res.json()["id"]

    # Check Version 1 created
    ver_init_res = client.get(f"/decisions/{dec_id}/versions", headers=emp_headers)
    record_check(
        ver_init_res.status_code == 200 and len(ver_init_res.json()) == 1 and ver_init_res.json()[0]["version_number"] == 1,
        "2.2 Version 1 automatically created upon Decision creation"
    )

    # Check CREATE audit log as admin
    audit_init_res = client.get(f"/audit-logs?entity_type=Decision&entity_id={dec_id}&action=CREATE", headers=adm_headers)
    record_check(
        audit_init_res.status_code == 200 and audit_init_res.json()["total"] >= 1,
        "2.3 Automatic CREATE audit record generated with correct entity_type and action"
    )

    # =========================================================================
    # Step 3: Update Decision -> Auto UPDATE Audit Log & Version 2
    # =========================================================================
    print("\n--- Step 3: Update Decision & Verify Diff + Version 2 (Swagger Step 3) ---")
    update_payload = {
        "title": "Select PostgreSQL 16 Database Cluster",
        "problem_statement": "Need robust transactional RDBMS with streaming replication",
        "category": "Technology"
    }
    update_res = client.put(f"/decisions/{dec_id}", json=update_payload, headers=emp_headers)
    record_check(update_res.status_code == 200, "3.1 PUT /decisions/{id} updates Decision (200 OK)")

    # Check Version 2 created
    ver_update_res = client.get(f"/decisions/{dec_id}/versions", headers=emp_headers)
    vers = ver_update_res.json()
    record_check(
        len(vers) == 2 and vers[1]["version_number"] == 2 and vers[1]["title"] == "Select PostgreSQL 16 Database Cluster",
        "3.2 Version 2 sequentially created with updated snapshot"
    )

    # Check UPDATE audit log with old_value and new_value diffs
    audit_update_res = client.get(f"/audit-logs?entity_type=Decision&entity_id={dec_id}&action=UPDATE", headers=adm_headers)
    audit_items = audit_update_res.json()["items"]
    has_diff = any(
        i.get("old_value") and i.get("new_value") and i["old_value"].get("title") == "Select PostgreSQL Database"
        for i in audit_items
    )
    record_check(has_diff, "3.3 Audit record preserves old_value and new_value diffs")

    # =========================================================================
    # Step 4: Add Alternative -> Auto CREATE Audit Record
    # =========================================================================
    print("\n--- Step 4: Add Alternative (Swagger Step 4) ---")
    alt_res = client.post(f"/decisions/{dec_id}/alternatives", json={
        "name": "AWS Aurora PostgreSQL",
        "description": "Managed cloud PostgreSQL database",
        "pros": "High availability, auto-scaling storage",
        "cons": "Cloud vendor lock-in",
        "estimated_cost": 1500.0,
        "feasibility_score": 5,
        "risk_level": "Low"
    }, headers=emp_headers)
    record_check(alt_res.status_code == 201, "4.1 POST /decisions/{id}/alternatives creates Alternative (201 Created)")
    alt_id = alt_res.json()["id"]

    audit_alt_res = client.get(f"/audit-logs?entity_type=Alternative&entity_id={alt_id}", headers=adm_headers)
    record_check(audit_alt_res.status_code == 200 and audit_alt_res.json()["total"] >= 1, "4.2 Alternative creation generates CREATE audit record")

    # =========================================================================
    # Step 5: Add Comment -> Auto CREATE Audit Record
    # =========================================================================
    print("\n--- Step 5: Add Comment (Swagger Step 5) ---")
    comm_res = client.post(f"/decisions/{dec_id}/comments", json={
        "content": "Aurora read replicas tested with 10ms replication lag."
    }, headers=emp_headers)
    record_check(comm_res.status_code == 201, "5.1 POST /decisions/{id}/comments creates Comment (201 Created)")
    comm_id = comm_res.json()["id"]

    audit_comm_res = client.get(f"/audit-logs?entity_type=Comment&entity_id={comm_id}", headers=adm_headers)
    record_check(audit_comm_res.status_code == 200 and audit_comm_res.json()["total"] >= 1, "5.2 Comment creation generates CREATE audit record")

    # =========================================================================
    # Step 6: Submit Decision -> Auto SUBMIT Audit Record & Version 3
    # =========================================================================
    print("\n--- Step 6: Submit Decision (Swagger Step 6) ---")
    submit_res = client.post(f"/decisions/{dec_id}/submit", json={
        "reviewer_id": rev_id,
        "approval_level": 1,
        "comments": "Ready for initial architectural review"
    }, headers=emp_headers)
    record_check(submit_res.status_code == 201, "6.1 POST /decisions/{id}/submit submits Decision (201 Created)")
    approval_id = submit_res.json()["id"]

    # Check Version 3 created
    ver_submit_res = client.get(f"/decisions/{dec_id}/versions", headers=emp_headers)
    vers_after_submit = ver_submit_res.json()
    record_check(
        len(vers_after_submit) == 3 and vers_after_submit[2]["version_number"] == 3 and vers_after_submit[2]["status"] == "Under Review",
        "6.2 Version 3 created with 'Under Review' status"
    )

    # Check SUBMIT audit log
    audit_sub_res = client.get(f"/audit-logs?entity_type=Decision&entity_id={dec_id}&action=SUBMIT", headers=adm_headers)
    record_check(audit_sub_res.status_code == 200 and audit_sub_res.json()["total"] >= 1, "6.3 SUBMIT audit record generated")

    # =========================================================================
    # Step 7: Approve Decision -> Auto APPROVE Audit Record & Version 4
    # =========================================================================
    print("\n--- Step 7: Approve Decision (Swagger Step 7) ---")
    apprv_action_res = client.post(f"/approvals/{approval_id}/action", json={
        "status": "Approved",
        "comments": "Architecture is verified and compliant with enterprise standards."
    }, headers=rev_headers)
    record_check(apprv_action_res.status_code == 200 and apprv_action_res.json()["status"] == "Approved", "7.1 POST /approvals/{id}/action approves request (200 OK)")

    # Check Version 4 created
    ver_apprv_res = client.get(f"/decisions/{dec_id}/versions", headers=emp_headers)
    vers_after_apprv = ver_apprv_res.json()
    record_check(
        len(vers_after_apprv) == 4 and vers_after_apprv[3]["version_number"] == 4 and vers_after_apprv[3]["status"] == "Approved",
        "7.2 Version 4 created with 'Approved' status"
    )

    # Check APPROVE audit log
    audit_apprv_res = client.get(f"/audit-logs?entity_type=Approval&entity_id={approval_id}&action=APPROVE", headers=adm_headers)
    record_check(audit_apprv_res.status_code == 200 and audit_apprv_res.json()["total"] >= 1, "7.3 APPROVE audit record generated")

    # =========================================================================
    # Step 8: Check Decision History
    # =========================================================================
    print("\n--- Step 8: Check Decision History (Swagger Step 8) ---")
    hist_res = client.get(f"/decisions/{dec_id}/history", headers=emp_headers)
    record_check(
        hist_res.status_code == 200 and hist_res.json()["total_events"] >= 4,
        "8.1 GET /decisions/{id}/history returns chronological change history (200 OK)"
    )
    hist_events = hist_res.json()["history"]
    event_actions = [e["action"] for e in hist_events]
    record_check("CREATE" in event_actions and "UPDATE" in event_actions and "SUBMIT" in event_actions, "8.2 History contains complete lifecycle actions")

    # =========================================================================
    # Step 9: Check Versions List
    # =========================================================================
    print("\n--- Step 9: Check All Versions (Swagger Step 9) ---")
    all_vers_res = client.get(f"/decisions/{dec_id}/versions", headers=emp_headers)
    all_vers = all_vers_res.json()
    record_check(
        all_vers_res.status_code == 200 and len(all_vers) == 4,
        f"9.1 GET /decisions/{{id}}/versions returns all 4 sequential versions ({[v['version_number'] for v in all_vers]})"
    )

    # =========================================================================
    # Step 10: Get Specific Version
    # =========================================================================
    print("\n--- Step 10: Get Specific Version (Swagger Step 10) ---")
    v2_res = client.get(f"/decisions/{dec_id}/versions/2", headers=emp_headers)
    record_check(
        v2_res.status_code == 200 and v2_res.json()["version_number"] == 2 and v2_res.json()["title"] == "Select PostgreSQL 16 Database Cluster",
        "10.1 GET /decisions/{id}/versions/2 returns historical state of Version 2"
    )

    # =========================================================================
    # Step 11: Check Audit Logs as Admin with Pagination
    # =========================================================================
    print("\n--- Step 11: Check Audit Logs as Admin (Swagger Step 11) ---")
    audit_page_res = client.get("/audit-logs?page=1&page_size=10", headers=adm_headers)
    record_check(
        audit_page_res.status_code == 200 and "items" in audit_page_res.json() and audit_page_res.json()["page_size"] == 10,
        f"11.1 GET /audit-logs?page=1&page_size=10 returns paginated response (Total: {audit_page_res.json()['total']})"
    )

    # =========================================================================
    # Step 12: Test Unauthorized Access (Employee -> 403 Forbidden)
    # =========================================================================
    print("\n--- Step 12: Role-Based Authorization Checks (Swagger Step 12) ---")
    emp_audit_res = client.get("/audit-logs", headers=emp_headers)
    record_check(emp_audit_res.status_code == 403, "12.1 Employee accessing /audit-logs receives 403 Forbidden")

    emp_sec_res = client.get("/security-logs", headers=emp_headers)
    record_check(emp_sec_res.status_code == 403, "12.2 Employee accessing /security-logs receives 403 Forbidden")

    emp_acc_res = client.get("/access-logs", headers=emp_headers)
    record_check(emp_acc_res.status_code == 403, "12.3 Employee accessing /access-logs receives 403 Forbidden")

    # =========================================================================
    # Step 13: Test Without JWT (401 Unauthorized)
    # =========================================================================
    print("\n--- Step 13: Unauthenticated Access Checks (Swagger Step 13) ---")
    no_jwt_audit = client.get("/audit-logs")
    record_check(no_jwt_audit.status_code == 401, "13.1 GET /audit-logs without JWT receives 401 Unauthorized")

    no_jwt_sec = client.get("/security-logs")
    record_check(no_jwt_sec.status_code == 401, "13.2 GET /security-logs without JWT receives 401 Unauthorized")

    no_jwt_acc = client.get("/access-logs")
    record_check(no_jwt_acc.status_code == 401, "13.3 GET /access-logs without JWT receives 401 Unauthorized")

    # =========================================================================
    # Step 14: Security Logs Verification (Login Success & Failure)
    # =========================================================================
    print("\n--- Step 14: Security Logging Verification ---")
    # Trigger a failed login
    client.post("/auth/login", json={"email": "s11_nonexistent@example.com", "password": "SecretPassword123!"})

    sec_res = client.get("/security-logs", headers=adm_headers)
    record_check(sec_res.status_code == 200, "14.1 Admin GET /security-logs (200 OK)")
    sec_events = [s["event_type"] for s in sec_res.json()["items"]]
    record_check("LOGIN_SUCCESS" in sec_events and "LOGIN_FAILED" in sec_events, "14.2 Security log records both LOGIN_SUCCESS and LOGIN_FAILED")

    # Verify no credentials leaked
    clean_descriptions = all("SecretPassword123!" not in s["description"] and "Password123!" not in s["description"] for s in sec_res.json()["items"])
    record_check(clean_descriptions, "14.3 Sensitive passwords are NEVER stored in security logs")

    # =========================================================================
    # Step 15: Access Logs Verification
    # =========================================================================
    print("\n--- Step 15: Access Logging Verification ---")
    client.get(f"/decisions/{dec_id}", headers=emp_headers)
    acc_res = client.get("/access-logs", headers=adm_headers)
    record_check(acc_res.status_code == 200, "15.1 Admin GET /access-logs (200 OK)")
    acc_resources = [a["resource_type"] for a in acc_res.json()["items"]]
    record_check("Decision" in acc_resources and "AuditLog" in acc_resources, "15.2 Access log tracks Decision and AuditLog access events")

    # =========================================================================
    # Step 16: Validation & Error Handling (404, 422)
    # =========================================================================
    print("\n--- Step 16: Error Handling & Validations ---")
    # 404 Non-existing Decision
    record_check(client.get("/decisions/99999/versions", headers=emp_headers).status_code == 404, "16.1 Non-existing Decision -> 404 Not Found")
    record_check(client.get("/decisions/99999/history", headers=emp_headers).status_code == 404, "16.2 Non-existing Decision history -> 404 Not Found")

    # 404 Non-existing Version
    record_check(client.get(f"/decisions/{dec_id}/versions/999", headers=emp_headers).status_code == 404, "16.3 Non-existing Version -> 404 Not Found")

    # 422 Invalid Action Filter
    record_check(client.get("/audit-logs?action=HACK_SYSTEM", headers=adm_headers).status_code == 422, "16.4 Invalid action filter -> 422 Unprocessable Entity")

    # 422 Invalid Entity Type Filter
    record_check(client.get("/audit-logs?entity_type=UnknownTable", headers=adm_headers).status_code == 422, "16.5 Invalid entity_type filter -> 422 Unprocessable Entity")

    # 422 Invalid Date Range (start_date > end_date)
    record_check(client.get("/audit-logs?start_date=2026-12-31&end_date=2026-01-01", headers=adm_headers).status_code == 422, "16.6 start_date > end_date -> 422 Unprocessable Entity")

    # 422 Invalid Date Format
    record_check(client.get("/audit-logs?start_date=31-08-2026", headers=adm_headers).status_code == 422, "16.7 Invalid date format -> 422 Unprocessable Entity")

    # =========================================================================
    # Step 17: PostgreSQL Schema & Tables Inspection
    # =========================================================================
    print("\n--- Step 17: PostgreSQL Schema & Table Verification ---")
    insp = inspect(engine)
    db_tables = insp.get_table_names()
    required_tables = ["audit_logs", "decision_versions", "security_logs", "access_logs"]
    all_present = all(t in db_tables for t in required_tables)
    record_check(all_present, f"17.1 PostgreSQL audit tables verified: {', '.join(required_tables)}")

    # Verify audit_logs columns
    audit_cols = {c["name"] for c in insp.get_columns("audit_logs")}
    required_audit_cols = {"id", "user_id", "action", "entity_type", "entity_id", "description", "ip_address", "old_value", "new_value", "created_at"}
    record_check(required_audit_cols.issubset(audit_cols), f"17.2 audit_logs table columns verified: {', '.join(sorted(required_audit_cols))}")

    # Verify decision_versions columns
    ver_cols = {c["name"] for c in insp.get_columns("decision_versions")}
    required_ver_cols = {"id", "decision_id", "version_number", "title", "problem_statement", "status", "created_by", "created_at"}
    record_check(required_ver_cols.issubset(ver_cols), f"17.3 decision_versions table columns verified: {', '.join(sorted(required_ver_cols))}")

    # =========================================================================
    # Summary
    # =========================================================================
    print("\n" + "=" * 85)
    print(f" SPRINT 11 VERIFICATION SUMMARY: {passed_count}/{total_count} CHECKS PASSED ({(passed_count/total_count)*100:.1f}%)")
    print("=" * 85)

    if passed_count == total_count:
        print(" >>> SUCCESS: ALL SPRINT 11 AUDIT & COMPLIANCE CRITERIA MET! <<<\n")
        return 0
    else:
        print(" >>> FAILURE: SOME CHECKS FAILED <<<\n")
        return 1


if __name__ == "__main__":
    exit_code = run_sprint11_verification()
    sys.exit(exit_code)
