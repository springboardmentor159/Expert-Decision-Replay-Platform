from app.core.security import create_access_token
from app.models.enums import UserRole
from app.models.user import User


def _user(db_session, email, employee_id, role=UserRole.EMPLOYEE):
    user = User(
        full_name="Document Tester",
        email=email,
        employee_id=employee_id,
        password="hashed",
        role=role,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _headers(user, make_token):
    return {"Authorization": f"Bearer {make_token(str(user.id))}"}


def _decision(client, headers):
    response = client.post(
        "/decisions",
        json={"title": "Document decision", "problem_statement": "A problem", "category": "Engineering"},
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_document_upload_list_download_and_invalid_file(client, db_session, make_token, monkeypatch, tmp_path):
    from app.routers import document as document_router

    monkeypatch.setattr(document_router, "UPLOAD_ROOT", tmp_path)
    user = _user(db_session, "document-owner@example.com", "DOC-1")
    headers = _headers(user, make_token)
    decision_id = _decision(client, headers)

    upload = client.post(
        f"/decisions/{decision_id}/documents",
        headers=headers,
        files={"file": ("brief.txt", b"real document", "text/plain")},
    )
    assert upload.status_code == 201
    document = upload.json()
    assert document["filename"] == "brief.txt"
    assert document["decision_id"] == decision_id

    listing = client.get(f"/decisions/{decision_id}/documents", headers=headers)
    assert listing.status_code == 200
    assert listing.json()[0]["id"] == document["id"]

    download = client.get(document["download_url"], headers=headers)
    assert download.status_code == 200
    assert download.content == b"real document"
    assert download.headers["content-type"].startswith("text/plain")

    invalid = client.post(
        f"/decisions/{decision_id}/documents",
        headers=headers,
        files={"file": ("script.exe", b"not allowed", "application/octet-stream")},
    )
    assert invalid.status_code == 422


def test_document_upload_requires_decision_permission(client, db_session, make_token):
    owner = _user(db_session, "document-owner-2@example.com", "DOC-2")
    other = _user(db_session, "document-other@example.com", "DOC-3")
    owner_headers = _headers(owner, make_token)
    other_headers = _headers(other, make_token)
    decision_id = _decision(client, owner_headers)

    response = client.post(
        f"/decisions/{decision_id}/documents",
        headers=other_headers,
        files={"file": ("brief.txt", b"blocked", "text/plain")},
    )
    assert response.status_code == 403


def test_dashboard_report_filter_export_document_flow(client, db_session, make_token, monkeypatch, tmp_path):
    from app.routers import document as document_router

    monkeypatch.setattr(document_router, "UPLOAD_ROOT", tmp_path)
    user = _user(db_session, "phase3-flow@example.com", "DOC-FLOW")
    headers = _headers(user, make_token)
    decision_id = _decision(client, headers)
    status_update = client.patch(f"/decisions/{decision_id}/status", json={"status": "Approved"}, headers=headers)
    assert status_update.status_code == 200

    dashboard = client.get("/dashboard/employee", headers=headers)
    assert dashboard.status_code == 200
    assert dashboard.json()["total_decisions"] == 1

    report = client.get("/reports/decisions", params={"status": "Approved", "page": 1}, headers=headers)
    assert report.status_code == 200
    assert report.json()["total"] == 1

    export = client.get("/reports/decisions/export/pdf", params={"status": "Approved"}, headers=headers)
    assert export.status_code == 200
    assert export.headers["content-type"].startswith("application/pdf")

    upload = client.post(
        f"/decisions/{decision_id}/documents",
        headers=headers,
        files={"file": ("flow.txt", b"flow document", "text/plain")},
    )
    assert upload.status_code == 201
