import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8000"

def make_request(method, endpoint, data=None, token=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f"Bearer {token}"
    
    req_data = None
    if data:
        req_data = json.dumps(data).encode('utf-8')
    
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except:
            return e.code, e.read().decode()

def run_tests():
    print("--- Starting Server Tests ---")
    
    # 1. Login and obtain JWT
    print("\n1. Login and obtain JWT")
    login_data = {
        "email": "john.doe@example.com",
        "password": "secretpassword"
    }
    # Create test user just in case
    user_data = {
        "full_name": "John Doe",
        "email": "john.doe@example.com",
        "role": "Employee",
        "password": "secretpassword",
        "employee_id": "EMP001"
    }
    make_request("POST", "/users", data=user_data)
    
    status, response = make_request("POST", "/users/login", data=login_data)
    assert status == 200, f"Login failed: {response}"
    token = response["access_token"]
    print("Login successful, JWT obtained.")
    
    # 2. Try accessing API without authentication
    print("\n2. Try accessing without authentication")
    status, response = make_request("GET", "/decisions")
    assert status == 401, f"Expected 401, got {status}"
    print("Received 401 Unauthorized as expected.")
    
    # 3. Create a decision
    print("\n3. Create a decision")
    decision_data = {
        "title": "Move to PostgreSQL",
        "problem_statement": "Our current database does not support the required relational queries.",
        "category": "Technology"
    }
    status, response = make_request("POST", "/decisions", data=decision_data, token=token)
    assert status == 201, f"Failed to create decision: {response}"
    print(f"Decision created with ID {response['id']} and status {response['status']}.")
    decision_id = response["id"]
    
    # 4. Get all decisions
    print("\n4. Get all decisions")
    status, response = make_request("GET", "/decisions", token=token)
    assert status == 200, f"Failed to get decisions: {response}"
    print(f"Retrieved {len(response)} decisions.")
    
    # 5. Get decision by ID
    print("\n5. Get decision by ID")
    status, response = make_request("GET", f"/decisions/{decision_id}", token=token)
    assert status == 200, f"Failed to get decision by ID: {response}"
    print(f"Retrieved decision: {response['title']}")
    
    # 6. Request invalid decision ID
    print("\n6. Request invalid decision ID")
    status, response = make_request("GET", "/decisions/99999", token=token)
    assert status == 404, f"Expected 404, got {status}"
    print("Received 404 Not Found as expected.")
    
    print("\n--- All tests passed! ---")

if __name__ == "__main__":
    run_tests()
