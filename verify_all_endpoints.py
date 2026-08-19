import sys
import json
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import SessionLocal
from app.models.user import User

client = TestClient(app)

def run_comprehensive_endpoint_checks():
    print("=" * 70)
    print(" COMPREHENSIVE ENDPOINT AUDIT & VERIFICATION REPORT")
    print("=" * 70)

    results = []

    def record_result(endpoint, method, description, status, passed, details=""):
        results.append({
            "endpoint": endpoint,
            "method": method,
            "description": description,
            "status": status,
            "passed": passed,
            "details": details
        })
        icon = "[PASS]" if passed else "[FAIL]"
        print(f"{icon} {method:<6} {endpoint:<22} -> Status {status} | {description}")
        if not passed and details:
            print(f"       ERROR: {details}")

    # -------------------------------------------------------------
    # 1. DOCUMENTATION & OPENAPI ENDPOINTS
    # -------------------------------------------------------------
    print("\n--- 1. Documentation & OpenAPI Endpoints ---")
    
    # GET /docs
    res = client.get("/docs")
    passed = (res.status_code == 200)
    record_result("/docs", "GET", "Swagger UI interactive documentation", res.status_code, passed)

    # GET /redoc
    res = client.get("/redoc")
    passed = (res.status_code == 200)
    record_result("/redoc", "GET", "ReDoc alternative documentation", res.status_code, passed)

    # GET /openapi.json
    res = client.get("/openapi.json")
    passed = (res.status_code == 200 and "paths" in res.json())
    record_result("/openapi.json", "GET", "OpenAPI JSON Schema specification", res.status_code, passed)

    # -------------------------------------------------------------
    # 2. USER REGISTRATION (POST /users)
    # -------------------------------------------------------------
    print("\n--- 2. User Registration (POST /users) ---")

    # Cleanup any old test users
    test_emails = [
        "audit_emp@example.com",
        "audit_rev@example.com",
        "audit_mgr@example.com",
        "audit_adm@example.com",
        "audit_dup@example.com"
    ]
    db = SessionLocal()
    db.query(User).filter(User.email.in_(test_emails)).delete(synchronize_session=False)
    db.commit()
    db.close()

    # Invalid role validation (Expect 422)
    bad_role_payload = {
        "full_name": "Invalid Role Tester",
        "email": "audit_bad_role@example.com",
        "role": "SuperAdmin",
        "password": "Password123!",
        "employee_id": "AUDIT_BAD_01"
    }
    res = client.post("/users", json=bad_role_payload)
    passed = (res.status_code == 422)
    record_result("/users", "POST", "Role validation rejects non-enum role (422)", res.status_code, passed)

    # Valid User Creation: Employee
    emp_payload = {
        "full_name": "Audit Employee",
        "email": "audit_emp@example.com",
        "role": "Employee",
        "password": "SecurePassword123!",
        "employee_id": "EMP_AUDIT_01",
        "department": "Core Platform",
        "designation": "Software Engineer",
        "phone_number": "+1-555-0101"
    }
    res = client.post("/users", json=emp_payload)
    emp_user = res.json() if res.status_code == 201 else {}
    emp_id = emp_user.get("id")
    passed = (res.status_code == 201 and emp_user.get("email") == "audit_emp@example.com" and emp_user.get("role") == "Employee")
    record_result("/users", "POST", "Create user with Employee role & profile metadata (201)", res.status_code, passed)

    # Valid User Creation: Reviewer
    rev_payload = {
        "full_name": "Audit Reviewer",
        "email": "audit_rev@example.com",
        "role": "Reviewer",
        "password": "SecurePassword123!",
        "employee_id": "REV_AUDIT_01",
        "department": "QA",
        "designation": "Senior Reviewer"
    }
    res = client.post("/users", json=rev_payload)
    rev_user = res.json() if res.status_code == 201 else {}
    rev_id = rev_user.get("id")
    passed = (res.status_code == 201 and rev_user.get("role") == "Reviewer")
    record_result("/users", "POST", "Create user with Reviewer role (201)", res.status_code, passed)

    # Valid User Creation: Manager
    mgr_payload = {
        "full_name": "Audit Manager",
        "email": "audit_mgr@example.com",
        "role": "Manager",
        "password": "SecurePassword123!",
        "employee_id": "MGR_AUDIT_01",
        "department": "Engineering Operations",
        "designation": "Engineering Manager"
    }
    res = client.post("/users", json=mgr_payload)
    mgr_user = res.json() if res.status_code == 201 else {}
    mgr_id = mgr_user.get("id")
    passed = (res.status_code == 201 and mgr_user.get("role") == "Manager")
    record_result("/users", "POST", "Create user with Manager role (201)", res.status_code, passed)

    # Valid User Creation: Administrator
    adm_payload = {
        "full_name": "Audit Administrator",
        "email": "audit_adm@example.com",
        "role": "Administrator",
        "password": "SecurePassword123!",
        "employee_id": "ADM_AUDIT_01",
        "department": "IT & SecOps",
        "designation": "System Administrator"
    }
    res = client.post("/users", json=adm_payload)
    adm_user = res.json() if res.status_code == 201 else {}
    adm_id = adm_user.get("id")
    passed = (res.status_code == 201 and adm_user.get("role") == "Administrator")
    record_result("/users", "POST", "Create user with Administrator role (201)", res.status_code, passed)

    # Duplicate Email Validation (Expect 400)
    dup_email_payload = {
        "full_name": "Duplicate Email Tester",
        "email": "audit_emp@example.com", # Already used
        "role": "Employee",
        "password": "Password123!",
        "employee_id": "EMP_AUDIT_UNIQUE"
    }
    res = client.post("/users", json=dup_email_payload)
    passed = (res.status_code == 400 and "already registered" in res.text.lower())
    record_result("/users", "POST", "Reject duplicate email with 400 Bad Request", res.status_code, passed)

    # Duplicate Employee ID Validation (Expect 400)
    dup_empid_payload = {
        "full_name": "Duplicate Emp ID Tester",
        "email": "audit_dup@example.com",
        "role": "Employee",
        "password": "Password123!",
        "employee_id": "EMP_AUDIT_01" # Already used
    }
    res = client.post("/users", json=dup_empid_payload)
    passed = (res.status_code == 400 and "employee id" in res.text.lower())
    record_result("/users", "POST", "Reject duplicate employee_id with 400 Bad Request", res.status_code, passed)

    # -------------------------------------------------------------
    # 3. AUTHENTICATION & LOGIN (POST /auth/login & POST /users/login)
    # -------------------------------------------------------------
    print("\n--- 3. Authentication & Login Endpoints ---")

    # POST /auth/login with wrong password (401)
    res = client.post("/auth/login", json={"email": "audit_emp@example.com", "password": "WrongPassword"})
    passed = (res.status_code == 401)
    record_result("/auth/login", "POST", "Reject invalid password with 401 Unauthorized", res.status_code, passed)

    # POST /auth/login with non-existent email (401)
    res = client.post("/auth/login", json={"email": "nonexistent@example.com", "password": "Password123!"})
    passed = (res.status_code == 401)
    record_result("/auth/login", "POST", "Reject non-existent email with 401 Unauthorized", res.status_code, passed)

    # POST /auth/login with valid credentials (200)
    res = client.post("/auth/login", json={"email": "audit_emp@example.com", "password": "SecurePassword123!"})
    token_emp = res.json().get("access_token") if res.status_code == 200 else None
    passed = (res.status_code == 200 and token_emp is not None and res.json().get("token_type") == "bearer")
    record_result("/auth/login", "POST", "Authenticate valid user & return JWT Bearer token (200)", res.status_code, passed)

    # POST /users/login alias with valid credentials (200)
    res = client.post("/users/login", json={"email": "audit_adm@example.com", "password": "SecurePassword123!"})
    token_adm = res.json().get("access_token") if res.status_code == 200 else None
    passed = (res.status_code == 200 and token_adm is not None)
    record_result("/users/login", "POST", "Authenticate via /users/login alias endpoint (200)", res.status_code, passed)

    emp_headers = {"Authorization": f"Bearer {token_emp}"}

    # -------------------------------------------------------------
    # 4. UNPROTECTED ACCESS ATTEMPTS ON PROTECTED ROUTES (Expect 401)
    # -------------------------------------------------------------
    print("\n--- 4. Protected Route Security (Unauthorized Checks - 401) ---")

    protected_routes = [
        ("GET", "/users/me", "GET /users/me without Bearer token"),
        ("GET", "/users", "GET /users without Bearer token"),
        ("GET", f"/users/{emp_id}", f"GET /users/{emp_id} without Bearer token"),
        ("PUT", f"/users/{emp_id}", f"PUT /users/{emp_id} without Bearer token"),
        ("DELETE", f"/users/{emp_id}", f"DELETE /users/{emp_id} without Bearer token"),
    ]

    for meth, path, desc in protected_routes:
        if meth == "GET":
            r = client.get(path)
        elif meth == "PUT":
            r = client.put(path, json={"designation": "Hacker"})
        elif meth == "DELETE":
            r = client.delete(path)
        passed = (r.status_code == 401)
        record_result(path, meth, f"Reject unauthenticated request (401): {desc}", r.status_code, passed)

    # -------------------------------------------------------------
    # 5. USER PROFILE & USER LIST (GET /users/me, GET /users, GET /users/{id})
    # -------------------------------------------------------------
    print("\n--- 5. Protected Query Endpoints (GET /users/me, GET /users, GET /users/{id}) ---")

    # GET /users/me with token
    res = client.get("/users/me", headers=emp_headers)
    passed = (res.status_code == 200 and res.json().get("email") == "audit_emp@example.com" and res.json().get("employee_id") == "EMP_AUDIT_01")
    record_result("/users/me", "GET", "Fetch current authenticated user profile (200)", res.status_code, passed)

    # GET /users with token
    res = client.get("/users", headers=emp_headers)
    users_list = res.json() if res.status_code == 200 else []
    passed = (res.status_code == 200 and isinstance(users_list, list) and len(users_list) >= 4)
    record_result("/users", "GET", f"List all users in directory ({len(users_list)} users found) (200)", res.status_code, passed)

    # GET /users/{id} with valid id
    res = client.get(f"/users/{emp_id}", headers=emp_headers)
    passed = (res.status_code == 200 and res.json().get("id") == emp_id and res.json().get("full_name") == "Audit Employee")
    record_result(f"/users/{emp_id}", "GET", f"Fetch user by ID ({emp_id}) (200)", res.status_code, passed)

    # GET /users/{id} with non-existent id (404)
    res = client.get("/users/9999999", headers=emp_headers)
    passed = (res.status_code == 404)
    record_result("/users/9999999", "GET", "Return 404 Not Found for non-existent user ID", res.status_code, passed)

    # -------------------------------------------------------------
    # 6. USER UPDATE (PUT /users/{id})
    # -------------------------------------------------------------
    print("\n--- 6. User Update (PUT /users/{id}) ---")

    # PUT /users/{id} update designation, phone, and department
    update_payload = {
        "designation": "Principal Software Engineer",
        "phone_number": "+1-555-9999",
        "department": "Platform Architecture"
    }
    res = client.put(f"/users/{emp_id}", json=update_payload, headers=emp_headers)
    updated_data = res.json() if res.status_code == 200 else {}
    passed = (
        res.status_code == 200 and 
        updated_data.get("designation") == "Principal Software Engineer" and
        updated_data.get("phone_number") == "+1-555-9999" and
        updated_data.get("department") == "Platform Architecture"
    )
    record_result(f"/users/{emp_id}", "PUT", "Update user profile fields successfully (200)", res.status_code, passed)

    # PUT /users/{id} non-existent user (404)
    res = client.put("/users/9999999", json=update_payload, headers=emp_headers)
    passed = (res.status_code == 404)
    record_result("/users/9999999", "PUT", "Return 404 Not Found when updating non-existent user", res.status_code, passed)

    # -------------------------------------------------------------
    # 7. USER DELETION (DELETE /users/{id})
    # -------------------------------------------------------------
    print("\n--- 7. User Deletion (DELETE /users/{id}) ---")

    # DELETE non-existent user (404) while token is still active
    res = client.delete("/users/9999999", headers=emp_headers)
    passed = (res.status_code == 404)
    record_result("/users/9999999", "DELETE", "Return 404 Not Found when deleting non-existent user", res.status_code, passed)

    # DELETE other created test users
    for uid, rname in [(rev_id, "Reviewer"), (mgr_id, "Manager"), (adm_id, "Administrator")]:
        res = client.delete(f"/users/{uid}", headers=emp_headers)
        passed = (res.status_code == 200 and res.json().get("message") == "User deleted successfully")
        record_result(f"/users/{uid}", "DELETE", f"Delete {rname} user ID {uid} (200)", res.status_code, passed)

    # Finally DELETE self (Employee)
    res = client.delete(f"/users/{emp_id}", headers=emp_headers)
    passed = (res.status_code == 200 and res.json().get("message") == "User deleted successfully")
    record_result(f"/users/{emp_id}", "DELETE", f"Delete Employee (Self) user ID {emp_id} (200)", res.status_code, passed)

    # -------------------------------------------------------------
    # FINAL SUMMARY
    # -------------------------------------------------------------
    total = len(results)
    passed_cnt = sum(1 for r in results if r["passed"])
    failed_cnt = total - passed_cnt

    print("\n" + "=" * 70)
    print(f" TOTAL ENDPOINTS / SCENARIOS TESTED: {total}")
    print(f" PASSED: {passed_cnt}")
    print(f" FAILED: {failed_cnt}")
    print(f" SUCCESS RATE: {(passed_cnt / total) * 100:.1f}%")
    print("=" * 70)

    if failed_cnt > 0:
        print("\nFailed test details:")
        for r in results:
            if not r["passed"]:
                print(f"- {r['method']} {r['endpoint']}: {r['description']} (Status {r['status']})")
        sys.exit(1)
    else:
        print("\n>>> ALL ENDPOINTS ARE FULLY FUNCTIONAL AND WORKING PROPERLY! <<<")

if __name__ == "__main__":
    run_comprehensive_endpoint_checks()
