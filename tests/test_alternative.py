import time

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.alternative import Alternative
from app.models.decision import Decision
from app.models.enums import UserRole
from app.models.user import User
from app.core.security import hash_password


def _create_user(db_session, email="alt_user@example.com", employee_id="EMP_ALT"):
    user = User(
        full_name="Alt User",
        email=email,
        role=UserRole.EMPLOYEE,
        password=hash_password("password123"),
        employee_id=employee_id,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _create_decision(db_session, user):
    decision = Decision(
        title="Select Database",
        problem_statement="Pick a database",
        category="Technology",
        status="Draft",
        created_by=user.id,
    )
    db_session.add(decision)
    db_session.commit()
    db_session.refresh(decision)
    return decision


def _auth_headers(user, make_token):
    token = make_token(str(user.id))
    return {"Authorization": f"Bearer {token}"}


ALT_BODY = {
    "name": "PostgreSQL",
    "description": "Open source relational DB",
    "pros": "ACID, mature",
    "cons": "Scaling",
    "estimated_cost": 5000,
    "feasibility_score": 4,
    "risk_level": "Low",
}


def test_create_alternative(client, db_session, make_token):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    headers = _auth_headers(user, make_token)

    response = client.post(f"/decisions/{decision.id}/alternatives", json=ALT_BODY, headers=headers)

    assert response.status_code == 201
    body = response.json()
    assert body["decision_id"] == decision.id
    assert body["name"] == "PostgreSQL"
    assert body["estimated_cost"] == 5000
    assert body["feasibility_score"] == 4
    assert body["risk_level"] == "Low"
    assert body["id"] is not None


def test_create_alternative_decision_not_found(client, db_session, make_token):
    user = _create_user(db_session)
    headers = _auth_headers(user, make_token)

    response = client.post("/decisions/99999999/alternatives", json=ALT_BODY, headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Decision not found"


def test_create_alternative_ignores_decision_id_in_body(client, db_session, make_token):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    headers = _auth_headers(user, make_token)

    response = client.post(f"/decisions/{decision.id}/alternatives",
                           json={**ALT_BODY, "decision_id": 1, "id": 123, "created_at": "2020-01-01T00:00:00"},
                           headers=headers)

    assert response.status_code == 201
    body = response.json()
    assert body["decision_id"] == decision.id
    assert body["id"] != 123


def test_get_alternatives_by_decision(client, db_session, make_token):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    headers = _auth_headers(user, make_token)

    for name in ["PostgreSQL", "MySQL", "MongoDB"]:
        client.post(f"/decisions/{decision.id}/alternatives",
                    json={**ALT_BODY, "name": name}, headers=headers)

    response = client.get(f"/decisions/{decision.id}/alternatives", headers=headers)

    assert response.status_code == 200
    names = [alt["name"] for alt in response.json()]
    assert set(names) == {"PostgreSQL", "MySQL", "MongoDB"}
    assert all(alt["decision_id"] == decision.id for alt in response.json())


def test_get_alternatives_by_decision_not_found(client, db_session, make_token):
    user = _create_user(db_session)
    headers = _auth_headers(user, make_token)

    response = client.get("/decisions/99999999/alternatives", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Decision not found"


def test_get_alternative(client, db_session, make_token):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    headers = _auth_headers(user, make_token)

    created = client.post(f"/decisions/{decision.id}/alternatives", json=ALT_BODY, headers=headers).json()

    response = client.get(f"/alternatives/{created['id']}", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created["id"]
    assert body["decision_id"] == decision.id
    assert body["name"] == "PostgreSQL"


def test_get_alternative_not_found(client, db_session, make_token):
    user = _create_user(db_session)
    headers = _auth_headers(user, make_token)

    response = client.get("/alternatives/99999999", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Alternative not found"


def test_alternatives_without_token(client, db_session):
    for url, method in [("/decisions/1/alternatives", "post"),
                        ("/decisions/1/alternatives", "get"),
                        ("/alternatives/1", "get")]:
        kwargs = {"json": ALT_BODY} if method == "post" else {}
        response = getattr(client, method)(url, **kwargs)
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"


def test_multiple_alternatives_reference_same_decision_in_db(client, db_session, make_token):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    headers = _auth_headers(user, make_token)

    for name in ["PostgreSQL", "MySQL", "MongoDB"]:
        client.post(f"/decisions/{decision.id}/alternatives",
                    json={**ALT_BODY, "name": name}, headers=headers)

    assert len(decision.alternatives) == 3
    assert all(alt.decision_id == decision.id for alt in decision.alternatives)


def test_create_feasibility_score_out_of_range(client, db_session, make_token):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    headers = _auth_headers(user, make_token)

    response = client.post(f"/decisions/{decision.id}/alternatives",
                           json={**ALT_BODY, "feasibility_score": 10}, headers=headers)

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "feasibility_score"]


def test_create_risk_level_invalid(client, db_session, make_token):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    headers = _auth_headers(user, make_token)

    response = client.post(f"/decisions/{decision.id}/alternatives",
                           json={**ALT_BODY, "risk_level": "Very Dangerous"}, headers=headers)

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "risk_level"]


def test_valid_score_and_risk_values_accepted(client, db_session, make_token):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    headers = _auth_headers(user, make_token)

    response = client.post(f"/decisions/{decision.id}/alternatives",
                           json={**ALT_BODY, "feasibility_score": 5, "risk_level": "Medium"},
                           headers=headers)

    assert response.status_code == 201
    assert response.json()["feasibility_score"] == 5
    assert response.json()["risk_level"] == "Medium"


def test_update_alternative(client, db_session, make_token):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    headers = _auth_headers(user, make_token)

    created = client.post(f"/decisions/{decision.id}/alternatives", json=ALT_BODY, headers=headers).json()

    time.sleep(1.1)

    response = client.put(f"/alternatives/{created['id']}", json={
        "name": "PostgreSQL 16",
        "description": "Updated desc",
        "pros": "ACID",
        "cons": "Ops",
        "estimated_cost": 6000,
        "feasibility_score": 5,
        "risk_level": "Medium",
    }, headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "PostgreSQL 16"
    assert body["description"] == "Updated desc"
    assert body["estimated_cost"] == 6000
    assert body["feasibility_score"] == 5
    assert body["risk_level"] == "Medium"
    assert body["id"] == created["id"]
    assert body["decision_id"] == decision.id
    assert body["created_at"] == created["created_at"]
    assert body["updated_at"] > created["updated_at"]


def test_update_alternative_ignores_backend_controlled_fields(client, db_session, make_token):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    headers = _auth_headers(user, make_token)

    created = client.post(f"/decisions/{decision.id}/alternatives", json=ALT_BODY, headers=headers).json()

    response = client.put(f"/alternatives/{created['id']}", json={
        "name": "Ignored Injection",
        "id": 999,
        "decision_id": 1,
        "created_at": "2020-01-01T00:00:00",
        "updated_at": "2020-01-01T00:00:00",
    }, headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Ignored Injection"
    assert body["id"] == created["id"]
    assert body["decision_id"] == decision.id
    assert body["created_at"] == created["created_at"]


def test_update_alternative_not_found(client, db_session, make_token):
    user = _create_user(db_session)
    headers = _auth_headers(user, make_token)

    response = client.put("/alternatives/99999999", json={"name": "X"}, headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Alternative not found"


def test_update_alternative_feasibility_score_out_of_range(client, db_session, make_token):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    headers = _auth_headers(user, make_token)

    created = client.post(f"/decisions/{decision.id}/alternatives", json=ALT_BODY, headers=headers).json()

    response = client.put(f"/alternatives/{created['id']}", json={"feasibility_score": 0}, headers=headers)

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "feasibility_score"]


def test_update_alternative_risk_level_invalid(client, db_session, make_token):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    headers = _auth_headers(user, make_token)

    created = client.post(f"/decisions/{decision.id}/alternatives", json=ALT_BODY, headers=headers).json()

    response = client.put(f"/alternatives/{created['id']}", json={"risk_level": "Very Dangerous"}, headers=headers)

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "risk_level"]


def test_update_alternative_without_token(client, db_session):
    response = client.put("/alternatives/1", json={"name": "X"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_db_constraint_rejects_invalid_feasibility_score(db_session):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    alt = Alternative(
        decision_id=decision.id,
        name="Bad Score",
        feasibility_score=10,
    )
    db_session.add(alt)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_db_constraint_rejects_invalid_risk_level(db_session):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    alt = Alternative(
        decision_id=decision.id,
        name="Bad Risk",
        risk_level="Very Dangerous",
    )
    db_session.add(alt)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_compare_alternatives(client, db_session, make_token):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    headers = _auth_headers(user, make_token)

    alts_data = [
        {"name": "PostgreSQL", "estimated_cost": 5000, "feasibility_score": 5, "risk_level": "Low"},
        {"name": "MySQL", "estimated_cost": 3000, "feasibility_score": 4, "risk_level": "Medium"},
        {"name": "MongoDB", "estimated_cost": 4000, "feasibility_score": 3, "risk_level": "High"},
    ]

    for alt in alts_data:
        res = client.post(f"/decisions/{decision.id}/alternatives", json=alt, headers=headers)
        assert res.status_code == 201

    response = client.get(f"/decisions/{decision.id}/alternatives/compare", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["decision_id"] == decision.id
    assert len(body["alternatives"]) == 3
    assert body["alternatives"] == [
        {"name": "PostgreSQL", "estimated_cost": 5000, "feasibility_score": 5, "risk_level": "Low"},
        {"name": "MySQL", "estimated_cost": 3000, "feasibility_score": 4, "risk_level": "Medium"},
        {"name": "MongoDB", "estimated_cost": 4000, "feasibility_score": 3, "risk_level": "High"},
    ]


def test_compare_alternatives_empty_list(client, db_session, make_token):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    headers = _auth_headers(user, make_token)

    response = client.get(f"/decisions/{decision.id}/alternatives/compare", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["decision_id"] == decision.id
    assert body["alternatives"] == []


def test_compare_alternatives_decision_not_found(client, db_session, make_token):
    user = _create_user(db_session)
    headers = _auth_headers(user, make_token)

    response = client.get("/decisions/99999999/alternatives/compare", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Decision not found"


def test_create_alternative_missing_required_field(client, db_session, make_token):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    headers = _auth_headers(user, make_token)

    response = client.post(f"/decisions/{decision.id}/alternatives", json={"description": "no name"}, headers=headers)

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "name"]


def test_all_five_alternative_endpoints_without_token(client, db_session):
    endpoints = [
        ("post", "/decisions/1/alternatives", {"json": ALT_BODY}),
        ("get", "/decisions/1/alternatives", {}),
        ("get", "/alternatives/1", {}),
        ("put", "/alternatives/1", {"json": {"name": "Updated"}}),
        ("get", "/decisions/1/alternatives/compare", {}),
    ]

    for method, url, kwargs in endpoints:
        response = getattr(client, method)(url, **kwargs)
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"