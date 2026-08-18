import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.security import create_access_token

client = TestClient(app)


def get_authenticated_headers():
    user_data = {
        "full_name": "Alternative Tester",
        "email": "alt_tester@example.com",
        "role": "Employee",
        "password": "Password123!",
        "employee_id": "EMP-ALT-001",
        "department": "Architecture",
        "designation": "Staff Architect",
        "phone_number": "+1234567890"
    }
    client.post("/users", json=user_data)
    login_resp = client.post("/auth/login", json={"email": user_data["email"], "password": user_data["password"]})
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_sample_decision(headers):
    payload = {
        "title": "Select Database Platform",
        "problem_statement": "Need a scalable database for analytics and transactions",
        "category": "Architecture"
    }
    res = client.post("/decisions", json=payload, headers=headers)
    assert res.status_code == 201
    return res.json()


def test_unauthenticated_requests():
    headers = get_authenticated_headers()
    decision = create_sample_decision(headers)
    decision_id = decision["id"]

    alt_payload = {
        "name": "PostgreSQL",
        "description": "Primary relational DB",
        "pros": "Reliable",
        "cons": "Schema migrations",
        "estimated_cost": 5000,
        "feasibility_score": 5,
        "risk_level": "Low"
    }
    # POST without auth -> 401
    res = client.post(f"/decisions/{decision_id}/alternatives", json=alt_payload)
    assert res.status_code == 401

    # GET all without auth -> 401
    res = client.get(f"/decisions/{decision_id}/alternatives")
    assert res.status_code == 401

    # GET compare without auth -> 401
    res = client.get(f"/decisions/{decision_id}/alternatives/compare")
    assert res.status_code == 401

    # GET one without auth -> 401
    res = client.get("/alternatives/1")
    assert res.status_code == 401

    # PUT without auth -> 401
    res = client.put("/alternatives/1", json={"name": "New Name"})
    assert res.status_code == 401


def test_create_alternative_non_existing_decision():
    headers = get_authenticated_headers()
    alt_payload = {
        "name": "PostgreSQL",
        "description": "Primary relational DB",
        "pros": "Reliable",
        "cons": "Schema migrations",
        "estimated_cost": 5000,
        "feasibility_score": 5,
        "risk_level": "Low"
    }
    res = client.post("/decisions/99999/alternatives", json=alt_payload, headers=headers)
    assert res.status_code == 404
    assert res.json()["detail"] == "Decision not found"


def test_feasibility_score_validation():
    headers = get_authenticated_headers()
    decision = create_sample_decision(headers)
    decision_id = decision["id"]

    # Score too high (> 5)
    bad_payload_high = {
        "name": "PostgreSQL",
        "description": "Relational DB",
        "pros": "Reliable",
        "cons": "None",
        "estimated_cost": 5000,
        "feasibility_score": 10,
        "risk_level": "Low"
    }
    res = client.post(f"/decisions/{decision_id}/alternatives", json=bad_payload_high, headers=headers)
    assert res.status_code == 422

    # Score too low (< 1)
    bad_payload_low = {
        "name": "PostgreSQL",
        "description": "Relational DB",
        "pros": "Reliable",
        "cons": "None",
        "estimated_cost": 5000,
        "feasibility_score": 0,
        "risk_level": "Low"
    }
    res = client.post(f"/decisions/{decision_id}/alternatives", json=bad_payload_low, headers=headers)
    assert res.status_code == 422


def test_risk_level_validation():
    headers = get_authenticated_headers()
    decision = create_sample_decision(headers)
    decision_id = decision["id"]

    bad_risk_payload = {
        "name": "PostgreSQL",
        "description": "Relational DB",
        "pros": "Reliable",
        "cons": "None",
        "estimated_cost": 5000,
        "feasibility_score": 4,
        "risk_level": "Very Dangerous"
    }
    res = client.post(f"/decisions/{decision_id}/alternatives", json=bad_risk_payload, headers=headers)
    assert res.status_code == 422


