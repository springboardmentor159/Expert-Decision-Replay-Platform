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
    "feasibility_score": 8,
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
    assert body["feasibility_score"] == 8
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