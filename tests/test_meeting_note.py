from datetime import datetime, timezone
import time
import pytest

from app.models.decision import Decision
from app.models.enums import UserRole
from app.models.meeting_note import MeetingNote
from app.models.user import User
from app.core.security import hash_password


def _create_user(db_session, email="mn_user@example.com", employee_id="EMP_MN", role=UserRole.EMPLOYEE):
    user = User(
        full_name="Meeting Note User",
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
        title="Architecture Decision",
        problem_statement="Choose microservice orchestration framework",
        category="Architecture",
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


NOTE_BODY = {
    "title": "Architecture Sync",
    "content": "Discussed Kubernetes vs Nomad.",
    "meeting_date": "2026-08-25T10:00:00Z"
}


def test_create_meeting_note(client, db_session, make_token):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    headers = _auth_headers(user, make_token)

    response = client.post(f"/decisions/{decision.id}/meeting-notes",
                           json=NOTE_BODY,
                           headers=headers)

    assert response.status_code == 201
    body = response.json()
    assert body["decision_id"] == decision.id
    assert body["created_by"] == user.id
    assert body["title"] == "Architecture Sync"
    assert body["content"] == "Discussed Kubernetes vs Nomad."
    assert "meeting_date" in body
    assert body["id"] is not None
    assert "created_at" in body
    assert "updated_at" in body


def test_create_meeting_note_decision_not_found(client, db_session, make_token):
    user = _create_user(db_session)
    headers = _auth_headers(user, make_token)

    response = client.post("/decisions/99999999/meeting-notes",
                           json=NOTE_BODY,
                           headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Decision not found"


def test_create_meeting_note_ignores_injected_fields(client, db_session, make_token):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    headers = _auth_headers(user, make_token)

    response = client.post(f"/decisions/{decision.id}/meeting-notes",
                           json={
                               **NOTE_BODY,
                               "id": 999,
                               "created_by": 1234,
                               "decision_id": 5678,
                               "created_at": "2020-01-01T00:00:00Z"
                           },
                           headers=headers)

    assert response.status_code == 201
    body = response.json()
    assert body["decision_id"] == decision.id
    assert body["created_by"] == user.id
    assert body["id"] != 999


def test_create_meeting_note_missing_required_field(client, db_session, make_token):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    headers = _auth_headers(user, make_token)

    # Missing title
    response = client.post(f"/decisions/{decision.id}/meeting-notes",
                           json={"content": "Content only", "meeting_date": "2026-08-25T10:00:00Z"},
                           headers=headers)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "title"]


def test_get_meeting_notes_by_decision(client, db_session, make_token):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    headers = _auth_headers(user, make_token)

    for i in range(3):
        client.post(f"/decisions/{decision.id}/meeting-notes",
                    json={
                        "title": f"Meeting {i+1}",
                        "content": f"Notes {i+1}",
                        "meeting_date": f"2026-08-{20+i}T10:00:00Z"
                    },
                    headers=headers)

    response = client.get(f"/decisions/{decision.id}/meeting-notes", headers=headers)

    assert response.status_code == 200
    notes = response.json()
    assert len(notes) == 3
    assert [n["title"] for n in notes] == ["Meeting 1", "Meeting 2", "Meeting 3"]
    assert all(n["decision_id"] == decision.id for n in notes)


def test_get_meeting_notes_by_decision_not_found(client, db_session, make_token):
    user = _create_user(db_session)
    headers = _auth_headers(user, make_token)

    response = client.get("/decisions/99999999/meeting-notes", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Decision not found"


def test_get_meeting_note_by_id(client, db_session, make_token):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    headers = _auth_headers(user, make_token)

    created = client.post(f"/decisions/{decision.id}/meeting-notes",
                          json=NOTE_BODY,
                          headers=headers).json()

    response = client.get(f"/meeting-notes/{created['id']}", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created["id"]
    assert body["title"] == "Architecture Sync"
    assert body["created_by"] == user.id


def test_get_meeting_note_not_found(client, db_session, make_token):
    user = _create_user(db_session)
    headers = _auth_headers(user, make_token)

    response = client.get("/meeting-notes/99999999", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Meeting note not found"


def test_update_meeting_note_as_owner(client, db_session, make_token):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    headers = _auth_headers(user, make_token)

    created = client.post(f"/decisions/{decision.id}/meeting-notes",
                          json=NOTE_BODY,
                          headers=headers).json()

    time.sleep(1.1)

    response = client.put(f"/meeting-notes/{created['id']}",
                          json={
                              "title": "Architecture Sync - Revised",
                              "content": "Agreed on Kubernetes.",
                              "meeting_date": "2026-08-25T11:00:00Z"
                          },
                          headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Architecture Sync - Revised"
    assert body["content"] == "Agreed on Kubernetes."
    assert body["id"] == created["id"]
    assert body["decision_id"] == decision.id
    assert body["created_by"] == user.id
    assert body["created_at"] == created["created_at"]
    assert body["updated_at"] > created["updated_at"]


def test_update_meeting_note_as_admin(client, db_session, make_token):
    author = _create_user(db_session, email="author_mn@example.com", employee_id="EMP_MNAUTH")
    admin = _create_user(db_session, email="admin_mn@example.com", employee_id="EMP_MNADM", role=UserRole.ADMINISTRATOR)
    decision = _create_decision(db_session, author)
    author_headers = _auth_headers(author, make_token)
    admin_headers = _auth_headers(admin, make_token)

    created = client.post(f"/decisions/{decision.id}/meeting-notes",
                          json=NOTE_BODY,
                          headers=author_headers).json()

    response = client.put(f"/meeting-notes/{created['id']}",
                          json={"title": "Admin Edited Title"},
                          headers=admin_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Admin Edited Title"
    assert body["created_by"] == author.id  # Preserved original author


def test_update_meeting_note_as_non_owner_forbidden(client, db_session, make_token):
    user_a = _create_user(db_session, email="user_amn@example.com", employee_id="EMP_MNA")
    user_b = _create_user(db_session, email="user_bmn@example.com", employee_id="EMP_MNB", role=UserRole.EMPLOYEE)
    decision = _create_decision(db_session, user_a)
    headers_a = _auth_headers(user_a, make_token)
    headers_b = _auth_headers(user_b, make_token)

    created = client.post(f"/decisions/{decision.id}/meeting-notes",
                          json=NOTE_BODY,
                          headers=headers_a).json()

    response = client.put(f"/meeting-notes/{created['id']}",
                          json={"title": "Unauthorized update"},
                          headers=headers_b)

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to modify this meeting note"


def test_update_meeting_note_not_found(client, db_session, make_token):
    user = _create_user(db_session)
    headers = _auth_headers(user, make_token)

    response = client.put("/meeting-notes/99999999",
                          json={"title": "New Title"},
                          headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Meeting note not found"


def test_delete_meeting_note_as_owner(client, db_session, make_token):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    headers = _auth_headers(user, make_token)

    created = client.post(f"/decisions/{decision.id}/meeting-notes",
                          json=NOTE_BODY,
                          headers=headers).json()

    response = client.delete(f"/meeting-notes/{created['id']}", headers=headers)

    assert response.status_code == 200
    assert response.json()["message"] == "Meeting note deleted successfully"

    # Verify note is gone
    get_res = client.get(f"/meeting-notes/{created['id']}", headers=headers)
    assert get_res.status_code == 404


def test_delete_meeting_note_as_admin(client, db_session, make_token):
    author = _create_user(db_session, email="author_mndel@example.com", employee_id="EMP_MNDEL1")
    admin = _create_user(db_session, email="admin_mndel@example.com", employee_id="EMP_MNDEL2", role=UserRole.ADMINISTRATOR)
    decision = _create_decision(db_session, author)
    author_headers = _auth_headers(author, make_token)
    admin_headers = _auth_headers(admin, make_token)

    created = client.post(f"/decisions/{decision.id}/meeting-notes",
                          json=NOTE_BODY,
                          headers=author_headers).json()

    response = client.delete(f"/meeting-notes/{created['id']}", headers=admin_headers)

    assert response.status_code == 200
    assert response.json()["message"] == "Meeting note deleted successfully"


def test_delete_meeting_note_as_non_owner_forbidden(client, db_session, make_token):
    user_a = _create_user(db_session, email="user_adelmn@example.com", employee_id="EMP_MNADEL")
    user_b = _create_user(db_session, email="user_bdelmn@example.com", employee_id="EMP_MNBDEL", role=UserRole.EMPLOYEE)
    decision = _create_decision(db_session, user_a)
    headers_a = _auth_headers(user_a, make_token)
    headers_b = _auth_headers(user_b, make_token)

    created = client.post(f"/decisions/{decision.id}/meeting-notes",
                          json=NOTE_BODY,
                          headers=headers_a).json()

    response = client.delete(f"/meeting-notes/{created['id']}", headers=headers_b)

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to delete this meeting note"


def test_delete_meeting_note_not_found(client, db_session, make_token):
    user = _create_user(db_session)
    headers = _auth_headers(user, make_token)

    response = client.delete("/meeting-notes/99999999", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Meeting note not found"


def test_all_five_meeting_note_endpoints_without_token(client, db_session):
    endpoints = [
        ("post", "/decisions/1/meeting-notes", {"json": NOTE_BODY}),
        ("get", "/decisions/1/meeting-notes", {}),
        ("get", "/meeting-notes/1", {}),
        ("put", "/meeting-notes/1", {"json": {"title": "new"}}),
        ("delete", "/meeting-notes/1", {}),
    ]

    for method, url, kwargs in endpoints:
        response = getattr(client, method)(url, **kwargs)
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"


def test_cascade_delete_decision_deletes_meeting_notes(client, db_session, make_token):
    user = _create_user(db_session)
    decision = _create_decision(db_session, user)
    headers = _auth_headers(user, make_token)

    created = client.post(f"/decisions/{decision.id}/meeting-notes",
                          json=NOTE_BODY,
                          headers=headers).json()

    # Verify note in DB
    note = db_session.query(MeetingNote).filter(MeetingNote.id == created["id"]).first()
    assert note is not None

    # Delete decision directly
    db_session.delete(decision)
    db_session.commit()

    # Verify note is deleted
    note = db_session.query(MeetingNote).filter(MeetingNote.id == created["id"]).first()
    assert note is None
