import sys
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def run_sprint10_verification():
    print("=" * 80)
    print(" SPRINT 10: DASHBOARD, ACTIVITY TRACKING & ANALYTICS VERIFICATION")
    print("=" * 80)

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

    # Register & Login Helper
    def setup_user(email: str, role: str, department: str = "Platform Engineering"):
        u_data = {
            "full_name": email.split("@")[0].replace("_", " ").title(),
            "email": email,
            "role": role,
            "password": "Password123!",
            "employee_id": f"EMP_S10_{email[:6]}",
            "department": department,
            "designation": f"Senior {role}",
            "phone_number": "+1-555-1000"
        }
        client.post("/users", json=u_data)
        login_res = client.post("/auth/login", json={"email": email, "password": "Password123!"})
        assert login_res.status_code == 200
        return login_res.json()["access_token"], login_res.json()["user"]["id"]

    # Step 1 – Setup Users for Employee, Manager, Admin
    print("\n--- Step 1: User Roles Setup & JWT Acquisition ---")
    emp_token, emp_id = setup_user("s10_employee@example.com", "Employee", "Platform Engineering")
    emp_headers = {"Authorization": f"Bearer {emp_token}"}
    record_check(bool(emp_token), "1.1 Login as Employee & Acquire JWT Token (200 OK)")

    mgr_token, mgr_id = setup_user("s10_manager@example.com", "Manager", "Platform Engineering")
    mgr_headers = {"Authorization": f"Bearer {mgr_token}"}
    record_check(bool(mgr_token), "1.2 Login as Manager & Acquire JWT Token (200 OK)")

    adm_token, adm_id = setup_user("s10_admin@example.com", "Administrator", "Executive")
    adm_headers = {"Authorization": f"Bearer {adm_token}"}
    record_check(bool(adm_token), "1.3 Login as Admin & Acquire JWT Token (200 OK)")

    # Step 2 – Employee Dashboard Initial State
    print("\n--- Step 2: Employee Dashboard Initial Check ---")
    res_emp_dash_init = client.get("/dashboard/employee", headers=emp_headers)
    record_check(
        res_emp_dash_init.status_code == 200 and "total_decisions" in res_emp_dash_init.json(),
        "2.1 GET /dashboard/employee returns Employee Overview (200 OK)"
    )
    init_emp_total = res_emp_dash_init.json()["total_decisions"]

    # Step 3 – Create a Decision & Check Dashboard Count Update
    print("\n--- Step 3: Create Decision & Verify Metric Update ---")
    dec_res = client.post("/decisions", json={
        "title": "Migrate In-Memory Cache to Redis Cluster",
        "problem_statement": "Need distributed Redis cluster to support microservices cache layer",
        "category": "Technology"
    }, headers=emp_headers)
    record_check(dec_res.status_code == 201, "3.1 Create Decision by Employee (201 Created)")
    dec_id = dec_res.json()["id"]

    res_emp_dash_after = client.get("/dashboard/employee", headers=emp_headers)
    new_emp_total = res_emp_dash_after.json()["total_decisions"]
    record_check(new_emp_total == init_emp_total + 1, f"3.2 Employee total_decisions incremented ({init_emp_total} -> {new_emp_total})")

    # Step 4 – Add Alternative & Check Activity Log
    print("\n--- Step 4: Add Alternatives & Automatic Activity Logging ---")
    alt_res = client.post(f"/decisions/{dec_id}/alternatives", json={
        "name": "AWS ElastiCache Redis",
        "description": "Managed multi-AZ Redis",
        "pros": "Fully managed, automatic failover",
        "cons": "Higher hourly compute cost",
        "estimated_cost": 800.0,
        "feasibility_score": 5,
        "risk_level": "Low"
    }, headers=emp_headers)
    record_check(alt_res.status_code == 201, "4.1 Create Alternative for Decision (201 Created)")

    # Step 5 – Add Comment & Recent Activities
    print("\n--- Step 5: Add Comment & Verify Recent Activities ---")
    com_res = client.post(f"/decisions/{dec_id}/comments", json={"content": "ElastiCache latency benchmarks tested in staging."}, headers=emp_headers)
    record_check(com_res.status_code == 201, "5.1 Add Comment on Decision (201 Created)")

    emp_acts_res = client.get("/dashboard/employee/recent-activities", headers=emp_headers)
    emp_acts = emp_acts_res.json()
    record_check(
        emp_acts_res.status_code == 200 and len(emp_acts) >= 2,
        f"5.2 GET /dashboard/employee/recent-activities returns latest {len(emp_acts)} activities in chronological order"
    )

    # Step 6 – Submit Decision for Approval
    print("\n--- Step 6: Submit Decision for Review ---")
    submit_res = client.post(
        f"/decisions/{dec_id}/submit",
        json={"decision_id": dec_id, "reviewer_id": mgr_id, "comments": "Ready for manager review"},
        headers=emp_headers
    )
    record_check(submit_res.status_code == 201, "6.1 Submit Decision for Review to Manager (201 Created)")
    apprv_id = submit_res.json()["id"]

    dec_under_review = client.get(f"/decisions/{dec_id}", headers=emp_headers).json()
    record_check(dec_under_review["status"] == "Under Review", "6.2 Decision status successfully transitioned to 'Under Review'")

    # Step 7 – Manager Pending Approvals
    print("\n--- Step 7: Manager Reviews Pending Approvals ---")
    mgr_pending_res = client.get("/dashboard/manager/pending-approvals", headers=mgr_headers)
    mgr_pending = mgr_pending_res.json()
    record_check(
        mgr_pending_res.status_code == 200 and any(a["id"] == apprv_id for a in mgr_pending),
        f"7.1 GET /dashboard/manager/pending-approvals contains submission task (Total: {len(mgr_pending)}) (200 OK)"
    )

    # Step 8 – Process Approval Action & Completion Rate / Turnaround Time
    print("\n--- Step 8: Manager Approval Action ---")
    action_res = client.post(
        f"/approvals/{apprv_id}/action",
        json={"status": "Approved", "comments": "Approved. Ready for implementation sprint."},
        headers=mgr_headers
    )
    record_check(action_res.status_code == 200 and action_res.json()["status"] == "Approved", "8.1 Process Approval Action -> 'Approved' (200 OK)")

    dec_final = client.get(f"/decisions/{dec_id}", headers=emp_headers).json()
    record_check(dec_final["status"] == "Approved", "8.2 Decision status transitioned to 'Approved'")

    # Step 9 – Manager Dashboard & Team Statistics
    print("\n--- Step 9: Manager Dashboard & Team Statistics ---")
    mgr_dash = client.get("/dashboard/manager", headers=mgr_headers).json()
    record_check(
        mgr_dash["team_decisions"] >= 1 and mgr_dash["approved_decisions"] >= 1,
        f"9.1 GET /dashboard/manager returns team statistics (Team Decisions: {mgr_dash['team_decisions']}, Approved: {mgr_dash['approved_decisions']})"
    )

    mgr_team_decs = client.get("/dashboard/manager/team-decisions", headers=mgr_headers)
    record_check(mgr_team_decs.status_code == 200 and len(mgr_team_decs.json()) >= 1, "9.2 GET /dashboard/manager/team-decisions returns department decisions (200 OK)")

    mgr_stats_res = client.get("/dashboard/manager/statistics", headers=mgr_headers)
    record_check(mgr_stats_res.status_code == 200 and "total_decisions" in mgr_stats_res.json(), "9.3 GET /dashboard/manager/statistics returns aggregated metrics (200 OK)")

    # Step 10 – Admin Dashboard & System Analytics
    print("\n--- Step 10: Admin Dashboard & System Analytics ---")
    adm_dash = client.get("/dashboard/admin", headers=adm_headers).json()
    record_check(
        adm_dash["total_users"] >= 3 and adm_dash["total_decisions"] >= 1,
        f"10.1 GET /dashboard/admin returns org-wide stats (Users: {adm_dash['total_users']}, Decisions: {adm_dash['total_decisions']})"
    )

    adm_analytics = client.get("/dashboard/admin/analytics", headers=adm_headers)
    record_check(
        adm_analytics.status_code == 200 and "decision_statistics" in adm_analytics.json() and "user_statistics" in adm_analytics.json(),
        "10.2 GET /dashboard/admin/analytics returns system analytics breakdown (200 OK)"
    )

    adm_dec_activity = client.get("/dashboard/admin/decision-activity", headers=adm_headers)
    record_check(
        adm_dec_activity.status_code == 200 and isinstance(adm_dec_activity.json(), dict) and len(adm_dec_activity.json()) >= 1,
        f"10.3 GET /dashboard/admin/decision-activity returns SQL-grouped creation activity: {adm_dec_activity.json()}"
    )

    adm_app_stats = client.get("/dashboard/admin/approval-statistics", headers=adm_headers).json()
    record_check(
        "completion_rate" in adm_app_stats and adm_app_stats["total_approvals"] >= 1,
        f"10.4 GET /dashboard/admin/approval-statistics returns performance metrics (Completion Rate: {adm_app_stats['completion_rate']}%, Avg Turnaround: {adm_app_stats['average_approval_time_hours']}h)"
    )

    adm_user_act = client.get("/dashboard/admin/user-activity", headers=adm_headers).json()
    record_check(
        adm_user_act["active_users_count"] >= 1 and len(adm_user_act["active_users"]) >= 1,
        f"10.5 GET /dashboard/admin/user-activity returns active user profiles (Active: {adm_user_act['active_users_count']})"
    )

    # Step 11 – Role-Based Authorization & Error Handling
    print("\n--- Step 11: Role-Based Authorization Enforcement ---")
    emp_mgr_attempt = client.get("/dashboard/manager", headers=emp_headers)
    record_check(emp_mgr_attempt.status_code == 403, "11.1 Employee accessing Manager Dashboard receives 403 Forbidden")

    emp_adm_attempt = client.get("/dashboard/admin", headers=emp_headers)
    record_check(emp_adm_attempt.status_code == 403, "11.2 Employee accessing Admin Dashboard receives 403 Forbidden")

    mgr_adm_attempt = client.get("/dashboard/admin", headers=mgr_headers)
    record_check(mgr_adm_attempt.status_code == 403, "11.3 Manager accessing Admin Dashboard receives 403 Forbidden")

    # Step 12 – Unauthenticated Requests
    print("\n--- Step 12: Unauthenticated Requests (401 Unauthorized) ---")
    record_check(client.get("/dashboard/employee").status_code == 401, "12.1 Employee Dashboard without JWT returns 401")
    record_check(client.get("/dashboard/manager").status_code == 401, "12.2 Manager Dashboard without JWT returns 401")
    record_check(client.get("/dashboard/admin").status_code == 401, "12.3 Admin Dashboard without JWT returns 401")
    record_check(client.get("/activities").status_code == 401, "12.4 Activities API without JWT returns 401")

    # Step 13 – Date Range Validation
    print("\n--- Step 13: Date Range Validation & Error Handling ---")
    invalid_date_fmt = client.get("/dashboard/admin/analytics?start_date=invalid-date-format", headers=adm_headers)
    record_check(invalid_date_fmt.status_code == 422, "13.1 Invalid date format returns 422 Validation Error")

    invalid_date_range = client.get("/dashboard/admin/analytics?start_date=2026-12-31&end_date=2026-01-01", headers=adm_headers)
    record_check(invalid_date_range.status_code == 422, "13.2 start_date > end_date returns 422 Validation Error")

    # Step 14 – Activities Log API & Filtering
    print("\n--- Step 14: System Activity Logs Retrieval & Filtering ---")
    all_acts_res = client.get("/activities", headers=adm_headers)
    record_check(all_acts_res.status_code == 200 and all_acts_res.json()["total"] >= 5, "14.1 Admin GET /activities returns system-wide activities (200 OK)")

    filtered_action = client.get("/activities?action=create_decision", headers=adm_headers)
    record_check(
        filtered_action.status_code == 200 and all(a["action"] == "create_decision" for a in filtered_action.json()["items"]),
        "14.2 Filter activities by action=create_decision (200 OK)"
    )

    filtered_entity = client.get("/activities?entity_type=decision", headers=adm_headers)
    record_check(
        filtered_entity.status_code == 200 and all(a["entity_type"] == "decision" for a in filtered_entity.json()["items"]),
        "14.3 Filter activities by entity_type=decision (200 OK)"
    )

    print("\n" + "=" * 80)
    print(f" SPRINT 10 VERIFICATION SUMMARY: {passed_count}/{total_count} CHECKS PASSED")
    print("=" * 80)
    return passed_count == total_count


if __name__ == "__main__":
    success = run_sprint10_verification()
    sys.exit(0 if success else 1)
