import requests
import json
import time

# Base URL
BASE_URL = "http://localhost:8000"

print("=" * 60)
print("SPRINT 12 - REPORTS MODULE TESTING")
print("=" * 60)

# First, try to create a test user
print("\n1. Creating test user...")
user_data = {
    "full_name": "Test Admin",
    "email": "testadmin@example.com",
    "role": "Administrator",
    "password": "testpassword123",
    "employee_id": "EMP001",
    "department": "IT",
    "designation": "Admin",
    "phone_number": "1234567890"
}

response = requests.post(f"{BASE_URL}/users", json=user_data)
print(f"Status: {response.status_code}")
if response.status_code == 201:
    print("✓ User created successfully")
elif response.status_code == 422:
    print("⚠ User already exists (this is OK)")
elif response.status_code in [200, 400]:
    print(f"⚠ Response: {response.text[:100]}")
else:
    print(f"✗ Error: {response.text}")

# Now login with the test user
print("\n2. Testing Login...")
login_data = {
    "email": "testadmin@example.com",
    "password": "testpassword123"
}

print("=" * 60)
print("SPRINT 12 - REPORTS MODULE TESTING")
print("=" * 60)

print("\n1. Testing Login...")
response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    token = response.json()["access_token"]
    print(f"✓ Token obtained successfully")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test Decision Reports endpoint
    print("\n2. Testing GET /reports/decisions...")
    response = requests.get(f"{BASE_URL}/reports/decisions", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Total records: {data.get('total_records')}")
        print(f"  Summary Statistics:")
        summary = data.get('summary')
        print(f"    - Total Decisions: {summary.get('total_decisions')}")
        print(f"    - Draft: {summary.get('draft_decisions')}")
        print(f"    - Under Review: {summary.get('decisions_under_review')}")
        print(f"    - Approved: {summary.get('approved_decisions')}")
        print(f"    - Rejected: {summary.get('rejected_decisions')}")
        print(f"    - Archived: {summary.get('archived_decisions')}")
    else:
        print(f"✗ Error: {response.text}")
    
    # Test with filters
    print("\n3. Testing GET /reports/decisions with filters...")
    response = requests.get(f"{BASE_URL}/reports/decisions?status=Approved&page=1&page_size=10", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Filtered records: {data.get('total_records')}")
        print(f"  Page: {data.get('page')}, Page Size: {data.get('page_size')}")
    else:
        print(f"✗ Error: {response.text}")
    
    # Test Approval Reports endpoint
    print("\n4. Testing GET /reports/approvals...")
    response = requests.get(f"{BASE_URL}/reports/approvals", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Total records: {data.get('total_records')}")
        summary = data.get('summary')
        print(f"  Summary Statistics:")
        print(f"    - Total Approvals: {summary.get('total_approvals')}")
        print(f"    - Pending: {summary.get('pending_approvals')}")
        print(f"    - Approved: {summary.get('approved_approvals')}")
        print(f"    - Rejected: {summary.get('rejected_approvals')}")
        print(f"    - Avg Turnaround: {summary.get('average_approval_turnaround_time_hours'):.2f} hrs")
        print(f"    - Completion Rate: {summary.get('approval_completion_rate'):.2f}%")
    else:
        print(f"✗ Error: {response.text}")
    
    # Test Team Reports endpoint
    print("\n5. Testing GET /reports/teams...")
    response = requests.get(f"{BASE_URL}/reports/teams", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Total teams: {data.get('total_records')}")
        if data.get('data'):
            print(f"  First team: {data['data'][0].get('team_name')}")
            team = data['data'][0]
            print(f"    - Members: {team.get('number_of_members')}")
            print(f"    - Total Decisions: {team['decision_stats'].get('total_decisions')}")
    else:
        print(f"✗ Error: {response.text}")
    
    # Test Audit Reports endpoint (should fail for non-admin)
    print("\n6. Testing GET /reports/audit (auth check)...")
    response = requests.get(f"{BASE_URL}/reports/audit", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 403:
        print("✓ Correctly rejected non-admin access (403 Forbidden)")
    elif response.status_code == 200:
        print("⚠ Admin has access to audit reports")
        data = response.json()
        print(f"  Total records: {data.get('total_records')}")
    else:
        print(f"⚠ Unexpected status: {response.status_code}")
    
    # Test PDF export
    print("\n7. Testing GET /reports/decisions/export/pdf...")
    response = requests.get(f"{BASE_URL}/reports/decisions/export/pdf", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✓ PDF generated (size: {len(response.content)} bytes)")
    else:
        print(f"✗ Error: {response.text}")
    
    # Test Excel export
    print("\n8. Testing GET /reports/decisions/export/excel...")
    response = requests.get(f"{BASE_URL}/reports/decisions/export/excel", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✓ Excel generated (size: {len(response.content)} bytes)")
    else:
        print(f"✗ Error: {response.text}")
    
    # Test pagination
    print("\n9. Testing pagination...")
    response1 = requests.get(f"{BASE_URL}/reports/decisions?page=1&page_size=5", headers=headers)
    response2 = requests.get(f"{BASE_URL}/reports/decisions?page=2&page_size=5", headers=headers)
    print(f"Page 1 Status: {response1.status_code}")
    print(f"Page 2 Status: {response2.status_code}")
    if response1.status_code == 200 and response2.status_code == 200:
        print(f"✓ Pagination working")
        print(f"  Page 1 records: {len(response1.json().get('data', []))}")
        print(f"  Page 2 records: {len(response2.json().get('data', []))}")
    
    # Test without JWT
    print("\n10. Testing request without JWT (should return 401)...")
    response = requests.get(f"{BASE_URL}/reports/decisions")
    print(f"Status: {response.status_code}")
    if response.status_code == 403:
        print("✓ Correctly rejected request without JWT (403)")
    elif response.status_code == 401:
        print("✓ Correctly rejected request without JWT (401)")
    else:
        print(f"⚠ Unexpected status: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60)
    
else:
    print(f"✗ Login failed: {response.text}")
