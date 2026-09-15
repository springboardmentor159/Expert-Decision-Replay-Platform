import io
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.decision import Decision, DecisionStatus


def test_teams_crud_and_membership(client: TestClient, admin_headers, manager_headers, employee_user):
    # 1. Manager creates a team
    create_resp = client.post(
        "/teams",
        headers=manager_headers,
        json={
            "name": "Cloud Infrastructure Guild",
            "description": "Cross-functional team responsible for AWS, Kubernetes, and Observability.",
        },
    )
    assert create_resp.status_code == 201
    team_data = create_resp.json()
    team_id = team_data["id"]
    assert team_data["name"] == "Cloud Infrastructure Guild"

    # 2. Get teams list
    list_resp = client.get("/teams", headers=manager_headers)
    assert list_resp.status_code == 200
    teams = list_resp.json()
    assert any(t["id"] == team_id for t in teams)

    # 3. Add employee as team member
    add_member_resp = client.post(
        f"/teams/{team_id}/members",
        headers=manager_headers,
        json={"user_id": employee_user.id},
    )
    assert add_member_resp.status_code == 200
    members = add_member_resp.json()["members"]
    assert any(m["id"] == employee_user.id for m in members)

    # 4. Remove member
    rem_resp = client.delete(f"/teams/{team_id}/members/{employee_user.id}", headers=manager_headers)
    assert rem_resp.status_code == 200
    assert not any(m["id"] == employee_user.id for m in rem_resp.json()["members"])

    # 5. Delete team (Admin only)
    del_resp = client.delete(f"/teams/{team_id}", headers=admin_headers)
    assert del_resp.status_code == 204


def test_decision_outcomes_and_implementation_status(client: TestClient, employee_headers):
    # Create a draft decision
    create_resp = client.post(
        "/decisions",
        headers=employee_headers,
        json={
            "title": "Adopt Event-Driven Microservices Architecture",
            "problem_statement": "Monolith latency and tight coupling degrade team velocity.",
            "category": "Architecture",
            "evaluation_criteria": "Maintainability, Throughput > 5000 RPS, P99 < 50ms",
        },
    )
    assert create_resp.status_code == 201
    decision_id = create_resp.json()["id"]

    # Update implementation status
    impl_resp = client.patch(
        f"/decisions/{decision_id}/implementation",
        headers=employee_headers,
        json={"implementation_status": "In Progress"},
    )
    assert impl_resp.status_code == 200
    assert impl_resp.json()["implementation_status"] == "In Progress"

    # Update final outcomes / retrospective
    outcomes_resp = client.patch(
        f"/decisions/{decision_id}/outcomes",
        headers=employee_headers,
        json={"final_outcomes": "P99 latency dropped by 45% and deployments are now independent."},
    )
    assert outcomes_resp.status_code == 200
    assert "P99 latency dropped" in outcomes_resp.json()["final_outcomes"]

    # Update criteria
    crit_resp = client.patch(
        f"/decisions/{decision_id}/criteria",
        headers=employee_headers,
        json={"evaluation_criteria": "Throughput > 10000 RPS"},
    )
    assert crit_resp.status_code == 200
    assert crit_resp.json()["evaluation_criteria"] == "Throughput > 10000 RPS"


