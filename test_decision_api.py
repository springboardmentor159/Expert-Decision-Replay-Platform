#!/usr/bin/env python
"""
Test script for Decision Management API endpoints.
This script tests all the required endpoints without needing Swagger.
"""

import json
import sys
from datetime import timedelta

# Test locally without running a server
sys.path.insert(0, '/Users/Asus/Desktop/web/expert-decision-replay')

from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token
from app.core.config import settings

# Create test client
client = TestClient(app)

# Test data
test_user = {
    "full_name": "Test User",
    "email": "testuser@example.com",
    "role": "Employee",
    "employee_id": "EMP001",
    "department": "Technology",
    "designation": "Software Engineer",
    "phone_number": "1234567890",
    "password": "TestPassword123"
}

test_decision = {
    "title": "Migrate to PostgreSQL",
    "problem_statement": "Current system uses SQLite which has limitations",
    "category": "Technology"
}

updated_decision = {
    "title": "Migrate to PostgreSQL - Updated",
    "problem_statement": "Current system uses SQLite which has scalability limitations",
    "category": "Infrastructure"
}

test_status_update = {
    "status": "Under Review"
}


def test_health_check():
    """Test health check endpoint"""
    print("\n1. Testing Health Check...")
    response = client.get("/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200, "Health check failed"
    print("✓ Health check passed")


def test_create_user():
    """Test user creation"""
    print("\n2. Testing User Creation...")
    response = client.post("/users", json=test_user)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        print("✓ User created successfully")
        return response.json()
    elif response.status_code == 400 and "already registered" in response.json().get("detail", ""):
        print("✓ User already exists (this is OK for testing)")
        # Get the user by logging in
        return None
    else:
        print(f"✗ Failed to create user: {response.json()}")
        return None


def test_login():
    """Test user login"""
    print("\n3. Testing User Login...")
    response = client.post("/token", data={
        "username": test_user["email"],
        "password": test_user["password"]
    })
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"✓ Login successful, token: {token[:20]}...")
        return token
    else:
        print(f"✗ Login failed: {response.json()}")
        return None


def test_create_decision(token):
    """Test decision creation"""
    print("\n4. Testing Decision Creation...")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/decisions", json=test_decision, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        decision = response.json()
        print(f"✓ Decision created with ID: {decision['id']}")
        print(f"  Status: {decision['status']}")
        assert decision['status'] == 'Draft', "New decision should have Draft status"
        return decision
    else:
        print(f"✗ Failed to create decision: {response.json()}")
        return None


def test_get_decision(token, decision_id):
    """Test getting a specific decision"""
    print(f"\n5. Testing Get Decision (ID: {decision_id})...")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/decisions/{decision_id}", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✓ Decision retrieved successfully")
        return response.json()
    else:
        print(f"✗ Failed to get decision: {response.json()}")
        return None


def test_update_decision(token, decision_id):
    """Test updating a decision"""
    print(f"\n6. Testing Update Decision (ID: {decision_id})...")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.put(f"/decisions/{decision_id}", json=updated_decision, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        decision = response.json()
        print("✓ Decision updated successfully")
        assert decision['title'] == updated_decision['title'], "Title should be updated"
        assert decision['problem_statement'] == updated_decision['problem_statement'], "Problem statement should be updated"
        return decision
    else:
        print(f"✗ Failed to update decision: {response.json()}")
        return None


def test_update_decision_status(token, decision_id):
    """Test updating decision status"""
    print(f"\n7. Testing Update Decision Status (ID: {decision_id})...")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.patch(f"/decisions/{decision_id}/status", json=test_status_update, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        decision = response.json()
        print("✓ Decision status updated successfully")
        assert decision['status'] == test_status_update['status'], f"Status should be {test_status_update['status']}"
        return decision
    else:
        print(f"✗ Failed to update decision status: {response.json()}")
        return None


def test_invalid_status(token, decision_id):
    """Test invalid status value"""
    print(f"\n8. Testing Invalid Status Value...")
    headers = {"Authorization": f"Bearer {token}"}
    invalid_status = {"status": "Completed"}  # Invalid status
    response = client.patch(f"/decisions/{decision_id}/status", json=invalid_status, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code in [422, 400]:  # Validation error
        print("✓ Invalid status correctly rejected")
        return True
    else:
        print(f"✗ Invalid status should have been rejected")
        return False


def test_filter_by_status(token):
    """Test filtering decisions by status"""
    print(f"\n9. Testing Filter by Status...")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/decisions?status=Draft", headers=headers)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Number of Draft decisions: {len(data)}")
    
    if response.status_code == 200:
        # Verify all returned decisions have Draft status
        for decision in data:
            if decision['status'] != 'Draft':
                print(f"✗ Found non-Draft decision: {decision}")
                return False
        print("✓ Filter by status works correctly")
        return True
    else:
        print(f"✗ Failed to filter by status: {data}")
        return False


def test_filter_by_category(token):
    """Test filtering decisions by category"""
    print(f"\n10. Testing Filter by Category...")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/decisions?category=Infrastructure", headers=headers)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Number of Infrastructure decisions: {len(data)}")
    
    if response.status_code == 200:
        # Verify all returned decisions have Infrastructure category
        for decision in data:
            if decision['category'] != 'Infrastructure':
                print(f"✗ Found non-Infrastructure decision: {decision}")
                return False
        print("✓ Filter by category works correctly")
        return True
    else:
        print(f"✗ Failed to filter by category: {data}")
        return False


def test_without_auth(decision_id):
    """Test API without JWT token"""
    print(f"\n11. Testing API Without JWT Token...")
    response = client.get(f"/decisions/{decision_id}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 401:
        print("✓ API correctly rejects request without JWT")
        return True
    else:
        print(f"✗ API should reject request without JWT")
        return False


def test_not_found(token):
    """Test non-existent decision"""
    print(f"\n12. Testing 404 Not Found...")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/decisions/99999", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 404:
        print("✓ 404 error correctly returned for non-existent decision")
        return True
    else:
        print(f"✗ Should return 404 for non-existent decision")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Decision Management API - Comprehensive Test Suite")
    print("=" * 60)
    
    try:
        # Test health check
        test_health_check()
        
        # Create user (or get existing)
        test_create_user()
        
        # Login to get token
        token = test_login()
        if not token:
            print("\n✗ Failed to get authentication token. Stopping tests.")
            return False
        
        # Test decision operations
        decision = test_create_decision(token)
        if not decision:
            print("\n✗ Failed to create decision. Stopping tests.")
            return False
        
        decision_id = decision['id']
        
        # Test retrieve
        test_get_decision(token, decision_id)
        
        # Test update
        test_update_decision(token, decision_id)
        
        # Test status update
        test_update_decision_status(token, decision_id)
        
        # Test invalid status
        test_invalid_status(token, decision_id)
        
        # Test filtering
        test_filter_by_status(token)
        test_filter_by_category(token)
        
        # Test authentication
        test_without_auth(decision_id)
        
        # Test not found
        test_not_found(token)
        
        print("\n" + "=" * 60)
        print("✓ All tests completed!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n✗ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
