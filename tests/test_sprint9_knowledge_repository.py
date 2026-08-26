import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_auth_headers(user_email: str, password: str = "Password123!"):
    login_res = client.post("/auth/login", json={"email": user_email, "password": password})
    assert login_res.status_code == 200, f"Login failed for {user_email}: {login_res.text}"
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def setup_sprint9_data():
    # 1. Register Users
    u1 = {
        "full_name": "Alice Developer",
        "email": "alice_s9@example.com",
        "role": "Employee",
        "password": "Password123!",
        "employee_id": "EMP_S9_01",
        "department": "Engineering"
    }
    r1 = client.post("/users", json=u1)
    assert r1.status_code == 201

    h1 = get_auth_headers("alice_s9@example.com")

    # 2. Create Decisions across various categories
    d1_payload = {
        "title": "Select Relational Database",
        "problem_statement": "Need a powerful SQL database for transaction processing.",
        "category": "Technology"
    }
    d1 = client.post("/decisions", json=d1_payload, headers=h1).json()

    d2_payload = {
        "title": "Cloud Provider Migration",
        "problem_statement": "Evaluate multi-cloud infrastructure for high availability.",
        "category": "Infrastructure"
    }
    d2 = client.post("/decisions", json=d2_payload, headers=h1).json()

    d3_payload = {
        "title": "Budget Allocation for Q3",
        "problem_statement": "Allocate quarterly engineering budget.",
        "category": "Finance"
    }
    d3 = client.post("/decisions", json=d3_payload, headers=h1).json()

    # 3. Create Tags
    t1 = client.post("/tags", json={"name": "PostgreSQL"}, headers=h1).json()
    t2 = client.post("/tags", json={"name": "Database"}, headers=h1).json()
    t3 = client.post("/tags", json={"name": "Backend"}, headers=h1).json()
    t4 = client.post("/tags", json={"name": "Cloud"}, headers=h1).json()

    # 4. Associate Tags
    client.post(f"/decisions/{d1['id']}/tags", json={"tag_ids": [t1["id"], t2["id"], t3["id"]]}, headers=h1)
    client.post(f"/decisions/{d2['id']}/tags", json={"tag_ids": [t4["id"], t3["id"]]}, headers=h1)

    return {
        "headers": h1,
        "d1": d1,
        "d2": d2,
        "d3": d3,
        "t1": t1,
        "t2": t2,
        "t3": t3,
        "t4": t4,
    }


def test_tag_crud_and_duplicates(setup_sprint9_data):
    h = setup_sprint9_data["headers"]

    # Create new tag
    res = client.post("/tags", json={"name": "Redis"}, headers=h)
    assert res.status_code == 201
    tag_id = res.json()["id"]
    assert res.json()["name"] == "Redis"

    # Duplicate tag rejection
    dup_res = client.post("/tags", json={"name": "Redis"}, headers=h)
    assert dup_res.status_code == 400
    assert "already exists" in dup_res.json()["detail"]

    # Get all tags
    all_tags = client.get("/tags", headers=h)
    assert all_tags.status_code == 200
    names = [t["name"] for t in all_tags.json()]
    assert "Redis" in names
    assert "PostgreSQL" in names

    # Get tag by ID
    get_res = client.get(f"/tags/{tag_id}", headers=h)
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Redis"

    # Non-existing tag
    missing_res = client.get("/tags/99999", headers=h)
    assert missing_res.status_code == 404

    # Delete tag
    del_res = client.delete(f"/tags/{tag_id}", headers=h)
    assert del_res.status_code == 200

    # Verify deleted
    assert client.get(f"/tags/{tag_id}", headers=h).status_code == 404


def test_decision_tags_management(setup_sprint9_data):
    h = setup_sprint9_data["headers"]
    d3_id = setup_sprint9_data["d3"]["id"]
    t1_id = setup_sprint9_data["t1"]["id"]

    # Assign tag to d3
    assign_res = client.post(f"/decisions/{d3_id}/tags", json={"tag_ids": [t1_id]}, headers=h)
    assert assign_res.status_code == 200

    # Get decision tags
    tags_res = client.get(f"/decisions/{d3_id}/tags", headers=h)
    assert tags_res.status_code == 200
    assert len(tags_res.json()) == 1
    assert tags_res.json()[0]["id"] == t1_id

    # Assign invalid tag ID -> 404
    invalid_assign = client.post(f"/decisions/{d3_id}/tags", json={"tag_ids": [99999]}, headers=h)
    assert invalid_assign.status_code == 404

    # Remove tag from decision
    rem_res = client.delete(f"/decisions/{d3_id}/tags/{t1_id}", headers=h)
    assert rem_res.status_code == 200

    # Verify tag removed
    tags_after = client.get(f"/decisions/{d3_id}/tags", headers=h)
    assert len(tags_after.json()) == 0

    # Verify tag still exists globally
    tag_check = client.get(f"/tags/{t1_id}", headers=h)
    assert tag_check.status_code == 200


