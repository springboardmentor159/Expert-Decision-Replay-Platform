import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def create_user_and_login(full_name: str, email: str, role: str, emp_id: str):
    user_data = {
        "full_name": full_name,
        "email": email,
        "role": role,
        "password": "Password123!",
        "employee_id": emp_id,
        "department": "Engineering",
        "designation": "Software Engineer",
        "phone_number": "+1234567890"
    }
    client.post("/users", json=user_data)
    login_resp = client.post("/auth/login", json={"email": email, "password": "Password123!"})
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_decision(headers):
    payload = {
        "title": "Select Cloud Provider",
        "problem_statement": "Select the primary cloud infrastructure for hosting",
        "category": "Infrastructure"
    }
    res = client.post("/decisions", json=payload, headers=headers)
    assert res.status_code == 201
    return res.json()


def test_unauthenticated_requests():
    # Attempt calls without JWT -> 401
    assert client.post("/decisions/1/comments", json={"content": "test"}).status_code == 401
    assert client.get("/decisions/1/comments").status_code == 401
    assert client.get("/comments/1").status_code == 401
    assert client.put("/comments/1", json={"content": "test"}).status_code == 401
    assert client.delete("/comments/1").status_code == 401

    assert client.post("/decisions/1/threads", json={"title": "Thread 1"}).status_code == 401
    assert client.get("/decisions/1/threads").status_code == 401
    assert client.get("/threads/1").status_code == 401
    assert client.put("/threads/1", json={"title": "Updated"}).status_code == 401
    assert client.delete("/threads/1").status_code == 401
    assert client.post("/threads/1/comments", json={"content": "Reply"}).status_code == 401
    assert client.get("/threads/1/comments").status_code == 401

    assert client.post("/decisions/1/meeting-notes", json={"title": "Note 1", "content": "Notes"}).status_code == 401
    assert client.get("/decisions/1/meeting-notes").status_code == 401
    assert client.get("/meeting-notes/1").status_code == 401
    assert client.put("/meeting-notes/1", json={"title": "Updated Note"}).status_code == 401
    assert client.delete("/meeting-notes/1").status_code == 401

    assert client.put("/decisions/1/rationale", json={"rationale": "Because"}).status_code == 401
    assert client.get("/decisions/1/rationale").status_code == 401


def test_non_existent_resources_404():
    headers = create_user_and_login("Alice Dev", "alice@example.com", "Employee", "EMP-001")

    # Non-existent decision
    assert client.post("/decisions/99999/comments", json={"content": "comment"}, headers=headers).status_code == 404
    assert client.get("/decisions/99999/comments", headers=headers).status_code == 404
    assert client.post("/decisions/99999/threads", json={"title": "thread"}, headers=headers).status_code == 404
    assert client.get("/decisions/99999/threads", headers=headers).status_code == 404
    assert client.post("/decisions/99999/meeting-notes", json={"title": "note", "content": "content"}, headers=headers).status_code == 404
    assert client.get("/decisions/99999/meeting-notes", headers=headers).status_code == 404
    assert client.put("/decisions/99999/rationale", json={"rationale": "rationale"}, headers=headers).status_code == 404
    assert client.get("/decisions/99999/rationale", headers=headers).status_code == 404

    # Non-existent direct IDs
    assert client.get("/comments/99999", headers=headers).status_code == 404
    assert client.put("/comments/99999", json={"content": "edit"}, headers=headers).status_code == 404
    assert client.delete("/comments/99999", headers=headers).status_code == 404

    assert client.get("/threads/99999", headers=headers).status_code == 404
    assert client.put("/threads/99999", json={"title": "edit"}, headers=headers).status_code == 404
    assert client.delete("/threads/99999", headers=headers).status_code == 404
    assert client.post("/threads/99999/comments", json={"content": "reply"}, headers=headers).status_code == 404
    assert client.get("/threads/99999/comments", headers=headers).status_code == 404

    assert client.get("/meeting-notes/99999", headers=headers).status_code == 404
    assert client.put("/meeting-notes/99999", json={"title": "edit"}, headers=headers).status_code == 404
    assert client.delete("/meeting-notes/99999", headers=headers).status_code == 404


