# Sprint 13 - Bug Tracking & Resolution Register

This register documents all issues identified, reproduced, classified, and resolved during system integration and regression testing for the **Expert Decision Replay Platform**.

---

### BUG-001: Missing Reviewer Authorization on Decision Approvals & Rejections
- **Bug ID**: BUG-001
- **Module**: Approval Workflow (`app/routers/approvals.py`)
- **Severity**: High
- **Status**: Fixed
- **Description**: An unassigned basic employee was able to call `POST /approvals/{id}/approve` or `POST /approvals/{id}/reject` on approvals assigned to another reviewer.
- **Steps to Reproduce**:
  1. Create a Decision as Employee A.
  2. Submit Decision for Approval assigning Reviewer B (`POST /approvals`).
  3. Authenticate as Employee C (unassigned user).
  4. Call `POST /approvals/{id}/approve` using Employee C's bearer token.
- **Expected Result**: HTTP `403 Forbidden` with detail `"Not authorized to approve this decision"`.
- **Actual Result**: Approval succeeded (HTTP `200 OK`) and changed approval status.
- **Fix**: Added explicit RBAC check in both `approve_decision` and `reject_decision` verifying `current_user.id == approval.reviewer_id or current_user.role in ["Administrator", "Manager"]`.

---

### BUG-002: Multi-Level Approval Premature Decision Status Resolution
- **Bug ID**: BUG-002
- **Module**: Approval Workflow (`app/routers/approvals.py`)
- **Severity**: High
- **Status**: Fixed
- **Description**: In a multi-level approval process (e.g. Level 1 Technical Reviewer and Level 2 Department Manager), approving Level 1 immediately changed the parent Decision status to `"Approved"` even though Level 2 was still `"Pending"`.
- **Steps to Reproduce**:
  1. Create a Decision.
  2. Create Approval Level 1 for Reviewer.
  3. Create Approval Level 2 for Manager.
  4. Reviewer approves Level 1.
  5. Check `GET /decisions/{id}` status.
- **Expected Result**: Decision status must remain `"Under Review"` until all multi-level approvals are completed.
- **Actual Result**: Decision status was prematurely set to `"Approved"`.
- **Fix**: In `approve_decision`, query all sibling approvals for `decision.id`. If any other approval is still `"Pending"`, preserve `decision.status = "Under Review"`. Only transition to `"Approved"` when all pending approvals are cleared.

---

### BUG-003: Unenforced State Transitions in Decision Lifecycle
- **Bug ID**: BUG-003
- **Module**: Decision Management (`app/routers/decisions.py`)
- **Severity**: Medium
- **Status**: Fixed
- **Description**: `PATCH /decisions/{id}/status` only guarded against modifying an already archived decision if the new status was also archived. It permitted invalid arbitrary transitions such as `"Archived" -> "Draft"` or `"Approved" -> "Draft"`.
- **Steps to Reproduce**:
  1. Create and Approve a Decision.
  2. Call `PATCH /decisions/{id}/status` with `{"status": "Draft"}`.
- **Expected Result**: HTTP `400 Bad Request` with an error indicating an invalid state transition.
- **Actual Result**: Status changed to `"Draft"`, breaking decision lifecycle history and integrity.
- **Fix**: Defined an explicit `VALID_TRANSITIONS` state table in `update_decision_status` and rejected any unauthorized state transitions with HTTP `400 Bad Request`.

---

### BUG-004: Missing Environment Configuration Template
- **Bug ID**: BUG-004
- **Module**: Configuration & Deployment
- **Severity**: Low
- **Status**: Fixed
- **Description**: Repository lacked an environment template (`.env.example`) to guide development setup without exposing production secrets.
- **Steps to Reproduce**: Check repository root for `.env.example`.
- **Expected Result**: `.env.example` present with placeholder variables.
- **Actual Result**: File was missing.
- **Fix**: Created `.env.example` containing clean, standardized placeholders for `DATABASE_URL`, `SECRET_KEY`, `ALGORITHM`, and `ACCESS_TOKEN_EXPIRE_MINUTES`.
