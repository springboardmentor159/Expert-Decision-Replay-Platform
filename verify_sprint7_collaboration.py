"""
Comprehensive Sprint 7 Discussion & Collaboration Module Verification Script
"""
import sys
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import SessionLocal
from app.models.user import User

client = TestClient(app)

def run_sprint7_verification():
    print("=" * 75)
    print(" SPRINT 7 – DISCUSSION AND COLLABORATION MODULE VERIFICATION")
    print("=" * 75)

    results = []

    def log_result(step, endpoint, method, status, passed, details=""):
        results.append({
            "step": step,
            "endpoint": endpoint,
            "method": method,
            "status": status,
            "passed": passed,
            "details": details
        })
        icon = "[PASS]" if passed else "[FAIL]"
        print(f"{icon} Step {step:<2} | {method:<6} {endpoint:<32} -> Status {status} | {details}")

    # Clean up test users
    db = SessionLocal()
    db.query(User).filter(User.email.in_(["sprint7_user1@example.com", "sprint7_user2@example.com"])).delete(synchronize_session=False)
    db.commit()
    db.close()

    # Step 0: User Setup & Authentication
    print("\n--- Setup: Register Users & Obtain JWT Tokens ---")
    u1_res = client.post("/users", json={
        "full_name": "Sprint 7 Lead User",
        "email": "sprint7_user1@example.com",
        "role": "Employee",
        "password": "Password123!",
        "employee_id": "S7_EMP_01"
    })
    log_result(0, "/users", "POST", u1_res.status_code, u1_res.status_code == 201, "Registered User 1")

    u2_res = client.post("/users", json={
        "full_name": "Sprint 7 Secondary User",
        "email": "sprint7_user2@example.com",
        "role": "Employee",
        "password": "Password123!",
        "employee_id": "S7_EMP_02"
    })
    log_result(0, "/users", "POST", u2_res.status_code, u2_res.status_code == 201, "Registered User 2")

    # Step 1 – Login (POST /users/login or /auth/login)
    print("\n--- Step 1: Login & Obtain Tokens ---")
    login1 = client.post("/users/login", json={"email": "sprint7_user1@example.com", "password": "Password123!"})
    token1 = login1.json().get("access_token")
    headers1 = {"Authorization": f"Bearer {token1}"}
    log_result(1, "/users/login", "POST", login1.status_code, login1.status_code == 200, "Obtained JWT token for User 1")

    login2 = client.post("/users/login", json={"email": "sprint7_user2@example.com", "password": "Password123!"})
    token2 = login2.json().get("access_token")
    headers2 = {"Authorization": f"Bearer {token2}"}
    log_result(1, "/users/login", "POST", login2.status_code, login2.status_code == 200, "Obtained JWT token for User 2")

    # Step 2 – Create a Decision
    print("\n--- Step 2: Create Decision ---")
    dec_res = client.post("/decisions", json={
        "title": "Select Primary Database Engine",
        "problem_statement": "We must evaluate relational vs document stores for high availability.",
        "category": "Infrastructure"
    }, headers=headers1)
    decision_id = dec_res.json().get("id")
    log_result(2, "/decisions", "POST", dec_res.status_code, dec_res.status_code == 201, f"Created Decision ID #{decision_id}")

    # Step 3 – Create Comments (At least 3 comments)
    print("\n--- Step 3: Create Comments ---")
    c1_res = client.post(f"/decisions/{decision_id}/comments", json={"content": "PostgreSQL provides better relational support."}, headers=headers1)
    c1 = c1_res.json()
    log_result(3, f"/decisions/{decision_id}/comments", "POST", c1_res.status_code, c1_res.status_code == 201, "Comment 1 created")

    c2_res = client.post(f"/decisions/{decision_id}/comments", json={"content": "MongoDB may provide easier horizontal scaling."}, headers=headers2)
    c2 = c2_res.json()
    log_result(3, f"/decisions/{decision_id}/comments", "POST", c2_res.status_code, c2_res.status_code == 201, "Comment 2 created")

    c3_res = client.post(f"/decisions/{decision_id}/comments", json={"content": "Cost analysis should also be considered."}, headers=headers1)
    c3 = c3_res.json()
    log_result(3, f"/decisions/{decision_id}/comments", "POST", c3_res.status_code, c3_res.status_code == 201, "Comment 3 created")

    # Step 4 – Retrieve Comments for Decision
    print("\n--- Step 4: Retrieve Comments ---")
    get_c_res = client.get(f"/decisions/{decision_id}/comments", headers=headers1)
    log_result(4, f"/decisions/{decision_id}/comments", "GET", get_c_res.status_code, get_c_res.status_code == 200 and len(get_c_res.json()) == 3, f"Retrieved {len(get_c_res.json())} comments")

    # Step 5 – Retrieve One Comment by ID
    print("\n--- Step 5: Retrieve One Comment ---")
    c1_id = c1["id"]
    get_c1_res = client.get(f"/comments/{c1_id}", headers=headers1)
    log_result(5, f"/comments/{c1_id}", "GET", get_c1_res.status_code, get_c1_res.status_code == 200, f"Retrieved comment #{c1_id}")

    # Step 6 – Update a Comment
    print("\n--- Step 6: Update Comment ---")
    up_c_res = client.put(f"/comments/{c1_id}", json={"content": "Updated discussion: PostgreSQL provides strong relational support and a mature ecosystem."}, headers=headers1)
    log_result(6, f"/comments/{c1_id}", "PUT", up_c_res.status_code, up_c_res.status_code == 200 and "mature ecosystem" in up_c_res.json()["content"], "Updated comment content")

    # Step 7 – Delete a Comment
    print("\n--- Step 7: Delete Comment ---")
    del_c_res = client.delete(f"/comments/{c1_id}", headers=headers1)
    log_result(7, f"/comments/{c1_id}", "DELETE", del_c_res.status_code, del_c_res.status_code == 200, "Deleted comment")

    # Step 8 – Create Discussion Thread
    print("\n--- Step 8: Create Discussion Thread ---")
    thread_res = client.post(f"/decisions/{decision_id}/threads", json={
        "title": "Database scalability",
        "description": "Let's discuss the scalability requirements before finalizing the database."
    }, headers=headers1)
    thread_id = thread_res.json().get("id")
    log_result(8, f"/decisions/{decision_id}/threads", "POST", thread_res.status_code, thread_res.status_code == 201, f"Created Discussion Thread ID #{thread_id}")

    # Step 9 – Add Replies to Thread
    print("\n--- Step 9: Add Thread Replies ---")
    r1_res = client.post(f"/threads/{thread_id}/comments", json={"content": "PostgreSQL can support our expected workload with proper indexing and scaling."}, headers=headers1)
    log_result(9, f"/threads/{thread_id}/comments", "POST", r1_res.status_code, r1_res.status_code == 201, "Added Reply 1 to Thread")

    r2_res = client.post(f"/threads/{thread_id}/comments", json={"content": "Read replicas can handle read traffic spikes."}, headers=headers2)
    log_result(9, f"/threads/{thread_id}/comments", "POST", r2_res.status_code, r2_res.status_code == 201, "Added Reply 2 to Thread")

    # Step 10 – Create Meeting Notes
    print("\n--- Step 10: Create Meeting Note ---")
    mn_res = client.post(f"/decisions/{decision_id}/meeting-notes", json={
        "title": "Database Tech Sync",
        "content": "Meeting concluded with preference for PostgreSQL due to strong ACID guarantees."
    }, headers=headers1)
    note_id = mn_res.json().get("id")
    log_result(10, f"/decisions/{decision_id}/meeting-notes", "POST", mn_res.status_code, mn_res.status_code == 201, f"Created Meeting Note ID #{note_id}")

    # Step 11 – Add Decision Rationale
    print("\n--- Step 11: Add Decision Rationale ---")
    rat_res = client.put(f"/decisions/{decision_id}/rationale", json={
        "rationale": "PostgreSQL was selected because it provided the best balance between reliability, feasibility, cost, and operational risk."
    }, headers=headers1)
    log_result(11, f"/decisions/{decision_id}/rationale", "PUT", rat_res.status_code, rat_res.status_code == 200, "Recorded Decision Rationale")

    # Step 12 – Test Authentication (Missing Token -> 401)
    print("\n--- Step 12: Test Authentication (No JWT) ---")
    unauth_c = client.get(f"/decisions/{decision_id}/comments")
    log_result(12, f"/decisions/{decision_id}/comments", "GET", unauth_c.status_code, unauth_c.status_code == 401, "Unauthenticated request correctly returned 401 Unauthorized")

    # Step 13 – Test Authorization (Non-owner attempt -> 403)
    print("\n--- Step 13: Test Authorization (Non-Owner Edit) ---")
    c2_id = c2["id"]
    forbidden_edit = client.put(f"/comments/{c2_id}", json={"content": "Attempted hack by User 1"}, headers=headers1)
    log_result(13, f"/comments/{c2_id}", "PUT", forbidden_edit.status_code, forbidden_edit.status_code == 403, "Non-owner edit correctly returned 403 Forbidden")

    # Step 14-18 – Error Handling & Edge Cases
    print("\n--- Step 14-18: Error Handling & Validation ---")
    non_exist_dec = client.post("/decisions/99999/comments", json={"content": "Orphan comment"}, headers=headers1)
    log_result(14, "/decisions/99999/comments", "POST", non_exist_dec.status_code, non_exist_dec.status_code == 404, "Non-existing decision returned 404 Not Found")

    non_exist_c = client.get("/comments/99999", headers=headers1)
    log_result(15, "/comments/99999", "GET", non_exist_c.status_code, non_exist_c.status_code == 404, "Non-existing comment returned 404 Not Found")

    non_exist_t = client.get("/threads/99999", headers=headers1)
    log_result(16, "/threads/99999", "GET", non_exist_t.status_code, non_exist_t.status_code == 404, "Non-existing thread returned 404 Not Found")

    non_exist_mn = client.get("/meeting-notes/99999", headers=headers1)
    log_result(17, "/meeting-notes/99999", "GET", non_exist_mn.status_code, non_exist_mn.status_code == 404, "Non-existing meeting note returned 404 Not Found")

    bad_req = client.post(f"/decisions/{decision_id}/comments", json={}, headers=headers1)
    log_result(18, f"/decisions/{decision_id}/comments", "POST", bad_req.status_code, bad_req.status_code == 422, "Missing required content field returned 422 Validation Error")

    print("\n" + "=" * 75)
    total_passed = sum(1 for r in results if r["passed"])
    total_steps = len(results)
    print(f" SPRINT 7 VERIFICATION SUMMARY: {total_passed}/{total_steps} STEPS PASSED")
    print("=" * 75)

    if total_passed < total_steps:
        sys.exit(1)

if __name__ == "__main__":
    run_sprint7_verification()
