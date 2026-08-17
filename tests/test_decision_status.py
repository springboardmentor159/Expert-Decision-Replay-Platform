import time

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.decision import Decision
from app.models.user import User
from app.models.enums import UserRole
from app.core.security import hash_password


def _create_user(db_session, email="decision_user@example.com", employee_id="EMP_DECISION"):
    user = User(
        full_name="Decision User",
        email=email,
        role=UserRole.EMPLOYEE,
        password=hash_password("password123"),
        employee_id=employee_id,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _create_decision(db_session, user, status="Draft"):
    decision = Decision(
        title="Test Decision",
        problem_statement="Problem statement",
        category="General",
        status=status,
        created_by=user.id,
    )
    db_session.add(decision)
    db_session.commit()
    db_session.refresh(decision)
    return decision


def test_create_decision_defaults_to_draft(client, db_session, make_token):
    user = _create_user(db_session)
    token = make_token(str(user.id))
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/decisions", json={
        "title": "New Decision",
        "problem_statement": "Problem",
        "category": "General",
    }, headers=headers)

    assert response.status_code == 201
    assert response.json()["status"] == "Draft"


def test_patch_status_valid(client, db_session, make_token):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    token = make_token(str(user.id))
    headers = {"Authorization": f"Bearer {token}"}

    response = client.patch(f"/decisions/{decision.id}/status", json={
        "status": "Under Review"
    }, headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "Under Review"
    assert body["title"] == "Test Decision"


def test_patch_status_updates_updated_at(client, db_session, make_token):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    token = make_token(str(user.id))
    headers = {"Authorization": f"Bearer {token}"}

    first = client.patch(f"/decisions/{decision.id}/status", json={
        "status": "Under Review"
    }, headers=headers).json()["updated_at"]

    time.sleep(1.1)

    second = client.patch(f"/decisions/{decision.id}/status", json={
        "status": "Approved"
    }, headers=headers).json()["updated_at"]

    assert second > first


def test_patch_status_invalid_value(client, db_session, make_token):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    token = make_token(str(user.id))
    headers = {"Authorization": f"Bearer {token}"}

    response = client.patch(f"/decisions/{decision.id}/status", json={
        "status": "Completed"
    }, headers=headers)

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "status"]


def test_patch_status_decision_not_found(client, db_session, make_token):
    user = _create_user(db_session)
    token = make_token(str(user.id))
    headers = {"Authorization": f"Bearer {token}"}

    response = client.patch("/decisions/99999999/status", json={
        "status": "Under Review"
    }, headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Decision not found"


def test_patch_status_without_token(client, db_session):
    response = client.patch("/decisions/1/status", json={
        "status": "Under Review"
    })

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_patch_status_updates_in_db(client, db_session, make_token):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user, status="Approved")
    token = make_token(str(user.id))
    headers = {"Authorization": f"Bearer {token}"}

    client.patch(f"/decisions/{decision.id}/status", json={
        "status": "Archived"
    }, headers=headers)

    db_session.refresh(decision)
    assert decision.status == "Archived"


def test_database_check_constraint_rejects_invalid_status(db_session):
    user = _create_user(db_session)
    decision = Decision(
        title="Bad Status Decision",
        problem_statement="Problem",
        category="General",
        status="Completed",
        created_by=user.id,
    )
    db_session.add(decision)

    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()