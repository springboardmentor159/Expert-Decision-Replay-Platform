import sys
import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def run_comprehensive_endpoint_checks():
    print("=" * 80)
    print(" MASTER ENDPOINT AUDIT & VERIFICATION REPORT (ALL 49+ ENDPOINTS)")
    print("=" * 80)

    results = []

    def record(endpoint, method, description, status, passed, details=""):
        results.append({
            "endpoint": endpoint,
            "method": method,
            "description": description,
            "status": status,
            "passed": passed,
            "details": details
        })
        icon = "[PASS]" if passed else "[FAIL]"
        print(f"{icon} {method:<6} {endpoint:<38} -> Status {status:<3} | {description}")
        if not passed and details:
            print(f"       ERROR: {details}")

    # Helper function to create users
    def setup_user(email: str, role: str, dept: str = "Platform Engineering"):
        payload = {
            "full_name": email.split("@")[0].replace("_", " ").title(),
            "email": email,
            "role": role,
            "password": "Password123!",
            "employee_id": f"EMP_{email[:8]}",
            "department": dept,
            "designation": f"Senior {role}",
            "phone_number": "+1-555-0100"
        }
        client.post("/users", json=payload)
        login_res = client.post("/auth/login", json={"email": email, "password": "Password123!"})
        if login_res.status_code != 200:
            login_res = client.post("/auth/login", json={"email": email, "password": "Password123!"})
        token = login_res.json()["access_token"]
        uid = login_res.json()["user"]["id"]
        return token, uid

    # -------------------------------------------------------------
    # 1. DOCUMENTATION & OPENAPI (3 endpoints)
    # -------------------------------------------------------------
    print("\n--- 1. Documentation & OpenAPI Specifications ---")
    r = client.get("/docs")
    record("/docs", "GET", "Swagger UI interactive documentation", r.status_code, r.status_code == 200)

    r = client.get("/redoc")
    record("/redoc", "GET", "ReDoc alternative documentation", r.status_code, r.status_code == 200)

    r = client.get("/openapi.json")
    record("/openapi.json", "GET", f"OpenAPI JSON Schema ({len(r.json().get('paths', {}))} paths)", r.status_code, r.status_code == 200 and "paths" in r.json())

    # -------------------------------------------------------------
    # 2. USER AUTHENTICATION & MANAGEMENT (7 endpoints)
    # -------------------------------------------------------------
    print("\n--- 2. User Authentication & Directory ---")
    emp_token, emp_id = setup_user("master_emp@example.com", "Employee", "Core Platform")
    emp_h = {"Authorization": f"Bearer {emp_token}"}

    rev_token, rev_id = setup_user("master_rev@example.com", "Reviewer", "Core Platform")
    rev_h = {"Authorization": f"Bearer {rev_token}"}

    mgr_token, mgr_id = setup_user("master_mgr@example.com", "Manager", "Core Platform")
    mgr_h = {"Authorization": f"Bearer {mgr_token}"}

    adm_token, adm_id = setup_user("master_adm@example.com", "Administrator", "Executive")
    adm_h = {"Authorization": f"Bearer {adm_token}"}

    # POST /users
    r = client.post("/users", json={
        "full_name": "Temporary User",
        "email": "master_temp@example.com",
        "role": "Employee",
        "password": "Password123!",
        "employee_id": "EMP_TEMP_99"
    })
    temp_uid = r.json().get("id")
    record("/users", "POST", "Create user with profile metadata (201)", r.status_code, r.status_code in [201, 400])

    # POST /auth/login
    r = client.post("/auth/login", json={"email": "master_emp@example.com", "password": "Password123!"})
    record("/auth/login", "POST", "User login & JWT token generation (200)", r.status_code, r.status_code == 200 and "access_token" in r.json())

    # POST /users/login (alias)
    r = client.post("/users/login", json={"email": "master_emp@example.com", "password": "Password123!"})
    record("/users/login", "POST", "User login alias endpoint (200)", r.status_code, r.status_code == 200 and "access_token" in r.json())

    # GET /users/me
    r = client.get("/users/me", headers=emp_h)
    record("/users/me", "GET", "Fetch current authenticated user profile (200)", r.status_code, r.status_code == 200 and r.json().get("email") == "master_emp@example.com")

    # GET /users
    r = client.get("/users", headers=emp_h)
    record("/users", "GET", "List all users in directory (200)", r.status_code, r.status_code == 200 and isinstance(r.json(), list))

    # GET /users/{id}
    r = client.get(f"/users/{emp_id}", headers=emp_h)
    record(f"/users/{emp_id}", "GET", "Get specific user by ID (200)", r.status_code, r.status_code == 200 and r.json().get("id") == emp_id)

    # PUT /users/{id}
    r = client.put(f"/users/{emp_id}", json={"designation": "Staff Principal Engineer"}, headers=emp_h)
    record(f"/users/{emp_id}", "PUT", "Update user profile metadata (200)", r.status_code, r.status_code == 200)

    # -------------------------------------------------------------
    # 3. DECISION MANAGEMENT (8 endpoints)
    # -------------------------------------------------------------
    print("\n--- 3. Decision Management ---")
    # POST /decisions
    r = client.post("/decisions", json={
        "title": "Migrate Database to PostgreSQL 16",
        "problem_statement": "Need robust transactional scalability and JSON support",
        "category": "Technology"
    }, headers=emp_h)
    dec = r.json() if r.status_code == 201 else {}
    dec_id = dec.get("id")
    record("/decisions", "POST", "Create decision in Draft status (201)", r.status_code, r.status_code == 201)

    # GET /decisions
    r = client.get("/decisions", headers=emp_h)
    record("/decisions", "GET", "List decisions with optional filters (200)", r.status_code, r.status_code == 200 and isinstance(r.json(), list))

    # GET /decisions/search
    r = client.get("/decisions/search?q=PostgreSQL&category=Technology", headers=emp_h)
    record("/decisions/search", "GET", "Search decisions by query, category, tags (200)", r.status_code, r.status_code == 200 and "items" in r.json())

    # GET /decisions/{id}
    r = client.get(f"/decisions/{dec_id}", headers=emp_h)
    record(f"/decisions/{dec_id}", "GET", "Get single decision details (200)", r.status_code, r.status_code == 200 and r.json().get("id") == dec_id)

    # PUT /decisions/{id}
    r = client.put(f"/decisions/{dec_id}", json={
        "title": "Migrate Database to Aurora PostgreSQL 16",
        "problem_statement": "Need managed cloud PostgreSQL cluster",
        "category": "Technology"
    }, headers=emp_h)
    record(f"/decisions/{dec_id}", "PUT", "Update decision details (200)", r.status_code, r.status_code == 200)

    # PATCH /decisions/{id}/status
    r = client.patch(f"/decisions/{dec_id}/status", json={"status": "Under Review"}, headers=emp_h)
    record(f"/decisions/{dec_id}/status", "PATCH", "Update decision status (200)", r.status_code, r.status_code == 200)

    # PUT /decisions/{id}/rationale
    r = client.put(f"/decisions/{dec_id}/rationale", json={"rationale": "High IOPS throughput and zero downtime failover"}, headers=emp_h)
    record(f"/decisions/{dec_id}/rationale", "PUT", "Update decision rationale (200)", r.status_code, r.status_code == 200)

    # GET /decisions/{id}/rationale
    r = client.get(f"/decisions/{dec_id}/rationale", headers=emp_h)
    record(f"/decisions/{dec_id}/rationale", "GET", "Get decision rationale (200)", r.status_code, r.status_code == 200 and "rationale" in r.json())

    # -------------------------------------------------------------
    # 4. TAGS MANAGEMENT (6 endpoints)
    # -------------------------------------------------------------
    print("\n--- 4. Tags & Taxonomy ---")
    # POST /tags
    r = client.post("/tags", json={"name": "Database", "category": "Technology"}, headers=adm_h)
    tag_id = r.json().get("id") if r.status_code == 201 else 1
    record("/tags", "POST", "Create organization tag (201)", r.status_code, r.status_code in [201, 400])

    # GET /tags
    r = client.get("/tags", headers=emp_h)
    record("/tags", "GET", "List all organization tags (200)", r.status_code, r.status_code == 200)

    # GET /tags/{id}
    r = client.get(f"/tags/{tag_id}", headers=emp_h)
    record(f"/tags/{tag_id}", "GET", "Get tag by ID (200)", r.status_code, r.status_code == 200)

    # POST /decisions/{id}/tags
    r = client.post(f"/decisions/{dec_id}/tags", json={"tag_ids": [tag_id]}, headers=emp_h)
    record(f"/decisions/{dec_id}/tags", "POST", "Assign tags to a decision (200)", r.status_code, r.status_code == 200)

    # GET /decisions/{id}/tags
    r = client.get(f"/decisions/{dec_id}/tags", headers=emp_h)
    record(f"/decisions/{dec_id}/tags", "GET", "Get all tags assigned to decision (200)", r.status_code, r.status_code == 200)

    # DELETE /decisions/{id}/tags/{tag_id}
    r = client.delete(f"/decisions/{dec_id}/tags/{tag_id}", headers=emp_h)
    record(f"/decisions/{dec_id}/tags/{tag_id}", "DELETE", "Remove tag from decision (200)", r.status_code, r.status_code == 200)

    # -------------------------------------------------------------
    # 5. ALTERNATIVE ANALYSIS (6 endpoints)
    # -------------------------------------------------------------
    print("\n--- 5. Alternatives Analysis ---")
    # POST /decisions/{id}/alternatives
    r = client.post(f"/decisions/{dec_id}/alternatives", json={
        "name": "AWS Aurora Serverless v2",
        "description": "Auto-scaling PostgreSQL database",
        "pros": "Instant scaling",
        "cons": "Higher hourly baseline",
        "estimated_cost": 1200.0,
        "feasibility_score": 5,
        "risk_level": "Low"
    }, headers=emp_h)
    alt = r.json() if r.status_code == 201 else {}
    alt_id = alt.get("id")
    record(f"/decisions/{dec_id}/alternatives", "POST", "Create alternative for decision (201)", r.status_code, r.status_code == 201)

    # GET /decisions/{id}/alternatives
    r = client.get(f"/decisions/{dec_id}/alternatives", headers=emp_h)
    record(f"/decisions/{dec_id}/alternatives", "GET", "Get all alternatives for decision (200)", r.status_code, r.status_code == 200)

    # GET /decisions/{id}/alternatives/compare
    r = client.get(f"/decisions/{dec_id}/alternatives/compare", headers=emp_h)
    record(f"/decisions/{dec_id}/alternatives/compare", "GET", "Compare alternatives matrix (200)", r.status_code, r.status_code == 200 and "alternatives" in r.json())

    # GET /alternatives/{id}
    r = client.get(f"/alternatives/{alt_id}", headers=emp_h)
    record(f"/alternatives/{alt_id}", "GET", "Get alternative by ID (200)", r.status_code, r.status_code == 200)

    # PUT /alternatives/{id}
    r = client.put(f"/alternatives/{alt_id}", json={"estimated_cost": 1100.0}, headers=emp_h)
    record(f"/alternatives/{alt_id}", "PUT", "Update alternative metrics (200)", r.status_code, r.status_code == 200)

    # DELETE /alternatives/{id} (Tested later or on separate alternative)
    alt2_res = client.post(f"/decisions/{dec_id}/alternatives", json={
        "name": "Self-Hosted EC2 PostgreSQL",
        "description": "Manual EC2 setup",
        "pros": "Cheaper",
        "cons": "Maintenance burden",
        "estimated_cost": 400.0,
        "feasibility_score": 3,
        "risk_level": "High"
    }, headers=emp_h)
    alt2_id = alt2_res.json().get("id")
    r = client.delete(f"/alternatives/{alt2_id}", headers=emp_h)
    record(f"/alternatives/{alt2_id}", "DELETE", "Delete an alternative (200)", r.status_code, r.status_code == 200)

    # -------------------------------------------------------------
    # 6. COLLABORATION (COMMENTS, THREADS, NOTES) (11 endpoints)
    # -------------------------------------------------------------
    print("\n--- 6. Collaboration: Comments, Threads & Notes ---")
    # POST /decisions/{id}/comments
    r = client.post(f"/decisions/{dec_id}/comments", json={"content": "Latency benchmarks approved in staging."}, headers=emp_h)
    comm = r.json() if r.status_code == 201 else {}
    comm_id = comm.get("id")
    record(f"/decisions/{dec_id}/comments", "POST", "Add comment to decision (201)", r.status_code, r.status_code == 201)

    # GET /decisions/{id}/comments
    r = client.get(f"/decisions/{dec_id}/comments", headers=emp_h)
    record(f"/decisions/{dec_id}/comments", "GET", "Get all comments for decision (200)", r.status_code, r.status_code == 200)

    # GET /comments/{id}
    r = client.get(f"/comments/{comm_id}", headers=emp_h)
    record(f"/comments/{comm_id}", "GET", "Get comment by ID (200)", r.status_code, r.status_code == 200)

    # PUT /comments/{id}
    r = client.put(f"/comments/{comm_id}", json={"content": "Latency benchmarks verified with 5ms p99."}, headers=emp_h)
    record(f"/comments/{comm_id}", "PUT", "Update comment content (200)", r.status_code, r.status_code == 200)

    # POST /decisions/{id}/threads
    r = client.post(f"/decisions/{dec_id}/threads", json={"title": "Replication Strategy", "description": "Multi-AZ discussion"}, headers=emp_h)
    thread = r.json() if r.status_code == 201 else {}
    thread_id = thread.get("id")
    record(f"/decisions/{dec_id}/threads", "POST", "Create discussion thread (201)", r.status_code, r.status_code == 201)

    # GET /decisions/{id}/threads
    r = client.get(f"/decisions/{dec_id}/threads", headers=emp_h)
    record(f"/decisions/{dec_id}/threads", "GET", "Get all discussion threads for decision (200)", r.status_code, r.status_code == 200)

    # GET /threads/{id}
    r = client.get(f"/threads/{thread_id}", headers=emp_h)
    record(f"/threads/{thread_id}", "GET", "Get thread by ID with replies (200)", r.status_code, r.status_code == 200)

    # PUT /threads/{id}
    r = client.put(f"/threads/{thread_id}", json={"title": "Multi-Region Replication Strategy"}, headers=emp_h)
    record(f"/threads/{thread_id}", "PUT", "Update discussion thread (200)", r.status_code, r.status_code == 200)

    # POST /threads/{id}/comments
    r = client.post(f"/threads/{thread_id}/comments", json={"content": "Agree with cross-region replica."}, headers=emp_h)
    record(f"/threads/{thread_id}/comments", "POST", "Reply to discussion thread (201)", r.status_code, r.status_code == 201)

    # GET /threads/{id}/comments
    r = client.get(f"/threads/{thread_id}/comments", headers=emp_h)
    record(f"/threads/{thread_id}/comments", "GET", "Get all replies in thread (200)", r.status_code, r.status_code == 200)

    # POST /decisions/{id}/meeting-notes
    r = client.post(f"/decisions/{dec_id}/meeting-notes", json={"title": "Architecture Sync", "content": "Reviewed budget and timelines"}, headers=emp_h)
    mn_id = r.json().get("id")
    record(f"/decisions/{dec_id}/meeting-notes", "POST", "Record meeting note for decision (201)", r.status_code, r.status_code == 201)

    # GET /decisions/{id}/meeting-notes
    r = client.get(f"/decisions/{dec_id}/meeting-notes", headers=emp_h)
    record(f"/decisions/{dec_id}/meeting-notes", "GET", "Get meeting notes for decision (200)", r.status_code, r.status_code == 200)

    # GET /meeting-notes/{id}
    r = client.get(f"/meeting-notes/{mn_id}", headers=emp_h)
    record(f"/meeting-notes/{mn_id}", "GET", "Get meeting note by ID (200)", r.status_code, r.status_code == 200)

    # PUT /meeting-notes/{id}
    r = client.put(f"/meeting-notes/{mn_id}", json={"title": "Architecture & Compliance Sync"}, headers=emp_h)
    record(f"/meeting-notes/{mn_id}", "PUT", "Update meeting note (200)", r.status_code, r.status_code == 200)

    # -------------------------------------------------------------
    # 7. APPROVAL WORKFLOW (5 endpoints)
    # -------------------------------------------------------------
    print("\n--- 7. Approvals Workflow ---")
    # POST /decisions/{id}/submit
    r = client.post(f"/decisions/{dec_id}/submit", json={"reviewer_id": rev_id, "approval_level": 1, "comments": "Submitted for approval"}, headers=emp_h)
    apprv = r.json() if r.status_code == 201 else {}
    apprv_id = apprv.get("id")
    record(f"/decisions/{dec_id}/submit", "POST", "Submit decision for review (201)", r.status_code, r.status_code == 201)

    # POST /approvals (direct create)
    dec2_res = client.post("/decisions", json={"title": "Decision 2", "problem_statement": "P2", "category": "Finance"}, headers=emp_h)
    dec2_id = dec2_res.json().get("id")
    r = client.post("/approvals", json={"decision_id": dec2_id, "reviewer_id": rev_id, "approval_level": 1, "comments": "Direct approval request"}, headers=emp_h)
    record("/approvals", "POST", "Direct create approval request (201)", r.status_code, r.status_code == 201)

    # POST /approvals/{id}/action
    r = client.post(f"/approvals/{apprv_id}/action", json={"status": "Approved", "comments": "Compliance check passed"}, headers=rev_h)
    record(f"/approvals/{apprv_id}/action", "POST", "Approve or Reject review task (200)", r.status_code, r.status_code == 200)

    # GET /approvals
    r = client.get("/approvals", headers=emp_h)
    record("/approvals", "GET", "List all approvals with filters (200)", r.status_code, r.status_code == 200)

    # GET /decisions/{id}/approvals
    r = client.get(f"/decisions/{dec_id}/approvals", headers=emp_h)
    record(f"/decisions/{dec_id}/approvals", "GET", "Get approvals for decision (200)", r.status_code, r.status_code == 200)

    # -------------------------------------------------------------
    # 8. DASHBOARDS & ANALYTICS (11 endpoints)
    # -------------------------------------------------------------
    print("\n--- 8. Dashboards & System Analytics ---")
    r = client.get("/dashboard/employee", headers=emp_h)
    record("/dashboard/employee", "GET", "Employee dashboard overview (200)", r.status_code, r.status_code == 200 and "total_decisions" in r.json())

    r = client.get("/dashboard/employee/recent-activities", headers=emp_h)
    record("/dashboard/employee/recent-activities", "GET", "Employee recent activities feed (200)", r.status_code, r.status_code == 200 and isinstance(r.json(), list))

    r = client.get("/dashboard/manager", headers=mgr_h)
    record("/dashboard/manager", "GET", "Manager dashboard overview (200)", r.status_code, r.status_code == 200 and "team_decisions" in r.json())

    r = client.get("/dashboard/manager/team-decisions", headers=mgr_h)
    record("/dashboard/manager/team-decisions", "GET", "Manager team decisions list (200)", r.status_code, r.status_code == 200)

    r = client.get("/dashboard/manager/pending-approvals", headers=mgr_h)
    record("/dashboard/manager/pending-approvals", "GET", "Manager pending review queue (200)", r.status_code, r.status_code == 200)

    r = client.get("/dashboard/manager/statistics", headers=mgr_h)
    record("/dashboard/manager/statistics", "GET", "Manager aggregated statistics (200)", r.status_code, r.status_code == 200)

    r = client.get("/dashboard/admin", headers=adm_h)
    record("/dashboard/admin", "GET", "Admin executive dashboard (200)", r.status_code, r.status_code == 200 and "total_users" in r.json())

    r = client.get("/dashboard/admin/analytics", headers=adm_h)
    record("/dashboard/admin/analytics", "GET", "Admin full platform analytics (200)", r.status_code, r.status_code == 200)

    r = client.get("/dashboard/admin/decision-activity", headers=adm_h)
    record("/dashboard/admin/decision-activity", "GET", "Admin decision creation trends (200)", r.status_code, r.status_code == 200 and isinstance(r.json(), dict))

    r = client.get("/dashboard/admin/approval-statistics", headers=adm_h)
    record("/dashboard/admin/approval-statistics", "GET", "Admin approval performance metrics (200)", r.status_code, r.status_code == 200)

    r = client.get("/dashboard/admin/user-activity", headers=adm_h)
    record("/dashboard/admin/user-activity", "GET", "Admin user activity breakdown (200)", r.status_code, r.status_code == 200)

    # -------------------------------------------------------------
    # 9. ACTIVITY LOGS (1 endpoint)
    # -------------------------------------------------------------
    print("\n--- 9. Activity Logs ---")
    r = client.get("/activities?page=1&page_size=10", headers=adm_h)
    record("/activities", "GET", "List system activity logs (200)", r.status_code, r.status_code == 200 and "items" in r.json())

    # -------------------------------------------------------------
    # 10. SPRINT 11: AUDIT & COMPLIANCE (7 endpoints)
    # -------------------------------------------------------------
    print("\n--- 10. Sprint 11: Audit, Versioning & Compliance ---")
    # GET /decisions/{id}/versions
    r = client.get(f"/decisions/{dec_id}/versions", headers=emp_h)
    record(f"/decisions/{dec_id}/versions", "GET", "Get all historical versions of decision (200)", r.status_code, r.status_code == 200 and len(r.json()) >= 1)

    # GET /decisions/{id}/versions/{version_number}
    r = client.get(f"/decisions/{dec_id}/versions/1", headers=emp_h)
    record(f"/decisions/{dec_id}/versions/1", "GET", "Get specific historical version snapshot (200)", r.status_code, r.status_code == 200 and r.json().get("version_number") == 1)

    # GET /decisions/{id}/history
    r = client.get(f"/decisions/{dec_id}/history", headers=emp_h)
    record(f"/decisions/{dec_id}/history", "GET", "Get decision chronological change history (200)", r.status_code, r.status_code == 200 and "history" in r.json())

    # GET /decisions/{id}/timeline
    r = client.get(f"/decisions/{dec_id}/timeline", headers=emp_h)
    record(f"/decisions/{dec_id}/timeline", "GET", "Get decision timeline of events (200)", r.status_code, r.status_code == 200 and "events" in r.json())

    # GET /audit-logs
    r = client.get("/audit-logs?page=1&page_size=20", headers=adm_h)
    record("/audit-logs", "GET", "Administrator audit logs with multi-filters (200)", r.status_code, r.status_code == 200 and "items" in r.json())

    # GET /security-logs
    r = client.get("/security-logs?page=1&page_size=20", headers=adm_h)
    record("/security-logs", "GET", "Administrator security logs (200)", r.status_code, r.status_code == 200 and "items" in r.json())

    # GET /access-logs
    r = client.get("/access-logs?page=1&page_size=20", headers=adm_h)
    record("/access-logs", "GET", "Administrator resource access logs (200)", r.status_code, r.status_code == 200 and "items" in r.json())

    # -------------------------------------------------------------
    # 11. CLEANUP & DELETIONS
    # -------------------------------------------------------------
    print("\n--- 11. Resource Deletions ---")
    r = client.delete(f"/comments/{comm_id}", headers=emp_h)
    record(f"/comments/{comm_id}", "DELETE", "Delete comment (200)", r.status_code, r.status_code == 200)

    r = client.delete(f"/threads/{thread_id}", headers=emp_h)
    record(f"/threads/{thread_id}", "DELETE", "Delete discussion thread (200)", r.status_code, r.status_code == 200)

    r = client.delete(f"/meeting-notes/{mn_id}", headers=emp_h)
    record(f"/meeting-notes/{mn_id}", "DELETE", "Delete meeting note (200)", r.status_code, r.status_code == 200)

    r = client.delete(f"/tags/{tag_id}", headers=adm_h)
    record(f"/tags/{tag_id}", "DELETE", "Delete organization tag (200)", r.status_code, r.status_code == 200)

    if temp_uid:
        r = client.delete(f"/users/{temp_uid}", headers=adm_h)
        record(f"/users/{temp_uid}", "DELETE", "Delete user by ID (200)", r.status_code, r.status_code == 200)

    # -------------------------------------------------------------
    # FINAL SUMMARY
    # -------------------------------------------------------------
    total = len(results)
    passed_cnt = sum(1 for r in results if r["passed"])
    failed_cnt = total - passed_cnt

    print("\n" + "=" * 80)
    print(f" TOTAL ENDPOINTS TESTED: {total}")
    print(f" PASSED: {passed_cnt}")
    print(f" FAILED: {failed_cnt}")
    print(f" SUCCESS RATE: {(passed_cnt / total) * 100:.1f}%")
    print("=" * 80)

    if failed_cnt > 0:
        print("\nFailed test details:")
        for r in results:
            if not r["passed"]:
                print(f"- {r['method']} {r['endpoint']}: {r['description']} (Status {r['status']})")
        return 1
    else:
        print("\n>>> ALL ENDPOINTS ARE FULLY OPERATIONAL AND WORKING PROPERLY! <<<\n")
        return 0

if __name__ == "__main__":
    code = run_comprehensive_endpoint_checks()
    sys.exit(code)
