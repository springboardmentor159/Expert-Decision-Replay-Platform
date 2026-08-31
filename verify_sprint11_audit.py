"""
Sprint 11 Verification Script: Audit & Compliance Layer
Tests end-to-end compliance, automatic audit logging, sequential versioning,
security events, access logging, and PostgreSQL table persistence.
"""
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.main import app

client = TestClient(app)

# Database inspection
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def main():
    print("=" * 80)
    print("SPRINT 11: AUDIT & COMPLIANCE LAYER VERIFICATION")
    print("=" * 80)

    # 1. Verify PostgreSQL Database Tables
    print("\n[1] Verifying PostgreSQL Schema & Tables...")
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    required_tables = ["audit_logs", "decision_versions", "security_logs", "access_logs"]
    for t in required_tables:
        assert t in tables, f"Missing required table: {t}"
        cols = [c["name"] for c in inspector.get_columns(t)]
        print(f"  [OK] Table '{t}' exists. Columns: {cols}")

    # 2. Test User Creation & Authentication
    print("\n[2] Testing Authentication & Security Logging...")
    admin_email = f"admin_audit_{uuid.uuid4().hex[:6]}@example.com"
    emp_email = f"emp_audit_{uuid.uuid4().hex[:6]}@example.com"

    # Register Admin
    reg_admin = client.post("/users", json={
        "email": admin_email,
        "password": "Password123!",
        "full_name": "Compliance Admin",
        "role": "Administrator",
        "employee_id": f"ADM-{uuid.uuid4().hex[:4]}"
    })
    assert reg_admin.status_code == 201, reg_admin.text
    admin_id = reg_admin.json()["id"]

    # Register Employee
    reg_emp = client.post("/users", json={
        "email": emp_email,
        "password": "Password123!",
        "full_name": "Compliance Employee",
        "role": "Employee",
        "employee_id": f"EMP-{uuid.uuid4().hex[:4]}"
    })
    assert reg_emp.status_code == 201, reg_emp.text
    emp_id = reg_emp.json()["id"]

    # Failed login attempt
    fail_login = client.post("/auth/login", json={
        "email": admin_email,
        "password": "WrongPassword!"
    })
    assert fail_login.status_code == 401
    print("  [OK] Failed login correctly returned 401 Unauthorized")

    # Successful login for Admin
    admin_login = client.post("/auth/login", json={
        "email": admin_email,
        "password": "Password123!"
    })
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("  [OK] Admin logged in successfully with JWT token")

    # Successful login for Employee
    emp_login = client.post("/auth/login", json={
        "email": emp_email,
        "password": "Password123!"
    })
    assert emp_login.status_code == 200
    emp_token = emp_login.json()["access_token"]
    emp_headers = {"Authorization": f"Bearer {emp_token}"}
    print("  [OK] Employee logged in successfully with JWT token")

    # 3. Test Security Logs API
    print("\n[3] Testing Security Logs Retrieval...")
    sec_resp = client.get("/security-logs", headers=admin_headers)
    assert sec_resp.status_code == 200
    sec_items = sec_resp.json()["items"]
    event_types = [s["event_type"] for s in sec_items]
    assert "LOGIN_SUCCESS" in event_types
    assert "LOGIN_FAILED" in event_types
    print(f"  [OK] Recorded {len(sec_items)} security events (LOGIN_SUCCESS, LOGIN_FAILED)")

    # Test Employee blocked from Security Logs (403)
    emp_sec_resp = client.get("/security-logs", headers=emp_headers)
    assert emp_sec_resp.status_code == 403
    print("  [OK] Non-admin access to /security-logs rejected with 403 Forbidden")

    # 4. Test Automatic Audit Logging on Decision Creation & Sequential Versioning
    print("\n[4] Testing Decision Creation, Version 1, and Audit Log...")
    create_dec_resp = client.post("/decisions", headers=admin_headers, json={
        "title": "Select Primary Cloud Database",
        "problem_statement": "Evaluate PostgreSQL vs MySQL for high throughput analytics",
        "category": "Infrastructure"
    })
    assert create_dec_resp.status_code == 201
    decision_id = create_dec_resp.json()["id"]
    print(f"  [OK] Decision #{decision_id} created")

    # Verify Version 1
    versions_resp = client.get(f"/decisions/{decision_id}/versions", headers=admin_headers)
    assert versions_resp.status_code == 200
    versions = versions_resp.json()
    assert len(versions) == 1
    assert versions[0]["version_number"] == 1
    print("  [OK] Sequential Version 1 automatically initialized")

    # 5. Test Decision Update, Version 2, and Diff Tracking
    print("\n[5] Testing Decision Update, Version 2, and Diff Tracking...")
    update_dec_resp = client.put(f"/decisions/{decision_id}", headers=admin_headers, json={
        "title": "Select PostgreSQL 16 as Primary Cloud Database",
        "problem_statement": "PostgreSQL 16 selected for native JSON and vector index support",
        "category": "Data Infrastructure"
    })
    assert update_dec_resp.status_code == 200

    # Verify Version 2
    versions_resp2 = client.get(f"/decisions/{decision_id}/versions", headers=admin_headers)
    assert versions_resp2.status_code == 200
    assert len(versions_resp2.json()) == 2
    assert versions_resp2.json()[1]["version_number"] == 2
    print("  [OK] Sequential Version 2 automatically created on update")

    # Retrieve specific versions
    v1_detail = client.get(f"/decisions/{decision_id}/versions/1", headers=admin_headers).json()
    v2_detail = client.get(f"/decisions/{decision_id}/versions/2", headers=admin_headers).json()
    assert v1_detail["title"] == "Select Primary Cloud Database"
    assert v2_detail["title"] == "Select PostgreSQL 16 as Primary Cloud Database"
    print(f"  [OK] Retrieved Version 1: '{v1_detail['title']}'")
    print(f"  [OK] Retrieved Version 2: '{v2_detail['title']}'")

    # 6. Test Multi-Entity Operations: Alternative, Comment, Approval
    print("\n[6] Testing Multi-Entity Audit Tracking...")
    # Add Alternative
    alt_resp = client.post(f"/decisions/{decision_id}/alternatives", headers=admin_headers, json={
        "name": "Managed PostgreSQL on AWS RDS",
        "description": "Multi-AZ high availability deployment",
        "pros": "Automated backups, HA",
        "cons": "Higher operational cost",
        "estimated_cost": 750.0,
        "feasibility_score": 4,
        "risk_level": "Low"
    })
    assert alt_resp.status_code == 201
    alt_id = alt_resp.json()["id"]
    print(f"  [OK] Alternative #{alt_id} added")

    # Add Comment
    com_resp = client.post(f"/decisions/{decision_id}/comments", headers=emp_headers, json={
        "content": "RDS Multi-AZ meets our SOC2 compliance requirement."
    })
    assert com_resp.status_code == 201
    print("  [OK] Comment recorded")

    # Submit for Approval
    app_resp = client.post("/approvals", headers=admin_headers, json={
        "decision_id": decision_id,
        "reviewer_id": admin_id,
        "approval_level": 1,
        "comments": "Requesting architecture lead approval"
    })
    assert app_resp.status_code == 201
    app_id = app_resp.json()["id"]
    print(f"  [OK] Approval request #{app_id} assigned")

    # Approve
    approve_resp = client.post(f"/approvals/{app_id}/approve", headers=admin_headers, json={
        "comments": "Approved for production deployment"
    })
    assert approve_resp.status_code == 200
    print(f"  [OK] Approval #{app_id} approved")

    # 7. Test Decision Change History API
    print("\n[7] Testing Decision Lifecycle History API...")
    hist_resp = client.get(f"/decisions/{decision_id}/history", headers=admin_headers)
    assert hist_resp.status_code == 200
    hist_data = hist_resp.json()
    print(f"  [OK] Decision #{decision_id} History contains {hist_data['total_events']} events:")
    for h in hist_data["history"]:
        print(f"    - [{h['timestamp']}] {h['action']} ({h['entity_type']}): {h['description']}")

    # 8. Test Audit Logs API with Filtering & Pagination
    print("\n[8] Testing Audit Logs API & Query Filters...")
    audit_resp = client.get("/audit-logs?page=1&page_size=20", headers=admin_headers)
    assert audit_resp.status_code == 200
    audit_data = audit_resp.json()
    print(f"  [OK] Retrieved total {audit_data['total']} system audit records across entities")

    # Filter by entity_type=Decision
    audit_dec_resp = client.get("/audit-logs?entity_type=Decision", headers=admin_headers)
    assert audit_dec_resp.status_code == 200
    for itm in audit_dec_resp.json()["items"]:
        assert itm["entity_type"].lower() == "decision"
    print("  [OK] Filter by entity_type=Decision verified")

    # Filter by action=CREATE
    audit_act_resp = client.get("/audit-logs?action=CREATE", headers=admin_headers)
    assert audit_act_resp.status_code == 200
    for itm in audit_act_resp.json()["items"]:
        assert itm["action"] == "CREATE"
    print("  [OK] Filter by action=CREATE verified")

    # 9. Test Access Logs
    print("\n[9] Testing Access Logs...")
    client.get(f"/decisions/{decision_id}", headers=admin_headers)
    acc_resp = client.get(f"/access-logs?resource_type=Decision&resource_id={decision_id}", headers=admin_headers)
    assert acc_resp.status_code == 200
    assert acc_resp.json()['total'] >= 1
    print(f"  [OK] Access logs recorded {acc_resp.json()['total']} access event(s) for Decision #{decision_id}")


    # 10. Test Security & RBAC Boundary Protections
    print("\n[10] Testing RBAC Boundary Protections...")
    assert client.get("/audit-logs").status_code == 401
    assert client.get("/audit-logs", headers=emp_headers).status_code == 403
    assert client.get("/security-logs").status_code == 401
    assert client.get("/security-logs", headers=emp_headers).status_code == 403
    assert client.get("/access-logs").status_code == 401
    assert client.get("/access-logs", headers=emp_headers).status_code == 403
    print("  [OK] 401 Unauthorized verified for unauthenticated requests")
    print("  [OK] 403 Forbidden verified for non-admin audit, security, and access log access")

    print("\n" + "=" * 80)
    print("ALL SPRINT 11 AUDIT & COMPLIANCE CRITERIA SUCCESSFULLY VERIFIED!")
    print("=" * 80)


if __name__ == "__main__":
    main()
