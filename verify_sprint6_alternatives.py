import sys
from fastapi.testclient import TestClient

from app.main import app
from app.db.database import SessionLocal
from app.models.user import User
from app.models.decision import Decision
from app.models.alternative import Alternative

client = TestClient(app)


def run_verification():
    print("=" * 70)
    print(" SPRINT 6: ALTERNATIVE ANALYSIS MODULE - VERIFICATION REPORT")
    print("=" * 70)

    passed_tests = 0
    total_tests = 0

    def assert_check(condition, title, details=""):
        nonlocal passed_tests, total_tests
        total_tests += 1
        if condition:
            passed_tests += 1
            print(f" [PASS] {title}")
        else:
            print(f" [FAIL] {title} -> {details}")

    # 1. Clean up & Register User for Testing
    print("\n--- 1. Authentication & JWT Setup ---")
    test_email = "sprint6_architect@example.com"
    test_password = "SecurePassword123!"

    db = SessionLocal()
    existing_user = db.query(User).filter(User.email == test_email).first()
    if existing_user:
        db.query(Decision).filter(Decision.created_by == existing_user.id).delete(synchronize_session=False)
        db.query(User).filter(User.id == existing_user.id).delete(synchronize_session=False)
        db.commit()
    db.close()

    reg_payload = {
        "full_name": "Sprint 6 Architect",
        "email": test_email,
        "role": "Employee",
        "password": test_password,
        "employee_id": "EMP_SPRINT6_01",
        "department": "Platform Architecture",
        "designation": "Lead Architect",
        "phone_number": "+1-555-0606"
    }
    res = client.post("/users", json=reg_payload)
    assert_check(res.status_code == 201, "Register test user (201 Created)")

    login_res = client.post("/auth/login", json={"email": test_email, "password": test_password})
    assert_check(login_res.status_code == 200 and "access_token" in login_res.json(), "Login and obtain JWT token (200 OK)")
    token = login_res.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Decision
    print("\n--- 2. Create Decision ---")
    decision_payload = {
        "title": "Select Primary Database Platform",
        "problem_statement": "Select high-performance database supporting relational integrity and scalable analytics",
        "category": "Data Engineering"
    }
    dec_res = client.post("/decisions", json=decision_payload, headers=headers)
    assert_check(dec_res.status_code == 201, "Create Decision via POST /decisions (201 Created)")
    decision_id = dec_res.json().get("id")

    # 3. Create Alternatives (PostgreSQL, MySQL, MongoDB)
    print("\n--- 3. Create Alternatives (POST /decisions/{decision_id}/alternatives) ---")
    
    # 3a. PostgreSQL
    pg_payload = {
        "name": "PostgreSQL",
        "description": "Use PostgreSQL as the primary relational database.",
        "pros": "Reliable, mature ecosystem, rich SQL support, extensions like pgvector",
        "cons": "Requires relational schema design and connection pooling",
        "estimated_cost": 5000.0,
        "feasibility_score": 5,
        "risk_level": "Low"
    }
    res_pg = client.post(f"/decisions/{decision_id}/alternatives", json=pg_payload, headers=headers)
    assert_check(
        res_pg.status_code == 201 and res_pg.json().get("name") == "PostgreSQL" and res_pg.json().get("decision_id") == decision_id,
        "Create Alternative: PostgreSQL (201 Created)"
    )
    pg_id = res_pg.json().get("id")

    # 3b. MySQL
    mysql_payload = {
        "name": "MySQL",
        "description": "Use MySQL 8.0 enterprise engine.",
        "pros": "Ubiquitous, widely understood, high read throughput",
        "cons": "Lacks some advanced analytics and complex JSON query capabilities",
        "estimated_cost": 4500.0,
        "feasibility_score": 4,
        "risk_level": "Low"
    }
    res_mysql = client.post(f"/decisions/{decision_id}/alternatives", json=mysql_payload, headers=headers)
    assert_check(
        res_mysql.status_code == 201 and res_mysql.json().get("name") == "MySQL",
        "Create Alternative: MySQL (201 Created)"
    )
    mysql_id = res_mysql.json().get("id")

    # 3c. MongoDB
    mongo_payload = {
        "name": "MongoDB",
        "description": "Document-oriented database for flexible document storage.",
        "pros": "Schema flexibility, native sharding, fast prototyping",
        "cons": "Complex multi-document transaction overhead",
        "estimated_cost": 7000.0,
        "feasibility_score": 4,
        "risk_level": "Medium"
    }
    res_mongo = client.post(f"/decisions/{decision_id}/alternatives", json=mongo_payload, headers=headers)
    assert_check(
        res_mongo.status_code == 201 and res_mongo.json().get("name") == "MongoDB",
        "Create Alternative: MongoDB (201 Created)"
    )
    mongo_id = res_mongo.json().get("id")

    # 4. Error Handling & Validation
    print("\n--- 4. Validation & Error Handling ---")

    # 4a. Feasibility score too high (> 5)
    bad_score_payload = {
        "name": "Invalid Score DB",
        "description": "Testing invalid feasibility score",
        "pros": "None",
        "cons": "None",
        "estimated_cost": 1000.0,
        "feasibility_score": 10,
        "risk_level": "Low"
    }
    res_bad_score = client.post(f"/decisions/{decision_id}/alternatives", json=bad_score_payload, headers=headers)
    assert_check(res_bad_score.status_code == 422, "Reject feasibility_score = 10 (422 Unprocessable Entity)")

    # 4b. Feasibility score too low (< 1)
    bad_score_payload_0 = {
        "name": "Invalid Score DB",
        "description": "Testing invalid feasibility score",
        "pros": "None",
        "cons": "None",
        "estimated_cost": 1000.0,
        "feasibility_score": 0,
        "risk_level": "Low"
    }
    res_bad_score_0 = client.post(f"/decisions/{decision_id}/alternatives", json=bad_score_payload_0, headers=headers)
    assert_check(res_bad_score_0.status_code == 422, "Reject feasibility_score = 0 (422 Unprocessable Entity)")

    # 4c. Invalid risk level
    bad_risk_payload = {
        "name": "Invalid Risk DB",
        "description": "Testing invalid risk level",
        "pros": "None",
        "cons": "None",
        "estimated_cost": 1000.0,
        "feasibility_score": 3,
        "risk_level": "Very Dangerous"
    }
    res_bad_risk = client.post(f"/decisions/{decision_id}/alternatives", json=bad_risk_payload, headers=headers)
    assert_check(res_bad_risk.status_code == 422, "Reject risk_level = 'Very Dangerous' (422 Unprocessable Entity)")

    # 4d. Non-existing decision
    res_bad_dec = client.post("/decisions/99999/alternatives", json=pg_payload, headers=headers)
    assert_check(
        res_bad_dec.status_code == 404 and res_bad_dec.json().get("detail") == "Decision not found",
        "Create alternative for non-existing decision 99999 -> (404 Decision not found)"
    )

    # 4e. Non-existing alternative (GET)
    res_bad_alt_get = client.get("/alternatives/99999", headers=headers)
    assert_check(
        res_bad_alt_get.status_code == 404 and res_bad_alt_get.json().get("detail") == "Alternative not found",
        "Get non-existing alternative 99999 -> (404 Alternative not found)"
    )

    # 4f. Non-existing alternative (PUT)
    res_bad_alt_put = client.put("/alternatives/99999", json={"name": "Ghost DB"}, headers=headers)
    assert_check(
        res_bad_alt_put.status_code == 404 and res_bad_alt_put.json().get("detail") == "Alternative not found",
        "Update non-existing alternative 99999 -> (404 Alternative not found)"
    )

    # 4g. Unauthenticated access without JWT
    res_unauth_post = client.post(f"/decisions/{decision_id}/alternatives", json=pg_payload)
    assert_check(res_unauth_post.status_code == 401, "Unauthorized POST without JWT (401 Unauthorized)")

    res_unauth_get = client.get(f"/decisions/{decision_id}/alternatives")
    assert_check(res_unauth_get.status_code == 401, "Unauthorized GET /alternatives without JWT (401 Unauthorized)")

    res_unauth_compare = client.get(f"/decisions/{decision_id}/alternatives/compare")
    assert_check(res_unauth_compare.status_code == 401, "Unauthorized GET /compare without JWT (401 Unauthorized)")

    # 5. Retrieve All Alternatives for Decision
    print("\n--- 5. Get All Alternatives for Decision (GET /decisions/{decision_id}/alternatives) ---")
    res_all = client.get(f"/decisions/{decision_id}/alternatives", headers=headers)
    assert_check(res_all.status_code == 200, "Get alternatives list (200 OK)")
    all_data = res_all.json()
    alt_names = [a.get("name") for a in all_data]
    assert_check(
        len(all_data) == 3 and "PostgreSQL" in alt_names and "MySQL" in alt_names and "MongoDB" in alt_names,
        f"Contains all 3 created alternatives: {alt_names}"
    )

    # 6. Retrieve Alternative by ID
    print("\n--- 6. Get Alternative by ID (GET /alternatives/{alternative_id}) ---")
    res_single = client.get(f"/alternatives/{pg_id}", headers=headers)
    assert_check(
        res_single.status_code == 200 and res_single.json().get("id") == pg_id and res_single.json().get("name") == "PostgreSQL",
        f"Get single alternative by ID {pg_id} (200 OK)"
    )

    # 7. Update Alternative
    print("\n--- 7. Update Alternative (PUT /alternatives/{alternative_id}) ---")
    update_payload = {
        "name": "PostgreSQL (Aurora / Cloud SQL)",
        "description": "Managed PostgreSQL with automated backups and read replicas",
        "pros": "High reliability, enterprise scaling, active community",
        "cons": "Requires relational schema migration discipline",
        "estimated_cost": 5500.0,
        "feasibility_score": 5,
        "risk_level": "Low"
    }
    res_put = client.put(f"/alternatives/{pg_id}", json=update_payload, headers=headers)
    assert_check(res_put.status_code == 200, "Update alternative via PUT /alternatives/{id} (200 OK)")
    put_data = res_put.json()
    assert_check(
        put_data.get("name") == "PostgreSQL (Aurora / Cloud SQL)" and put_data.get("estimated_cost") == 5500.0,
        "Verify updated name and estimated_cost in response"
    )

    # 8. Alternative Comparison API
    print("\n--- 8. Alternative Comparison API (GET /decisions/{decision_id}/alternatives/compare) ---")
    res_cmp = client.get(f"/decisions/{decision_id}/alternatives/compare", headers=headers)
    assert_check(res_cmp.status_code == 200, "Get alternative comparison (200 OK)")
    cmp_data = res_cmp.json()
    assert_check(
        cmp_data.get("decision_id") == decision_id and isinstance(cmp_data.get("alternatives"), list) and len(cmp_data.get("alternatives")) == 3,
        f"Comparison response contains decision_id {decision_id} and 3 comparison alternative items"
    )
    print("   Comparison Payload Structure:")
    for alt in cmp_data.get("alternatives"):
        print(f"     * {alt.get('name')}: Cost=${alt.get('estimated_cost')}, Feasibility={alt.get('feasibility_score')}/5, Risk={alt.get('risk_level')}")

    # 9. Direct PostgreSQL Database Verification
    print("\n--- 9. Direct PostgreSQL Database Verification ---")
    db = SessionLocal()
    try:
        # Check decision
        db_decision = db.query(Decision).filter(Decision.id == decision_id).first()
        assert_check(db_decision is not None, f"PostgreSQL: Decision row {decision_id} exists")

        # Check alternatives linked to decision via relationship
        db_alts = db.query(Alternative).filter(Alternative.decision_id == decision_id).all()
        assert_check(len(db_alts) == 3, f"PostgreSQL: Exactly 3 alternatives found for decision_id={decision_id}")

        # Check updated PostgreSQL alternative record
        db_pg = db.query(Alternative).filter(Alternative.id == pg_id).first()
        assert_check(
            db_pg is not None and db_pg.name == "PostgreSQL (Aurora / Cloud SQL)" and db_pg.estimated_cost == 5500.0 and db_pg.feasibility_score == 5 and db_pg.risk_level == "Low",
            f"PostgreSQL: Alternative {pg_id} stored with correct cost (5500.0), feasibility (5), risk ('Low')"
        )
        assert_check(db_pg.created_at is not None and db_pg.updated_at is not None, "PostgreSQL: Timestamps created_at and updated_at populated")
    finally:
        db.close()

    print("\n" + "=" * 70)
    print(f" SUMMARY: {passed_tests} / {total_tests} CHECKS PASSED")
    print("=" * 70)
    if passed_tests == total_tests:
        print(" ALL SPRINT 6 REQUIREMENTS FULLY VERIFIED AND WORKING!")
        return 0
    else:
        print(" SOME CHECKS FAILED.")
        return 1


if __name__ == "__main__":
    sys.exit(run_verification())