def test_comments_full_workflow():
    headers_alice = create_user_and_login("Alice Comments", "alice_c@example.com", "Employee", "EMP-COM-01")
    headers_bob = create_user_and_login("Bob Comments", "bob_c@example.com", "Employee", "EMP-COM-02")
    decision = create_decision(headers_alice)
    dec_id = decision["id"]

    # Step 3: Create at least 3 comments
    c1 = client.post(f"/decisions/{dec_id}/comments", json={"content": "PostgreSQL provides better relational support."}, headers=headers_alice).json()
    c2 = client.post(f"/decisions/{dec_id}/comments", json={"content": "MongoDB may provide easier horizontal scaling."}, headers=headers_bob).json()
    c3 = client.post(f"/decisions/{dec_id}/comments", json={"content": "Cost analysis should also be considered."}, headers=headers_alice).json()

    assert c1["content"] == "PostgreSQL provides better relational support."
    assert c1["decision_id"] == dec_id
    assert c2["decision_id"] == dec_id
    assert c3["decision_id"] == dec_id

    # Step 4: Get comments for decision
    res = client.get(f"/decisions/{dec_id}/comments", headers=headers_alice)
    assert res.status_code == 200
    comments = res.json()
    assert len(comments) == 3

    # Step 5: Get comment by ID
    res_single = client.get(f"/comments/{c1['id']}", headers=headers_alice)
    assert res_single.status_code == 200
    assert res_single.json()["id"] == c1["id"]

    # Step 6: Update comment (Author)
    update_res = client.put(f"/comments/{c1['id']}", json={"content": "Updated: PostgreSQL provides strong relational support."}, headers=headers_alice)
    assert update_res.status_code == 200
    assert update_res.json()["content"] == "Updated: PostgreSQL provides strong relational support."

    # Authorization test: Bob cannot edit Alice's comment
    forbidden_edit = client.put(f"/comments/{c1['id']}", json={"content": "Hacked content"}, headers=headers_bob)
    assert forbidden_edit.status_code == 403

    # Authorization test: Bob cannot delete Alice's comment
    forbidden_delete = client.delete(f"/comments/{c1['id']}", headers=headers_bob)
    assert forbidden_delete.status_code == 403

    # Step 7: Delete comment (Author)
    del_res = client.delete(f"/comments/{c1['id']}", headers=headers_alice)
    assert del_res.status_code == 200

    # Verify deleted
    assert client.get(f"/comments/{c1['id']}", headers=headers_alice).status_code == 404
    comments_after = client.get(f"/decisions/{dec_id}/comments", headers=headers_alice).json()
    assert len(comments_after) == 2


def test_discussion_threads_and_replies_workflow():
    headers_alice = create_user_and_login("Alice Threads", "alice_t@example.com", "Employee", "EMP-THR-01")
    headers_bob = create_user_and_login("Bob Threads", "bob_t@example.com", "Employee", "EMP-THR-02")
    decision = create_decision(headers_alice)
    dec_id = decision["id"]

    # Step 8: Create Discussion Thread
    thread_payload = {
        "title": "Database scalability",
        "description": "Let's discuss the scalability requirements before finalizing the database."
    }
    t_res = client.post(f"/decisions/{dec_id}/threads", json=thread_payload, headers=headers_alice)
    assert t_res.status_code == 201
    thread = t_res.json()
    thread_id = thread["id"]
    assert thread["title"] == "Database scalability"
    assert thread["status"] == "Open"

    # Get Threads for Decision
    threads_list = client.get(f"/decisions/{dec_id}/threads", headers=headers_alice).json()
    assert len(threads_list) == 1

    # Step 9: Add Replies to thread
    r1 = client.post(f"/threads/{thread_id}/comments", json={"content": "PostgreSQL can support our expected workload with proper indexing and scaling."}, headers=headers_alice)
    assert r1.status_code == 201
    assert r1.json()["thread_id"] == thread_id
    assert r1.json()["decision_id"] == dec_id

    r2 = client.post(f"/threads/{thread_id}/comments", json={"content": "We can also use read replicas for scaling read heavy queries."}, headers=headers_bob)
    assert r2.status_code == 201

    # Get Replies for thread
    replies = client.get(f"/threads/{thread_id}/comments", headers=headers_alice).json()
    assert len(replies) == 2
    assert replies[0]["content"] == "PostgreSQL can support our expected workload with proper indexing and scaling."

    # Get Thread by ID (with nested replies)
    thread_detail = client.get(f"/threads/{thread_id}", headers=headers_alice).json()
    assert thread_detail["id"] == thread_id
    assert len(thread_detail["comments"]) == 2

    # Update thread (Author)
    update_t = client.put(f"/threads/{thread_id}", json={"status": "Closed", "title": "Database scalability [Resolved]"}, headers=headers_alice)
    assert update_t.status_code == 200
    assert update_t.json()["status"] == "Closed"

    # Bob cannot update Alice's thread
    assert client.put(f"/threads/{thread_id}", json={"title": "Reopened"}, headers=headers_bob).status_code == 403
    # Bob cannot delete Alice's thread
    assert client.delete(f"/threads/{thread_id}", headers=headers_bob).status_code == 403

    # Delete thread (Author)
    assert client.delete(f"/threads/{thread_id}", headers=headers_alice).status_code == 200
    assert client.get(f"/threads/{thread_id}", headers=headers_alice).status_code == 404


