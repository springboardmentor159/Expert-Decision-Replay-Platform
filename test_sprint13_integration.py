import uuid

import requests

BASE_URL = "http://127.0.0.1:8001"


def request(method, path, token=None, expected=None, **kwargs):
    headers = kwargs.pop("headers", {})
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = requests.request(method, BASE_URL + path, headers=headers, timeout=10, **kwargs)
    if expected is not None and response.status_code != expected:
        raise AssertionError(f"{method} {path}: expected {expected}, got {response.status_code}: {response.text}")
    return response


def register(payload, token=None):
    return request("POST", "/users", token=token, json=payload)


def login(email, password):
    response = request("POST", "/auth/login", json={"email": email, "password": password}, expected=200)
    return response.json()["access_token"]


suffix = uuid.uuid4().hex[:8]
admin_email = "testadmin@example.com"
admin_token = login(admin_email, "testpassword123")

employee = {
    "full_name": "Sprint 13 Employee",
    "email": f"employee-{suffix}@example.com",
    "role": "Employee",
    "password": "EmployeePass123!",
    "employee_id": f"EMP-{suffix}",
    "department": "Engineering",
    "designation": "Engineer",
    "phone_number": "5550000001",
}
reviewer = {**employee, "full_name": "Sprint 13 Reviewer", "email": f"reviewer-{suffix}@example.com", "role": "Reviewer", "employee_id": f"REV-{suffix}"}
manager = {**employee, "full_name": "Sprint 13 Manager", "email": f"manager-{suffix}@example.com", "role": "Manager", "employee_id": f"MGR-{suffix}"}

employee_id = register(employee).json()["id"]
reviewer_id = register(reviewer, admin_token).json()["id"]
manager_id = register(manager, admin_token).json()["id"]
employee_token = login(employee["email"], employee["password"])
reviewer_token = login(reviewer["email"], reviewer["password"])
manager_token = login(manager["email"], manager["password"])

request("POST", "/users", json={**employee, "email": f"duplicate-{suffix}@example.com", "employee_id": employee["employee_id"]}, expected=409)
request("GET", "/decisions", expected=401)

created = request("POST", "/decisions", token=employee_token, json={
    "title": f"Sprint 13 Decision {suffix}",
    "problem_statement": "Validate the complete decision lifecycle.",
    "category": "Technology",
    "rationale": "Integration test rationale",
}, expected=201).json()
decision_id = created["id"]

for name in ("PostgreSQL", "MySQL", "MongoDB"):
    request("POST", f"/decisions/{decision_id}/alternatives", token=employee_token, json={
        "name": name,
        "description": f"{name} option",
        "pros": "Reliable",
        "cons": "Migration effort",
        "estimated_cost": 1000,
        "feasibility_score": 4,
        "risk_level": "Medium",
    }, expected=201)
request("GET", f"/decisions/{decision_id}/alternatives/compare", token=employee_token, expected=200)
request("POST", f"/decisions/{decision_id}/comments", token=employee_token, json={"content": "Lifecycle comment"}, expected=201)
request("POST", f"/decisions/{decision_id}/threads", token=employee_token, json={"title": "Lifecycle thread", "description": "Discussion"}, expected=201)
request("PUT", f"/decisions/{decision_id}", token=employee_token, json={
    "title": f"Sprint 13 Decision {suffix} v2",
    "problem_statement": "Validate the complete decision lifecycle after update one.",
    "category": "Technology",
    "rationale": "First decision update",
}, expected=200)
request("PUT", f"/decisions/{decision_id}", token=employee_token, json={
    "title": f"Sprint 13 Decision {suffix} v3",
    "problem_statement": "Validate the complete decision lifecycle after update two.",
    "category": "Technology",
    "rationale": "Second decision update",
}, expected=200)
request("PUT", f"/decisions/{decision_id}/rationale", token=employee_token, json={"rationale": "Updated rationale"}, expected=200)
request("POST", f"/decisions/{decision_id}/meeting-notes", token=employee_token, json={"title": "Review", "content": "Meeting", "meeting_date": "2026-09-04T10:00:00"}, expected=201)
document = request(
    "POST",
    f"/decisions/{decision_id}/documents",
    token=employee_token,
    files={"file": ("integration.txt", b"Sprint 13 document", "text/plain")},
    expected=201,
).json()
request("GET", f"/decisions/{decision_id}/documents", token=employee_token, expected=200)
download = request("GET", f"/documents/{document['id']}/download", token=employee_token, expected=200)
assert download.content == b"Sprint 13 document"

request("PATCH", f"/decisions/{decision_id}/status", token=employee_token, json={"status": "Under Review"}, expected=200)
request("PATCH", f"/decisions/{decision_id}/status", token=employee_token, json={"status": "Archived"}, expected=409)
approval_id = request("POST", "/approvals", token=manager_token, json={"decision_id": decision_id, "reviewer_id": reviewer_id, "approval_level": 1}, expected=201).json()["id"]
request("PATCH", f"/approvals/{approval_id}", token=reviewer_token, json={"decision": "Approved"}, expected=200)
final_decision = request("GET", f"/decisions/{decision_id}", token=employee_token, expected=200).json()
assert final_decision["status"] == "Approved", final_decision

versions = request("GET", f"/decisions/{decision_id}/versions", token=employee_token, expected=200).json()
assert len(versions) >= 3
assert [item["version_number"] for item in versions] == sorted(item["version_number"] for item in versions)
request("GET", f"/decisions/{decision_id}/versions/1", token=employee_token, expected=200)
request("GET", "/dashboard/employee", token=employee_token, expected=200)
request("GET", "/dashboard/manager", token=manager_token, expected=200)
request("GET", "/dashboard/admin", token=admin_token, expected=200)
request("GET", "/reports/decisions", token=employee_token, expected=200)
request("GET", "/reports/decisions/export/pdf", token=employee_token, expected=200)
request("GET", "/reports/decisions/export/excel", token=employee_token, expected=200)
request("GET", "/audit-logs", token=admin_token, expected=200)

print("SPRINT 13 INTEGRATION: PASS")
print(f"decision_id={decision_id} employee_id={employee_id} reviewer_id={reviewer_id} manager_id={manager_id}")
