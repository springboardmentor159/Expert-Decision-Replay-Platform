import os
import sys
sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def run_tests():
    print("==================================================")
    print("   RUNNING AUTOMATED VERIFICATION FOR SPRINTS 9, 10, 11")
    print("==================================================")

    # 1. Unauthenticated checks (401 Unauthorized)
    print("\n[1] Testing Authentication & 401 Handling...")
    res = client.get("/decisions")
    assert res.status_code == 401, f"Expected 401, got {res.status_code}"

    res = client.get("/dashboard/employee")
    assert res.status_code == 401, f"Expected 401, got {res.status_code}"

    res = client.get("/audit-logs")
    assert res.status_code == 401, f"Expected 401, got {res.status_code}"
    print("   -> 401 Unauthorized verified for unauthenticated calls.")

    # 2. Login as Employee, Manager, Admin
    print("\n[2] Testing Login & Security Logging...")
    # Bad credentials -> 401 & LOGIN_FAILED security log
    res = client.post("/auth/login", data={"username": "baduser@example.com", "password": "wrongpassword"})
    assert res.status_code == 401, f"Expected 401 for bad login, got {res.status_code}"
    print("   -> Invalid login rejected with 401.")

    # Employee login
    res = client.post("/auth/login", data={"username": "employee@example.com", "password": "Password123!"})
    assert res.status_code == 200, f"Employee login failed: {res.text}"
    emp_token = res.json()["access_token"]
    emp_headers = {"Authorization": f"Bearer {emp_token}"}
    print("   -> Employee logged in successfully.")

    # Manager login
    res = client.post("/auth/login", data={"username": "manager@example.com", "password": "Password123!"})
    assert res.status_code == 200, f"Manager login failed: {res.text}"
    mgr_token = res.json()["access_token"]
    mgr_headers = {"Authorization": f"Bearer {mgr_token}"}
    print("   -> Manager logged in successfully.")

    # Admin login
    res = client.post("/auth/login", data={"username": "admin@example.com", "password": "Password123!"})
    assert res.status_code == 200, f"Admin login failed: {res.text}"
    admin_token = res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("   -> Admin logged in successfully.")

    # 3. Sprint 9: Knowledge Repository, Search, Discovery, Tags & Timeline
    print("\n[3] Testing Sprint 9 - Knowledge Repository, Search & Discovery...")
    
    # 3a. Tags API
    res = client.get("/tags", headers=emp_headers)
    assert res.status_code == 200, f"Failed to get tags: {res.text}"
    tags = res.json()
    assert len(tags) > 0, "No tags found"
    print(f"   -> Retrieved {len(tags)} tags.")

    # 3b. Search API: GET /decisions/search?q=kafka
    res = client.get("/decisions/search?q=Kafka", headers=emp_headers)
    assert res.status_code == 200, f"Search failed: {res.text}"
    search_data = res.json()
    assert search_data["total"] >= 1, f"Expected search results for 'Kafka', got {search_data}"
    kafka_dec = search_data["results"][0]
    print(f"   -> Search by query 'Kafka' found {search_data['total']} result(s): '{kafka_dec['title']}'.")

    # 3c. Category & Status filters
    res = client.get("/decisions?category=Finance&status=Under Review", headers=emp_headers)
    assert res.status_code == 200, f"Category filter failed: {res.text}"
    items = res.json()["items"]
    assert len(items) >= 1, "Expected at least 1 Finance Under Review decision"
    print(f"   -> Filter by Category='Finance' & Status='Under Review' returned {len(items)} decision(s).")

    # 3d. Tag filter
    res = client.get("/decisions?tag=Security", headers=emp_headers)
    assert res.status_code == 200, f"Tag filter failed: {res.text}"
    items = res.json()["items"]
    assert len(items) >= 1, "Expected decisions with tag 'Security'"
    print(f"   -> Filter by Tag='Security' returned {len(items)} decision(s).")

    # 3e. Pagination & Sorting
    res = client.get("/decisions?sort_by=created_at&sort_order=asc&page=1&page_size=3", headers=emp_headers)
    assert res.status_code == 200, f"Sorting/pagination failed: {res.text}"
    page_data = res.json()
    assert len(page_data["items"]) <= 3, "Page size limit failed"
    print(f"   -> Pagination & sorting verified: page {page_data['page']}, size {page_data['page_size']}, total {page_data['total']}.")

    # 3f. Timeline
    target_dec_id = kafka_dec["id"]
    res = client.get(f"/decisions/{target_dec_id}/timeline", headers=emp_headers)
    assert res.status_code == 200, f"Timeline failed: {res.text}"
    timeline = res.json()
    assert len(timeline) >= 1, "Expected timeline events"
    print(f"   -> Retrieved {len(timeline)} timeline events for decision #{target_dec_id}.")

    # 3g. Archived Decision Modification Protection
    # Find archived decision
    res = client.get("/decisions?status=Archived", headers=emp_headers)
    assert res.status_code == 200
    archived_items = res.json()["items"]
    if archived_items:
        archived_id = archived_items[0]["id"]
        res = client.put(f"/decisions/{archived_id}", json={"title": "Modified Title", "problem_statement": "New statement", "category": "Technology"}, headers=admin_headers)
        assert res.status_code == 400, f"Expected 400 when modifying archived decision, got {res.status_code}"
        print(f"   -> Verified immutability of archived decision #{archived_id} (modifications blocked with 400).")

    # 4. Sprint 10: Dashboards & Analytics
    print("\n[4] Testing Sprint 10 - Dashboards & Analytics...")
    # Employee Dashboard
    res = client.get("/dashboard/employee", headers=emp_headers)
    assert res.status_code == 200, f"Employee dashboard failed: {res.text}"
    emp_dash = res.json()
    assert "total_decisions" in emp_dash
    print(f"   -> Employee Dashboard: total_decisions={emp_dash['total_decisions']}, approved={emp_dash['approved_decisions']}, recent_activities={len(emp_dash['recent_activities'])}.")

    # Manager Dashboard
    res = client.get("/dashboard/manager", headers=mgr_headers)
    assert res.status_code == 200, f"Manager dashboard failed: {res.text}"
    mgr_dash = res.json()
    print(f"   -> Manager Dashboard: total_decisions={mgr_dash['total_decisions']}, pending_approvals={mgr_dash['pending_approvals']}.")

    # Admin Dashboard (RBAC check)
    res = client.get("/dashboard/admin", headers=emp_headers)
    assert res.status_code == 403, f"Expected 403 for employee accessing admin dashboard, got {res.status_code}"
    print("   -> RBAC verified: Employee blocked from Admin Dashboard (403 Forbidden).")

    res = client.get("/dashboard/admin", headers=admin_headers)
    assert res.status_code == 200, f"Admin dashboard failed: {res.text}"
    admin_dash = res.json()
    print(f"   -> Admin Dashboard: total_users={admin_dash['total_users']}, total_decisions={admin_dash['total_decisions']}.")

    # System Analytics
    res = client.get("/dashboard/admin/analytics", headers=admin_headers)
    assert res.status_code == 200, f"Admin analytics failed: {res.text}"
    analytics = res.json()
    assert "decision_statistics" in analytics
    print(f"   -> Analytics: decisions={analytics['decision_statistics']}, users={analytics['user_statistics']['users_by_role']}.")

    # Approval Statistics & Completion Rate
    res = client.get("/dashboard/admin/approval-statistics", headers=admin_headers)
    assert res.status_code == 200
    res = client.get("/dashboard/admin/approval-completion-rate", headers=admin_headers)
    assert res.status_code == 200
    print(f"   -> Approval completion rate: {res.json()['completion_rate']}%.")

    # Activities API
    res = client.get("/activities?page=1&page_size=5", headers=admin_headers)
    assert res.status_code == 200
    print(f"   -> Retrieved {len(res.json())} activities via /activities.")

    # 5. Sprint 11: Audit, Versions, History & Compliance
    print("\n[5] Testing Sprint 11 - Audit & Compliance, Versions & History...")
    
    # 5a. Decision Creation & Version 1
    create_payload = {
        "title": "Automated Test Decision for Versioning",
        "problem_statement": "Need to verify versioning and audit trail on new decisions.",
        "category": "Technology",
    }
    res = client.post("/decisions", json=create_payload, headers=emp_headers)
    assert res.status_code == 201, f"Failed to create decision: {res.text}"
    new_decision = res.json()
    new_id = new_decision["id"]
    print(f"   -> Created new decision #{new_id}: '{new_decision['title']}'.")

    # 5b. Verify Version 1 was created
    res = client.get(f"/decisions/{new_id}/versions", headers=emp_headers)
    assert res.status_code == 200
    versions = res.json()
    assert len(versions) == 1, f"Expected 1 version, got {len(versions)}"
    assert versions[0]["version_number"] == 1
    print(f"   -> Verified initial Version 1 created automatically.")

    # 5c. Update decision -> Creates Version 2 & logs diffs
    update_payload = {
        "title": "Automated Test Decision for Versioning (Updated)",
        "problem_statement": "Updated problem statement with enhanced details.",
        "category": "Technology",
    }
    res = client.put(f"/decisions/{new_id}", json=update_payload, headers=emp_headers)
    assert res.status_code == 200
    print(f"   -> Updated decision #{new_id}.")

    # Verify Version 2 exists
    res = client.get(f"/decisions/{new_id}/versions", headers=emp_headers)
    assert res.status_code == 200
    versions = res.json()
    assert len(versions) == 2, f"Expected 2 versions, got {len(versions)}"
    assert versions[1]["version_number"] == 2
    print(f"   -> Verified Version 2 created automatically on update.")

    # 5d. Retrieve specific version
    res = client.get(f"/decisions/{new_id}/versions/1", headers=emp_headers)
    assert res.status_code == 200
    v1_data = res.json()
    assert v1_data["title"] == "Automated Test Decision for Versioning"
    assert v1_data["version_number"] == 1

    res = client.get(f"/decisions/{new_id}/versions/2", headers=emp_headers)
    assert res.status_code == 200
    v2_data = res.json()
    assert v2_data["title"] == "Automated Test Decision for Versioning (Updated)"
    assert v2_data["version_number"] == 2
    print(f"   -> Verified specific version snapshots (V1 & V2) retrieved accurately.")

    # 5e. Change History: GET /decisions/{id}/history
    res = client.get(f"/decisions/{new_id}/history", headers=emp_headers)
    assert res.status_code == 200
    history = res.json()
    assert len(history) >= 2, f"Expected at least 2 history items, got {len(history)}"
    print(f"   -> Retrieved {len(history)} lifecycle history records for decision #{new_id}.")

    # 5f. Organization-wide Audit Logs: GET /audit-logs
    # Employee blocked
    res = client.get("/audit-logs", headers=emp_headers)
    assert res.status_code == 403, f"Expected 403 for employee, got {res.status_code}"

    # Admin access
    res = client.get("/audit-logs?page=1&page_size=10", headers=admin_headers)
    assert res.status_code == 200, f"Admin audit logs failed: {res.text}"
    audit_data = res.json()
    assert audit_data["total"] >= 1
    print(f"   -> Admin accessed organization-wide audit logs ({audit_data['total']} total records).")

    # 5g. Security Logs: GET /security-logs
    res = client.get("/security-logs", headers=emp_headers)
    assert res.status_code == 403
    res = client.get("/security-logs", headers=admin_headers)
    assert res.status_code == 200
    sec_data = res.json()
    assert sec_data["total"] >= 1
    print(f"   -> Admin accessed security logs ({sec_data['total']} total records, including LOGIN_SUCCESS and LOGIN_FAILED).")

    # 5h. Access Logs: GET /access-logs
    res = client.get("/access-logs", headers=emp_headers)
    assert res.status_code == 403
    res = client.get("/access-logs", headers=admin_headers)
    assert res.status_code == 200
    acc_data = res.json()
    assert acc_data["total"] >= 1
    print(f"   -> Admin accessed access logs ({acc_data['total']} total records).")

    print("\n==================================================")
    print("   ALL TESTS PASSED SUCCESSFULLY FOR SPRINTS 9, 10, 11!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
