#!/usr/bin/env python
"""
Complete Examples for Testing Decision Management API
Copy and run these examples to verify the implementation works correctly
"""

import json
import requests
from typing import Dict

# ============================================================================
# Configuration
# ============================================================================
BASE_URL = "http://localhost:8000"

# Test user credentials
TEST_USER = {
    "email": "testuser@example.com",
    "password": "TestPassword123"
}

# ============================================================================
# Example 1: Authentication Flow
# ============================================================================
def example_1_login():
    """Example 1: Get JWT Token"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Login and Get JWT Token")
    print("="*70)
    
    url = f"{BASE_URL}/token"
    data = {
        "username": TEST_USER["email"],
        "password": TEST_USER["password"]
    }
    
    print(f"\n🔵 REQUEST:")
    print(f"  Method: POST")
    print(f"  URL: {url}")
    print(f"  Username: {TEST_USER['email']}")
    
    response = requests.post(url, data=data)
    
    print(f"\n🟢 RESPONSE:")
    print(f"  Status Code: {response.status_code}")
    print(f"  Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"\n✅ SUCCESS: Token received (first 50 chars): {token[:50]}...")
        return token
    else:
        print(f"\n❌ FAILED")
        return None


# ============================================================================
# Example 2: Create a Decision
# ============================================================================
def example_2_create_decision(token: str):
    """Example 2: Create a new decision"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Create a New Decision")
    print("="*70)
    
    url = f"{BASE_URL}/decisions"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "title": "Migrate Database to PostgreSQL",
        "problem_statement": "Our current SQLite database has scalability limitations for high-traffic scenarios",
        "category": "Technology"
    }
    
    print(f"\n🔵 REQUEST:")
    print(f"  Method: POST")
    print(f"  URL: {url}")
    print(f"  Headers: Authorization: Bearer {token[:30]}...")
    print(f"  Body: {json.dumps(data, indent=2)}")
    
    response = requests.post(url, json=data, headers=headers)
    
    print(f"\n🟢 RESPONSE:")
    print(f"  Status Code: {response.status_code}")
    print(f"  Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        decision = response.json()
        print(f"\n✅ SUCCESS: Decision created with ID {decision['id']}")
        print(f"   Status: {decision['status']} (default for new decisions)")
        return decision["id"]
    else:
        print(f"\n❌ FAILED")
        return None


# ============================================================================
# Example 3: Get All Decisions
# ============================================================================
def example_3_get_all_decisions(token: str):
    """Example 3: Retrieve all decisions"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Get All Decisions")
    print("="*70)
    
    url = f"{BASE_URL}/decisions"
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n🔵 REQUEST:")
    print(f"  Method: GET")
    print(f"  URL: {url}")
    print(f"  Headers: Authorization: Bearer {token[:30]}...")
    
    response = requests.get(url, headers=headers)
    
    print(f"\n🟢 RESPONSE:")
    print(f"  Status Code: {response.status_code}")
    decisions = response.json()
    print(f"  Total Decisions: {len(decisions)}")
    print(f"  Response: {json.dumps(decisions[:1], indent=2)}  [showing first decision only]")
    
    if response.status_code == 200:
        print(f"\n✅ SUCCESS: Retrieved {len(decisions)} decision(s)")
        return decisions
    else:
        print(f"\n❌ FAILED")
        return []


# ============================================================================
# Example 4: Get Specific Decision
# ============================================================================
def example_4_get_decision_by_id(token: str, decision_id: int):
    """Example 4: Get a specific decision by ID"""
    print("\n" + "="*70)
    print(f"EXAMPLE 4: Get Specific Decision (ID: {decision_id})")
    print("="*70)
    
    url = f"{BASE_URL}/decisions/{decision_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n🔵 REQUEST:")
    print(f"  Method: GET")
    print(f"  URL: {url}")
    print(f"  Headers: Authorization: Bearer {token[:30]}...")
    
    response = requests.get(url, headers=headers)
    
    print(f"\n🟢 RESPONSE:")
    print(f"  Status Code: {response.status_code}")
    print(f"  Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        decision = response.json()
        print(f"\n✅ SUCCESS: Retrieved decision '{decision['title']}'")
        print(f"   Created by: User ID {decision['created_by']}")
        print(f"   Status: {decision['status']}")
        return decision
    else:
        print(f"\n❌ FAILED")
        return None


# ============================================================================
# Example 5: Update a Decision
# ============================================================================
def example_5_update_decision(token: str, decision_id: int):
    """Example 5: Update decision details"""
    print("\n" + "="*70)
    print(f"EXAMPLE 5: Update Decision (ID: {decision_id})")
    print("="*70)
    
    url = f"{BASE_URL}/decisions/{decision_id}"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "title": "Migrate Database to PostgreSQL - Phase 1",
        "problem_statement": "Our current SQLite database has critical scalability limitations",
        "category": "Infrastructure"
    }
    
    print(f"\n🔵 REQUEST:")
    print(f"  Method: PUT")
    print(f"  URL: {url}")
    print(f"  Headers: Authorization: Bearer {token[:30]}...")
    print(f"  Body: {json.dumps(data, indent=2)}")
    
    response = requests.put(url, json=data, headers=headers)
    
    print(f"\n🟢 RESPONSE:")
    print(f"  Status Code: {response.status_code}")
    print(f"  Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        decision = response.json()
        print(f"\n✅ SUCCESS: Decision updated")
        print(f"   Title changed to: {decision['title']}")
        print(f"   Category changed to: {decision['category']}")
        print(f"   created_by (should not change): {decision['created_by']}")
        print(f"   created_at (should not change): {decision['created_at']}")
        print(f"   updated_at (should be newer): {decision['updated_at']}")
        return decision
    else:
        print(f"\n❌ FAILED")
        return None


# ============================================================================
# Example 6: Update Decision Status
# ============================================================================
def example_6_update_status(token: str, decision_id: int, new_status: str):
    """Example 6: Update decision status"""
    print("\n" + "="*70)
    print(f"EXAMPLE 6: Update Decision Status (ID: {decision_id})")
    print("="*70)
    
    url = f"{BASE_URL}/decisions/{decision_id}/status"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"status": new_status}
    
    print(f"\n🔵 REQUEST:")
    print(f"  Method: PATCH")
    print(f"  URL: {url}")
    print(f"  Headers: Authorization: Bearer {token[:30]}...")
    print(f"  Body: {json.dumps(data, indent=2)}")
    
    response = requests.patch(url, json=data, headers=headers)
    
    print(f"\n🟢 RESPONSE:")
    print(f"  Status Code: {response.status_code}")
    print(f"  Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        decision = response.json()
        print(f"\n✅ SUCCESS: Status updated to '{decision['status']}'")
        return decision
    else:
        print(f"\n❌ FAILED")
        return None


# ============================================================================
# Example 7: Invalid Status (Should Fail)
# ============================================================================
def example_7_invalid_status(token: str, decision_id: int):
    """Example 7: Try invalid status (should get error)"""
    print("\n" + "="*70)
    print(f"EXAMPLE 7: Attempt Invalid Status (Should Fail) (ID: {decision_id})")
    print("="*70)
    
    url = f"{BASE_URL}/decisions/{decision_id}/status"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"status": "Completed"}  # Invalid status!
    
    print(f"\n🔵 REQUEST:")
    print(f"  Method: PATCH")
    print(f"  URL: {url}")
    print(f"  Headers: Authorization: Bearer {token[:30]}...")
    print(f"  Body: {json.dumps(data, indent=2)}")
    print(f"  ⚠️  Note: 'Completed' is NOT a valid status!")
    
    response = requests.patch(url, json=data, headers=headers)
    
    print(f"\n🟢 RESPONSE:")
    print(f"  Status Code: {response.status_code}")
    print(f"  Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 422:
        error = response.json()
        print(f"\n✅ SUCCESS: Invalid status correctly rejected!")
        print(f"   Valid statuses are: Draft, Under Review, Approved, Rejected, Archived")
        return True
    else:
        print(f"\n❌ FAILED: Should have rejected invalid status")
        return False


# ============================================================================
# Example 8: Filter by Status
# ============================================================================
def example_8_filter_by_status(token: str):
    """Example 8: Filter decisions by status"""
    print("\n" + "="*70)
    print("EXAMPLE 8: Filter Decisions by Status")
    print("="*70)
    
    url = f"{BASE_URL}/decisions?status=Draft"
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n🔵 REQUEST:")
    print(f"  Method: GET")
    print(f"  URL: {url}")
    print(f"  Headers: Authorization: Bearer {token[:30]}...")
    
    response = requests.get(url, headers=headers)
    
    print(f"\n🟢 RESPONSE:")
    print(f"  Status Code: {response.status_code}")
    decisions = response.json()
    print(f"  Total Results: {len(decisions)}")
    if decisions:
        print(f"  Response (first result): {json.dumps(decisions[0], indent=2)}")
    
    if response.status_code == 200:
        print(f"\n✅ SUCCESS: Found {len(decisions)} decision(s) with status='Draft'")
        # Verify all results are Draft
        all_draft = all(d['status'] == 'Draft' for d in decisions)
        if all_draft:
            print(f"   ✅ All results are Draft (filter working correctly)")
        else:
            print(f"   ❌ Some results are not Draft (filter issue)")
        return decisions
    else:
        print(f"\n❌ FAILED")
        return []


# ============================================================================
# Example 9: Filter by Category
# ============================================================================
def example_9_filter_by_category(token: str):
    """Example 9: Filter decisions by category"""
    print("\n" + "="*70)
    print("EXAMPLE 9: Filter Decisions by Category")
    print("="*70)
    
    url = f"{BASE_URL}/decisions?category=Technology"
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n🔵 REQUEST:")
    print(f"  Method: GET")
    print(f"  URL: {url}")
    print(f"  Headers: Authorization: Bearer {token[:30]}...")
    
    response = requests.get(url, headers=headers)
    
    print(f"\n🟢 RESPONSE:")
    print(f"  Status Code: {response.status_code}")
    decisions = response.json()
    print(f"  Total Results: {len(decisions)}")
    if decisions:
        print(f"  Response (first result): {json.dumps(decisions[0], indent=2)}")
    
    if response.status_code == 200:
        print(f"\n✅ SUCCESS: Found {len(decisions)} decision(s) with category='Technology'")
        # Verify all results are Technology
        all_tech = all(d['category'] == 'Technology' for d in decisions)
        if all_tech:
            print(f"   ✅ All results are Technology (filter working correctly)")
        else:
            print(f"   ❌ Some results are not Technology (filter issue)")
        return decisions
    else:
        print(f"\n❌ FAILED")
        return []


# ============================================================================
# Example 10: Combined Filter
# ============================================================================
def example_10_combined_filter(token: str):
    """Example 10: Filter by both status AND category"""
    print("\n" + "="*70)
    print("EXAMPLE 10: Combined Filter (Status AND Category)")
    print("="*70)
    
    url = f"{BASE_URL}/decisions?status=Approved&category=Technology"
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n🔵 REQUEST:")
    print(f"  Method: GET")
    print(f"  URL: {url}")
    print(f"  Headers: Authorization: Bearer {token[:30]}...")
    print(f"  Filters: status=Approved AND category=Technology")
    
    response = requests.get(url, headers=headers)
    
    print(f"\n🟢 RESPONSE:")
    print(f"  Status Code: {response.status_code}")
    decisions = response.json()
    print(f"  Total Results: {len(decisions)}")
    if decisions:
        print(f"  Response (first result): {json.dumps(decisions[0], indent=2)}")
    
    if response.status_code == 200:
        print(f"\n✅ SUCCESS: Found {len(decisions)} decision(s) matching both filters")
        print(f"   Filters Applied: status=Approved AND category=Technology")
        return decisions
    else:
        print(f"\n❌ FAILED")
        return []


# ============================================================================
# Example 11: Without JWT Token (Should Fail)
# ============================================================================
def example_11_without_jwt():
    """Example 11: Try accessing API without JWT (should get 401)"""
    print("\n" + "="*70)
    print("EXAMPLE 11: Access Without JWT Token (Should Fail)")
    print("="*70)
    
    url = f"{BASE_URL}/decisions"
    # NO Authorization header!
    
    print(f"\n🔵 REQUEST:")
    print(f"  Method: GET")
    print(f"  URL: {url}")
    print(f"  Headers: (NO Authorization header)")
    
    response = requests.get(url)
    
    print(f"\n🟢 RESPONSE:")
    print(f"  Status Code: {response.status_code}")
    print(f"  Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 401:
        print(f"\n✅ SUCCESS: API correctly rejected request without JWT (401 Unauthorized)")
        return True
    else:
        print(f"\n❌ FAILED: Should return 401 Unauthorized")
        return False


# ============================================================================
# Example 12: Non-existent Decision (Should Return 404)
# ============================================================================
def example_12_not_found(token: str):
    """Example 12: Try to get non-existent decision"""
    print("\n" + "="*70)
    print("EXAMPLE 12: Get Non-existent Decision (Should Return 404)")
    print("="*70)
    
    url = f"{BASE_URL}/decisions/99999"
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n🔵 REQUEST:")
    print(f"  Method: GET")
    print(f"  URL: {url}")
    print(f"  Headers: Authorization: Bearer {token[:30]}...")
    print(f"  Note: Decision ID 99999 probably doesn't exist")
    
    response = requests.get(url, headers=headers)
    
    print(f"\n🟢 RESPONSE:")
    print(f"  Status Code: {response.status_code}")
    print(f"  Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 404:
        print(f"\n✅ SUCCESS: API correctly returned 404 for non-existent decision")
        return True
    else:
        print(f"\n❌ FAILED: Should return 404 Not Found")
        return False


# ============================================================================
# Main: Run All Examples
# ============================================================================
def main():
    """Run all examples"""
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  DECISION MANAGEMENT API - COMPLETE TESTING EXAMPLES  ".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    
    print("\n⚠️  Make sure the server is running on http://localhost:8000")
    print("   Start server with: python main.py")
    
    # Example 1: Login
    token = example_1_login()
    if not token:
        print("\n❌ Could not get token. Make sure server is running.")
        return
    
    # Example 2: Create decision
    decision_id = example_2_create_decision(token)
    if not decision_id:
        print("\n❌ Could not create decision. Stopping examples.")
        return
    
    # Example 3: Get all decisions
    example_3_get_all_decisions(token)
    
    # Example 4: Get specific decision
    example_4_get_decision_by_id(token, decision_id)
    
    # Example 5: Update decision
    example_5_update_decision(token, decision_id)
    
    # Example 6: Update status to Under Review
    example_6_update_status(token, decision_id, "Under Review")
    
    # Example 7: Try invalid status
    example_7_invalid_status(token, decision_id)
    
    # Example 8: Filter by status
    example_8_filter_by_status(token)
    
    # Example 9: Filter by category
    example_9_filter_by_category(token)
    
    # Example 10: Combined filter
    example_10_combined_filter(token)
    
    # Example 11: Without JWT
    example_11_without_jwt()
    
    # Example 12: Non-existent decision
    example_12_not_found(token)
    
    # Summary
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  ALL EXAMPLES COMPLETED  ".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    print("\n✅ Check the outputs above to verify each endpoint works correctly!")
    print("\nKey things to verify:")
    print("  ✓ Example 2: New decision should have status='Draft'")
    print("  ✓ Example 5: created_at and created_by should NOT change")
    print("  ✓ Example 5: updated_at should change (be newer)")
    print("  ✓ Example 7: Invalid status should return error")
    print("  ✓ Example 11: Request without JWT should return 401")
    print("  ✓ Example 12: Non-existent ID should return 404")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to http://localhost:8000")
        print("   Make sure the server is running!")
        print("   Run: python main.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
