"""Phase 5 — Complete End-to-End Test (Fresh Data)

Register -> Login -> Decision -> Alternatives -> Discussion -> Submit -> Review
-> Approval -> Audit -> Version -> Dashboard -> Report -> PDF -> Excel

Verifies:
1. Full flow succeeds end-to-end
2. Database contains the expected linked records
"""
import io
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import psycopg2
from fastapi.testclient import TestClient
from app.main import app

DB_URL = "postgresql+psycopg2://postgres:admin@localhost:5432/expert_decision_replay"
conn = psycopg2.connect(
    host="localhost", port=5432,
    database="expert_decision_replay",
    user="postgres", password="admin",
)
conn.autocommit = True
cur = conn.cursor()

client = TestClient(app)


def cleanup():
    print("\n--- Cleanup ---")
    tables = [
        "activity_log", "audit_log", "security_log", "access_log",
        "decision_versions", "alternatives", "comments",
        "discussion_threads", "meeting_notes", "decisions", "users",
    ]
    for t in tables:
        cur.execute(f"DELETE FROM {t}")
    conn.commit()
    print("All test data cleaned up.")


def main():
    cleanup()

    # =========================================================================
    # 1. REGISTER 4 users (all default to Employee; Admin promotes later)
    # =========================================================================
    print("\n=== 1. REGISTER USERS ===")
    users_data = [
        ("emp_e2e@test.com", "Employee E2E", "E2EEMP01", "Engineering"),
        ("rev_e2e@test.com", "Reviewer E2E", "E2EREV01", "QA"),
        ("mgr_e2e@test.com", "Manager E2E", "E2EMGR01", "Engineering"),
        ("adm_e2e@test.com", "Admin E2E", "E2EADM01", "Executive"),
    ]
    tokens = {}
    user_ids = {}
    for email, name, emp_id, dept in users_data:
        r = client.post("/users", json={
            "full_name": name, "email": email, "password": "Password123!",
            "employee_id": emp_id, "department": dept, "designation": "Test User",
        })
        assert r.status_code == 201, f"Register {email} failed: {r.status_code} {r.text}"
        uid = r.json()["id"]
        user_ids[email] = uid
        print(f"  Registered: id={uid}, email={email}")

    # =========================================================================
    # 1b. Promote roles via direct DB (registration forces EMPLOYEE)
    # =========================================================================
    print("\n=== 1b. PROMOTE ROLES ===")
    cur.execute("UPDATE users SET role = 'Administrator' WHERE id = %s", (user_ids["adm_e2e@test.com"],))
    cur.execute("UPDATE users SET role = 'Manager' WHERE id = %s", (user_ids["mgr_e2e@test.com"],))
    cur.execute("UPDATE users SET role = 'Reviewer' WHERE id = %s", (user_ids["rev_e2e@test.com"],))
    conn.commit()
    print(f"  Promoted user {user_ids['adm_e2e@test.com']} to Administrator")
    print(f"  Promoted user {user_ids['mgr_e2e@test.com']} to Manager")
    print(f"  Promoted user {user_ids['rev_e2e@test.com']} to Reviewer")

    # =========================================================================
    # 2. LOGIN all 4 users
    # =========================================================================
    print("\n=== 2. LOGIN ===")
    for email, name, emp_id, dept in users_data:
        r = client.post("/login", json={"email": email, "password": "Password123!"})
        assert r.status_code == 200, f"Login {email} failed: {r.status_code}"
        tokens[email] = r.json()["access_token"]
        print(f"  Logged in {email}")

    def hdr(email):
        return {"Authorization": f"Bearer {tokens[email]}"}

    # =========================================================================
    # 3. EMPLOYEE creates a decision
    # =========================================================================
    print("\n=== 3. CREATE DECISION ===")
    emp_email = "emp_e2e@test.com"
    rev_email = "rev_e2e@test.com"
    mgr_email = "mgr_e2e@test.com"
    adm_email = "adm_e2e@test.com"

    r = client.post("/decisions", headers=hdr(emp_email), json={
        "title": "E2E Phase 5 Decision",
        "problem_statement": "End-to-end validation of the full decision lifecycle.",
        "category": "Technology",
    })
    assert r.status_code == 201, f"Create decision failed: {r.status_code} {r.text}"
    decision = r.json()
    did = decision["id"]
    print(f"  Created decision id={did}, status={decision['status']}")

    # Verify status defaults to Draft
    assert decision["status"] == "Draft"
    assert decision["created_by"] == user_ids[emp_email]

    # =========================================================================
    # 4. EMPLOYEE adds 3 alternatives
    # =========================================================================
    print("\n=== 4. ADD ALTERNATIVES ===")
    alt_ids = []
    alts = [
        ("PostgreSQL", "Production DB", "ACID compliant", "Complex setup", 5000, 4, "Medium"),
        ("MySQL", "Alternative DB", "Fast reads", "Less features", 3000, 3, "Low"),
        ("MongoDB", "Document DB", "Flexible schema", "No joins", 2500, 2, "High"),
    ]
    for name, desc, pros, cons, cost, score, risk in alts:
        r = client.post(f"/decisions/{did}/alternatives", headers=hdr(emp_email), json={
            "name": name, "description": desc, "pros": pros, "cons": cons,
            "estimated_cost": cost, "feasibility_score": score, "risk_level": risk,
        })
        assert r.status_code == 201, f"Create alt failed: {r.status_code} {r.text}"
        alt_ids.append(r.json()["id"])
        print(f"  Created alternative '{name}' id={r.json()['id']}")

    # Compare
    r = client.get(f"/decisions/{did}/alternatives/compare", headers=hdr(emp_email))
    assert r.status_code == 200
    assert len(r.json()["alternatives"]) == 3
    print("  Compare endpoint returned 3 alternatives")

    # =========================================================================
    # 5. DISCUSSION: Comments + Thread + Meeting Note
    # =========================================================================
    print("\n=== 5. DISCUSSION ===")

    # Employee posts a comment
    r = client.post(f"/decisions/{did}/comments", headers=hdr(emp_email), json={
        "content": "I recommend PostgreSQL for reliability.",
    })
    assert r.status_code == 201
    comment_id = r.json()["id"]
    print(f"  Employee comment id={comment_id}")

    # Reviewer creates a discussion thread
    r = client.post(f"/decisions/{did}/threads", headers=hdr(rev_email), json={
        "title": "Database Selection Debate",
        "description": "Let's evaluate trade-offs.",
    })
    assert r.status_code == 201
    thread_id = r.json()["id"]
    print(f"  Reviewer thread id={thread_id}")

    # Manager replies to the thread
    r = client.post(f"/threads/{thread_id}/comments", headers=hdr(mgr_email), json={
        "content": "Good thread. Let's include benchmark results.",
    })
    assert r.status_code == 201
    print(f"  Manager reply id={r.json()['id']}")

    # Manager creates a meeting note
    r = client.post(f"/decisions/{did}/meeting-notes", headers=hdr(mgr_email), json={
        "title": "DB Selection Review Meeting",
        "content": "Reviewed all alternatives. PostgreSQL recommended.",
        "meeting_date": "2026-09-08",
    })
    assert r.status_code == 201
    note_id = r.json()["id"]
    print(f"  Manager meeting note id={note_id}")

    # =========================================================================
    # 6. EMPLOYEE sets rationale
    # =========================================================================
    print("\n=== 6. SET RATIONALE ===")
    r = client.put(f"/decisions/{did}/rationale", headers=hdr(emp_email), json={
        "rationale": "PostgreSQL chosen for ACID compliance and team expertise.",
    })
    assert r.status_code == 200
    assert r.json()["rationale"] == "PostgreSQL chosen for ACID compliance and team expertise."
    print("  Rationale set successfully")

    # =========================================================================
    # 7. SUBMIT: Draft -> Under Review
    # =========================================================================
    print("\n=== 7. SUBMIT (Draft -> Under Review) ===")
    r = client.patch(f"/decisions/{did}/status", headers=hdr(emp_email), json={
        "status": "Under Review",
    })
    assert r.status_code == 200
    assert r.json()["status"] == "Under Review"
    print("  Status changed to 'Under Review'")

    # =========================================================================
    # 8. REVIEWER APPROVES: Under Review -> Approved
    # =========================================================================
    print("\n=== 8. REVIEWER APPROVES (Under Review -> Approved) ===")
    r = client.patch(f"/decisions/{did}/status", headers=hdr(rev_email), json={
        "status": "Approved",
    })
    assert r.status_code == 200
    assert r.json()["status"] == "Approved"
    print("  Status changed to 'Approved'")

    # =========================================================================
    # 9. AUDIT: Verify decision history
    # =========================================================================
    print("\n=== 9. AUDIT TRAIL ===")
    r = client.get(f"/decisions/{did}/history", headers=hdr(adm_email))
    assert r.status_code == 200
    history = r.json()["items"]
    actions = [h["action"] for h in history]
    print(f"  Decision history has {len(history)} entries: {actions}")
    assert "create" in actions
    assert "update" in actions  # rationale
    assert "status_change" in actions

    # Audit logs endpoint
    r = client.get("/audit-logs", headers=hdr(adm_email))
    assert r.status_code == 200
    audit_total = r.json()["total"]
    print(f"  Audit logs total: {audit_total}")
    assert audit_total > 0

    # =========================================================================
    # 10. VERSION: Verify version snapshots
    # =========================================================================
    print("\n=== 10. VERSION HISTORY ===")
    r = client.get(f"/decisions/{did}/versions", headers=hdr(emp_email))
    assert r.status_code == 200
    versions = r.json()["versions"]
    version_numbers = [v["version_number"] for v in versions]
    print(f"  Versions: {version_numbers}")
    assert len(versions) >= 3  # v1 (create), v2 (update/rationale), v3 (status_change)
    # Verify v1 has Draft status
    v1 = next(v for v in versions if v["version_number"] == 1)
    assert v1["status"] == "Draft"
    print("  v1 has Draft status (correct)")

    # Get specific version
    r = client.get(f"/decisions/{did}/versions/1", headers=hdr(emp_email))
    assert r.status_code == 200
    assert r.json()["status"] == "Draft"

    # =========================================================================
    # 11. DASHBOARD: Employee, Manager, Admin
    # =========================================================================
    print("\n=== 11. DASHBOARDS ===")

    # Employee dashboard
    r = client.get("/dashboard/employee", headers=hdr(emp_email))
    assert r.status_code == 200
    emp_dash = r.json()
    print(f"  Employee: total_decisions={emp_dash['total_decisions']}, "
          f"recent_activity_count={len(emp_dash['recent_activity'])}")
    assert emp_dash["total_decisions"] >= 1
    assert len(emp_dash["recent_activity"]) >= 5

    # Manager statistics
    r = client.get("/dashboard/manager/statistics", headers=hdr(mgr_email))
    assert r.status_code == 200
    mgr_stats = r.json()
    print(f"  Manager: total={mgr_stats['total']}, approved={mgr_stats['approved']}")
    assert mgr_stats["total"] >= 1
    assert mgr_stats["approved"] >= 1

    # Admin dashboard
    r = client.get("/dashboard/admin", headers=hdr(adm_email))
    assert r.status_code == 200
    adm_dash = r.json()
    print(f"  Admin: total_users={adm_dash['total_users']}, total_decisions={adm_dash['total_decisions']}")
    assert adm_dash["total_users"] >= 4
    assert adm_dash["total_decisions"] >= 1

    # Admin analytics
    r = client.get("/dashboard/admin/analytics", headers=hdr(adm_email))
    assert r.status_code == 200
    print(f"  Admin analytics: OK")

    # Admin user activity
    r = client.get("/dashboard/admin/user-activity", headers=hdr(adm_email))
    assert r.status_code == 200
    print(f"  Admin user-activity: {r.json()['total_active_users']} active users")

    # =========================================================================
    # 12. REPORTS: All 4 JSON endpoints
    # =========================================================================
    print("\n=== 12. REPORTS (JSON) ===")

    # Decisions report
    r = client.get("/reports/decisions", headers=hdr(emp_email))
    assert r.status_code == 200
    rep = r.json()
    print(f"  Decisions report: total={rep['summary']['total']}")
    assert rep["summary"]["total"] >= 1

    # Approvals report
    r = client.get("/reports/approvals", headers=hdr(adm_email))
    assert r.status_code == 200
    print(f"  Approvals report: total={r.json()['summary']['total']}")

    # Teams report
    r = client.get("/reports/teams", headers=hdr(emp_email))
    assert r.status_code == 200
    print(f"  Teams report: {len(r.json()['items'])} teams")

    # Audit report
    r = client.get("/reports/audit", headers=hdr(adm_email))
    assert r.status_code == 200
    print(f"  Audit report: {r.json()['total']} entries")

    # =========================================================================
    # 13. PDF & EXCEL EXPORTS
    # =========================================================================
    print("\n=== 13. EXPORTS (PDF + Excel) ===")

    exports = [
        "/reports/decisions/export/pdf",
        "/reports/decisions/export/excel",
        "/reports/approvals/export/pdf",
        "/reports/approvals/export/excel",
        "/reports/teams/export/pdf",
        "/reports/teams/export/excel",
        "/reports/audit/export/pdf",
        "/reports/audit/export/excel",
    ]
    for path in exports:
        r = client.get(path, headers=hdr(adm_email))
        assert r.status_code == 200, f"Export {path} failed: {r.status_code}"
        ct = r.headers.get("content-type", "")
        cd = r.headers.get("content-disposition", "")
        if "pdf" in path:
            assert r.content[:5] == b"%PDF-", f"{path} not valid PDF"
        else:
            assert "spreadsheetml" in ct or "octet" in ct or "excel" in ct, f"{path} not valid Excel"
        print(f"  {path}: OK (Content-Disposition: {cd})")

    # =========================================================================
    # 14. ACTIVITY FEED
    # =========================================================================
    print("\n=== 14. ACTIVITY FEED ===")
    r = client.get("/activities", headers=hdr(emp_email))
    assert r.status_code == 200
    activities = r.json()
    print(f"  Employee activity feed: {activities['total']} entries")
    assert activities["total"] >= 5  # create decision, 3 alts, comment, rationale, status change

    r = client.get("/activities", headers=hdr(adm_email))
    assert r.status_code == 200
    print(f"  Admin activity feed: {r.json()['total']} entries")

    # =========================================================================
    # 15. SECURITY & ACCESS LOGS
    # =========================================================================
    print("\n=== 15. SECURITY & ACCESS LOGS ===")
    r = client.get("/security/logs", headers=hdr(adm_email))
    assert r.status_code == 200
    sec_data = r.json()
    sec_count = len(sec_data) if isinstance(sec_data, list) else sec_data.get("total", 0)
    print(f"  Security logs: {sec_count} entries")

    r = client.get("/access/logs", headers=hdr(adm_email))
    assert r.status_code == 200
    acc_data = r.json()
    acc_count = len(acc_data) if isinstance(acc_data, list) else acc_data.get("total", 0)
    print(f"  Access logs: {acc_count} entries")

    # =========================================================================
    # 16. VERIFY DB LINKED RECORDS
    # =========================================================================
    print("\n=== 16. DATABASE VERIFICATION ===")

    cur.execute("SELECT COUNT(*) FROM decisions WHERE id = %s", (did,))
    assert cur.fetchone()[0] == 1
    print(f"  Decision {did} exists in DB")

    cur.execute("SELECT COUNT(*) FROM alternatives WHERE decision_id = %s", (did,))
    alt_count = cur.fetchone()[0]
    assert alt_count == 3
    print(f"  3 alternatives exist for decision {did}")

    cur.execute("SELECT COUNT(*) FROM comments WHERE decision_id = %s", (did,))
    comment_count = cur.fetchone()[0]
    assert comment_count >= 1
    print(f"  {comment_count} comments on decision {did}")

    cur.execute("SELECT COUNT(*) FROM discussion_threads WHERE decision_id = %s", (did,))
    thread_count = cur.fetchone()[0]
    assert thread_count >= 1
    print(f"  {thread_count} threads on decision {did}")

    cur.execute("SELECT COUNT(*) FROM meeting_notes WHERE decision_id = %s", (did,))
    note_count = cur.fetchone()[0]
    assert note_count >= 1
    print(f"  {note_count} meeting notes on decision {did}")

    cur.execute("SELECT COUNT(*) FROM decision_versions WHERE decision_id = %s", (did,))
    ver_count = cur.fetchone()[0]
    assert ver_count >= 3
    print(f"  {ver_count} version snapshots for decision {did}")

    cur.execute("SELECT COUNT(*) FROM activity_log WHERE entity_id = %s AND entity_type = 'decision'", (did,))
    act_count = cur.fetchone()[0]
    assert act_count >= 1
    print(f"  {act_count} activity_log entries for decision {did}")

    cur.execute("SELECT COUNT(*) FROM audit_log WHERE entity_id = %s AND entity_type = 'decision'", (did,))
    audit_count = cur.fetchone()[0]
    assert audit_count >= 1
    print(f"  {audit_count} audit_log entries for decision {did}")

    # Verify FK integrity
    cur.execute("""
        SELECT a.id FROM alternatives a
        LEFT JOIN decisions d ON a.decision_id = d.id
        WHERE d.id IS NULL
    """)
    orphans = cur.fetchall()
    assert len(orphans) == 0, f"Orphan alternatives: {orphans}"
    print("  No orphan alternatives (FK integrity OK)")

    cur.execute("""
        SELECT c.id FROM comments c
        LEFT JOIN decisions d ON c.decision_id = d.id
        WHERE d.id IS NULL
    """)
    orphans = cur.fetchall()
    assert len(orphans) == 0, f"Orphan comments: {orphans}"
    print("  No orphan comments (FK integrity OK)")

    # Verify decision status in DB
    cur.execute("SELECT status FROM decisions WHERE id = %s", (did,))
    db_status = cur.fetchone()[0]
    assert db_status == "Approved", f"Expected 'Approved', got '{db_status}'"
    print(f"  Decision status in DB: {db_status}")

    # Verify rationale in DB
    cur.execute("SELECT rationale FROM decisions WHERE id = %s", (did,))
    db_rationale = cur.fetchone()[0]
    assert db_rationale is not None
    print(f"  Decision rationale in DB: present")

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 60)
    print("PHASE 5 E2E TEST: ALL CHECKS PASSED")
    print("=" * 60)
    print(f"  Decision: id={did}, status=Approved")
    print(f"  Alternatives: {alt_count}")
    print(f"  Comments: {comment_count}")
    print(f"  Threads: {thread_count}")
    print(f"  Meeting Notes: {note_count}")
    print(f"  Version Snapshots: {ver_count}")
    print(f"  Audit Log Entries: {audit_count}")
    print(f"  Activity Log Entries: {act_count}")
    print(f"  Reports: 4 JSON + 8 exports (PDF/Excel) all OK")
    print(f"  Dashboards: Employee, Manager, Admin all OK")
    print(f"  Security/Access Logs: present")
    print(f"  FK Integrity: OK (no orphan records)")
    print(f"  DB state: decision status='Approved', rationale=present")

    cleanup()

    cur.close()
    conn.close()
    print("\nDone. Database cleaned up.")


if __name__ == "__main__":
    main()
