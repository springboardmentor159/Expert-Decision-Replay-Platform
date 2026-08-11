"""Comprehensive verification script for User Management & Auth module."""
import sys
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import SessionLocal
from app.models.user import User

client = TestClient(app)


def run_tests():
    print("==================================================")
    print("STARTING USER MANAGEMENT & AUTH VERIFICATION TESTS")
    print("==================================================")

    # 1. TEST ROLE VALIDATION ON REGISTRATION
    print("\n--- 1. Testing Role Management ---")

    # Test invalid role
    invalid_user_data = {
        "full_name": "Invalid Role User",
        "email": "invalidrole@example.com",
        "password": "Password123!",
        "role": "SuperUser",
        "employee_id": "EMP_INV_01"
    }
    res = client.post("/users", json=invalid_user_data)
    print(f"POST /users with invalid role 'SuperUser': Status {res.status_code}")
    assert res.status_code == 422, f"Expected 422 for invalid role, got {res.status_code}: {res.text}"
    print(" [PASS] Invalid role automatically rejected with 422.")

    # Test valid roles: Employee, Reviewer, Manager, Administrator
    valid_roles = ["Employee", "Reviewer", "Manager", "Administrator"]
    created_user_ids = []

    for role in valid_roles:
        email = f"test_{role.lower()}@example.com"
        emp_id = f"EMP_{role.upper()[:3]}_001"

        # Cleanup in case previous run left it
        db = SessionLocal()
        db.query(User).filter((User.email == email) | (User.employee_id == emp_id)).delete()
        db.commit()
        db.close()

        user_data = {
            "full_name": f"Test {role}",
            "email": email,
            "password": "SecurePassword123!",
            "role": role,
            "employee_id": emp_id,
            "department": f"{role} Dept",
            "designation": f"Senior {role}",
            "phone_number": "+1-555-0100"
        }
        res = client.post("/users", json=user_data)
        print(f"POST /users with valid role '{role}': Status {res.status_code}")
        assert res.status_code == 201, f"Failed to create user with role {role}: {res.text}"
        data = res.json()
        assert data["role"] == role, f"Role mismatch: {data['role']} vs {role}"
        assert data["employee_id"] == emp_id
        assert data["department"] == f"{role} Dept"
        assert data["designation"] == f"Senior {role}"
        assert data["phone_number"] == "+1-555-0100"
        created_user_ids.append(data["id"])
        print(f" [PASS] User with role '{role}' and profile successfully created.")

    # 2. TEST PROFILE ENHANCEMENT & UNIQUENESS
    print("\n--- 2. Testing User Profile Enhancement ---")

    # Test duplicate employee_id
    duplicate_emp_user = {
        "full_name": "Duplicate Emp User",
        "email": "dup_emp@example.com",
        "password": "Password123!",
        "role": "Employee",
        "employee_id": "EMP_EMP_001"  # Already used above
    }
    res = client.post("/users", json=duplicate_emp_user)
    print(f"POST /users with duplicate employee_id: Status {res.status_code}")
    assert res.status_code == 400, f"Expected 400 for duplicate employee_id, got {res.status_code}"
    print(" [PASS] Duplicate employee_id rejected with 400 Bad Request.")

    # 3. TEST JWT AUTHENTICATION & LOGIN
    print("\n--- 3. Testing JWT Authentication & Login ---")

    # Invalid login
    res = client.post("/auth/login", json={"email": "test_employee@example.com", "password": "WrongPassword"})
    print(f"POST /auth/login with wrong password: Status {res.status_code}")
    assert res.status_code == 401, f"Expected 401 for wrong credentials, got {res.status_code}"
    print(" [PASS] Login with wrong credentials rejected with 401 Unauthorized.")

    # Valid JSON login to /auth/login
    res = client.post("/auth/login", json={"email": "test_employee@example.com", "password": "SecurePassword123!"})
    print(f"POST /auth/login with valid credentials: Status {res.status_code}")
    assert res.status_code == 200, f"Login failed: {res.text}"
    token_data = res.json()
    assert "access_token" in token_data
    assert token_data["token_type"].lower() == "bearer"
    token = token_data["access_token"]
    print(" [PASS] /auth/login returned valid JWT access token.")

    # Valid JSON login to /users/login alias
    res = client.post("/users/login", json={"email": "test_employee@example.com", "password": "SecurePassword123!"})
    print(f"POST /users/login alias with valid credentials: Status {res.status_code}")
    assert res.status_code == 200, f"JSON alias login failed: {res.text}"
    assert "access_token" in res.json()
    print(" [PASS] /users/login alias returned valid JWT access token.")

    # 4. TEST PROTECTED ENDPOINTS WITHOUT TOKEN (Expect 401)
    print("\n--- 4. Testing Protected APIs without Token ---")
    emp_user_id = created_user_ids[0]

    endpoints_to_test = [
        ("GET", "/users"),
        ("GET", "/users/me"),
        ("GET", f"/users/{emp_user_id}"),
        ("PUT", f"/users/{emp_user_id}"),
        ("DELETE", f"/users/{emp_user_id}")
    ]

    for method, path in endpoints_to_test:
        if method == "GET":
            res = client.get(path)
        elif method == "PUT":
            res = client.put(path, json={"full_name": "Unauth Edit"})
        elif method == "DELETE":
            res = client.delete(path)
        print(f"{method} {path} without token: Status {res.status_code}")
        assert res.status_code == 401, f"Expected 401 for unauthenticated {method} {path}, got {res.status_code}"
    print(" [PASS] All protected endpoints returned 401 Unauthorized when unauthenticated.")

    # 5. TEST PROTECTED ENDPOINTS WITH BEARER TOKEN
    print("\n--- 5. Testing Protected APIs with Valid Bearer Token ---")
    headers = {"Authorization": f"Bearer {token}"}

    # GET /users/me
    res = client.get("/users/me", headers=headers)
    print(f"GET /users/me with token: Status {res.status_code}")
    assert res.status_code == 200, f"GET /users/me failed: {res.text}"
    profile = res.json()
    assert profile["email"] == "test_employee@example.com"
    assert profile["role"] == "Employee"
    assert profile["employee_id"] == "EMP_EMP_001"
    print(f" [PASS] /users/me returned authenticated user profile: {profile['full_name']} ({profile['role']})")

    # GET /users
    res = client.get("/users", headers=headers)
    print(f"GET /users with token: Status {res.status_code}")
    assert res.status_code == 200
    all_users = res.json()
    assert len(all_users) >= len(valid_roles)
    print(f" [PASS] GET /users returned {len(all_users)} users.")

    # GET /users/{id}
    res = client.get(f"/users/{emp_user_id}", headers=headers)
    print(f"GET /users/{emp_user_id} with token: Status {res.status_code}")
    assert res.status_code == 200
    assert res.json()["id"] == emp_user_id
    print(" [PASS] GET /users/{id} returned requested user.")

    # PUT /users/{id} (Update profile)
    update_data = {
        "designation": "Lead Employee",
        "phone_number": "+1-555-9999",
        "department": "Engineering Core"
    }
    res = client.put(f"/users/{emp_user_id}", json=update_data, headers=headers)
    print(f"PUT /users/{emp_user_id} with token: Status {res.status_code}")
    assert res.status_code == 200
    updated_user = res.json()
    assert updated_user["designation"] == "Lead Employee"
    assert updated_user["phone_number"] == "+1-555-9999"
    assert updated_user["department"] == "Engineering Core"
    print(" [PASS] PUT /users/{id} successfully updated user profile.")

    # 6. TEST DELETE PROTECTED ENDPOINT
    print("\n--- 6. Testing DELETE user ---")
    # Delete non-current users first while current_user token is valid
    for uid in created_user_ids[1:]:
        res = client.delete(f"/users/{uid}", headers=headers)
        print(f"DELETE /users/{uid} with valid token: Status {res.status_code}")
        assert res.status_code == 200, f"Failed to delete user {uid}: {res.text}"

    # Now delete the current_user itself
    res = client.delete(f"/users/{emp_user_id}", headers=headers)
    print(f"DELETE /users/{emp_user_id} (current user) with valid token: Status {res.status_code}")
    assert res.status_code == 200, f"Failed to delete current user {emp_user_id}: {res.text}"
    print(f" [PASS] Deleted {len(created_user_ids)} test users successfully.")


    print("\n==================================================")
    print(" ALL USER MANAGEMENT & AUTH TESTS PASSED SUCCESSFULLY! ")
    print("==================================================")


if __name__ == "__main__":
    run_tests()
