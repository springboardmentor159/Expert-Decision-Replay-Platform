import time
import pytest

from app.models.comment import Comment
from app.models.decision import Decision
from app.models.enums import UserRole
from app.models.user import User
from app.core.security import hash_password


def _create_user(db_session, email="comm_user@example.com", employee_id="EMP_COMM", role=UserRole.EMPLOYEE):
    user = User(
        full_name="Comment Test User",
        email=email,
        role=role,
        password=hash_password("password123"),
        employee_id=employee_id,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _create_decision(db_session, user):
    decision = Decision(
        title="Comment Test Decision",
        problem_statement="Test statement",
        category="Engineering",
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


def test_create_comment(client, db_session, make_token):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    headers = _auth_headers(user, make_token)

    response = client.post(f"/decisions/{decision.id}/comments",
                           json={"content": "This is a great idea."},
                           headers=headers)

    assert response.status_code == 201
    body = response.json()
    assert body["decision_id"] == decision.id
    assert body["user_id"] == user.id
    assert body["content"] == "This is a great idea."
    assert body["id"] is not None
    assert "created_at" in body
    assert "updated_at" in body


def test_create_comment_decision_not_found(client, db_session, make_token):
    user = _create_user(db_session)
    headers = _auth_headers(user, make_token)

    response = client.post("/decisions/99999999/comments",
                           json={"content": "Orphan comment"},
                           headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Decision not found"


def test_create_comment_ignores_body_injections(client, db_session, make_token):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    headers = _auth_headers(user, make_token)

    response = client.post(f"/decisions/{decision.id}/comments",
                           json={
                               "content": "Clean content",
                               "id": 999,
                               "user_id": 1234,
                               "decision_id": 5678,
                               "created_at": "2020-01-01T00:00:00"
                           },
                           headers=headers)

    assert response.status_code == 201
    body = response.json()
    assert body["decision_id"] == decision.id
    assert body["user_id"] == user.id
    assert body["id"] != 999


def test_get_comments_by_decision(client, db_session, make_token):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    headers = _auth_headers(user, make_token)

    for i in range(3):
        client.post(f"/decisions/{decision.id}/comments",
                    json={"content": f"Comment {i+1}"},
                    headers=headers)

    response = client.get(f"/decisions/{decision.id}/comments", headers=headers)

    assert response.status_code == 200
    comments = response.json()
    assert len(comments) == 3
    assert [c["content"] for c in comments] == ["Comment 1", "Comment 2", "Comment 3"]
    assert all(c["decision_id"] == decision.id for c in comments)


def test_get_comments_by_decision_not_found(client, db_session, make_token):
    user = _create_user(db_session)
    headers = _auth_headers(user, make_token)

    response = client.get("/decisions/99999999/comments", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Decision not found"


def test_get_comment_by_id(client, db_session, make_token):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    headers = _auth_headers(user, make_token)

    created = client.post(f"/decisions/{decision.id}/comments",
                          json={"content": "Single comment"},
                          headers=headers).json()

    response = client.get(f"/comments/{created['id']}", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created["id"]
    assert body["content"] == "Single comment"
    assert body["user_id"] == user.id


def test_get_comment_not_found(client, db_session, make_token):
    user = _create_user(db_session)
    headers = _auth_headers(user, make_token)

    response = client.get("/comments/99999999", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Comment not found"


def test_update_comment_as_owner(client, db_session, make_token):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    headers = _auth_headers(user, make_token)

    created = client.post(f"/decisions/{decision.id}/comments",
                          json={"content": "Original comment"},
                          headers=headers).json()

    time.sleep(1.1)

    response = client.put(f"/comments/{created['id']}",
                          json={"content": "Updated comment"},
                          headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["content"] == "Updated comment"
    assert body["id"] == created["id"]
    assert body["decision_id"] == decision.id
    assert body["user_id"] == user.id
    assert body["created_at"] == created["created_at"]
    assert body["updated_at"] > created["updated_at"]


def test_update_comment_as_admin(client, db_session, make_token):
    author = _create_user(db_session, email="author@example.com", employee_id="EMP_AUTH")
    admin = _create_user(db_session, email="admin@example.com", employee_id="EMP_ADM", role=UserRole.ADMINISTRATOR)
    decision = _create_decision(db_session, author)
    author_headers = _auth_headers(author, make_token)
    admin_headers = _auth_headers(admin, make_token)

    created = client.post(f"/decisions/{decision.id}/comments",
                          json={"content": "Author's content"},
                          headers=author_headers).json()

    response = client.put(f"/comments/{created['id']}",
                          json={"content": "Moderated by Admin"},
                          headers=admin_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["content"] == "Moderated by Admin"
    assert body["user_id"] == author.id  # Original author preserved


def test_update_comment_as_other_user_forbidden(client, db_session, make_token):
    user_a = _create_user(db_session, email="user_a@example.com", employee_id="EMP_A")
    user_b = _create_user(db_session, email="user_b@example.com", employee_id="EMP_B", role=UserRole.EMPLOYEE)
    decision = _create_decision(db_session, user_a)
    headers_a = _auth_headers(user_a, make_token)
    headers_b = _auth_headers(user_b, make_token)

    created = client.post(f"/decisions/{decision.id}/comments",
                          json={"content": "User A comment"},
                          headers=headers_a).json()

    response = client.put(f"/comments/{created['id']}",
                          json={"content": "Hacked by User B"},
                          headers=headers_b)

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to modify this comment"


def test_update_comment_not_found(client, db_session, make_token):
    user = _create_user(db_session)
    headers = _auth_headers(user, make_token)

    response = client.put("/comments/99999999", json={"content": "X"}, headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Comment not found"


def test_delete_comment_as_owner(client, db_session, make_token):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    headers = _auth_headers(user, make_token)

    created = client.post(f"/decisions/{decision.id}/comments",
                          json={"content": "To be deleted"},
                          headers=headers).json()

    response = client.delete(f"/comments/{created['id']}", headers=headers)

    assert response.status_code == 200
    assert response.json()["message"] == "Comment deleted successfully"

    # Confirm it is gone
    get_res = client.get(f"/comments/{created['id']}", headers=headers)
    assert get_res.status_code == 404


def test_delete_comment_as_admin(client, db_session, make_token):
    author = _create_user(db_session, email="author_del@example.com", employee_id="EMP_AUTHDEL")
    admin = _create_user(db_session, email="admin_del@example.com", employee_id="EMP_ADMDEL", role=UserRole.ADMINISTRATOR)
    decision = _create_decision(db_session, author)
    author_headers = _auth_headers(author, make_token)
    admin_headers = _auth_headers(admin, make_token)

    created = client.post(f"/decisions/{decision.id}/comments",
                          json={"content": "Author text"},
                          headers=author_headers).json()

    response = client.delete(f"/comments/{created['id']}", headers=admin_headers)

    assert response.status_code == 200
    assert response.json()["message"] == "Comment deleted successfully"


def test_delete_comment_as_other_user_forbidden(client, db_session, make_token):
    user_a = _create_user(db_session, email="user_adel@example.com", employee_id="EMP_ADEL")
    user_b = _create_user(db_session, email="user_bdel@example.com", employee_id="EMP_BDEL", role=UserRole.EMPLOYEE)
    decision = _create_decision(db_session, user_a)
    headers_a = _auth_headers(user_a, make_token)
    headers_b = _auth_headers(user_b, make_token)

    created = client.post(f"/decisions/{decision.id}/comments",
                          json={"content": "User A text"},
                          headers=headers_a).json()

    response = client.delete(f"/comments/{created['id']}", headers=headers_b)

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to delete this comment"


def test_delete_comment_not_found(client, db_session, make_token):
    user = _create_user(db_session)
    headers = _auth_headers(user, make_token)

    response = client.delete("/comments/99999999", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Comment not found"


def test_all_five_comment_endpoints_without_token(client, db_session):
    endpoints = [
        ("post", "/decisions/1/comments", {"json": {"content": "text"}}),
        ("get", "/decisions/1/comments", {}),
        ("get", "/comments/1", {}),
        ("put", "/comments/1", {"json": {"content": "updated"}}),
        ("delete", "/comments/1", {}),
    ]

    for method, url, kwargs in endpoints:
        response = getattr(client, method)(url, **kwargs)
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"
