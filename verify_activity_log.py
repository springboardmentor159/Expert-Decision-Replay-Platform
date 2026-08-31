"""Swagger-style E2E verification for Activity Log auto-logging.

Runs the 6 required actions against the LIVE PostgreSQL database (via the
real FastAPI app / TestClient) and then verifies the activity_log table
structure and the created rows directly with psycopg2. Cleans up afterwards.

Run with:  venv/Scripts/python.exe verify_activity_log.py
"""
import os
import sys
import traceback

# Use the real DATABASE_URL from .env (NOT the sqlite override used by pytest).
from app.core.config import settings
from app.core.security import hash_password
from app.db.database import SessionLocal
from app.models.user import User
from fastapi.testclient import TestClient
from app.main import app

import psycopg2

DB_URL = settings.DATABASE_URL
# psycopg2 needs the plain "postgresql://" scheme, not "postgresql+psycopg2://".
PSYCOPG_URL = DB_URL.replace("postgresql+psycopg2://", "postgresql://")
UNIQUE = "actlog_verify"
EMAIL = f"{UNIQUE}@example.com"
EMP_ID = "EMP_ACTLOG_VERIFY"
PASSWORD = "password123"

PASS = "PASS"
FAIL = "FAIL"
results = []


def record(step, status, detail):
    results.append((step, status, detail))
    print(f"[{status}] {step} — {detail}")


def direct_query(sql, params=None):
    conn = psycopg2.connect(PSYCOPG_URL)
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        return cur.fetchall()
    finally:
        conn.close()


