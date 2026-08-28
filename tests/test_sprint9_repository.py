import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.decision import Decision
from app.models.tag import Tag
from app.models.user import User

client = TestClient(app)


def get_token(email: str, role: str = "Employee", password: str = "Password123!"):
    user_in = {
        "full_name": email.split("@")[0].capitalize(),
        "email": email,
        "role": role,
        "password": password,
        "employee_id": f"EMP_{email[:8]}",
        "department": "Engineering"
    }
    client.post("/users", json=user_in)

    res = client.post("/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200
    return res.json()["access_token"]


def test_sprint9_tag_crud():
    token = get_token("tag_tester@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create Tag
    res = client.post("/tags", json={"name": "PostgreSQL"}, headers=headers)
    assert res.status_code in [201, 400]
    if res.status_code == 201:
        assert res.json()["name"] == "PostgreSQL"

    # 2. Duplicate Tag returns 400
    res_dup = client.post("/tags", json={"name": "PostgreSQL"}, headers=headers)
    assert res_dup.status_code == 400

    # 3. Create more tags
    client.post("/tags", json={"name": "Database"}, headers=headers)
    client.post("/tags", json={"name": "Backend"}, headers=headers)
    client.post("/tags", json={"name": "Cloud"}, headers=headers)
    client.post("/tags", json={"name": "Infrastructure"}, headers=headers)

    # 4. Get all tags
    res_list = client.get("/tags", headers=headers)
    assert res_list.status_code == 200
    tag_names = [t["name"] for t in res_list.json()]
    assert "PostgreSQL" in tag_names
    assert "Database" in tag_names

    # 5. Get Tag by ID
    tag_id = res_list.json()[0]["id"]
    res_get = client.get(f"/tags/{tag_id}", headers=headers)
    assert res_get.status_code == 200
    assert res_get.json()["id"] == tag_id

    # 6. Non-existing tag
    assert client.get("/tags/999999", headers=headers).status_code == 404


def test_sprint9_decision_tag_association():
    token = get_token("decision_tag_tester@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Ensure tags exist
    t1 = client.post("/tags", json={"name": "PostgreSQL"}, headers=headers).json()
    t2 = client.post("/tags", json={"name": "Database"}, headers=headers).json()
    t3 = client.post("/tags", json={"name": "Backend"}, headers=headers).json()

    # 1. Create decision
    dec_res = client.post(
        "/decisions",
        json={
            "title": "Select Primary Database",
            "problem_statement": "Select high performance SQL database",
            "category": "Technology"
        },
        headers=headers
    )
    assert dec_res.status_code == 201
    dec_id = dec_res.json()["id"]

    # 2. Get tags
    tags_res = client.get("/tags", headers=headers)
    all_tags = tags_res.json()
    assert len(all_tags) >= 2
    tag_ids = [t["id"] for t in all_tags[:2]]

    # 3. Assign tags to decision
    assign_res = client.post(f"/decisions/{dec_id}/tags", json={"tag_ids": tag_ids}, headers=headers)
    assert assign_res.status_code == 200
    assigned = assign_res.json()
    assert len(assigned) >= len(tag_ids)

    # 4. Get decision tags
    get_tags_res = client.get(f"/decisions/{dec_id}/tags", headers=headers)
    assert get_tags_res.status_code == 200
    assert len(get_tags_res.json()) >= len(tag_ids)

    # 5. Remove a tag from decision
    removed_tag_id = tag_ids[0]
    del_res = client.delete(f"/decisions/{dec_id}/tags/{removed_tag_id}", headers=headers)
    assert del_res.status_code == 200

    # Verify removed
    get_tags_res_after = client.get(f"/decisions/{dec_id}/tags", headers=headers)
    remaining_ids = [t["id"] for t in get_tags_res_after.json()]
    assert removed_tag_id not in remaining_ids


def test_sprint9_search_filtering_sorting_pagination():
    token = get_token("search_tester@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Create several decisions with distinct categories and titles
    d1 = client.post("/decisions", json={"title": "PostgreSQL Migration Plan", "problem_statement": "Migrate database to RDS PostgreSQL", "category": "Technology"}, headers=headers).json()
    d2 = client.post("/decisions", json={"title": "AWS Cloud Infrastructure", "problem_statement": "Set up VPC and EKS clusters", "category": "Infrastructure"}, headers=headers).json()
    d3 = client.post("/decisions", json={"title": "Q3 Budget Plan", "problem_statement": "Allocate engineering compute budget", "category": "Finance"}, headers=headers).json()

    # Assign PostgreSQL tag to d1
    client.post("/tags", json={"name": "PostgreSQL"}, headers=headers)
    tags_res = client.get("/tags", headers=headers).json()
    pg_tag = next((t for t in tags_res if t["name"] == "PostgreSQL"), None)
    if pg_tag:
        client.post(f"/decisions/{d1['id']}/tags", json={"tag_ids": [pg_tag["id"]]}, headers=headers)

    # Update d1 status to Approved
    client.patch(f"/decisions/{d1['id']}/status", json={"status": "Approved"}, headers=headers)

    # 1. Keyword search (q=database)
    res_search = client.get("/decisions/search?q=database", headers=headers)
    assert res_search.status_code == 200
    items = res_search.json()["items"]
    assert any("database" in i["problem_statement"].lower() or "database" in i["title"].lower() for i in items)

    # 2. Category filter (category=Technology)
    res_cat = client.get("/decisions?category=Technology", headers=headers)
    assert res_cat.status_code == 200
    assert all(i["category"] == "Technology" for i in res_cat.json())

    # 3. Status filter (status=Approved)
    res_status = client.get("/decisions?status=Approved", headers=headers)
    assert res_status.status_code == 200
    assert all(i["status"] == "Approved" for i in res_status.json())

    # 4. Tag filter (tag=PostgreSQL)
    if pg_tag:
        res_tag = client.get("/decisions?tag=PostgreSQL", headers=headers)
        assert res_tag.status_code == 200
        assert len(res_tag.json()) >= 1

    # 5. Combined Search & Filters
    res_combined = client.get("/decisions/search?q=PostgreSQL&category=Technology&status=Approved", headers=headers)
    assert res_combined.status_code == 200
    assert res_combined.json()["total"] >= 1

    # 6. Pagination
    res_page = client.get("/decisions?page=1&page_size=2", headers=headers)
    assert res_page.status_code == 200
    page_data = res_page.json()
    assert page_data["page"] == 1
    assert page_data["page_size"] == 2
    assert "total" in page_data

    # 7. Sorting
    res_sort_asc = client.get("/decisions?sort=created_at&order=asc", headers=headers)
    assert res_sort_asc.status_code == 200
    res_sort_desc = client.get("/decisions?sort=created_at&order=desc", headers=headers)
    assert res_sort_desc.status_code == 200


def test_sprint9_decision_timeline():
    token = get_token("timeline_tester@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create Decision
    dec = client.post("/decisions", json={"title": "Authentication Strategy", "problem_statement": "Select OAuth2 or SAML", "category": "Security"}, headers=headers).json()
    dec_id = dec["id"]

    # 2. Add alternative
    client.post(f"/decisions/{dec_id}/alternatives", json={"name": "OAuth2 / OIDC", "description": "Token-based standard", "pros": "Widely supported", "cons": "Token expiration", "estimated_cost": 500.0, "feasibility_score": 4, "risk_level": "Low"}, headers=headers)

    # 3. Add comment
    client.post(f"/decisions/{dec_id}/comments", json={"content": "Looks solid, team agrees"}, headers=headers)

    # 4. Add meeting note
    client.post(f"/decisions/{dec_id}/meeting-notes", json={"title": "Security Architecture Review", "content": "Reviewed OIDC flow"}, headers=headers)

    # 5. Get timeline
    timeline_res = client.get(f"/decisions/{dec_id}/timeline", headers=headers)
    assert timeline_res.status_code == 200
    t_data = timeline_res.json()
    assert t_data["decision_id"] == dec_id
    assert len(t_data["events"]) >= 4

    event_types = [e["event_type"] for e in t_data["events"]]
    assert "Decision created" in event_types
    assert "Alternative created" in event_types
    assert "Comment added" in event_types
    assert "Meeting note added" in event_types


def test_sprint9_error_handling_and_auth():
    # 1. No JWT -> 401
    assert client.get("/decisions/search?q=test").status_code == 401
    assert client.get("/tags").status_code == 401

    token = get_token("error_tester@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Non-existing Decision -> 404
    assert client.get("/decisions/999999/timeline", headers=headers).status_code == 404

    # 3. Invalid Sort field -> 422
    assert client.get("/decisions/search?sort=invalid_column", headers=headers).status_code == 422

    # 4. Invalid Status filter -> 422
    assert client.get("/decisions/search?status=NonExistentStatus", headers=headers).status_code == 422

    # 5. Non-existing category filter -> empty list / total = 0, NOT error
    res_cat = client.get("/decisions?category=NonExistentCategory", headers=headers)
    assert res_cat.status_code == 200
    assert len(res_cat.json()) == 0
