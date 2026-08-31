from app.models.activity_log import ActivityLog
from app.models.decision import Decision
from app.models.enums import UserRole
from app.models.user import User
from app.core.security import hash_password


def _create_user(db_session, email="log_user@example.com", employee_id="EMP_LOG", role=UserRole.EMPLOYEE):
    user = User(
        full_name="Activity Log Test User",
        email=email,
        role=role,
        password=hash_password("password123"),
        employee_id=employee_id,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _auth_headers(user, make_token):
    token = make_token(str(user.id))
    return {"Authorization": f"Bearer {token}"}


def _last_logs(db_session, user_id):
    return (
        db_session.query(ActivityLog)
        .filter(ActivityLog.user_id == user_id)
        .order_by(ActivityLog.id.desc())
        .all()
    )


def test_log_on_decision_create(client, db_session, make_token):
    user = _create_user(db_session)
    headers = _auth_headers(user, make_token)

    response = client.post(
        "/decisions",
        json={"title": "Log Decision", "problem_statement": "PS", "category": "Engineering"},
        headers=headers,
    )
    assert response.status_code == 201
    decision_id = response.json()["id"]

    logs = _last_logs(db_session, user.id)
    assert any(
        l.action == "create" and l.entity_type == "decision" and l.entity_id == decision_id
        for l in logs
    )


def test_log_on_decision_update(client, db_session, make_token):
    user = _create_user(db_session)
    headers = _auth_headers(user, make_token)
    decision_id = client.post(
        "/decisions",
        json={"title": "Before Update", "problem_statement": "PS", "category": "Engineering"},
        headers=headers,
    ).json()["id"]

    response = client.put(
        f"/decisions/{decision_id}",
        json={"title": "After Update"},
        headers=headers,
    )
    assert response.status_code == 200

    logs = _last_logs(db_session, user.id)
    assert any(
        l.action == "update" and l.entity_type == "decision" and l.entity_id == decision_id
        for l in logs
    )


def test_log_on_decision_status_change(client, db_session, make_token):
    user = _create_user(db_session)
    headers = _auth_headers(user, make_token)
    decision_id = client.post(
        "/decisions",
        json={"title": "Status Decision", "problem_statement": "PS", "category": "Engineering"},
        headers=headers,
    ).json()["id"]

    response = client.patch(
        f"/decisions/{decision_id}/status",
        json={"status": "Under Review"},
        headers=headers,
    )
    assert response.status_code == 200

    logs = _last_logs(db_session, user.id)
    assert any(
        l.action == "status_change" and l.entity_type == "decision" and l.entity_id == decision_id
        for l in logs
    )


def test_log_on_alternative_create(client, db_session, make_token):
    user = _create_user(db_session)
    headers = _auth_headers(user, make_token)
    decision_id = client.post(
        "/decisions",
        json={"title": "Alt Decision", "problem_statement": "PS", "category": "Engineering"},
        headers=headers,
    ).json()["id"]

    response = client.post(
        f"/decisions/{decision_id}/alternatives",
        json={"name": "Option A", "description": "d", "pros": "p", "cons": "c"},
        headers=headers,
    )
    assert response.status_code == 201
    alternative_id = response.json()["id"]

    logs = _last_logs(db_session, user.id)
    assert any(
        l.action == "create" and l.entity_type == "alternative" and l.entity_id == alternative_id
        for l in logs
    )


def test_log_on_comment_create(client, db_session, make_token):
    user = _create_user(db_session)
    headers = _auth_headers(user, make_token)
    decision_id = client.post(
        "/decisions",
        json={"title": "Comment Decision", "problem_statement": "PS", "category": "Engineering"},
        headers=headers,
    ).json()["id"]

    response = client.post(
        f"/decisions/{decision_id}/comments",
        json={"content": "A comment"},
        headers=headers,
    )
    assert response.status_code == 201
    comment_id = response.json()["id"]

    logs = _last_logs(db_session, user.id)
    assert any(
        l.action == "create" and l.entity_type == "comment" and l.entity_id == comment_id
        for l in logs
    )


def test_log_on_thread_create(client, db_session, make_token):
    user = _create_user(db_session)
    headers = _auth_headers(user, make_token)
    decision_id = client.post(
        "/decisions",
        json={"title": "Thread Decision", "problem_statement": "PS", "category": "Engineering"},
        headers=headers,
    ).json()["id"]

    response = client.post(
        f"/decisions/{decision_id}/threads",
        json={"title": "Thread A", "description": "d"},
        headers=headers,
    )
    assert response.status_code == 201
    thread_id = response.json()["id"]

    logs = _last_logs(db_session, user.id)
    assert any(
        l.action == "create"
        and l.entity_type == "discussion_thread"
        and l.entity_id == thread_id
        for l in logs
    )