def main():
    client = TestClient(app)

    # Ensure a clean test user (delete any leftover first).
    with SessionLocal() as s:
        old = s.query(User).filter(User.email == EMAIL).first()
        if old:
            s.delete(old)
            s.commit()

    # 0. Signup + login to get JWT
    signup = client.post(
        "/users",
        json={
            "full_name": "Activity Log Verifier",
            "email": EMAIL,
            "password": PASSWORD,
            "employee_id": EMP_ID,
            "role": "Employee",
        },
    )
    if signup.status_code != 201:
        record("Setup: signup", FAIL, f"status={signup.status_code} {signup.text}")
        return
    user_id = signup.json()["id"]

    login = client.post("/login", json={"email": EMAIL, "password": PASSWORD})
    if login.status_code != 200:
        record("Setup: login", FAIL, f"status={login.status_code} {login.text}")
        return
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    def check_log(action, entity_type, entity_id):
        rows = (
            SessionLocal()
            .query(__import__("app.models.activity_log", fromlist=["ActivityLog"]).ActivityLog)
            .filter_by(user_id=user_id, action=action, entity_type=entity_type, entity_id=entity_id)
            .all()
        )
        return rows

    # 1. Create a Decision
    r = client.post(
        "/decisions",
        json={"title": "ActLog Decision", "problem_statement": "PS", "category": "Engineering"},
        headers=headers,
    )
    ok = r.status_code == 201 and check_log("create", "decision", r.json()["id"])
    record("1. Create Decision auto-logs", PASS if ok else FAIL,
           f"decision id={r.json().get('id')}, log rows={len(check_log('create','decision',r.json()['id']))}" if r.status_code==201 else r.text)
    decision_id = r.json()["id"]

    # 2. Update the Decision
    r = client.put(f"/decisions/{decision_id}", json={"title": "ActLog Decision Updated"}, headers=headers)
    ok = r.status_code == 200 and check_log("update", "decision", decision_id)
    record("2. Update Decision auto-logs", PASS if ok else FAIL,
           f"status={r.status_code}, log rows={len(check_log('update','decision',decision_id))}")

    # 3. Change its status
    r = client.patch(f"/decisions/{decision_id}/status", json={"status": "Under Review"}, headers=headers)
    ok = r.status_code == 200 and check_log("status_change", "decision", decision_id)
    record("3. Status change auto-logs", PASS if ok else FAIL,
           f"status={r.status_code}, log rows={len(check_log('status_change','decision',decision_id))}")

    # 4. Create an Alternative
    r = client.post(
        f"/decisions/{decision_id}/alternatives",
        json={"name": "Alt Option", "description": "d", "pros": "p", "cons": "c"},
        headers=headers,
    )
    ok = r.status_code == 201 and check_log("create", "alternative", r.json()["id"])
    record("4. Create Alternative auto-logs", PASS if ok else FAIL,
           f"alt id={r.json().get('id')}, log rows={len(check_log('create','alternative',r.json()['id']))}" if r.status_code==201 else r.text)
    alt_id = r.json()["id"]

    # 5. Create a Comment
    r = client.post(f"/decisions/{decision_id}/comments", json={"content": "A comment"}, headers=headers)
    ok = r.status_code == 201 and check_log("create", "comment", r.json()["id"])
    record("5. Create Comment auto-logs", PASS if ok else FAIL,
           f"comment id={r.json().get('id')}, log rows={len(check_log('create','comment',r.json()['id']))}" if r.status_code==201 else r.text)
    comment_id = r.json()["id"]

    # 6. Create a Discussion Thread
    r = client.post(f"/decisions/{decision_id}/threads", json={"title": "ActLog Thread", "description": "d"}, headers=headers)
    ok = r.status_code == 201 and check_log("create", "discussion_thread", r.json()["id"])
    record("6. Create Discussion Thread auto-logs", PASS if ok else FAIL,
           f"thread id={r.json().get('id')}, log rows={len(check_log('create','discussion_thread',r.json()['id']))}" if r.status_code==201 else r.text)
    thread_id = r.json()["id"]

    # ---- Postgres direct verification ----
    try:
        cols = direct_query(
            """SELECT column_name, data_type, is_nullable
               FROM information_schema.columns
               WHERE table_name = 'activity_log' ORDER BY ordinal_position"""
        )
        expected = {
            "id": "integer",
            "user_id": "integer",
            "action": "character varying",
            "entity_type": "character varying",
            "entity_id": "integer",
            "description": "text",
            "created_at": "timestamp with time zone",
        }
        got = {c[0]: c[1] for c in cols}
        struct_ok = all(got.get(k) == v for k, v in expected.items())
        record("Postgres: activity_log structure", PASS if struct_ok else FAIL,
               f"columns/types = {got}")
    except Exception as e:
        record("Postgres: activity_log structure", FAIL, str(e))

    try:
        rows = direct_query(
            "SELECT user_id, entity_type, entity_id, action FROM activity_log "
            "WHERE user_id = %s ORDER BY id",
            (user_id,),
        )
        expected_entries = [
            (user_id, "decision", decision_id, "create"),
            (user_id, "decision", decision_id, "update"),
            (user_id, "decision", decision_id, "status_change"),
            (user_id, "alternative", alt_id, "create"),
            (user_id, "comment", comment_id, "create"),
            (user_id, "discussion_thread", thread_id, "create"),
        ]
        found = [(r[0], r[1], r[2], r[3]) for r in rows]
        entries_ok = all(e in found for e in expected_entries)
        record("Postgres: entries correct (user_id/entity_type/entity_id/action)",
               PASS if entries_ok else FAIL,
               f"found {len(found)} rows: {found}")
    except Exception as e:
        record("Postgres: entries correct", FAIL, str(e))

    # ---- Cleanup ----
    try:
        with SessionLocal() as s:
            # Remove activity logs for this user first (FK from activity_log.user_id
            # to users.id has no cascade), then the user (cascades its entities).
            ActivityLog = __import__("app.models.activity_log", fromlist=["ActivityLog"]).ActivityLog
            s.query(ActivityLog).filter_by(user_id=user_id).delete()
            u = s.query(User).filter(User.id == user_id).first()
            if u:
                s.delete(u)
            s.commit()
        record("Cleanup", PASS, "test user and all related rows removed")
    except Exception as e:
        record("Cleanup", FAIL, str(e))

    print("\n=== SUMMARY ===")
    failed = [r for r in results if r[1] == FAIL]
    print(f"{len(results) - len(failed)} passed, {len(failed)} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(2)
