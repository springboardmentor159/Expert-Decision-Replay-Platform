from app.models.decision import Decision
from app.models.enums import UserRole
from app.models.user import User
from app.core.security import hash_password


def _create_user(db_session, email="filter_user@example.com", employee_id="EMP_FILTER"):
    user = User(
        full_name="Filter User",
        email=email,
        role=UserRole.EMPLOYEE,
        password=hash_password("password123"),
        employee_id=employee_id,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _create_decision(db_session, user, title, category, status):
    decision = Decision(
        title=title,
        problem_statement="Problem statement",
        category=category,
        status=status,
        created_by=user.id,
    )
    db_session.add(decision)
    db_session.commit()
    db_session.refresh(decision)
    return decision


def _seed(client, db_session, make_token):
    user = _create_user(db_session)
    token = make_token(str(user.id))
    headers = {"Authorization": f"Bearer {token}"}

    _create_decision(db_session, user, "Draft Tech", "Technology", "Draft")
    _create_decision(db_session, user, "Draft Finance", "Finance", "Draft")
    _create_decision(db_session, user, "Approved Tech", "Technology", "Approved")
    _create_decision(db_session, user, "Approved Finance", "Finance", "Approved")

    return user, headers


def test_get_decisions_no_filters_returns_all(client, db_session, make_token):
    _, headers = _seed(client, db_session, make_token)

    response = client.get("/decisions", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 4


def test_get_decisions_filter_by_status(client, db_session, make_token):
    _, headers = _seed(client, db_session, make_token)

    response = client.get("/decisions?status=Draft", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert all(decision["status"] == "Draft" for decision in body)


def test_get_decisions_filter_by_category(client, db_session, make_token):
    _, headers = _seed(client, db_session, make_token)

    response = client.get("/decisions?category=Technology", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert all(decision["category"] == "Technology" for decision in body)


def test_get_decisions_filter_by_status_and_category(client, db_session, make_token):
    _, headers = _seed(client, db_session, make_token)

    response = client.get("/decisions?status=Approved&category=Technology", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["title"] == "Approved Tech"
    assert body[0]["status"] == "Approved"
    assert body[0]["category"] == "Technology"


def test_get_decisions_filter_invalid_status(client, db_session, make_token):
    _, headers = _seed(client, db_session, make_token)

    response = client.get("/decisions?status=Completed", headers=headers)

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", "status"]


def test_get_decisions_filter_without_token(client, db_session):
    response = client.get("/decisions?status=Draft")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"