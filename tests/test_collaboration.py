import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_auth_headers(user_email: str, password: str = "Password123!"):
    login_res = client.post("/users/login", json={"email": user_email, "password": password})
    assert login_res.status_code == 200, f"Login failed for {user_email}: {login_res.text}"
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def setup_users_and_decision():
    # Register User 1 (Employee)
    u1_payload = {
        "full_name": "Alice Employee",
        "email": "alice@example.com",
        "role": "Employee",
        "password": "Password123!",
        "employee_id": "EMP_ALICE_01"
    }
    r1 = client.post("/users", json=u1_payload)
    assert r1.status_code == 201

    # Register User 2 (Employee - Other User)
    u2_payload = {
        "full_name": "Bob Employee",
        "email": "bob@example.com",
        "role": "Employee",
        "password": "Password123!",
        "employee_id": "EMP_BOB_01"
    }
    r2 = client.post("/users", json=u2_payload)
    assert r2.status_code == 201

    h1 = get_auth_headers("alice@example.com")
    h2 = get_auth_headers("bob@example.com")

    # Create Decision as User 1
    d_payload = {
        "title": "Select Database Architecture",
        "problem_statement": "We need a robust database for high-throughput transactional and relational workloads.",
        "category": "Infrastructure"
    }
    rd = client.post("/decisions", json=d_payload, headers=h1)
    assert rd.status_code == 201
    decision_id = rd.json()["id"]

    return {
        "user1_headers": h1,
        "user2_headers": h2,
        "decision_id": decision_id,
        "user1_id": r1.json()["id"],
        "user2_id": r2.json()["id"]
    }


def test_unauthenticated_requests_return_401(setup_users_and_decision):
    d_id = setup_users_and_decision["decision_id"]

    assert client.post(f"/decisions/{d_id}/comments", json={"content": "test"}).status_code == 401
    assert client.get(f"/decisions/{d_id}/comments").status_code == 401
    assert client.get("/comments/1").status_code == 401
    assert client.put("/comments/1", json={"content": "test"}).status_code == 401
    assert client.delete("/comments/1").status_code == 401

    assert client.post(f"/decisions/{d_id}/threads", json={"title": "test"}).status_code == 401
    assert client.get(f"/decisions/{d_id}/threads").status_code == 401
    assert client.get("/threads/1").status_code == 401
    assert client.put("/threads/1", json={"title": "test"}).status_code == 401
    assert client.delete("/threads/1").status_code == 401

    assert client.post(f"/decisions/{d_id}/meeting-notes", json={"title": "m", "content": "c"}).status_code == 401
    assert client.get(f"/decisions/{d_id}/meeting-notes").status_code == 401
    assert client.put(f"/decisions/{d_id}/rationale", json={"rationale": "r"}).status_code == 401


def test_comments_workflow(setup_users_and_decision):
    h1 = setup_users_and_decision["user1_headers"]
    h2 = setup_users_and_decision["user2_headers"]
    d_id = setup_users_and_decision["decision_id"]

    # 1. Non-existing decision
    r_404 = client.post("/decisions/99999/comments", json={"content": "Test comment"}, headers=h1)
    assert r_404.status_code == 404
    assert r_404.json()["detail"] == "Decision not found"

    # 2. Add 3 comments
    c1 = client.post(f"/decisions/{d_id}/comments", json={"content": "PostgreSQL provides better relational support."}, headers=h1)
    assert c1.status_code == 201
    c1_data = c1.json()
    assert c1_data["decision_id"] == d_id
    assert c1_data["content"] == "PostgreSQL provides better relational support."

    c2 = client.post(f"/decisions/{d_id}/comments", json={"content": "MongoDB may provide easier horizontal scaling."}, headers=h2)
    assert c2.status_code == 201

    c3 = client.post(f"/decisions/{d_id}/comments", json={"content": "Cost analysis should also be considered."}, headers=h1)
    assert c3.status_code == 201

    # 3. Get all comments for decision
    r_comments = client.get(f"/decisions/{d_id}/comments", headers=h1)
    assert r_comments.status_code == 200
    comments_list = r_comments.json()
    assert len(comments_list) == 3

    # 4. Get single comment by ID
    c1_id = c1_data["id"]
    r_single = client.get(f"/comments/{c1_id}", headers=h1)
    assert r_single.status_code == 200
    assert r_single.json()["id"] == c1_id

    # 5. Non-existing comment by ID
    assert client.get("/comments/99999", headers=h1).status_code == 404

    # 6. Update comment by owner
    up_res = client.put(f"/comments/{c1_id}", json={"content": "Updated discussion: PostgreSQL provides strong relational support and a mature ecosystem."}, headers=h1)
    assert up_res.status_code == 200
    assert up_res.json()["content"] == "Updated discussion: PostgreSQL provides strong relational support and a mature ecosystem."

    # 7. Update comment by non-owner -> 403 Forbidden
    unauth_up = client.put(f"/comments/{c1_id}", json={"content": "Hacked content"}, headers=h2)
    assert unauth_up.status_code == 403

    # 8. Delete comment by non-owner -> 403 Forbidden
    unauth_del = client.delete(f"/comments/{c1_id}", headers=h2)
    assert unauth_del.status_code == 403

    # 9. Delete comment by owner
    del_res = client.delete(f"/comments/{c1_id}", headers=h1)
    assert del_res.status_code == 200

    # 10. Verify comment deleted
    assert client.get(f"/comments/{c1_id}", headers=h1).status_code == 404


