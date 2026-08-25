import time
import pytest

from app.models.comment import Comment
from app.models.decision import Decision
from app.models.discussion_thread import DiscussionThread
from app.models.enums import UserRole
from app.models.user import User
from app.core.security import hash_password


def _create_user(db_session, email="thread_user@example.com", employee_id="EMP_THREAD", role=UserRole.EMPLOYEE):
    user = User(
        full_name="Thread Test User",
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
        title="Thread Test Decision",
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


def test_create_thread(client, db_session, make_token):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    headers = _auth_headers(user, make_token)

    response = client.post(f"/decisions/{decision.id}/threads",
                          json={"title": "Discussion Topic", "description": "Let's discuss this."},
                          headers=headers)

    assert response.status_code == 201
    body = response.json()
    assert body["decision_id"] == decision.id
    assert body["created_by"] == user.id
    assert body["title"] == "Discussion Topic"
    assert body["description"] == "Let's discuss this."
    assert body["status"] == "Open"
    assert body["id"] is not None
    assert "created_at" in body
    assert "updated_at" in body


def test_create_thread_decision_not_found(client, db_session, make_token):
    user = _create_user(db_session)
    headers = _auth_headers(user, make_token)

    response = client.post("/decisions/99999999/threads",
                           json={"title": "Orphan thread"},
                           headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Decision not found"


def test_create_thread_ignores_body_injections(client, db_session, make_token):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    headers = _auth_headers(user, make_token)

    response = client.post(f"/decisions/{decision.id}/threads",
                          json={
                              "title": "Clean title",
                              "description": "Clean desc",
                              "id": 999,
                              "decision_id": 5678,
                              "created_by": 1234,
                              "created_at": "2020-01-01T00:00:00"
                          },
                          headers=headers)

    assert response.status_code == 201
    body = response.json()
    assert body["decision_id"] == decision.id
    assert body["created_by"] == user.id
    assert body["id"] != 999


def test_get_threads_by_decision(client, db_session, make_token):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    headers = _auth_headers(user, make_token)

    for i in range(3):
        client.post(f"/decisions/{decision.id}/threads",
                   json={"title": f"Thread {i+1}"},
                   headers=headers)

    response = client.get(f"/decisions/{decision.id}/threads", headers=headers)

    assert response.status_code == 200
    threads = response.json()
    assert len(threads) == 3
    assert [t["title"] for t in threads] == ["Thread 1", "Thread 2", "Thread 3"]
    assert all(t["decision_id"] == decision.id for t in threads)


def test_get_threads_by_decision_not_found(client, db_session, make_token):
    user = _create_user(db_session)
    headers = _auth_headers(user, make_token)

    response = client.get("/decisions/99999999/threads", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Decision not found"


def test_get_thread_by_id(client, db_session, make_token):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    headers = _auth_headers(user, make_token)

    created = client.post(f"/decisions/{decision.id}/threads",
                          json={"title": "Single thread"},
                          headers=headers).json()

    response = client.get(f"/threads/{created['id']}", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created["id"]
    assert body["title"] == "Single thread"
    assert body["created_by"] == user.id


def test_get_thread_not_found(client, db_session, make_token):
    user = _create_user(db_session)
    headers = _auth_headers(user, make_token)

    response = client.get("/threads/99999999", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Thread not found"


def test_update_thread_as_owner(client, db_session, make_token):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    headers = _auth_headers(user, make_token)

    created = client.post(f"/decisions/{decision.id}/threads",
                          json={"title": "Original title", "description": "Original desc"},
                          headers=headers).json()

    time.sleep(1.1)

    response = client.put(f"/threads/{created['id']}",
                         json={"title": "Updated title", "description": "Updated desc"},
                         headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Updated title"
    assert body["description"] == "Updated desc"
    assert body["id"] == created["id"]
    assert body["decision_id"] == decision.id
    assert body["created_by"] == user.id
    assert body["created_at"] == created["created_at"]
    assert body["updated_at"] > created["updated_at"]


def test_update_thread_as_admin(client, db_session, make_token):
    author = _create_user(db_session, email="author_thread@example.com", employee_id="EMP_AUTH_T")
    admin = _create_user(db_session, email="admin_thread@example.com", employee_id="EMP_ADM_T", role=UserRole.ADMINISTRATOR)
    decision = _create_decision(db_session, author)
    author_headers = _auth_headers(author, make_token)
    admin_headers = _auth_headers(admin, make_token)

    created = client.post(f"/decisions/{decision.id}/threads",
                          json={"title": "Author's thread"},
                          headers=author_headers).json()

    response = client.put(f"/threads/{created['id']}",
                        json={"title": "Moderated by Admin"},
                        headers=admin_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Moderated by Admin"
    assert body["created_by"] == author.id


def test_update_thread_as_other_user_forbidden(client, db_session, make_token):
    user_a = _create_user(db_session, email="user_athread@example.com", employee_id="EMP_ATHREAD")
    user_b = _create_user(db_session, email="user_bthread@example.com", employee_id="EMP_BTHREAD", role=UserRole.EMPLOYEE)
    decision = _create_decision(db_session, user_a)
    headers_a = _auth_headers(user_a, make_token)
    headers_b = _auth_headers(user_b, make_token)

    created = client.post(f"/decisions/{decision.id}/threads",
                          json={"title": "User A thread"},
                          headers=headers_a).json()

    response = client.put(f"/threads/{created['id']}",
                          json={"title": "Hacked by User B"},
                          headers=headers_b)

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to modify this thread"


def test_update_thread_not_found(client, db_session, make_token):
    user = _create_user(db_session)
    headers = _auth_headers(user, make_token)

    response = client.put("/threads/99999999", json={"title": "X"}, headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Thread not found"


def test_update_thread_backend_controlled_fields_unchanged(client, db_session, make_token):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    headers = _auth_headers(user, make_token)

    created = client.post(f"/decisions/{decision.id}/threads",
                          json={"title": "Original"},
                          headers=headers).json()

    client.put(f"/threads/{created['id']}",
               json={
                   "title": "Updated",
                   "id": 999,
                   "decision_id": 5678,
                   "created_by": 1234,
                   "created_at": "2020-01-01T00:00:00"
               },
               headers=headers)

    body = client.get(f"/threads/{created['id']}", headers=headers).json()
    assert body["id"] == created["id"]
    assert body["decision_id"] == decision.id
    assert body["created_by"] == user.id
    assert body["created_at"] == created["created_at"]


def test_delete_thread_as_owner(client, db_session, make_token):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    headers = _auth_headers(user, make_token)

    created = client.post(f"/decisions/{decision.id}/threads",
                          json={"title": "To be deleted"},
                          headers=headers).json()

    response = client.delete(f"/threads/{created['id']}", headers=headers)

    assert response.status_code == 200
    assert response.json()["message"] == "Thread deleted successfully"

    get_res = client.get(f"/threads/{created['id']}", headers=headers)
    assert get_res.status_code == 404


def test_delete_thread_as_admin(client, db_session, make_token):
    author = _create_user(db_session, email="author_delthread@example.com", employee_id="EMP_AUTHDEL_T")
    admin = _create_user(db_session, email="admin_delthread@example.com", employee_id="EMP_ADMDEL_T", role=UserRole.ADMINISTRATOR)
    decision = _create_decision(db_session, author)
    author_headers = _auth_headers(author, make_token)
    admin_headers = _auth_headers(admin, make_token)

    created = client.post(f"/decisions/{decision.id}/threads",
                          json={"title": "Author text"},
                          headers=author_headers).json()

    response = client.delete(f"/threads/{created['id']}", headers=admin_headers)

    assert response.status_code == 200
    assert response.json()["message"] == "Thread deleted successfully"


def test_delete_thread_as_other_user_forbidden(client, db_session, make_token):
    user_a = _create_user(db_session, email="user_adelthread@example.com", employee_id="EMP_ADEL_T")
    user_b = _create_user(db_session, email="user_bdelthread@example.com", employee_id="EMP_BDEL_T", role=UserRole.EMPLOYEE)
    decision = _create_decision(db_session, user_a)
    headers_a = _auth_headers(user_a, make_token)
    headers_b = _auth_headers(user_b, make_token)

    created = client.post(f"/decisions/{decision.id}/threads",
                          json={"title": "User A text"},
                          headers=headers_a).json()

    response = client.delete(f"/threads/{created['id']}", headers=headers_b)

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to delete this thread"


def test_delete_thread_not_found(client, db_session, make_token):
    user = _create_user(db_session)
    headers = _auth_headers(user, make_token)

    response = client.delete("/threads/99999999", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Thread not found"


def test_create_thread_reply(client, db_session, make_token):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    headers = _auth_headers(user, make_token)

    thread = client.post(f"/decisions/{decision.id}/threads",
                        json={"title": "Discussion Thread"},
                        headers=headers).json()

    response = client.post(f"/threads/{thread['id']}/comments",
                          json={"content": "This is a reply."},
                          headers=headers)

    assert response.status_code == 201
    body = response.json()
    assert body["thread_id"] == thread["id"]
    assert body["decision_id"] == decision.id
    assert body["user_id"] == user.id
    assert body["content"] == "This is a reply."


def test_create_thread_reply_thread_not_found(client, db_session, make_token):
    user = _create_user(db_session)
    headers = _auth_headers(user, make_token)

    response = client.post("/threads/99999999/comments",
                          json={"content": "Reply to ghost thread"},
                          headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Thread not found"


def test_create_multiple_replies_to_thread(client, db_session, make_token):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    headers = _auth_headers(user, make_token)

    thread = client.post(f"/decisions/{decision.id}/threads",
                        json={"title": "Multi-reply Thread"},
                        headers=headers).json()

    for i in range(3):
        response = client.post(f"/threads/{thread['id']}/comments",
                              json={"content": f"Reply {i+1}"},
                              headers=headers)
        assert response.status_code == 201

    replies = client.get(f"/decisions/{decision.id}/comments", headers=headers).json()
    thread_replies = [r for r in replies if r["thread_id"] == thread["id"]]
    assert len(thread_replies) == 3


def test_all_thread_endpoints_without_token(client, db_session):
    endpoints = [
        ("post", "/decisions/1/threads", {"json": {"title": "Thread"}}),
        ("get", "/decisions/1/threads", {}),
        ("get", "/threads/1", {}),
        ("put", "/threads/1", {"json": {"title": "Updated"}}),
        ("delete", "/threads/1", {}),
        ("post", "/threads/1/comments", {"json": {"content": "Reply"}}),
    ]

    for method, url, kwargs in endpoints:
        response = getattr(client, method)(url, **kwargs)
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"