def test_sequential_approvals_and_escalation(
    client: TestClient, employee_headers, reviewer_headers, manager_headers, reviewer_user, manager_user
):
    # Create decision
    create_resp = client.post(
        "/decisions",
        headers=employee_headers,
        json={
            "title": "Migrate to OpenSearch for Analytics",
            "problem_statement": "Elasticsearch legacy license is expiring.",
            "category": "Database",
        },
    )
    assert create_resp.status_code == 201
    decision_id = create_resp.json()["id"]

    # Assign reviewer at Stage 1
    apprv1_resp = client.post(
        "/approvals",
        headers=employee_headers,
        json={"decision_id": decision_id, "reviewer_id": reviewer_user.id, "sequence_order": 1},
    )
    assert apprv1_resp.status_code == 201
    apprv1_id = apprv1_resp.json()["id"]
    assert apprv1_resp.json()["sequence_order"] == 1

    # Escalate approval
    escalate_resp = client.post(
        f"/approvals/{apprv1_id}/escalate",
        headers=employee_headers,
        json={"reason": "Urgent procurement deadline approaching", "escalated_to_id": manager_user.id},
    )
    assert escalate_resp.status_code == 200
    assert escalate_resp.json()["is_escalated"] == 1

    # Complete Stage 1 approval
    complete_resp = client.patch(
        f"/approvals/{apprv1_id}/status",
        headers=reviewer_headers,
        json={"status": "Approved"},
    )
    assert complete_resp.status_code == 200
    assert complete_resp.json()["status"] == "Approved"


def test_notifications_lifecycle(client: TestClient, reviewer_headers):
    # Fetch notifications for reviewer
    notif_resp = client.get("/notifications", headers=reviewer_headers)
    assert notif_resp.status_code == 200
    notifs = notif_resp.json()
    assert isinstance(notifs, list)

    # Get unread count
    count_resp = client.get("/notifications/unread-count", headers=reviewer_headers)
    assert count_resp.status_code == 200
    assert "unread_count" in count_resp.json()

    # Mark all as read
    read_all_resp = client.post("/notifications/read-all", headers=reviewer_headers)
    assert read_all_resp.status_code == 200

    # Unread count should now be 0
    count_after = client.get("/notifications/unread-count", headers=reviewer_headers).json()
    assert count_after["unread_count"] == 0


def test_decision_replay_endpoint(client: TestClient, employee_headers):
    # Create decision
    create_resp = client.post(
        "/decisions",
        headers=employee_headers,
        json={
            "title": "Adopt GraphQL Federation Gateway",
            "problem_statement": "Multiple REST APIs result in over-fetching for mobile clients.",
            "category": "Architecture",
        },
    )
    decision_id = create_resp.json()["id"]

    # Call replay endpoint
    replay_resp = client.get(f"/decisions/{decision_id}/replay", headers=employee_headers)
    assert replay_resp.status_code == 200
    replay_data = replay_resp.json()
    assert replay_data["decision_id"] == decision_id
    assert replay_data["total_milestones"] >= 1
    assert any(m["event_type"] == "CREATION" for m in replay_data["milestones"])


def test_attachment_upload_and_download(client: TestClient, employee_headers):
    # Create decision
    create_resp = client.post(
        "/decisions",
        headers=employee_headers,
        json={
            "title": "Kubernetes Cluster Ingress Controller Standard",
            "problem_statement": "Evaluate ingress routing across ALB vs Envoy vs Traefik.",
            "category": "Infrastructure",
        },
    )
    decision_id = create_resp.json()["id"]

    # Upload sample architecture diagram file
    sample_file_content = b"Mock Architecture Diagram and Network Topology"
    files = {"file": ("architecture_topology.txt", io.BytesIO(sample_file_content), "text/plain")}
    upload_resp = client.post(
        f"/decisions/{decision_id}/attachments",
        headers=employee_headers,
        files=files,
    )
    assert upload_resp.status_code == 201
    attachment_id = upload_resp.json()["id"]
    assert upload_resp.json()["filename"] == "architecture_topology.txt"

    # List attachments
    list_resp = client.get(f"/decisions/{decision_id}/attachments", headers=employee_headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1

    # Check Document Archive endpoint
    archive_resp = client.get("/attachments/archive", headers=employee_headers)
    assert archive_resp.status_code == 200
    assert any(a["id"] == attachment_id for a in archive_resp.json())

    # Download attachment
    download_resp = client.get(f"/attachments/{attachment_id}/download", headers=employee_headers)
    assert download_resp.status_code == 200
    assert download_resp.content == sample_file_content

    # Delete attachment
    del_resp = client.delete(f"/attachments/{attachment_id}", headers=employee_headers)
    assert del_resp.status_code == 204
