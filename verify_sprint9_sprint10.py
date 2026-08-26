import sys
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def run_sprint9_and_10_verification():
    print("=" * 80)
    print("   SPRINT 9 & SPRINT 10 COMPREHENSIVE VERIFICATION SUITE")
    print("   Knowledge Repository, Search, Discovery, Dashboards & Analytics")
    print("=" * 80)

    passed_checks = 0
    total_checks = 0

    def check(name, condition, details=""):
        nonlocal passed_checks, total_checks
        total_checks += 1
        if condition:
            passed_checks += 1
            print(f" [PASS] {name}")
        else:
            print(f" [FAIL] {name} - Details: {details}")

    # =========================================================================
    # 1. AUTHENTICATION & SETUP
    # =========================================================================
    print("\n--- 1. User Setup & Authentication ---")

    users_to_create = [
        {"full_name": "Alice Engineer", "email": "alice_v@example.com", "role": "Employee", "password": "Password123!", "employee_id": "EMP_V1", "department": "Engineering"},
        {"full_name": "Bob Reviewer", "email": "bob_v@example.com", "role": "Reviewer", "password": "Password123!", "employee_id": "REV_V1", "department": "Engineering"},
        {"full_name": "Carol Manager", "email": "carol_v@example.com", "role": "Manager", "password": "Password123!", "employee_id": "MGR_V1", "department": "Engineering"},
        {"full_name": "Dave Admin", "email": "dave_v@example.com", "role": "Administrator", "password": "Password123!", "employee_id": "ADM_V1", "department": "Executive"},
    ]

    for u in users_to_create:
        r = client.post("/users", json=u)
        # 201 or 400 if already created
        check(f"Register user: {u['email']}", r.status_code in [201, 400])

    tokens = {}
    for u in users_to_create:
        lr = client.post("/auth/login", json={"email": u["email"], "password": "Password123!"})
        check(f"Login user: {u['email']}", lr.status_code == 200)
        tokens[u["role"]] = lr.json()["access_token"]

    h_emp = {"Authorization": f"Bearer {tokens['Employee']}"}
    h_rev = {"Authorization": f"Bearer {tokens['Reviewer']}"}
    h_mgr = {"Authorization": f"Bearer {tokens['Manager']}"}
    h_adm = {"Authorization": f"Bearer {tokens['Administrator']}"}

    # =========================================================================
    # 2. SPRINT 9: TAG MANAGEMENT
    # =========================================================================
    print("\n--- 2. Sprint 9: Tag Management APIs ---")

    tag_names = ["PostgreSQL", "Database", "Backend", "Cloud", "Infrastructure", "Security"]
    created_tags = {}

    for tname in tag_names:
        res = client.post("/tags", json={"name": tname}, headers=h_emp)
        if res.status_code == 201:
            created_tags[tname] = res.json()["id"]
            check(f"Create tag '{tname}' (201)", True)
        elif res.status_code == 400:
            # Already exists
            all_tags = client.get("/tags", headers=h_emp).json()
            for t in all_tags:
                if t["name"].lower() == tname.lower():
                    created_tags[tname] = t["id"]
            check(f"Tag '{tname}' already exists (400 duplicate check)", True)

    # Test Duplicate Tag creation rejection
    dup_res = client.post("/tags", json={"name": "PostgreSQL"}, headers=h_emp)
    check("Prevent duplicate tag creation (400 Bad Request)", dup_res.status_code == 400)

    # Get all tags
    all_tags_res = client.get("/tags", headers=h_emp)
    check("Get all tags (200 OK)", all_tags_res.status_code == 200 and len(all_tags_res.json()) >= 6)

    # Get tag by ID
    t_id = created_tags["PostgreSQL"]
    get_tag_res = client.get(f"/tags/{t_id}", headers=h_emp)
    check("Get tag by ID (200 OK)", get_tag_res.status_code == 200 and get_tag_res.json()["name"] == "PostgreSQL")

    # =========================================================================
    # 3. SPRINT 9: DECISION CREATION & TAG ASSOCIATIONS
    # =========================================================================
    print("\n--- 3. Sprint 9: Decision Creation & Tag Associations ---")

    d1 = client.post(
        "/decisions",
        json={
            "title": "Select Core Database",
            "problem_statement": "Need a scalable relational database for persistent business transactions.",
            "category": "Technology"
        },
        headers=h_emp
    ).json()
    check("Create Decision 1: Select Core Database (201)", d1.get("id") is not None)

    d2 = client.post(
        "/decisions",
        json={
            "title": "Select Cloud Provider",
            "problem_statement": "Determine primary cloud vendor for microservices.",
            "category": "Infrastructure"
        },
        headers=h_emp
    ).json()
    check("Create Decision 2: Select Cloud Provider (201)", d2.get("id") is not None)

    d3 = client.post(
        "/decisions",
        json={
            "title": "Choose Authentication Strategy",
            "problem_statement": "Implement secure JWT and OAuth2 federated authentication.",
            "category": "Security"
        },
        headers=h_emp
    ).json()
    check("Create Decision 3: Choose Authentication Strategy (201)", d3.get("id") is not None)

    # Assign tags to Decision 1: PostgreSQL, Database, Backend
    assign_d1 = client.post(
        f"/decisions/{d1['id']}/tags",
        json={"tag_ids": [created_tags["PostgreSQL"], created_tags["Database"], created_tags["Backend"]]},
        headers=h_emp
    )
    check("Assign tags to Decision 1 (200 OK)", assign_d1.status_code == 200 and len(assign_d1.json()["tags"]) == 3)

    # Assign tags to Decision 2: Cloud, Infrastructure
    assign_d2 = client.post(
        f"/decisions/{d2['id']}/tags",
        json={"tag_ids": [created_tags["Cloud"], created_tags["Infrastructure"]]},
        headers=h_emp
    )
    check("Assign tags to Decision 2 (200 OK)", assign_d2.status_code == 200 and len(assign_d2.json()["tags"]) == 2)

    # Get tags for Decision 1
    d1_tags_res = client.get(f"/decisions/{d1['id']}/tags", headers=h_emp)
    check("Get tags for Decision 1 (200 OK)", d1_tags_res.status_code == 200 and len(d1_tags_res.json()) == 3)

    # Remove tag from Decision 1
    rem_tag_res = client.delete(f"/decisions/{d1['id']}/tags/{created_tags['Backend']}", headers=h_emp)
    check("Remove tag from Decision 1 (200 OK)", rem_tag_res.status_code == 200)

    # Re-add tag for subsequent tests
    client.post(f"/decisions/{d1['id']}/tags", json={"tag_ids": [created_tags["Backend"]]}, headers=h_emp)

    # =========================================================================
    # 4. SPRINT 9: SEARCH, FILTERING, PAGINATION & SORTING
    # =========================================================================
    print("\n--- 4. Sprint 9: Search, Filtering, Pagination & Sorting ---")

    # Keyword search
    search_q = client.get("/decisions/search?q=database", headers=h_emp)
    check("Search decisions by keyword q=database", search_q.status_code == 200 and search_q.json()["total"] >= 1)

    # Category filter
    cat_filter = client.get("/decisions?category=Technology", headers=h_emp)
    check("Filter decisions by Category=Technology", cat_filter.status_code == 200 and len(cat_filter.json()) >= 1)

    # Empty category returns empty list
    empty_cat = client.get("/decisions?category=NonExistentCategory", headers=h_emp)
    check("Non-existing category returns empty list (200 OK)", empty_cat.status_code == 200 and empty_cat.json() == [])

    # Status filter
    status_filter = client.get("/decisions?status=Draft", headers=h_emp)
    check("Filter decisions by Status=Draft", status_filter.status_code == 200 and len(status_filter.json()) >= 3)

    # Tag filter
    tag_filter = client.get("/decisions?tag=PostgreSQL", headers=h_emp)
    check("Filter decisions by Tag=PostgreSQL", tag_filter.status_code == 200 and len(tag_filter.json()) >= 1)

    # Combined Search & Filters
    comb_search = client.get("/decisions/search?q=Database&category=Technology&status=Draft&tag=PostgreSQL", headers=h_emp)
    check("Combined Search (q + category + status + tag)", comb_search.status_code == 200 and comb_search.json()["total"] >= 1)

    # Pagination
    p1 = client.get("/decisions/search?page=1&page_size=2", headers=h_emp)
    p2 = client.get("/decisions/search?page=2&page_size=2", headers=h_emp)
    check("Pagination (page 1 and page 2)", p1.status_code == 200 and p2.status_code == 200 and len(p1.json()["items"]) == 2)

    # Controlled Sorting
    sort_asc = client.get("/decisions?sort=title&order=asc", headers=h_emp)
    check("Sorting by title ASC", sort_asc.status_code == 200)

    invalid_sort = client.get("/decisions?sort=secret_col", headers=h_emp)
    check("Invalid sort column returns 422 Unprocessable Entity", invalid_sort.status_code == 422)

    # =========================================================================
    # 5. SPRINT 9: TIMELINE & ARCHIVED DECISIONS
    # =========================================================================
    print("\n--- 5. Sprint 9: Decision Timeline & Archived Decisions ---")

    # Add alternative, comment, thread to Decision 1
    client.post(
        f"/decisions/{d1['id']}/alternatives",
        json={"name": "Managed PostgreSQL", "description": "AWS RDS DB", "pros": "ACID compliance", "cons": "Cost", "estimated_cost": 300.0, "feasibility_score": 5, "risk_level": "Low"},
        headers=h_emp
    )
    client.post(f"/decisions/{d1['id']}/comments", json={"content": "PostgreSQL is standard."}, headers=h_emp)
    client.post(f"/decisions/{d1['id']}/threads", json={"title": "High Availability setup", "description": "Read replicas"}, headers=h_emp)

    timeline_res = client.get(f"/decisions/{d1['id']}/timeline", headers=h_emp)
    check("Get decision timeline (200 OK)", timeline_res.status_code == 200 and len(timeline_res.json()["events"]) >= 4)

    # Archive Decision 3
    client.patch(f"/decisions/{d3['id']}/status", json={"status": "Archived"}, headers=h_emp)
    archived_list = client.get("/decisions?status=Archived", headers=h_emp)
    check("Retrieve archived decisions (200 OK)", archived_list.status_code == 200 and len(archived_list.json()) >= 1)

    # Prevent modification of archived decision
    mod_archived = client.put(f"/decisions/{d3['id']}", json={"title": "New Title", "problem_statement": "New", "category": "Security"}, headers=h_emp)
    check("Prevent modification of archived decision (400 Bad Request)", mod_archived.status_code == 400)

    # =========================================================================
    # 6. SPRINT 10: EMPLOYEE DASHBOARD
    # =========================================================================
    print("\n--- 6. Sprint 10: Employee Dashboard ---")

    emp_dash = client.get("/dashboard/employee", headers=h_emp)
    check("Employee Dashboard (GET /dashboard/employee)", emp_dash.status_code == 200 and emp_dash.json()["total_decisions"] >= 2)

    emp_dec = client.get("/dashboard/employee/decisions", headers=h_emp)
    check("Employee My Decisions (GET /dashboard/employee/decisions)", emp_dec.status_code == 200 and len(emp_dec.json()) >= 2)

    emp_acts = client.get("/dashboard/employee/recent-activities", headers=h_emp)
    check("Employee Recent Activities (GET /dashboard/employee/recent-activities)", emp_acts.status_code == 200 and len(emp_acts.json()) >= 1)

    # =========================================================================
    # 7. SPRINT 10: MANAGER DASHBOARD
    # =========================================================================
    print("\n--- 7. Sprint 10: Manager Dashboard ---")

    mgr_dash = client.get("/dashboard/manager", headers=h_mgr)
    check("Manager Dashboard (GET /dashboard/manager)", mgr_dash.status_code == 200 and mgr_dash.json()["team_decisions"] >= 2)

    mgr_team_dec = client.get("/dashboard/manager/team-decisions", headers=h_mgr)
    check("Manager Team Decisions (GET /dashboard/manager/team-decisions)", mgr_team_dec.status_code == 200 and len(mgr_team_dec.json()) >= 2)

    mgr_stats = client.get("/dashboard/manager/statistics", headers=h_mgr)
    check("Manager Decision Statistics (GET /dashboard/manager/statistics)", mgr_stats.status_code == 200 and mgr_stats.json()["total_decisions"] >= 2)

    emp_forbidden_mgr = client.get("/dashboard/manager", headers=h_emp)
    check("Employee accessing Manager Dashboard receives 403 Forbidden", emp_forbidden_mgr.status_code == 403)

    # =========================================================================
    # 8. SPRINT 10: APPROVAL WORKFLOW & PERFORMANCE METRICS
    # =========================================================================
    print("\n--- 8. Sprint 10: Approvals & Turnaround Metrics ---")

    # Submit Decision 1 for Approval to Bob Reviewer
    rev_users = [u for u in client.get("/users", headers=h_emp).json() if u["role"] == "Reviewer"]
    rev_id = rev_users[0]["id"]

    approval_res = client.post(
        "/approvals",
        json={"decision_id": d1["id"], "reviewer_id": rev_id, "approval_level": 1, "comments": "Architecture review requested."},
        headers=h_emp
    )
    check("Submit decision for approval (201 Created)", approval_res.status_code == 201)
    app_id = approval_res.json()["id"]

    # Reviewer approves decision
    approve_action = client.post(f"/approvals/{app_id}/approve", json={"comments": "Approved by engineering lead."}, headers=h_rev)
    check("Reviewer approves decision (200 OK)", approve_action.status_code == 200 and approve_action.json()["status"] == "Approved")

    # Verify decision status changed to Approved
    d1_check = client.get(f"/decisions/{d1['id']}", headers=h_emp)
    check("Decision status updated to Approved in PostgreSQL", d1_check.status_code == 200 and d1_check.json()["status"] == "Approved")

    # =========================================================================
    # 9. SPRINT 10: ADMIN DASHBOARD & ANALYTICS
    # =========================================================================
    print("\n--- 9. Sprint 10: Admin Dashboard & Analytics ---")

    adm_dash = client.get("/dashboard/admin", headers=h_adm)
    check("Admin Dashboard overview (GET /dashboard/admin)", adm_dash.status_code == 200 and adm_dash.json()["total_users"] >= 4)

    emp_forbidden_adm = client.get("/dashboard/admin", headers=h_emp)
    check("Employee accessing Admin Dashboard receives 403 Forbidden", emp_forbidden_adm.status_code == 403)

    mgr_forbidden_adm = client.get("/dashboard/admin", headers=h_mgr)
    check("Manager accessing Admin Dashboard receives 403 Forbidden", mgr_forbidden_adm.status_code == 403)

    analytics_res = client.get("/dashboard/admin/analytics?start_date=2020-01-01&end_date=2030-12-31", headers=h_adm)
    check("Admin Analytics with Date Range (GET /dashboard/admin/analytics)", analytics_res.status_code == 200 and analytics_res.json()["decision_statistics"]["approved_decisions"] >= 1)

    dec_act_res = client.get("/dashboard/admin/decision-activity", headers=h_adm)
    check("Decision Creation Daily Breakdown (GET /dashboard/admin/decision-activity)", dec_act_res.status_code == 200 and len(dec_act_res.json()) >= 1)

    app_perf_res = client.get("/dashboard/admin/approval-statistics", headers=h_adm)
    check("Approval Performance & Turnaround Metrics (GET /dashboard/admin/approval-statistics)", app_perf_res.status_code == 200 and app_perf_res.json()["completion_rate"] > 0)

    user_act_res = client.get("/dashboard/admin/user-activity", headers=h_adm)
    check("Active User Metrics (GET /dashboard/admin/user-activity)", user_act_res.status_code == 200 and user_act_res.json()["active_users_count"] >= 1)

    # =========================================================================
    # 10. SPRINT 10: ACTIVITY LOGGING & FILTERING
    # =========================================================================
    print("\n--- 10. Sprint 10: Activity Logging & Filtering ---")

    all_acts = client.get("/activities", headers=h_adm)
    check("Retrieve Activity Logs as Admin (GET /activities)", all_acts.status_code == 200 and all_acts.json()["total"] >= 10)

    filtered_acts = client.get("/activities?entity_type=Decision", headers=h_adm)
    check("Filter Activities by entity_type=Decision", filtered_acts.status_code == 200 and len(filtered_acts.json()["items"]) >= 1)

    # =========================================================================
    # 11. AUTHENTICATION & ERROR HANDLING
    # =========================================================================
    print("\n--- 11. Authentication & Error Handling ---")

    check("GET /decisions without JWT returns 401", client.get("/decisions").status_code == 401)
    check("GET /dashboard/employee without JWT returns 401", client.get("/dashboard/employee").status_code == 401)
    check("GET /dashboard/admin without JWT returns 401", client.get("/dashboard/admin").status_code == 401)
    check("GET /activities without JWT returns 401", client.get("/activities").status_code == 401)
    check("Invalid date format returns 422", client.get("/dashboard/admin/analytics?start_date=bad-date", headers=h_adm).status_code == 422)

    print("\n" + "=" * 80)
    print(f" VERIFICATION SUMMARY: {passed_checks}/{total_checks} CHECKS PASSED ({(passed_checks/total_checks)*100:.1f}%)")
    print("=" * 80)

    return passed_checks == total_checks


if __name__ == "__main__":
    success = run_sprint9_and_10_verification()
    sys.exit(0 if success else 1)