def test_create_and_get_alternatives_workflow():
    headers = get_authenticated_headers()
    decision = create_sample_decision(headers)
    decision_id = decision["id"]

    # 1. Create PostgreSQL
    pg_payload = {
        "name": "PostgreSQL",
        "description": "Use PostgreSQL as the primary relational database.",
        "pros": "Reliable, mature ecosystem",
        "cons": "Requires relational schema design",
        "estimated_cost": 5000,
        "feasibility_score": 5,
        "risk_level": "Low"
    }
    res_pg = client.post(f"/decisions/{decision_id}/alternatives", json=pg_payload, headers=headers)
    assert res_pg.status_code == 201
    alt_pg = res_pg.json()
    assert alt_pg["name"] == "PostgreSQL"
    assert alt_pg["decision_id"] == decision_id
    assert alt_pg["feasibility_score"] == 5
    assert alt_pg["risk_level"] == "Low"
    assert "created_at" in alt_pg
    assert "updated_at" in alt_pg
    pg_id = alt_pg["id"]

    # 2. Create MySQL
    mysql_payload = {
        "name": "MySQL",
        "description": "Use MySQL community edition.",
        "pros": "Ubiquitous, easy to host",
        "cons": "Fewer advanced data types",
        "estimated_cost": 4500,
        "feasibility_score": 4,
        "risk_level": "Low"
    }
    res_mysql = client.post(f"/decisions/{decision_id}/alternatives", json=mysql_payload, headers=headers)
    assert res_mysql.status_code == 201
    alt_mysql = res_mysql.json()
    assert alt_mysql["name"] == "MySQL"

    # 3. Create MongoDB
    mongo_payload = {
        "name": "MongoDB",
        "description": "Document store for dynamic schemas.",
        "pros": "Flexible schema, easy horizontal scaling",
        "cons": "Eventual consistency trade-offs",
        "estimated_cost": 7000,
        "feasibility_score": 4,
        "risk_level": "Medium"
    }
    res_mongo = client.post(f"/decisions/{decision_id}/alternatives", json=mongo_payload, headers=headers)
    assert res_mongo.status_code == 201
    alt_mongo = res_mongo.json()
    assert alt_mongo["name"] == "MongoDB"

    # 4. Get all alternatives for decision
    res_all = client.get(f"/decisions/{decision_id}/alternatives", headers=headers)
    assert res_all.status_code == 200
    all_alts = res_all.json()
    assert len(all_alts) == 3
    names = [a["name"] for a in all_alts]
    assert "PostgreSQL" in names
    assert "MySQL" in names
    assert "MongoDB" in names

    # 5. Get single alternative by ID
    res_single = client.get(f"/alternatives/{pg_id}", headers=headers)
    assert res_single.status_code == 200
    single_data = res_single.json()
    assert single_data["id"] == pg_id
    assert single_data["name"] == "PostgreSQL"
    assert single_data["estimated_cost"] == 5000

    # 6. Update alternative
    update_payload = {
        "name": "PostgreSQL Enterprise",
        "description": "Updated database evaluation",
        "pros": "Reliable, scalable, mature ecosystem",
        "cons": "Requires relational schema design",
        "estimated_cost": 5500,
        "feasibility_score": 5,
        "risk_level": "Low"
    }
    res_update = client.put(f"/alternatives/{pg_id}", json=update_payload, headers=headers)
    assert res_update.status_code == 200
    updated_data = res_update.json()
    assert updated_data["name"] == "PostgreSQL Enterprise"
    assert updated_data["estimated_cost"] == 5500
    assert updated_data["id"] == pg_id
    assert updated_data["decision_id"] == decision_id

    # 7. Compare alternatives
    res_compare = client.get(f"/decisions/{decision_id}/alternatives/compare", headers=headers)
    assert res_compare.status_code == 200
    compare_data = res_compare.json()
    assert compare_data["decision_id"] == decision_id
    assert len(compare_data["alternatives"]) == 3
    comp_names = [a["name"] for a in compare_data["alternatives"]]
    assert "PostgreSQL Enterprise" in comp_names
    assert "MySQL" in comp_names
    assert "MongoDB" in comp_names


def test_not_found_handlers():
    headers = get_authenticated_headers()

    # Get alternatives for non-existent decision
    res = client.get("/decisions/99999/alternatives", headers=headers)
    assert res.status_code == 404
    assert res.json()["detail"] == "Decision not found"

    # Compare alternatives for non-existent decision
    res = client.get("/decisions/99999/alternatives/compare", headers=headers)
    assert res.status_code == 404
    assert res.json()["detail"] == "Decision not found"

    # Get non-existent alternative
    res = client.get("/alternatives/99999", headers=headers)
    assert res.status_code == 404
    assert res.json()["detail"] == "Alternative not found"

    # Update non-existent alternative
    res = client.put("/alternatives/99999", json={"name": "Ghost"}, headers=headers)
    assert res.status_code == 404
    assert res.json()["detail"] == "Alternative not found"