def test_discussion_threads_and_replies_workflow(setup_users_and_decision):
    h1 = setup_users_and_decision["user1_headers"]
    h2 = setup_users_and_decision["user2_headers"]
    d_id = setup_users_and_decision["decision_id"]

    # 1. Create Discussion Thread
    t_payload = {
        "title": "Database scalability",
        "description": "Let's discuss the scalability requirements before finalizing the database."
    }
    r_thread = client.post(f"/decisions/{d_id}/threads", json=t_payload, headers=h1)
    assert r_thread.status_code == 201
    thread_data = r_thread.json()
    assert thread_data["title"] == "Database scalability"
    assert thread_data["status"] == "Open"
    thread_id = thread_data["id"]

    # 2. Add Replies to Thread
    rep1 = client.post(f"/threads/{thread_id}/comments", json={"content": "PostgreSQL can support our expected workload with proper indexing and scaling."}, headers=h1)
    assert rep1.status_code == 201
    assert rep1.json()["thread_id"] == thread_id

    rep2 = client.post(f"/threads/{thread_id}/comments", json={"content": "Read replicas can also be added for read-heavy operations."}, headers=h2)
    assert rep2.status_code == 201

    # 3. Get Thread Replies
    r_replies = client.get(f"/threads/{thread_id}/comments", headers=h1)
    assert r_replies.status_code == 200
    assert len(r_replies.json()) == 2

    # 4. Get Threads for Decision
    r_all_threads = client.get(f"/decisions/{d_id}/threads", headers=h1)
    assert r_all_threads.status_code == 200
    threads_list = r_all_threads.json()
    assert len(threads_list) == 1
    assert len(threads_list[0]["replies"]) == 2

    # 5. Get Thread by ID
    r_single_thread = client.get(f"/threads/{thread_id}", headers=h1)
    assert r_single_thread.status_code == 200
    assert r_single_thread.json()["id"] == thread_id

    # 6. Update Thread
    up_t = client.put(f"/threads/{thread_id}", json={"title": "Database Scalability & Performance", "status": "Closed"}, headers=h1)
    assert up_t.status_code == 200
    assert up_t.json()["title"] == "Database Scalability & Performance"
    assert up_t.json()["status"] == "Closed"

    # 7. Non-owner update -> 403
    assert client.put(f"/threads/{thread_id}", json={"title": "Hijacked Title"}, headers=h2).status_code == 403

    # 8. Delete Thread by owner
    del_t = client.delete(f"/threads/{thread_id}", headers=h1)
    assert del_t.status_code == 200

    # 9. Verify Thread deleted
    assert client.get(f"/threads/{thread_id}", headers=h1).status_code == 404


def test_meeting_notes_workflow(setup_users_and_decision):
    h1 = setup_users_and_decision["user1_headers"]
    h2 = setup_users_and_decision["user2_headers"]
    d_id = setup_users_and_decision["decision_id"]

    # 1. Create Meeting Note
    mn_payload = {
        "title": "Architecture Alignment Sync",
        "content": "The team agreed on PostgreSQL as the primary data store after weighing scalability vs consistency."
    }
    r_mn = client.post(f"/decisions/{d_id}/meeting-notes", json=mn_payload, headers=h1)
    assert r_mn.status_code == 201
    mn_data = r_mn.json()
    assert mn_data["title"] == "Architecture Alignment Sync"
    note_id = mn_data["id"]

    # 2. Get Meeting Notes for Decision
    r_notes = client.get(f"/decisions/{d_id}/meeting-notes", headers=h1)
    assert r_notes.status_code == 200
    assert len(r_notes.json()) == 1

    # 3. Get Meeting Note by ID
    r_single = client.get(f"/meeting-notes/{note_id}", headers=h1)
    assert r_single.status_code == 200
    assert r_single.json()["id"] == note_id

    # 4. Update Meeting Note
    up_mn = client.put(f"/meeting-notes/{note_id}", json={"title": "Updated Architecture Alignment Sync"}, headers=h1)
    assert up_mn.status_code == 200
    assert up_mn.json()["title"] == "Updated Architecture Alignment Sync"

    # 5. Non-owner update -> 403
    assert client.put(f"/meeting-notes/{note_id}", json={"title": "Hacked Sync"}, headers=h2).status_code == 403

    # 6. Delete Meeting Note
    assert client.delete(f"/meeting-notes/{note_id}", headers=h1).status_code == 200
    assert client.get(f"/meeting-notes/{note_id}", headers=h1).status_code == 404


def test_decision_rationale_workflow(setup_users_and_decision):
    h1 = setup_users_and_decision["user1_headers"]
    h2 = setup_users_and_decision["user2_headers"]
    d_id = setup_users_and_decision["decision_id"]

    # 1. Update Decision Rationale
    rat_payload = {
        "rationale": "PostgreSQL was selected because it provided the best balance between reliability, feasibility, cost, and operational risk."
    }
    r_rat = client.put(f"/decisions/{d_id}/rationale", json=rat_payload, headers=h1)
    assert r_rat.status_code == 200
    assert r_rat.json()["rationale"] == rat_payload["rationale"]

    # 2. Get Decision Rationale
    g_rat = client.get(f"/decisions/{d_id}/rationale", headers=h1)
    assert g_rat.status_code == 200
    assert g_rat.json()["rationale"] == rat_payload["rationale"]

    # 3. Get Decision includes rationale
    g_dec = client.get(f"/decisions/{d_id}", headers=h1)
    assert g_dec.status_code == 200
    assert g_dec.json()["rationale"] == rat_payload["rationale"]

    # 4. Non-owner update rationale -> 403
    unauth_rat = client.put(f"/decisions/{d_id}/rationale", json={"rationale": "Unauthorized change"}, headers=h2)
    assert unauth_rat.status_code == 403