def test_decision_search_and_filters(setup_sprint9_data):
    h = setup_sprint9_data["headers"]

    # 1. Keyword search (q=database)
    s1 = client.get("/decisions/search?q=database", headers=h)
    assert s1.status_code == 200
    assert s1.json()["total"] >= 1
    assert any("Database" in item["title"] for item in s1.json()["items"])

    # 2. Category filter
    c_res = client.get("/decisions?category=Technology", headers=h)
    assert c_res.status_code == 200
    assert all(d["category"] == "Technology" for d in c_res.json())

    # 3. Non-existing category returns empty list (not error)
    empty_res = client.get("/decisions?category=NonExistingCategory", headers=h)
    assert empty_res.status_code == 200
    assert empty_res.json() == []

    # 4. Status filter
    status_res = client.get("/decisions?status=Draft", headers=h)
    assert status_res.status_code == 200
    assert len(status_res.json()) >= 3

    # 5. Tag filter
    tag_res = client.get("/decisions?tag=PostgreSQL", headers=h)
    assert tag_res.status_code == 200
    assert len(tag_res.json()) == 1
    assert tag_res.json()[0]["title"] == "Select Relational Database"

    # 6. Combined Search & Filters
    comb_res = client.get(
        "/decisions/search?q=Database&category=Technology&status=Draft&tag=PostgreSQL",
        headers=h
    )
    assert comb_res.status_code == 200
    assert comb_res.json()["total"] == 1
    assert comb_res.json()["items"][0]["title"] == "Select Relational Database"


def test_pagination_and_sorting(setup_sprint9_data):
    h = setup_sprint9_data["headers"]

    # Pagination page 1
    p1 = client.get("/decisions/search?page=1&page_size=2", headers=h)
    assert p1.status_code == 200
    assert len(p1.json()["items"]) == 2
    assert p1.json()["total"] >= 3

    # Pagination page 2
    p2 = client.get("/decisions/search?page=2&page_size=2", headers=h)
    assert p2.status_code == 200
    assert len(p2.json()["items"]) >= 1

    # Sorting by title asc
    sort_res = client.get("/decisions?sort=title&order=asc", headers=h)
    assert sort_res.status_code == 200
    titles = [d["title"] for d in sort_res.json()]
    assert titles == sorted(titles)

    # Invalid sort field -> 422
    inv_sort = client.get("/decisions?sort=invalid_col", headers=h)
    assert inv_sort.status_code == 422

    # Invalid order -> 422
    inv_order = client.get("/decisions?sort=title&order=sideways", headers=h)
    assert inv_order.status_code == 422


def test_decision_timeline(setup_sprint9_data):
    h = setup_sprint9_data["headers"]
    d1_id = setup_sprint9_data["d1"]["id"]

    # Add alternative
    alt_res = client.post(
        f"/decisions/{d1_id}/alternatives",
        json={
            "name": "PostgreSQL on AWS RDS",
            "description": "Managed PostgreSQL instance.",
            "pros": "Fully managed, automated backups",
            "cons": "Cloud vendor lock-in",
            "estimated_cost": 250.0,
            "feasibility_score": 5,
            "risk_level": "Low"
        },
        headers=h
    )
    assert alt_res.status_code == 201

    # Add comment
    comm_res = client.post(
        f"/decisions/{d1_id}/comments",
        json={"content": "Strongly support PostgreSQL for ACID compliance."},
        headers=h
    )
    assert comm_res.status_code == 201

    # Fetch Timeline
    timeline_res = client.get(f"/decisions/{d1_id}/timeline", headers=h)
    assert timeline_res.status_code == 200
    data = timeline_res.json()
    assert data["decision_id"] == d1_id
    assert len(data["events"]) >= 3

    event_types = [e["event_type"] for e in data["events"]]
    assert "Decision created" in event_types
    assert "Alternative added" in event_types
    assert "Comment added" in event_types


def test_archived_decision_restrictions(setup_sprint9_data):
    h = setup_sprint9_data["headers"]
    d1_id = setup_sprint9_data["d1"]["id"]

    # Archive decision
    arch_res = client.patch(f"/decisions/{d1_id}/status", json={"status": "Archived"}, headers=h)
    assert arch_res.status_code == 200
    assert arch_res.json()["status"] == "Archived"

    # Attempt to modify archived decision -> 400
    mod_res = client.put(
        f"/decisions/{d1_id}",
        json={
            "title": "Modified Title",
            "problem_statement": "Modified statement",
            "category": "Technology"
        },
        headers=h
    )
    assert mod_res.status_code == 400
    assert "Cannot modify an archived decision" in mod_res.json()["detail"]

    # Retrieve archived decisions
    archived_list = client.get("/decisions?status=Archived", headers=h)
    assert archived_list.status_code == 200
    assert any(d["id"] == d1_id for d in archived_list.json())


def test_unauthenticated_access_rejected(setup_sprint9_data):
    d1_id = setup_sprint9_data["d1"]["id"]

    # Without JWT -> 401
    assert client.get("/decisions").status_code == 401
    assert client.get("/decisions/search").status_code == 401
    assert client.get("/tags").status_code == 401
    assert client.get(f"/decisions/{d1_id}/timeline").status_code == 401
