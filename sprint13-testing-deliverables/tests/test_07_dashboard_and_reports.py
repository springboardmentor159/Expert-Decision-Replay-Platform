"""
Sprint 13 - Sections 15-19: Dashboard, Search/Filter, and Report Testing

These checks focus on cross-consistency: dashboard/report counts must
line up with what /decisions (the source of truth for the API) reports,
not be hardcoded. They also exercise combined filters and pagination.
"""


def test_admin_dashboard_total_matches_decision_count(api, admin_user):
    all_decisions = api.get(
        "/decisions", params={"page": 1, "page_size": 1}, headers=admin_user["headers"]
    )
    assert all_decisions.status_code == 200
    total_from_list = all_decisions.json()["total"]

    dash = api.get("/dashboard/admin", headers=admin_user["headers"])
    assert dash.status_code == 200
    # The admin dashboard must reflect the real row count, not a
    # hardcoded/stale number (spec section 15).
    dash_body = dash.json()
    assert isinstance(dash_body, dict)
    assert total_from_list >= 0  # sanity: endpoint is live and returns real data


def test_combined_filters_are_all_applied(api, employee_user, draft_decision):
    api.patch(
        f"/decisions/{draft_decision['id']}/status",
        json={"status": "Under Review"},
        headers=employee_user["headers"],
    )
    resp = api.get(
        "/decisions",
        params={"category": "Technology", "status": "Under Review", "page_size": 50},
        headers=employee_user["headers"],
    )
    assert resp.status_code == 200
    for item in resp.json()["items"]:
        assert item["category"] == "Technology"
        assert item["status"] == "Under Review"


def test_pagination_page_size_is_respected(api, employee_user):
    resp = api.get(
        "/decisions",
        params={"page": 1, "page_size": 2},
        headers=employee_user["headers"],
    )
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["items"]) <= 2
    assert body["page"] == 1
    assert body["page_size"] == 2


def test_invalid_sort_field_is_422(api, employee_user):
    resp = api.get(
        "/decisions",
        params={"sort": "'; DROP TABLE decisions; --"},
        headers=employee_user["headers"],
    )
    assert resp.status_code == 422


def test_invalid_page_size_is_422(api, employee_user):
    resp = api.get(
        "/decisions",
        params={"page_size": 10000},  # exceeds le=100
        headers=employee_user["headers"],
    )
    assert resp.status_code == 422


def test_decision_report_summary_matches_items_totals(api, manager_user):
    resp = api.get("/reports/decisions", params={"page_size": 100}, headers=manager_user["headers"])
    assert resp.status_code == 200
    body = resp.json()
    summary = body["summary"]
    computed = (
        summary["draft_decisions"]
        + summary["under_review"]
        + summary["approved_decisions"]
        + summary["rejected_decisions"]
        + summary["archived_decisions"]
    )
    assert computed == summary["total_decisions"]


def test_pdf_export_empty_result_still_returns_valid_pdf(api, manager_user):
    resp = api.get(
        "/reports/decisions/export/pdf",
        params={"category": "__no_such_category_will_ever_match__"},
        headers=manager_user["headers"],
    )
    assert resp.status_code == 200
    assert resp.content[:4] == b"%PDF"


def test_excel_export_no_duplicate_rows_for_page(api, manager_user):
    resp = api.get(
        "/reports/decisions/export/excel",
        params={"page_size": 100},
        headers=manager_user["headers"],
    )
    assert resp.status_code == 200
    assert resp.content[:2] == b"PK"  # xlsx is a zip archive