def test_meeting_notes_workflow():
    headers_alice = create_user_and_login("Alice Notes", "alice_n@example.com", "Employee", "EMP-NOT-01")
    headers_bob = create_user_and_login("Bob Notes", "bob_n@example.com", "Employee", "EMP-NOT-02")
    decision = create_decision(headers_alice)
    dec_id = decision["id"]

    # Step 10: Create Meeting Note
    note_payload = {
        "title": "Architecture Review Meeting",
        "content": "Discussed PostgreSQL vs MongoDB. Agreed on relational consistency requirement.",
        "meeting_date": "2026-08-21T10:00:00"
    }
    n_res = client.post(f"/decisions/{dec_id}/meeting-notes", json=note_payload, headers=headers_alice)
    assert n_res.status_code == 201
    note = n_res.json()
    note_id = note["id"]
    assert note["title"] == "Architecture Review Meeting"
    assert note["decision_id"] == dec_id

    # Get Meeting notes for decision
    notes_list = client.get(f"/decisions/{dec_id}/meeting-notes", headers=headers_alice).json()
    assert len(notes_list) == 1

    # Get Meeting note by ID
    get_note = client.get(f"/meeting-notes/{note_id}", headers=headers_alice).json()
    assert get_note["id"] == note_id

    # Update note (Author)
    updated_note = client.put(f"/meeting-notes/{note_id}", json={"title": "Architecture Review Meeting (Finalized)"}, headers=headers_alice)
    assert updated_note.status_code == 200
    assert updated_note.json()["title"] == "Architecture Review Meeting (Finalized)"

    # Bob cannot update or delete Alice's note
    assert client.put(f"/meeting-notes/{note_id}", json={"title": "Hacked"}, headers=headers_bob).status_code == 403
    assert client.delete(f"/meeting-notes/{note_id}", headers=headers_bob).status_code == 403

    # Delete note (Author)
    assert client.delete(f"/meeting-notes/{note_id}", headers=headers_alice).status_code == 200
    assert client.get(f"/meeting-notes/{note_id}", headers=headers_alice).status_code == 404


def test_decision_rationale_workflow():
    headers_alice = create_user_and_login("Alice Rationale", "alice_r@example.com", "Employee", "EMP-RAT-01")
    headers_bob = create_user_and_login("Bob Rationale", "bob_r@example.com", "Employee", "EMP-RAT-02")
    headers_admin = create_user_and_login("Admin Rationale", "admin_r@example.com", "Administrator", "EMP-RAT-ADM")
    decision = create_decision(headers_alice)
    dec_id = decision["id"]

    # Step 11: Add Decision Rationale
    rationale_text = "PostgreSQL was selected because it provided the best balance between reliability, feasibility, cost, and operational risk."
    put_res = client.put(f"/decisions/{dec_id}/rationale", json={"rationale": rationale_text}, headers=headers_alice)
    assert put_res.status_code == 200
    assert put_res.json()["rationale"] == rationale_text

    # Retrieve rationale via GET /decisions/{id}/rationale
    get_rat = client.get(f"/decisions/{dec_id}/rationale", headers=headers_alice)
    assert get_rat.status_code == 200
    assert get_rat.json()["rationale"] == rationale_text

    # Retrieve decision and verify rationale is included
    get_dec = client.get(f"/decisions/{dec_id}", headers=headers_alice)
    assert get_dec.status_code == 200
    assert get_dec.json()["rationale"] == rationale_text

    # Bob (non-creator Employee) cannot update Alice's decision rationale
    assert client.put(f"/decisions/{dec_id}/rationale", json={"rationale": "Changed by Bob"}, headers=headers_bob).status_code == 403

    # Administrator can update decision rationale
    admin_put = client.put(f"/decisions/{dec_id}/rationale", json={"rationale": "Admin approved rationale"}, headers=headers_admin)
    assert admin_put.status_code == 200
    assert admin_put.json()["rationale"] == "Admin approved rationale"


def test_admin_and_manager_moderation_permissions():
    headers_alice = create_user_and_login("Alice Regular", "alice_reg@example.com", "Employee", "EMP-REG-01")
    headers_manager = create_user_and_login("Manager User", "manager@example.com", "Manager", "EMP-MGR-01")
    decision = create_decision(headers_alice)
    dec_id = decision["id"]

    # Alice creates a comment, thread, and note
    comment = client.post(f"/decisions/{dec_id}/comments", json={"content": "Alice's comment"}, headers=headers_alice).json()
    thread = client.post(f"/decisions/{dec_id}/threads", json={"title": "Alice's thread"}, headers=headers_alice).json()
    note = client.post(f"/decisions/{dec_id}/meeting-notes", json={"title": "Alice's note", "content": "Note text"}, headers=headers_alice).json()

    # Manager can update/delete Alice's items
    mgr_c_update = client.put(f"/comments/{comment['id']}", json={"content": "Moderated by Manager"}, headers=headers_manager)
    assert mgr_c_update.status_code == 200
    assert mgr_c_update.json()["content"] == "Moderated by Manager"

    mgr_t_update = client.put(f"/threads/{thread['id']}", json={"title": "Moderated Thread"}, headers=headers_manager)
    assert mgr_t_update.status_code == 200

    mgr_n_update = client.put(f"/meeting-notes/{note['id']}", json={"title": "Moderated Note"}, headers=headers_manager)
    assert mgr_n_update.status_code == 200

    # Manager can delete them
    assert client.delete(f"/comments/{comment['id']}", headers=headers_manager).status_code == 200
    assert client.delete(f"/threads/{thread['id']}", headers=headers_manager).status_code == 200
    assert client.delete(f"/meeting-notes/{note['id']}", headers=headers_manager).status_code == 200
