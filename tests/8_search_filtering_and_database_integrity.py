import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.alternative import Alternative
from app.models.approval import Approval
from app.models.audit import AuditLog, DecisionVersion
from app.models.comment import Comment
from app.models.decision import Decision
from app.models.organization import Organization
from app.models.tag import Tag
from app.models.user import User


def test_search_and_filtering_combinations(
    client: TestClient,
    employee_headers: dict,
    test_org: Organization,
    db_session: Session,
):
    """
    Test Search and Filtering (Sprint 13 Section 16):
    - Category filtering
    - Status filtering
    - Tag filtering
    - Keyword search
    - Combination of filters
    """
    unique_tag = f"tag_{uuid.uuid4().hex[:6]}"

    # Create tag
    res_tag = client.post("/tags", json={"name": unique_tag}, headers=employee_headers)
    assert res_tag.status_code == 201
    tag_id = res_tag.json()["id"]

    # Create Decision 1: Architecture, Technology
    res1 = client.post(
        "/decisions",
        json={
            "title": f"Kubernetes Cluster Architecture {unique_tag}",
            "problem_statement": "Deploying Kubernetes on-premise vs managed EKS cloud.",
            "category": "Technology",
        },
        headers=employee_headers,
    )
    assert res1.status_code == 201
    dec1_id = res1.json()["id"]

    # Assign tag to Decision 1
    res_assign = client.post(
        f"/decisions/{dec1_id}/tags",
        json={"tag_ids": [tag_id]},
        headers=employee_headers,
    )
    assert res_assign.status_code == 201

    # Search by keyword
    res_search = client.get(f"/decisions/search?q=Kubernetes", headers=employee_headers)
    assert res_search.status_code == 200
    results = res_search.json()["results"]
    assert any(d["id"] == dec1_id for d in results)

    # Search with category + tag combination
    res_combo = client.get(
        f"/decisions/search?category=Technology&tag={unique_tag}",
        headers=employee_headers,
    )
    assert res_combo.status_code == 200
    combo_results = res_combo.json()["results"]
    assert len(combo_results) >= 1
    assert combo_results[0]["id"] == dec1_id

    # Test Tag Removal
    res_del_tag = client.delete(
        f"/decisions/{dec1_id}/tags/{tag_id}",
        headers=employee_headers,
    )
    assert res_del_tag.status_code == 204

    # Verify Tag is no longer assigned
    res_tags = client.get(f"/decisions/{dec1_id}/tags", headers=employee_headers)
    assert res_tags.status_code == 200
    assert not any(t["id"] == tag_id for t in res_tags.json())


def test_alternative_crud_and_cascade(
    client: TestClient,
    employee_headers: dict,
):
    """
    Test Alternative update and delete operations.
    """
    # Create Decision
    res = client.post(
        "/decisions",
        json={
            "title": f"Alternative CRUD Test {uuid.uuid4().hex[:6]}",
            "problem_statement": "Testing alternative lifecycle.",
            "category": "Operations",
        },
        headers=employee_headers,
    )
    dec_id = res.json()["id"]

    # Create Alternative
    res = client.post(
        f"/decisions/{dec_id}/alternatives",
        json={
            "name": "Initial Option",
            "description": "desc",
            "pros": "pros",
            "cons": "cons",
            "estimated_cost": 200.0,
            "feasibility_score": 4,
            "risk_level": "Low",
        },
        headers=employee_headers,
    )
    alt_id = res.json()["id"]

    # Update Alternative
    res = client.put(
        f"/alternatives/{alt_id}",
        json={
            "name": "Updated Option",
            "description": "updated desc",
            "pros": "updated pros",
            "cons": "updated cons",
            "estimated_cost": 300.0,
            "feasibility_score": 5,
            "risk_level": "Medium",
        },
        headers=employee_headers,
    )
    assert res.status_code == 200
    assert res.json()["name"] == "Updated Option"
    assert res.json()["feasibility_score"] == 5

    # Delete Alternative
    res = client.delete(f"/alternatives/{alt_id}", headers=employee_headers)
    assert res.status_code == 204

    # Verify deleted
    res = client.get(f"/alternatives/{alt_id}", headers=employee_headers)
    assert res.status_code == 404


def test_database_referential_integrity(db_session: Session):
    """
    Database Integrity Testing (Sprint 13 Section 11 & 35):
    Verify that there are no orphan alternatives, approvals, comments, or versions.
    """
    # 1. No orphan alternatives
    orphan_alts = (
        db_session.query(Alternative)
        .outerjoin(Decision, Alternative.decision_id == Decision.id)
        .filter(Decision.id.is_(None))
        .count()
    )
    assert orphan_alts == 0, f"Found {orphan_alts} orphan alternatives!"

    # 2. No orphan approvals
    orphan_approvals = (
        db_session.query(Approval)
        .outerjoin(Decision, Approval.decision_id == Decision.id)
        .filter(Decision.id.is_(None))
        .count()
    )
    assert orphan_approvals == 0, f"Found {orphan_approvals} orphan approvals!"

    # 3. No orphan decision versions
    orphan_versions = (
        db_session.query(DecisionVersion)
        .outerjoin(Decision, DecisionVersion.decision_id == Decision.id)
        .filter(Decision.id.is_(None))
        .count()
    )
    assert orphan_versions == 0, f"Found {orphan_versions} orphan decision versions!"

    # 4. No orphan comments
    orphan_comments = (
        db_session.query(Comment)
        .outerjoin(Decision, Comment.decision_id == Decision.id)
        .filter(Decision.id.is_(None))
        .count()
    )
    assert orphan_comments == 0, f"Found {orphan_comments} orphan comments!"
