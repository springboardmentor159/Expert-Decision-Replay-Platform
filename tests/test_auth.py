from app.core.security import hash_password
from app.models.user import User


def _create_user(db_session, email="user@example.com", password="secret123", employee_id="EMP001"):
    user = User(
        full_name="Test User",
        email=email,
        role="Employee",
        password=hash_password(password),
        employee_id=employee_id,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_login_valid(client, db_session):
    _create_user(db_session)

    response = client.post("/login", json={
        "email": "user@example.com",
        "password": "secret123",
    })

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"
    assert body["user"]["email"] == "user@example.com"


def test_login_wrong_password(client, db_session):
    _create_user(db_session)

    response = client.post("/login", json={
        "email": "user@example.com",
        "password": "wrong-password",
    })

    assert response.status_code == 401


def test_login_unknown_user(client, db_session):
    _create_user(db_session)

    response = client.post("/login", json={
        "email": "nobody@example.com",
        "password": "secret123",
    })

    assert response.status_code == 401
