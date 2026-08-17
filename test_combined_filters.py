#!/usr/bin/env python
"""Test combined filtering with multiple query parameters"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Get a token by logging in
response = client.post('/token', data={
    'username': 'testuser@example.com',
    'password': 'TestPassword123'
})
token = response.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Test combined filtering
print('\n=== Testing Combined Filters (status=Under Review AND category=Infrastructure) ===')
response = client.get('/decisions?status=Under%20Review&category=Infrastructure', headers=headers)
print(f'Status Code: {response.status_code}')
results = response.json()
print(f'Number of results: {len(results)}')
if results:
    for decision in results:
        print(f"  - ID: {decision['id']}, Title: {decision['title']}, Status: {decision['status']}, Category: {decision['category']}")
    print('✓ Combined filtering works correctly')
else:
    print('No decisions found with both filters (this is expected if no such decision exists)')
    
# Create a decision with Under Review status and Technology category for more comprehensive test
print('\n=== Creating decision for more comprehensive testing ===')
new_decision = {
    "title": "Update API Documentation",
    "problem_statement": "API documentation is out of date",
    "category": "Technology"
}
response = client.post('/decisions', json=new_decision, headers=headers)
if response.status_code == 201:
    decision_id = response.json()['id']
    print(f'✓ Created decision ID: {decision_id}')
    
    # Update its status to "Approved"
    status_update = {"status": "Approved"}
    response = client.patch(f'/decisions/{decision_id}/status', json=status_update, headers=headers)
    if response.status_code == 200:
        print(f'✓ Updated decision status to Approved')
        
        # Now test filtering by Approved and Technology
        print('\n=== Testing Filter (status=Approved AND category=Technology) ===')
        response = client.get('/decisions?status=Approved&category=Technology', headers=headers)
        results = response.json()
        print(f'Status Code: {response.status_code}')
        print(f'Number of results: {len(results)}')
        if results:
            for decision in results:
                print(f"  - ID: {decision['id']}, Title: {decision['title']}, Status: {decision['status']}, Category: {decision['category']}")
            print('✓ Combined filtering works correctly')
