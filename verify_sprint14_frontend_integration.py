"""
Sprint 14 End-to-End Frontend API Integration Verification Script.
Validates that all APIs called by the frontend work smoothly and return expected schemas.
"""
import sys
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import SessionLocal
from app.models.user import User

client = TestClient(app)

def test_sprint14_complete_flow():
    print("=== [SPRINT 14] Starting End-to-End Verification ===")

    # 1. User Registration
    emp_email = "e2e_emp_14@example.com"
    rev_email = "e2e_rev_14@example.com"
    mgr_email = "e2e_mgr_14@example.com"
    adm_email = "e2e_adm_14@example.com"

    roles_to_register = [
        (emp_email, "Employee", "Engineering", "Software Engineer"),
        (rev_email, "Reviewer", "Engineering", "Principal Engineer"),
        (mgr_email, "Manager", "Engineering", "Engineering Director"),
        (adm_email, "Administrator", "Executive", "Admin Officer"),
    ]

    for email, role, dept, title in roles_to_register:
        res = client.post("/users", json={
            "full_name": f"Test {role}",
            "email": email,
            "password": "Password123!",
            "role": role,
            "department": dept,
            "designation": title
        })
        if res.status_code == 400 and "already registered" in res.json().get("detail", ""):
            pass  # Already created
        else:
            assert res.status_code == 201, f"Registration failed for {email}: {res.text}"
    print("[PASS] Step 1: User Registration validated.")

    # 2. Login & JWT Token Retrieval for all roles
    tokens = {}
    for email, role, _, _ in roles_to_register:
        login_res = client.post("/auth/login", json={
            "email": email,
            "password": "Password123!"
        })
        assert login_res.status_code == 200, f"Login failed for {email}: {login_res.text}"
        data = login_res.json()
        assert "access_token" in data
        assert data["user"]["role"] == role
        tokens[role] = data["access_token"]
    print("[PASS] Step 2: Login & JWT Token issuance validated.")

    # Headers helper
    def auth_header(role):
        return {"Authorization": f"Bearer {tokens[role]}"}

    # 3. Role-Based Dashboards
    emp_dash = client.get("/dashboard/employee", headers=auth_header("Employee"))
    assert emp_dash.status_code == 200, f"Employee dashboard failed: {emp_dash.text}"

    rev_dash = client.get("/dashboard/reviewer", headers=auth_header("Reviewer"))
    assert rev_dash.status_code == 200, f"Reviewer dashboard failed: {rev_dash.text}"

    mgr_dash = client.get("/dashboard/manager", headers=auth_header("Manager"))
    assert mgr_dash.status_code == 200, f"Manager dashboard failed: {mgr_dash.text}"

    adm_dash = client.get("/dashboard/admin", headers=auth_header("Administrator"))
    assert adm_dash.status_code == 200, f"Admin dashboard failed: {adm_dash.text}"
    print("[PASS] Step 3: Role-based dashboards validated.")

    # 4. Create Decision
    create_res = client.post("/decisions", headers=auth_header("Employee"), json={
        "title": "Adopt Event-Driven Architecture with EventBridge",
        "category": "Architecture",
        "problem_statement": "The existing monolithic event bus experiences high latency during traffic spikes and lacks cross-region failover."
    })
    assert create_res.status_code == 201, f"Decision creation failed: {create_res.text}"
    decision = create_res.json()
    decision_id = decision["id"]
    assert decision["status"] == "Draft"
    print(f"[PASS] Step 4: Decision created (#{decision_id}).")

    # 5. Update Rationale and Tags
    rat_res = client.put(f"/decisions/{decision_id}/rationale", headers=auth_header("Employee"), json={
        "rationale": "EventBridge provides serverless scaling and native SaaS integrations."
    })
    assert rat_res.status_code == 200

    # Ensure tag exists
    tag_create = client.post("/tags", headers=auth_header("Employee"), json={"name": "CloudEvents"})
    if tag_create.status_code == 201:
        tag_id = tag_create.json()["id"]
    else:
        tags_list = client.get("/tags", headers=auth_header("Employee")).json()
        tag_id = next(t["id"] for t in tags_list if t["name"] == "CloudEvents")

    tag_res = client.post(f"/decisions/{decision_id}/tags", headers=auth_header("Employee"), json={
        "tag_ids": [tag_id]
    })
    assert tag_res.status_code == 200
    print("[PASS] Step 5: Decision rationale and tags updated.")

    # 6. Add Alternatives
    alt1_res = client.post(f"/decisions/{decision_id}/alternatives", headers=auth_header("Employee"), json={
        "name": "AWS EventBridge",
        "description": "Fully managed serverless event bus with schema registry",
        "pros": "Zero server management, seamless AWS integration",
        "cons": "Vendor lock-in, latency p99 higher than self-hosted Kafka",
        "estimated_cost": 4500.0,
        "feasibility_score": 4,
        "risk_level": "Low"
    })
    assert alt1_res.status_code == 201, f"Alt1 failed: {alt1_res.text}"

    alt2_res = client.post(f"/decisions/{decision_id}/alternatives", headers=auth_header("Employee"), json={
        "name": "Self-Hosted Apache Kafka",
        "description": "Clustered Kafka deployed on Kubernetes with Strimzi operator",
        "pros": "Sub-millisecond latency, open source",
        "cons": "Operational overhead, ZooKeeper/KRaft cluster maintenance",
        "estimated_cost": 12000.0,
        "feasibility_score": 3,
        "risk_level": "Medium"
    })
    assert alt2_res.status_code == 201, f"Alt2 failed: {alt2_res.text}"
    print("[PASS] Step 6: Alternatives added.")

    # 7. Compare Alternatives
    cmp_res = client.get(f"/decisions/{decision_id}/alternatives/compare", headers=auth_header("Employee"))
    assert cmp_res.status_code == 200
    cmp_data = cmp_res.json()
    assert len(cmp_data["alternatives"]) >= 2
    print("[PASS] Step 7: Alternatives compared successfully.")

    # 8. Start Discussion & Post Comment
    thread_res = client.post(f"/decisions/{decision_id}/threads", headers=auth_header("Employee"), json={
        "title": "Throughput Benchmarking",
        "description": "Has anyone run throughput benchmarks on EventBridge in our test account?"
    })
    assert thread_res.status_code == 201

    comment_res = client.post(f"/decisions/{decision_id}/comments", headers=auth_header("Reviewer"), json={
        "content": "Looking at the cost estimates, EventBridge offers lower initial TCO."
    })
    assert comment_res.status_code == 201
    print("[PASS] Step 8: Discussions and comments verified.")

    # 9. Submit Decision for Review
    # Get reviewer user id
    login_rev = client.post("/auth/login", json={"email": rev_email, "password": "Password123!"})
    rev_user_id = login_rev.json()["user"]["id"]

    submit_res = client.post("/approvals", headers=auth_header("Employee"), json={
        "decision_id": decision_id,
        "reviewer_id": rev_user_id,
        "approval_level": 1,
        "comments": "Please review EventBridge adoption proposal"
    })
    assert submit_res.status_code == 201, f"Submission failed: {submit_res.text}"
    approval = submit_res.json()
    approval_id = approval["id"]

    # Check status is now Under Review
    dec_check = client.get(f"/decisions/{decision_id}", headers=auth_header("Employee")).json()
    assert dec_check["status"] == "Under Review"
    print(f"[PASS] Step 9: Decision submitted for review (#{approval_id}), status is Under Review.")

    # 10. Reviewer Approves Decision
    approve_res = client.post(f"/approvals/{approval_id}/approve", headers=auth_header("Reviewer"), json={
        "comments": "Approved based on favorable TCO and automated failover capabilities."
    })
    assert approve_res.status_code == 200, f"Approve failed: {approve_res.text}"
    print("[PASS] Step 10: Reviewer approved the decision.")

    # 11. Decision Status is now Approved
    final_dec = client.get(f"/decisions/{decision_id}", headers=auth_header("Employee")).json()
    assert final_dec["status"] == "Approved"
    print("[PASS] Step 11: Final decision status verified as Approved.")

    # 12. Version History and Timeline
    versions_res = client.get(f"/decisions/{decision_id}/versions", headers=auth_header("Employee"))
    assert versions_res.status_code == 200
    assert len(versions_res.json()) >= 2

    timeline_res = client.get(f"/decisions/{decision_id}/timeline", headers=auth_header("Employee"))
    assert timeline_res.status_code == 200
    assert len(timeline_res.json()["events"]) >= 2
    print("[PASS] Step 12: Sequential versions and event timeline verified.")

    # 13. Search in Knowledge Repository
    search_res = client.get("/decisions/search", headers=auth_header("Employee"), params={
        "q": "EventBridge"
    })
    assert search_res.status_code == 200
    assert search_res.json()["total"] >= 1
    print("[PASS] Step 13: Knowledge repository full-text search verified.")

    # 14. Reports Generation
    rep_res = client.get("/reports/decisions", headers=auth_header("Manager"), params={
        "status": "Approved"
    })
    assert rep_res.status_code == 200
    assert rep_res.json()["total"] >= 1
    print("[PASS] Step 14: Report generation verified.")

    # 15. PDF and Excel Exports
    pdf_res = client.get("/reports/decisions/export/pdf", headers=auth_header("Manager"))
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert len(pdf_res.content) > 100

    excel_res = client.get("/reports/decisions/export/excel", headers=auth_header("Manager"))
    assert excel_res.status_code == 200
    assert "openxmlformats" in excel_res.headers["content-type"]
    assert len(excel_res.content) > 100
    print("[PASS] Step 15: PDF and Excel binary report exports verified.")

    # 16. RBAC Verification (Employee cannot access audit logs)
    audit_forbidden = client.get("/audit-logs", headers=auth_header("Employee"))
    assert audit_forbidden.status_code == 403, f"Expected 403 for employee, got {audit_forbidden.status_code}"

    audit_allowed = client.get("/audit-logs", headers=auth_header("Administrator"))
    assert audit_allowed.status_code == 200, f"Expected 200 for admin, got {audit_allowed.status_code}"
    print("[PASS] Step 16: RBAC restriction verified (403 for Employee, 200 for Admin).")

    print("=== [SPRINT 14] ALL FRONTEND & BACKEND INTEGRATION TESTS PASSED! ===")

if __name__ == "__main__":
    test_sprint14_complete_flow()
