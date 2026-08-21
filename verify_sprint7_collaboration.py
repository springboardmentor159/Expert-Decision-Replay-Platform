import sys
from datetime import datetime
from fastapi.testclient import TestClient

from app.main import app
from app.db.database import SessionLocal
from app.models.user import User
from app.models.decision import Decision
from app.models.comment import Comment
from app.models.discussion_thread import DiscussionThread
from app.models.meeting_note import MeetingNote

client = TestClient(app)


def run_verification():
    print("=" * 75)
    print(" SPRINT 7: DISCUSSION & COLLABORATION MODULE - VERIFICATION REPORT")
    print("=" * 75)

    passed_tests = 0
    total_tests = 0

    def assert_check(condition, title, details=""):
        nonlocal passed_tests, total_tests
        total_tests += 1
        if condition:
            passed_tests += 1
            print(f" [PASS] {title}")
        else:
            print(f" [FAIL] {title} -> {details}")

    # 0. Clean up previous test users if any
    test_user_email_1 = "sprint7_alice@example.com"
    test_user_email_2 = "sprint7_bob@example.com"
    test_user_email_admin = "sprint7_admin@example.com"

    db = SessionLocal()
    for em in [test_user_email_1, test_user_email_2, test_user_email_admin]:
        u = db.query(User).filter(User.email == em).first()
        if u:
            # Delete user's decisions & comments
            db.query(Decision).filter(Decision.created_by == u.id).delete(synchronize_session=False)
            db.query(User).filter(User.id == u.id).delete(synchronize_session=False)
            db.commit()
    db.close()

    # Step 1: Login / Register Users & Obtain JWT Tokens
    print("\n--- Step 1: Authentication & User Setup ---")
    alice_data = {
        "full_name": "Alice Architect",
        "email": test_user_email_1,
        "role": "Employee",
        "password": "Password123!",
        "employee_id": "EMP_S7_001",
        "department": "Platform Engineering",
        "designation": "Staff Engineer",
        "phone_number": "+1-555-0701"
    }
    res_reg_1 = client.post("/users", json=alice_data)
    assert_check(res_reg_1.status_code == 201, "Register Alice (Employee) (201 Created)")

    bob_data = {
        "full_name": "Bob Reviewer",
        "email": test_user_email_2,
        "role": "Employee",
        "password": "Password123!",
        "employee_id": "EMP_S7_002",
        "department": "Platform Engineering",
        "designation": "Senior Engineer",
        "phone_number": "+1-555-0702"
    }
    res_reg_2 = client.post("/users", json=bob_data)
    assert_check(res_reg_2.status_code == 201, "Register Bob (Employee) (201 Created)")

    admin_data = {
        "full_name": "Admin Leader",
        "email": test_user_email_admin,
        "role": "Administrator",
        "password": "Password123!",
        "employee_id": "EMP_S7_ADM",
        "department": "Executive",
        "designation": "Director",
        "phone_number": "+1-555-0799"
    }
    res_reg_adm = client.post("/users", json=admin_data)
    assert_check(res_reg_adm.status_code == 201, "Register Admin (Administrator) (201 Created)")

    # Log in
    login_alice = client.post("/auth/login", json={"email": test_user_email_1, "password": "Password123!"})
    token_alice = login_alice.json()["access_token"]
    headers_alice = {"Authorization": f"Bearer {token_alice}"}
    assert_check(login_alice.status_code == 200 and bool(token_alice), "Alice Login & JWT Acquisition (200 OK)")

    login_bob = client.post("/auth/login", json={"email": test_user_email_2, "password": "Password123!"})
    token_bob = login_bob.json()["access_token"]
    headers_bob = {"Authorization": f"Bearer {token_bob}"}
    assert_check(login_bob.status_code == 200 and bool(token_bob), "Bob Login & JWT Acquisition (200 OK)")

    login_admin = client.post("/auth/login", json={"email": test_user_email_admin, "password": "Password123!"})
    token_admin = login_admin.json()["access_token"]
    headers_admin = {"Authorization": f"Bearer {token_admin}"}
    assert_check(login_admin.status_code == 200 and bool(token_admin), "Admin Login & JWT Acquisition (200 OK)")

    # Step 2: Create Decision
    print("\n--- Step 2: Create Decision ---")
    decision_payload = {
        "title": "Select Database Engine for High-Throughput Analytics",
        "problem_statement": "Select the appropriate primary datastore supporting transactional reliability and analytical scale.",
        "category": "Architecture"
    }
    res_dec = client.post("/decisions", json=decision_payload, headers=headers_alice)
    assert_check(res_dec.status_code == 201, "Create Decision via POST /decisions (201 Created)")
    decision_id = res_dec.json()["id"]

    # Step 3: Create Comments
    print("\n--- Step 3: Create Comments for Decision ---")
    comment_1 = client.post(f"/decisions/{decision_id}/comments", json={"content": "PostgreSQL provides better relational support."}, headers=headers_alice)
    assert_check(comment_1.status_code == 201 and comment_1.json()["decision_id"] == decision_id, "Create Comment 1 (Alice)")

    comment_2 = client.post(f"/decisions/{decision_id}/comments", json={"content": "MongoDB may provide easier horizontal scaling."}, headers=headers_bob)
    assert_check(comment_2.status_code == 201 and comment_2.json()["decision_id"] == decision_id, "Create Comment 2 (Bob)")

    comment_3 = client.post(f"/decisions/{decision_id}/comments", json={"content": "Cost analysis should also be considered."}, headers=headers_alice)
    assert_check(comment_3.status_code == 201 and comment_3.json()["decision_id"] == decision_id, "Create Comment 3 (Alice)")

    c1_id = comment_1.json()["id"]
    c2_id = comment_2.json()["id"]
    c3_id = comment_3.json()["id"]

    # Step 4: Retrieve Comments for Decision
    print("\n--- Step 4: Retrieve Comments for Decision ---")
    comments_res = client.get(f"/decisions/{decision_id}/comments", headers=headers_alice)
    assert_check(comments_res.status_code == 200 and len(comments_res.json()) >= 3, f"GET /decisions/{decision_id}/comments returned {len(comments_res.json())} comments (200 OK)")

    # Step 5: Retrieve One Comment by ID
    print("\n--- Step 5: Retrieve One Comment by ID ---")
    c1_res = client.get(f"/comments/{c1_id}", headers=headers_alice)
    assert_check(c1_res.status_code == 200 and c1_res.json()["id"] == c1_id, f"GET /comments/{c1_id} (200 OK)")

    # Step 6: Update a Comment
    print("\n--- Step 6: Update a Comment ---")
    updated_comment_content = "Updated discussion: PostgreSQL provides strong relational support and a mature ecosystem."
    upd_res = client.put(f"/comments/{c1_id}", json={"content": updated_comment_content}, headers=headers_alice)
    assert_check(upd_res.status_code == 200 and upd_res.json()["content"] == updated_comment_content, f"PUT /comments/{c1_id} updated content successfully (200 OK)")

    # Step 7: Delete a Comment
    print("\n--- Step 7: Delete a Comment ---")
    del_res = client.delete(f"/comments/{c3_id}", headers=headers_alice)
    assert_check(del_res.status_code == 200, f"DELETE /comments/{c3_id} (200 OK)")

    get_del = client.get(f"/comments/{c3_id}", headers=headers_alice)
    assert_check(get_del.status_code == 404, "Verify deleted comment returns 404 Not Found")

    # Step 8: Create Discussion Thread
    print("\n--- Step 8: Create Discussion Thread ---")
    thread_payload = {
        "title": "Database scalability",
        "description": "Let's discuss the scalability requirements before finalizing the database."
    }
    thread_res = client.post(f"/decisions/{decision_id}/threads", json=thread_payload, headers=headers_alice)
    assert_check(thread_res.status_code == 201 and thread_res.json()["title"] == "Database scalability", "Create Discussion Thread via POST /decisions/{id}/threads (201 Created)")
    thread_id = thread_res.json()["id"]

    # Step 9: Add Replies to Discussion Thread
    print("\n--- Step 9: Add Replies to Discussion Thread ---")
    reply_1 = client.post(f"/threads/{thread_id}/comments", json={"content": "PostgreSQL can support our expected workload with proper indexing and scaling."}, headers=headers_alice)
    assert_check(reply_1.status_code == 201 and reply_1.json()["thread_id"] == thread_id, "Add Reply 1 to Thread (201 Created)")

    reply_2 = client.post(f"/threads/{thread_id}/comments", json={"content": "We can evaluate read replicas and connection pooling with PgBouncer."}, headers=headers_bob)
    assert_check(reply_2.status_code == 201 and reply_2.json()["thread_id"] == thread_id, "Add Reply 2 to Thread (201 Created)")

    thread_detail = client.get(f"/threads/{thread_id}", headers=headers_alice)
    assert_check(thread_detail.status_code == 200 and len(thread_detail.json()["comments"]) == 2, f"GET /threads/{thread_id} includes nested replies (200 OK)")

    # Step 10: Create Meeting Notes
    print("\n--- Step 10: Create Meeting Notes ---")
    meeting_note_payload = {
        "title": "Database Architecture Consensus Meeting",
        "content": "Meeting concluded with consensus on PostgreSQL for transactional durability with partitioned tables for historical log storage.",
        "meeting_date": "2026-08-21T14:00:00"
    }
    note_res = client.post(f"/decisions/{decision_id}/meeting-notes", json=meeting_note_payload, headers=headers_alice)
    assert_check(note_res.status_code == 201 and note_res.json()["decision_id"] == decision_id, "Create Meeting Note via POST /decisions/{id}/meeting-notes (201 Created)")
    note_id = note_res.json()["id"]

    notes_list = client.get(f"/decisions/{decision_id}/meeting-notes", headers=headers_alice)
    assert_check(notes_list.status_code == 200 and len(notes_list.json()) >= 1, f"GET /decisions/{decision_id}/meeting-notes returns meeting notes list (200 OK)")

    # Step 11: Add Decision Rationale
    print("\n--- Step 11: Add Decision Rationale ---")
    rationale_text = "PostgreSQL was selected because it provided the best balance between reliability, feasibility, cost, and operational risk."
    rat_res = client.put(f"/decisions/{decision_id}/rationale", json={"rationale": rationale_text}, headers=headers_alice)
    assert_check(rat_res.status_code == 200 and rat_res.json()["rationale"] == rationale_text, "PUT /decisions/{id}/rationale sets rationale on Decision (200 OK)")

    get_rat = client.get(f"/decisions/{decision_id}/rationale", headers=headers_alice)
    assert_check(get_rat.status_code == 200 and get_rat.json()["rationale"] == rationale_text, "GET /decisions/{id}/rationale returns rationale (200 OK)")

    # Step 12: Test Authentication (No JWT -> 401)
    print("\n--- Step 12: Test Authentication (Missing JWT -> 401) ---")
    endpoints_to_test_unauth = [
        ("POST", f"/decisions/{decision_id}/comments", {"content": "no auth"}),
        ("GET", f"/decisions/{decision_id}/comments", None),
        ("GET", f"/comments/{c1_id}", None),
        ("PUT", f"/comments/{c1_id}", {"content": "no auth"}),
        ("DELETE", f"/comments/{c1_id}", None),
        ("POST", f"/decisions/{decision_id}/threads", {"title": "no auth"}),
        ("GET", f"/decisions/{decision_id}/threads", None),
        ("GET", f"/threads/{thread_id}", None),
        ("PUT", f"/threads/{thread_id}", {"title": "no auth"}),
        ("DELETE", f"/threads/{thread_id}", None),
        ("POST", f"/threads/{thread_id}/comments", {"content": "no auth"}),
        ("POST", f"/decisions/{decision_id}/meeting-notes", {"title": "no auth", "content": "text"}),
        ("GET", f"/decisions/{decision_id}/meeting-notes", None),
        ("GET", f"/meeting-notes/{note_id}", None),
        ("PUT", f"/meeting-notes/{note_id}", {"title": "no auth"}),
        ("DELETE", f"/meeting-notes/{note_id}", None),
        ("PUT", f"/decisions/{decision_id}/rationale", {"rationale": "no auth"}),
        ("GET", f"/decisions/{decision_id}/rationale", None),
    ]

    all_unauth_pass = True
    for method, path, json_data in endpoints_to_test_unauth:
        if method == "POST":
            r = client.post(path, json=json_data)
        elif method == "GET":
            r = client.get(path)
        elif method == "PUT":
            r = client.put(path, json=json_data)
        elif method == "DELETE":
            r = client.delete(path)
        if r.status_code != 401:
            all_unauth_pass = False
            print(f" [FAIL] Expected 401 for {method} {path}, got {r.status_code}")

    assert_check(all_unauth_pass, "All 18 collaboration endpoints reject unauthenticated requests with 401 Unauthorized")

    # Step 13: Test Authorization (403 Forbidden on Unauthorized Access)
    print("\n--- Step 13: Test Authorization (Ownership Checks & Role Permissions) ---")
    # Bob attempts to modify Alice's comment -> 403
    bob_mod_c1 = client.put(f"/comments/{c1_id}", json={"content": "Bob altering Alice comment"}, headers=headers_bob)
    assert_check(bob_mod_c1.status_code == 403, "Bob cannot update Alice's comment (403 Forbidden)")

    bob_del_c1 = client.delete(f"/comments/{c1_id}", headers=headers_bob)
    assert_check(bob_del_c1.status_code == 403, "Bob cannot delete Alice's comment (403 Forbidden)")

    # Bob attempts to modify Alice's thread -> 403
    bob_mod_th = client.put(f"/threads/{thread_id}", json={"title": "Bob altering Alice thread"}, headers=headers_bob)
    assert_check(bob_mod_th.status_code == 403, "Bob cannot update Alice's thread (403 Forbidden)")

    # Bob attempts to modify Alice's meeting note -> 403
    bob_mod_note = client.put(f"/meeting-notes/{note_id}", json={"title": "Bob altering Alice note"}, headers=headers_bob)
    assert_check(bob_mod_note.status_code == 403, "Bob cannot update Alice's meeting note (403 Forbidden)")

    # Bob attempts to modify rationale of Alice's decision -> 403
    bob_mod_rat = client.put(f"/decisions/{decision_id}/rationale", json={"rationale": "Bob unauthorized rationale"}, headers=headers_bob)
    assert_check(bob_mod_rat.status_code == 403, "Bob cannot update rationale for Alice's decision (403 Forbidden)")

    # Administrator CAN update and moderate
    admin_mod_c1 = client.put(f"/comments/{c1_id}", json={"content": "Admin approved content"}, headers=headers_admin)
    assert_check(admin_mod_c1.status_code == 200, "Administrator can moderate/update comments (200 OK)")

    # Step 14: Error Handling Verification (404 and 422)
    print("\n--- Step 14: Error Handling Verification ---")
    assert_check(client.post("/decisions/99999/comments", json={"content": "test"}, headers=headers_alice).status_code == 404, "POST comment to non-existing decision returns 404")
    assert_check(client.post("/decisions/99999/threads", json={"title": "test"}, headers=headers_alice).status_code == 404, "POST thread to non-existing decision returns 404")
    assert_check(client.post("/threads/99999/comments", json={"content": "test"}, headers=headers_alice).status_code == 404, "POST reply to non-existing thread returns 404")
    assert_check(client.post("/decisions/99999/meeting-notes", json={"title": "test", "content": "text"}, headers=headers_alice).status_code == 404, "POST meeting note to non-existing decision returns 404")
    assert_check(client.get("/comments/99999", headers=headers_alice).status_code == 404, "GET non-existing comment returns 404")
    assert_check(client.get("/threads/99999", headers=headers_alice).status_code == 404, "GET non-existing thread returns 404")
    assert_check(client.get("/meeting-notes/99999", headers=headers_alice).status_code == 404, "GET non-existing meeting note returns 404")
    assert_check(client.post(f"/decisions/{decision_id}/comments", json={}, headers=headers_alice).status_code == 422, "Missing required field in comment payload returns 422 Validation Error")

    # Step 15: PostgreSQL Direct Database Verification
    print("\n--- Step 15: Direct PostgreSQL Database State Verification ---")
    db_verify = SessionLocal()
    db_dec = db_verify.query(Decision).filter(Decision.id == decision_id).first()
    db_comments = db_verify.query(Comment).filter(Comment.decision_id == decision_id).all()
    db_threads = db_verify.query(DiscussionThread).filter(DiscussionThread.decision_id == decision_id).all()
    db_notes = db_verify.query(MeetingNote).filter(MeetingNote.decision_id == decision_id).all()

    assert_check(db_dec is not None and db_dec.rationale == rationale_text, "PostgreSQL: Decision rationale persisted correctly in 'decisions' table")
    assert_check(len(db_comments) >= 3, f"PostgreSQL: {len(db_comments)} comments persisted correctly in 'comments' table")
    assert_check(len(db_threads) >= 1, f"PostgreSQL: {len(db_threads)} discussion thread persisted correctly in 'discussion_threads' table")
    assert_check(len(db_notes) >= 1, f"PostgreSQL: {len(db_notes)} meeting note persisted correctly in 'meeting_notes' table")

    # Verify foreign key linkages & timestamps
    thread_in_db = db_threads[0]
    thread_replies = [c for c in db_comments if c.thread_id == thread_in_db.id]
    assert_check(len(thread_replies) == 2, f"PostgreSQL: Thread foreign key verified with {len(thread_replies)} associated replies")
    assert_check(all(c.created_at is not None and c.updated_at is not None for c in db_comments), "PostgreSQL: Created and updated timestamps properly maintained on comments")

    db_verify.close()

    print("\n" + "=" * 75)
    print(f" SPRINT 7 VERIFICATION COMPLETE: {passed_tests}/{total_tests} CHECKS PASSED")
    print("=" * 75)
    return passed_tests == total_tests


if __name__ == "__main__":
    success = run_verification()
    sys.exit(0 if success else 1)
