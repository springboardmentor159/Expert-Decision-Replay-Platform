"""
Sprint 6 Alternative Analysis Module - Comprehensive Test
Tests all endpoints for alternatives functionality
"""

import requests
import json

BASE_URL = "http://localhost:8000"

# Test data
TEST_USER_EMAIL = "john.doe@company.com"
TEST_USER_PASSWORD = "TestPassword123"
JWT_TOKEN = None
DECISION_ID = None
ALTERNATIVE_IDS = []


def print_section(title):
    """Print a section header"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def print_result(endpoint, method, status_code, success):
    """Print test result"""
    status = "✓ PASS" if success else "✗ FAIL"
    print(f"{status} | {method:4} {endpoint:50} [{status_code}]")


def step(description):
    """Print a step description"""
    print(f"\n→ {description}")


# ========== Step 1: Create User ==========
def test_create_user():
    step("Creating test user")
    response = requests.post(
        f"{BASE_URL}/users",
        json={
            "full_name": "John Doe",
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "role": "Manager",
            "employee_id": "E001",
            "department": "IT",
            "designation": "Manager",
            "phone_number": "555-0001",
        },
    )
    success = response.status_code in [200, 201]
    print_result("/users", "POST", response.status_code, success)
    if not success:
        print(f"Error: {response.text}")
    return success


# ========== Step 2: Login and Get JWT Token ==========
def test_login():
    global JWT_TOKEN
    step("Logging in to get JWT token")
    response = requests.post(
        f"{BASE_URL}/token",
        data={"username": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
    )
    success = response.status_code == 200
    print_result("/token", "POST", response.status_code, success)
    if success:
        data = response.json()
        JWT_TOKEN = data["access_token"]
        print(f"JWT Token obtained: {JWT_TOKEN[:20]}...")
    else:
        print(f"Error: {response.text}")
    return success


def get_headers():
    """Get headers with JWT token"""
    return {
        "Authorization": f"Bearer {JWT_TOKEN}",
        "Content-Type": "application/json",
    }


# ========== Step 3: Create Decision ==========
def test_create_decision():
    global DECISION_ID
    step("Creating a decision")
    response = requests.post(
        f"{BASE_URL}/decisions",
        headers=get_headers(),
        json={
            "title": "Select Database",
            "problem_statement": "We need to choose a database for our new platform",
            "category": "Technology",
        },
    )
    success = response.status_code == 201
    print_result("/decisions", "POST", response.status_code, success)
    if success:
        data = response.json()
        DECISION_ID = data["id"]
        print(f"Decision created with ID: {DECISION_ID}")
    else:
        print(f"Error: {response.text}")
    return success


# ========== Step 4: Create Alternatives ==========
def test_create_alternatives():
    step("Creating 3 alternatives for the decision")
    
    alternatives_data = [
        {
            "name": "PostgreSQL",
            "description": "Use PostgreSQL as the primary relational database",
            "pros": "Reliable, mature ecosystem, excellent performance",
            "cons": "Requires relational schema design",
            "estimated_cost": 5000,
            "feasibility_score": 5,
            "risk_level": "Low",
        },
        {
            "name": "MySQL",
            "description": "Use MySQL as the database solution",
            "pros": "Easy to use, widely supported",
            "cons": "Limited advanced features",
            "estimated_cost": 4500,
            "feasibility_score": 4,
            "risk_level": "Low",
        },
        {
            "name": "MongoDB",
            "description": "Use MongoDB as a NoSQL database",
            "pros": "Scalable, flexible schema",
            "cons": "Requires different query patterns",
            "estimated_cost": 7000,
            "feasibility_score": 4,
            "risk_level": "Medium",
        },
    ]

    all_success = True
    for alt_data in alternatives_data:
        response = requests.post(
            f"{BASE_URL}/decisions/{DECISION_ID}/alternatives",
            headers=get_headers(),
            json=alt_data,
        )
        success = response.status_code == 201
        print_result(f"/decisions/{DECISION_ID}/alternatives", "POST", response.status_code, success)
        if success:
            data = response.json()
            ALTERNATIVE_IDS.append(data["id"])
            print(f"  Alternative created: {data['name']} (ID: {data['id']})")
        else:
            print(f"  Error: {response.text}")
            all_success = False

    return all_success


# ========== Step 5: Get All Alternatives ==========
def test_get_alternatives():
    step("Getting all alternatives for the decision")
    response = requests.get(
        f"{BASE_URL}/decisions/{DECISION_ID}/alternatives",
        headers=get_headers(),
    )
    success = response.status_code == 200
    print_result(f"/decisions/{DECISION_ID}/alternatives", "GET", response.status_code, success)
    if success:
        data = response.json()
        print(f"Retrieved {len(data)} alternatives:")
        for alt in data:
            print(f"  - {alt['name']} (ID: {alt['id']}, Cost: ${alt['estimated_cost']}, Feasibility: {alt['feasibility_score']}/5)")
    else:
        print(f"Error: {response.text}")
    return success


# ========== Step 6: Get Single Alternative ==========
def test_get_single_alternative():
    if not ALTERNATIVE_IDS:
        print("No alternatives to test")
        return False
    
    alt_id = ALTERNATIVE_IDS[0]
    step(f"Getting single alternative (ID: {alt_id})")
    response = requests.get(
        f"{BASE_URL}/alternatives/{alt_id}",
        headers=get_headers(),
    )
    success = response.status_code == 200
    print_result(f"/alternatives/{alt_id}", "GET", response.status_code, success)
    if success:
        data = response.json()
        print(f"Retrieved: {data['name']}")
        print(f"  Description: {data['description']}")
        print(f"  Pros: {data['pros']}")
        print(f"  Cons: {data['cons']}")
        print(f"  Cost: ${data['estimated_cost']}")
        print(f"  Feasibility: {data['feasibility_score']}/5")
        print(f"  Risk: {data['risk_level']}")
    else:
        print(f"Error: {response.text}")
    return success


# ========== Step 7: Update Alternative ==========
def test_update_alternative():
    if not ALTERNATIVE_IDS:
        print("No alternatives to test")
        return False
    
    alt_id = ALTERNATIVE_IDS[0]
    step(f"Updating alternative (ID: {alt_id})")
    response = requests.put(
        f"{BASE_URL}/alternatives/{alt_id}",
        headers=get_headers(),
        json={
            "estimated_cost": 5500,
            "feasibility_score": 5,
            "pros": "Reliable, scalable, mature ecosystem",
        },
    )
    success = response.status_code == 200
    print_result(f"/alternatives/{alt_id}", "PUT", response.status_code, success)
    if success:
        data = response.json()
        print(f"Updated: {data['name']}")
        print(f"  New Cost: ${data['estimated_cost']}")
        print(f"  New Feasibility: {data['feasibility_score']}/5")
        print(f"  New Pros: {data['pros']}")
    else:
        print(f"Error: {response.text}")
    return success


# ========== Step 8: Test Invalid Risk Level ==========
def test_invalid_risk_level():
    step("Testing invalid risk level validation")
    response = requests.post(
        f"{BASE_URL}/decisions/{DECISION_ID}/alternatives",
        headers=get_headers(),
        json={
            "name": "Invalid Risk Test",
            "description": "Test invalid risk",
            "pros": "Test",
            "cons": "Test",
            "estimated_cost": 1000,
            "feasibility_score": 3,
            "risk_level": "Very Dangerous",  # Invalid
        },
    )
    success = response.status_code == 422
    print_result("/decisions/{decision_id}/alternatives (Invalid Risk)", "POST", response.status_code, success)
    if success:
        print("✓ Correctly rejected invalid risk level")
    else:
        print(f"Error: Expected 422, got {response.status_code}")
    return success


# ========== Step 9: Test Invalid Feasibility Score ==========
def test_invalid_feasibility_score():
    step("Testing invalid feasibility score validation")
    response = requests.post(
        f"{BASE_URL}/decisions/{DECISION_ID}/alternatives",
        headers=get_headers(),
        json={
            "name": "Invalid Feasibility Test",
            "description": "Test invalid feasibility",
            "pros": "Test",
            "cons": "Test",
            "estimated_cost": 1000,
            "feasibility_score": 10,  # Invalid (must be 1-5)
            "risk_level": "Low",
        },
    )
    success = response.status_code == 422
    print_result("/decisions/{decision_id}/alternatives (Invalid Feasibility)", "POST", response.status_code, success)
    if success:
        print("✓ Correctly rejected invalid feasibility score")
    else:
        print(f"Error: Expected 422, got {response.status_code}")
    return success


# ========== Step 10: Compare Alternatives ==========
def test_compare_alternatives():
    step("Comparing alternatives for the decision")
    response = requests.get(
        f"{BASE_URL}/decisions/{DECISION_ID}/alternatives/compare",
        headers=get_headers(),
    )
    success = response.status_code == 200
    print_result(f"/decisions/{DECISION_ID}/alternatives/compare", "GET", response.status_code, success)
    if success:
        data = response.json()
        print(f"Decision ID: {data['decision_id']}")
        print(f"Alternatives ({len(data['alternatives'])} total):")
        for alt in data['alternatives']:
            print(f"  - {alt['name']}")
            print(f"      Cost: ${alt['estimated_cost']}")
            print(f"      Feasibility: {alt['feasibility_score']}/5")
            print(f"      Risk: {alt['risk_level']}")
    else:
        print(f"Error: {response.text}")
    return success


# ========== Step 11: Test Non-Existing Decision ==========
def test_nonexisting_decision():
    step("Testing non-existing decision (404)")
    response = requests.post(
        f"{BASE_URL}/decisions/99999/alternatives",
        headers=get_headers(),
        json={
            "name": "Test",
            "description": "Test",
            "pros": "Test",
            "cons": "Test",
            "estimated_cost": 1000,
            "feasibility_score": 3,
            "risk_level": "Low",
        },
    )
    success = response.status_code == 404
    print_result("/decisions/99999/alternatives", "POST", response.status_code, success)
    if success:
        print("✓ Correctly returned 404 for non-existing decision")
    else:
        print(f"Error: Expected 404, got {response.status_code}")
    return success


# ========== Step 12: Test Non-Existing Alternative ==========
def test_nonexisting_alternative():
    step("Testing non-existing alternative (404)")
    response = requests.get(
        f"{BASE_URL}/alternatives/99999",
        headers=get_headers(),
    )
    success = response.status_code == 404
    print_result("/alternatives/99999", "GET", response.status_code, success)
    if success:
        print("✓ Correctly returned 404 for non-existing alternative")
    else:
        print(f"Error: Expected 404, got {response.status_code}")
    return success


# ========== Step 13: Test No JWT Token ==========
def test_no_jwt_token():
    step("Testing request without JWT token")
    response = requests.get(
        f"{BASE_URL}/decisions/{DECISION_ID}/alternatives",
    )
    success = response.status_code == 403
    print_result("/decisions/{decision_id}/alternatives (No JWT)", "GET", response.status_code, success)
    if success:
        print("✓ Correctly returned 403 for missing JWT")
    else:
        print(f"Error: Expected 403, got {response.status_code}")
    return success


# ========== Run All Tests ==========
def main():
    print_section("SPRINT 6 - ALTERNATIVE ANALYSIS MODULE - COMPREHENSIVE TEST")
    
    results = []
    
    # User creation and authentication
    print_section("Phase 1: Authentication Setup")
    results.append(("Create User", test_create_user()))
    results.append(("Login", test_login()))
    
    # Decision and alternatives creation
    print_section("Phase 2: Data Creation")
    results.append(("Create Decision", test_create_decision()))
    results.append(("Create Alternatives", test_create_alternatives()))
    
    # Read operations
    print_section("Phase 3: Read Operations")
    results.append(("Get Alternatives List", test_get_alternatives()))
    results.append(("Get Single Alternative", test_get_single_alternative()))
    
    # Update operations
    print_section("Phase 4: Update Operations")
    results.append(("Update Alternative", test_update_alternative()))
    
    # Validation tests
    print_section("Phase 5: Validation Tests")
    results.append(("Invalid Risk Level", test_invalid_risk_level()))
    results.append(("Invalid Feasibility Score", test_invalid_feasibility_score()))
    
    # Comparison
    print_section("Phase 6: Comparison")
    results.append(("Compare Alternatives", test_compare_alternatives()))
    
    # Error handling
    print_section("Phase 7: Error Handling")
    results.append(("Non-existing Decision", test_nonexisting_decision()))
    results.append(("Non-existing Alternative", test_nonexisting_alternative()))
    results.append(("No JWT Token", test_no_jwt_token()))
    
    # Summary
    print_section("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed / total * 100):.1f}%")
    
    print("\nDetailed Results:")
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! 🎉")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")


if __name__ == "__main__":
    main()
