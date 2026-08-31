"""Swagger-style E2E verification for the Dashboard endpoints (Sprint 9, Part B).

Runs against the LIVE PostgreSQL database (real FastAPI app / TestClient), then
verifies /dashboard/manager/statistics counts against a direct SQL GROUP BY.
Cleans up afterwards.

Run with:  venv/Scripts/python.exe verify_dashboard.py
"""
import os
import sys
import traceback

from app.core.config import settings
from app.db.database import SessionLocal
from app.models.user import User
from fastapi.testclient import TestClient
from app.main import app

import psycopg2

DB_URL = settings.DATABASE_URL
PSYCOPG_URL = DB_URL.replace("postgresql+psycopg2://", "postgresql://")

EMP_EMAIL = "dash_verify_emp@example.com"
EMP_EID = "EMP_DASH_VERIFY"
MGR_EMAIL = "dash_verify_mgr@example.com"
MGR_EID = "MGR_DASH_VERIFY"
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

    # Clean any leftover test users (and their activity logs) before starting.
    ActivityLog = __import__("app.models.activity_log", fromlist=["ActivityLog"]).ActivityLog
    with SessionLocal() as s:
        for email in (EMP_EMAIL, MGR_EMAIL):
            old = s.query(User).filter(User.email == email).first()
            if old:
                s.query(ActivityLog).filter_by(user_id=old.id).delete()
                s.delete(old)
                s.commit()

    # Signup Employee + Manager, login both
    client.post("/users", json={
        "full_name": "Dash Verify Employee", "email": EMP_EMAIL,
        "password": PASSWORD, "employee_id": EMP_EID, "role": "Employee"})
    client.post("/users", json={
        "full_name": "Dash Verify Manager", "email": MGR_EMAIL,
        "password": PASSWORD, "employee_id": MGR_EID, "role": "Manager"})

    emp_login = client.post("/login", json={"email": EMP_EMAIL, "password": PASSWORD}).json()
    mgr_login = client.post("/login", json={"email": MGR_EMAIL, "password": PASSWORD}).json()
    emp_headers = {"Authorization": f"Bearer {emp_login['access_token']}"}
    mgr_headers = {"Authorization": f"Bearer {mgr_login['access_token']}"}
    emp_id = emp_login["user"]["id"]
    mgr_id = mgr_login["user"]["id"]

    # 1. Employee dashboard (own stats only, currently empty)
    r = client.get("/dashboard/employee", headers=emp_headers)
    ok = r.status_code == 200 and r.json()["user_id"] == emp_id and r.json()["total_decisions"] == 0
    record("1. Employee GET /dashboard/employee (empty)", PASS if ok else FAIL,
           f"status={r.status_code}, body={r.json()}" if ok else r.text)

    # 2. Employee creates decision + alternative + comment, then re-fetch
    d_id = client.post("/decisions", json={"title": "Dash D", "problem_statement": "PS", "category": "Eng"},
                      headers=emp_headers).json()["id"]
    client.post(f"/decisions/{d_id}/alternatives",
                json={"name": "A1", "description": "d", "pros": "p", "cons": "c"}, headers=emp_headers)
    client.post(f"/decisions/{d_id}/comments", json={"content": "hi"}, headers=emp_headers)

    r2 = client.get("/dashboard/employee", headers=emp_headers)
    body = r2.json()
    ok = (r2.status_code == 200 and body["total_decisions"] == 1
          and any(a["action"] == "create" and a["entity_type"] == "decision" for a in body["recent_activity"])
          and any(a["entity_type"] == "alternative" for a in body["recent_activity"])
          and any(a["entity_type"] == "comment" for a in body["recent_activity"]))
    record("2. Employee dashboard updates after create/alt/comment", PASS if ok else FAIL,
           f"total={body['total_decisions']}, activity_actions={sorted({(a['action'],a['entity_type']) for a in body['recent_activity']})}")

    # Manager creates an Approved decision so org-wide counts are non-trivial
    md_id = client.post("/decisions", json={"title": "Mgr D", "problem_statement": "PS", "category": "Eng"},
                       headers=mgr_headers).json()["id"]
    client.patch(f"/decisions/{md_id}/status", json={"status": "Approved"}, headers=mgr_headers)

    # 3. Manager statistics match direct SQL GROUP BY
    r3 = client.get("/dashboard/manager/statistics", headers=mgr_headers)
    stats = r3.json()
    pg_rows = direct_query("SELECT status, count(*) FROM decisions GROUP BY status")
    pg_counts = {row[0]: row[1] for row in pg_rows}
    expected = {
        "draft": pg_counts.get("Draft", 0),
        "under_review": pg_counts.get("Under Review", 0),
        "approved": pg_counts.get("Approved", 0),
        "rejected": pg_counts.get("Rejected", 0),
        "archived": pg_counts.get("Archived", 0),
    }
    ok = (r3.status_code == 200 and stats["scope"] == "org-wide"
          and stats["draft"] == expected["draft"] and stats["under_review"] == expected["under_review"]
          and stats["approved"] == expected["approved"] and stats["rejected"] == expected["rejected"]
          and stats["archived"] == expected["archived"]
          and stats["total"] == sum(expected.values()))
    record("3. Manager /dashboard/manager/statistics matches PG GROUP BY", PASS if ok else FAIL,
           f"api={stats}, pg={expected}")

    # 4. Manager pending-approvals is BLOCKED (501, no approval workflow)
    r4 = client.get("/dashboard/manager/pending-approvals", headers=mgr_headers)
    ok = r4.status_code == 501 and "approval workflow" in r4.json()["detail"].lower()
    record("4. Manager /dashboard/manager/pending-approvals BLOCKED (501)", PASS if ok else FAIL,
           f"status={r4.status_code}, detail={r4.json().get('detail') if r4.status_code!=200 else ''}")

    # 5. Employee attempting manager statistics → 403
    r5 = client.get("/dashboard/manager/statistics", headers=emp_headers)
    ok = r5.status_code == 403 and r5.json()["detail"] == "Not authorized to view manager dashboards"
    record("5. Employee -> manager/statistics is 403", PASS if ok else FAIL,
           f"status={r5.status_code}, detail={r5.json().get('detail') if r5.status_code!=200 else ''}")

    # 6. No token → 401 on all dashboard endpoints
    no_token_ok = True
    for url in ["/dashboard/employee", "/dashboard/manager/statistics", "/dashboard/manager/pending-approvals"]:
        rr = client.get(url)
        if rr.status_code != 401 or rr.json()["detail"] != "Not authenticated":
            no_token_ok = False
    record("6. All dashboard endpoints require token (401)", PASS if no_token_ok else FAIL,
           "all three returned 401 Not authenticated" if no_token_ok else "mismatch")

    # ---- Postgres direct verification of decision counts by status ----
    try:
        rows = direct_query(
            "SELECT status, count(*) FROM decisions GROUP BY status ORDER BY status")
        record("Postgres: decision counts by status", PASS,
               f"rows = {[ (r[0], r[1]) for r in rows ]}")
    except Exception as e:
        record("Postgres: decision counts by status", FAIL, str(e))

    # ---- Cleanup ----
    try:
        with SessionLocal() as s:
            ActivityLog = __import__("app.models.activity_log", fromlist=["ActivityLog"]).ActivityLog
            for uid in (emp_id, mgr_id):
                s.query(ActivityLog).filter_by(user_id=uid).delete()
                u = s.query(User).filter(User.id == uid).first()
                if u:
                    s.delete(u)
            s.commit()
        record("Cleanup", PASS, "test users and related rows removed")
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
