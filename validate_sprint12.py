#!/usr/bin/env python
"""Validation test for Sprint 12 completion"""

import requests
import json

print("=" * 60)
print("SPRINT 12 - FINAL VALIDATION")
print("=" * 60)

# First create test user
print("\n1. Creating Test User...")
user_data = {
    "full_name": "Test Admin",
    "email": "validationadmin@example.com",
    "role": "Administrator",
    "password": "validationpass123",
    "employee_id": "EMP_VAL",
    "department": "IT",
    "designation": "Admin",
    "phone_number": "1234567890"
}
response = requests.post('http://localhost:8000/users', json=user_data)
print(f"   Status: {response.status_code}")

# Test login
print("\n2. Testing Login Endpoint...")
response = requests.post('http://localhost:8000/auth/login', json={'email': 'validationadmin@example.com', 'password': 'validationpass123'})
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    token = response.json().get('access_token')
    print(f"   ✓ Token obtained: {token[:30]}...")
else:
    print(f"   ✗ Error: {response.text}")
    exit(1)

# Test all 4 GET endpoints
headers = {'Authorization': f'Bearer {token}'}

print("\n3. Testing GET /reports/decisions...")
response = requests.get('http://localhost:8000/reports/decisions', headers=headers)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   ✓ Records: {data.get('total')}")
    print(f"   ✓ Summary: {data.get('summary')}")

print("\n4. Testing GET /reports/approvals...")
response = requests.get('http://localhost:8000/reports/approvals', headers=headers)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   ✓ Records: {data.get('total')}")

print("\n5. Testing GET /reports/teams...")
response = requests.get('http://localhost:8000/reports/teams', headers=headers)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   ✓ Teams: {len(data.get('data', []))}")

print("\n6. Testing GET /reports/audit (Admin only)...")
response = requests.get('http://localhost:8000/reports/audit', headers=headers)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   ✓ Records: {data.get('total')}")
    print(f"   ✓ Admin access granted")

# Test all 8 export endpoints
print("\n6. Testing PDF Exports...")
response = requests.get('http://localhost:8000/reports/decisions/export/pdf', headers=headers)
print(f"   Decisions PDF: Status {response.status_code}, Size: {len(response.content)} bytes")

response = requests.get('http://localhost:8000/reports/approvals/export/pdf', headers=headers)
print(f"   Approvals PDF: Status {response.status_code}, Size: {len(response.content)} bytes")

response = requests.get('http://localhost:8000/reports/teams/export/pdf', headers=headers)
print(f"   Teams PDF: Status {response.status_code}, Size: {len(response.content)} bytes")

response = requests.get('http://localhost:8000/reports/audit/export/pdf', headers=headers)
print(f"   Audit PDF: Status {response.status_code}, Size: {len(response.content)} bytes")

print("\n7. Testing Excel Exports...")
response = requests.get('http://localhost:8000/reports/decisions/export/excel', headers=headers)
print(f"   Decisions Excel: Status {response.status_code}, Size: {len(response.content)} bytes")

response = requests.get('http://localhost:8000/reports/approvals/export/excel', headers=headers)
print(f"   Approvals Excel: Status {response.status_code}, Size: {len(response.content)} bytes")

response = requests.get('http://localhost:8000/reports/teams/export/excel', headers=headers)
print(f"   Teams Excel: Status {response.status_code}, Size: {len(response.content)} bytes")

response = requests.get('http://localhost:8000/reports/audit/export/excel', headers=headers)
print(f"   Audit Excel: Status {response.status_code}, Size: {len(response.content)} bytes")

# Test authorization
print("\n8. Testing Authorization...")
response = requests.get('http://localhost:8000/reports/decisions')
print(f"   No JWT: Status {response.status_code} (expected 401)")

response = requests.get('http://localhost:8000/reports/audit', headers={'Authorization': 'Bearer invalid'})
print(f"   Invalid JWT: Status {response.status_code} (expected 401 or 403)")

print("\n" + "=" * 60)
print("✓ SPRINT 12 VALIDATION COMPLETE")
print("=" * 60)
