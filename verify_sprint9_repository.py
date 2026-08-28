import sys
from fastapi.testclient import TestClient

from app.main import app
from app.db.database import SessionLocal
from app.models.decision import Decision
from app.models.tag import Tag
from app.models.user import User

client = TestClient(app)


def run_sprint9_verification():
    print("=" * 80)
    print(" SPRINT 9: KNOWLEDGE REPOSITORY, SEARCH & DECISION DISCOVERY VERIFICATION")
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

    # Step 1 – Authentication & User Setup
    print("\n--- Step 1: User Authentication & JWT Acquisition ---")
    user_email = "sprint9_architect@example.com"
    user_data = {
        "full_name": "Sarah Architect",
        "email": user_email,
        "role": "Employee",
        "password": "Password123!",
        "employee_id": "EMP_S9_001",
        "department": "Platform Architecture",
        "designation": "Principal Architect",
        "phone_number": "+1-555-0901"
    }
    client.post("/users", json=user_data)
    login_res = client.post("/auth/login", json={"email": user_email, "password": "Password123!"})
    record_check(login_res.status_code == 200, "1.1 User Login & JWT Token Generation (200 OK)")
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Step 2 – Create Decisions in Multiple Categories
    print("\n--- Step 2: Create Decisions in Controlled Categories ---")
    dec_tech_payload = {
        "title": "Select PostgreSQL as Primary Database",
        "problem_statement": "Select scalable SQL database for analytical and transactional workloads",
        "category": "Technology"
    }
    res_dec_1 = client.post("/decisions", json=dec_tech_payload, headers=headers)
    record_check(res_dec_1.status_code == 201 and res_dec_1.json()["category"] == "Technology", "2.1 Create Decision (Category: Technology) (201 Created)")
    dec_1_id = res_dec_1.json()["id"]

    dec_infra_payload = {
        "title": "Select Cloud Provider for Hosting",
        "problem_statement": "Choose reliable multi-region cloud provider with Kubernetes support",
        "category": "Infrastructure"
    }
    res_dec_2 = client.post("/decisions", json=dec_infra_payload, headers=headers)
    record_check(res_dec_2.status_code == 201 and res_dec_2.json()["category"] == "Infrastructure", "2.2 Create Decision (Category: Infrastructure) (201 Created)")
    dec_2_id = res_dec_2.json()["id"]

    dec_fin_payload = {
        "title": "Annual Cloud Budget Allocation",
        "problem_statement": "Allocate quarterly and annual compute infrastructure budget",
        "category": "Finance"
    }
    res_dec_3 = client.post("/decisions", json=dec_fin_payload, headers=headers)
    record_check(res_dec_3.status_code == 201 and res_dec_3.json()["category"] == "Finance", "2.3 Create Decision (Category: Finance) (201 Created)")
    dec_3_id = res_dec_3.json()["id"]

    # Step 3 – Create Tags
    print("\n--- Step 3: Create Tags Management ---")
    tag_names = ["Database", "PostgreSQL", "Cloud", "Infrastructure", "Backend"]
    created_tags = {}
    for name in tag_names:
        res_tag = client.post("/tags", json={"name": name}, headers=headers)
        if res_tag.status_code == 201:
            created_tags[name] = res_tag.json()["id"]
        elif res_tag.status_code == 400:
            # Already exists, fetch all tags to locate ID
            all_tags = client.get("/tags", headers=headers).json()
            for t in all_tags:
                if t["name"] == name:
                    created_tags[name] = t["id"]
    record_check(len(created_tags) == len(tag_names), f"3.1 Created/Found {len(created_tags)} Tags (Database, PostgreSQL, Cloud, Infrastructure, Backend)")

    # Test Duplicate Tag
    dup_tag_res = client.post("/tags", json={"name": "PostgreSQL"}, headers=headers)
    record_check(dup_tag_res.status_code == 400, "3.2 Duplicate Tag name returns 400 Bad Request")

    # Get all tags
    all_tags_res = client.get("/tags", headers=headers)
    record_check(all_tags_res.status_code == 200 and len(all_tags_res.json()) >= len(tag_names), "3.3 Get All Tags (200 OK)")

    # Step 4 – Assign Tags to Decisions
    print("\n--- Step 4: Assign Tags to Decisions ---")
    assign_1_ids = [created_tags["PostgreSQL"], created_tags["Database"], created_tags["Backend"]]
    res_assign_1 = client.post(f"/decisions/{dec_1_id}/tags", json={"tag_ids": assign_1_ids}, headers=headers)
    record_check(res_assign_1.status_code == 200 and len(res_assign_1.json()) >= 3, "4.1 Assign Tags [PostgreSQL, Database, Backend] to Decision 1")

    assign_2_ids = [created_tags["Cloud"], created_tags["Infrastructure"]]
    res_assign_2 = client.post(f"/decisions/{dec_2_id}/tags", json={"tag_ids": assign_2_ids}, headers=headers)
    record_check(res_assign_2.status_code == 200 and len(res_assign_2.json()) >= 2, "4.2 Assign Tags [Cloud, Infrastructure] to Decision 2")

    # Step 5 – Get Decision Tags & Remove Tag
    print("\n--- Step 5: Decision Tag Retrieval & Tag Removal ---")
    get_tags_res = client.get(f"/decisions/{dec_1_id}/tags", headers=headers)
    record_check(get_tags_res.status_code == 200 and len(get_tags_res.json()) >= 3, "5.1 Get Tags for Decision 1 (200 OK)")

    del_tag_res = client.delete(f"/decisions/{dec_1_id}/tags/{created_tags['Backend']}", headers=headers)
    record_check(del_tag_res.status_code == 200, "5.2 Remove Tag 'Backend' from Decision 1 without deleting Tag itself (200 OK)")

    tag_still_exists = client.get(f"/tags/{created_tags['Backend']}", headers=headers)
    record_check(tag_still_exists.status_code == 200, "5.3 Verified Tag entity persists in database after removal from decision")

    # Re-add Backend tag for complete search tests
    client.post(f"/decisions/{dec_1_id}/tags", json={"tag_ids": [created_tags["Backend"]]}, headers=headers)

    # Approve Decision 1 for status filtering tests
    client.patch(f"/decisions/{dec_1_id}/status", json={"status": "Approved"}, headers=headers)

    # Step 6 – Decision Search by Keyword
    print("\n--- Step 6: Decision Keyword Search ---")
    search_q_res = client.get("/decisions/search?q=database", headers=headers)
    record_check(
        search_q_res.status_code == 200 and any(dec_1_id == it["id"] for it in search_q_res.json()["items"]),
        "6.1 GET /decisions/search?q=database finds PostgreSQL Decision (200 OK)"
    )

    # Step 7 – Category Filtering
    print("\n--- Step 7: Category Filtering ---")
    cat_filter_res = client.get("/decisions?category=Technology", headers=headers)
    record_check(
        cat_filter_res.status_code == 200 and all(it["category"].lower() == "technology" for it in cat_filter_res.json()),
        "7.1 GET /decisions?category=Technology returns only Technology decisions (200 OK)"
    )

    # Test unused category returns empty list, not error
    cat_empty_res = client.get("/decisions?category=Human Resources", headers=headers)
    record_check(
        cat_empty_res.status_code == 200 and isinstance(cat_empty_res.json(), list),
        "7.2 Category with no records returns empty list [] rather than producing error (200 OK)"
    )

    # Step 8 – Status Filtering
    print("\n--- Step 8: Status Filtering ---")
    status_apprv_res = client.get("/decisions?status=Approved", headers=headers)
    record_check(
        status_apprv_res.status_code == 200 and all(it["status"] == "Approved" for it in status_apprv_res.json()),
        "8.1 GET /decisions?status=Approved returns only Approved decisions (200 OK)"
    )

    # Step 9 – Tag Filtering
    print("\n--- Step 9: Tag Filtering ---")
    tag_filter_res = client.get("/decisions?tag=PostgreSQL", headers=headers)
    record_check(
        tag_filter_res.status_code == 200 and any(dec_1_id == it["id"] for it in tag_filter_res.json()),
        "9.1 GET /decisions?tag=PostgreSQL returns decisions associated with PostgreSQL tag (200 OK)"
    )

    # Step 10 – Combined Search and Filters
    print("\n--- Step 10: Combined Search & Filters ---")
    comb_res = client.get("/decisions/search?q=database&category=Technology&status=Approved&tag=PostgreSQL", headers=headers)
    record_check(
        comb_res.status_code == 200 and comb_res.json()["total"] >= 1 and any(dec_1_id == it["id"] for it in comb_res.json()["items"]),
        "10.1 Combined Search (q=database, category=Technology, status=Approved, tag=PostgreSQL) matches target record (200 OK)"
    )

    # Step 11 – Pagination
    print("\n--- Step 11: Pagination ---")
    pag_res_1 = client.get("/decisions?page=1&page_size=2", headers=headers)
    record_check(
        pag_res_1.status_code == 200 and pag_res_1.json()["page"] == 1 and len(pag_res_1.json()["items"]) <= 2,
        "11.1 Pagination Page 1 with page_size=2 returns paginated response (200 OK)"
    )
    pag_res_2 = client.get("/decisions?page=2&page_size=2", headers=headers)
    record_check(
        pag_res_2.status_code == 200 and pag_res_2.json()["page"] == 2,
        "11.2 Pagination Page 2 returns next slice (200 OK)"
    )

    # Step 12 – Sorting
    print("\n--- Step 12: Controlled Sorting ---")
    sort_newest = client.get("/decisions?sort=created_at&order=desc", headers=headers)
    record_check(sort_newest.status_code == 200, "12.1 Sort by created_at DESC (Newest first) (200 OK)")
    sort_oldest = client.get("/decisions?sort=created_at&order=asc", headers=headers)
    record_check(sort_oldest.status_code == 200, "12.2 Sort by created_at ASC (Oldest first) (200 OK)")
    sort_title = client.get("/decisions?sort=title&order=asc", headers=headers)
    record_check(sort_title.status_code == 200, "12.3 Sort by title ASC (Alphabetical) (200 OK)")

    # Step 13 – Decision Timeline
    print("\n--- Step 13: Decision Timeline Reconstruction ---")
    # Add an alternative, comment, and meeting note to Decision 1
    client.post(f"/decisions/{dec_1_id}/alternatives", json={
        "name": "AWS Aurora PostgreSQL",
        "description": "Managed cloud relational store",
        "pros": "High performance, automated backups",
        "cons": "Cloud vendor lock-in",
        "estimated_cost": 1200.0,
        "feasibility_score": 5,
        "risk_level": "Low"
    }, headers=headers)
    client.post(f"/decisions/{dec_1_id}/comments", json={"content": "Evaluated Aurora benchmarks, look great."}, headers=headers)
    client.post(f"/decisions/{dec_1_id}/meeting-notes", json={"title": "DB Selection Signoff Meeting", "content": "Unanimous agreement on PostgreSQL."}, headers=headers)

    timeline_res = client.get(f"/decisions/{dec_1_id}/timeline", headers=headers)
    tl_data = timeline_res.json()
    record_check(
        timeline_res.status_code == 200 and len(tl_data["events"]) >= 4,
        f"13.1 GET /decisions/{dec_1_id}/timeline returns chronological progression ({len(tl_data.get('events', []))} events) (200 OK)"
    )

    # Step 14 – Archived Decisions
    print("\n--- Step 14: Archived Decisions Retrieval ---")
    client.patch(f"/decisions/{dec_3_id}/status", json={"status": "Archived"}, headers=headers)
    archived_res = client.get("/decisions?status=Archived", headers=headers)
    record_check(
        archived_res.status_code == 200 and any(dec_3_id == it["id"] for it in archived_res.json()),
        "14.1 GET /decisions?status=Archived discovers archived organizational decisions (200 OK)"
    )

    # Step 15 – Authentication & Error Validation
    print("\n--- Step 15: Authentication & Error Handling ---")
    no_auth_search = client.get("/decisions/search?q=database")
    record_check(no_auth_search.status_code == 401, "15.1 Search without JWT returns 401 Unauthorized")

    no_auth_tags = client.get("/tags")
    record_check(no_auth_tags.status_code == 401, "15.2 Tags API without JWT returns 401 Unauthorized")

    not_found_dec = client.get("/decisions/9999999", headers=headers)
    record_check(not_found_dec.status_code == 404, "15.3 Non-existent decision returns 404 Not Found")

    not_found_tag = client.get("/tags/9999999", headers=headers)
    record_check(not_found_tag.status_code == 404, "15.4 Non-existent tag returns 404 Not Found")

    invalid_sort = client.get("/decisions?sort=malicious_sql_injection", headers=headers)
    record_check(invalid_sort.status_code == 422, "15.5 Invalid sort column returns 422 Validation Error")

    invalid_status = client.get("/decisions?status=InvalidStatusValue", headers=headers)
    record_check(invalid_status.status_code == 422, "15.6 Invalid status filter returns 422 Validation Error")

    print("\n" + "=" * 80)
    print(f" SPRINT 9 VERIFICATION SUMMARY: {passed_count}/{total_count} CHECKS PASSED")
    print("=" * 80)
    return passed_count == total_count


if __name__ == "__main__":
    success = run_sprint9_verification()
    sys.exit(0 if success else 1)
