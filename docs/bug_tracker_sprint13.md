# Bug Tracker - Sprint 13

This document tracks all bugs identified, investigated, and resolved during Sprint 13 System Integration, Testing & Bug Fixing.

## Bug Severity Classification
- **Critical**: Application or major workflow is unusable.
- **High**: Important business functionality does not work.
- **Medium**: Feature works incorrectly in certain scenarios.
- **Low**: Minor UI/API/configuration/documentation issue.

---

## Bug Records

### BUG-001
- **Module**: Decision Management
- **Description**: Decision status transitions were not enforced in `PATCH /decisions/{decision_id}/status`. Users could transition decisions into invalid states (e.g., `Archived -> Draft` or `Draft -> Approved` directly without review).
- **Steps to Reproduce**:
  1. Create a decision (initial status: `Draft`).
  2. Send `PATCH /decisions/{id}/status` with `{"status": "Approved"}` or archive it and send `{"status": "Draft"}`.
- **Expected Result**: Backend validates lifecycle state machine and returns `400 Bad Request` with an explanatory error.
- **Actual Result**: Status was blindly overwritten without validation.
- **Severity**: Critical
- **Status**: Fixed
- **Fix**: Implemented `VALID_DECISION_STATUS_TRANSITIONS` lookup dictionary in `app/routers/decisions.py` to enforce allowed state transitions (`Draft -> Under Review / Archived`, `Under Review -> Approved / Rejected / Draft / Archived`, `Approved -> Archived`, `Rejected -> Draft / Archived`, `Archived -> Terminal`). Return `400 Bad Request` on illegal transitions.

---

### BUG-002
- **Module**: Decision Management
- **Description**: Missing formal decision submission endpoint `POST /decisions/{decision_id}/submit` to transition decisions from `Draft` to `Under Review` with audit tracking `AuditAction.SUBMIT`.
- **Steps to Reproduce**:
  1. Creator prepares a decision with alternatives.
  2. Attempt to invoke a submission endpoint.
- **Expected Result**: An endpoint `POST /decisions/{id}/submit` moves the decision from `Draft` or `Rejected` to `Under Review`, logs `AuditAction.SUBMIT`, and snapshots a version.
- **Actual Result**: No dedicated submit endpoint existed; client had to use a generic status patch without submit-specific validation.
- **Severity**: High
- **Status**: Fixed
- **Fix**: Implemented `POST /decisions/{decision_id}/submit` in `app/routers/decisions.py` with authorization check, status verification, audit log generation, and version creation.

---

### BUG-003
- **Module**: Authorization & Access Control
- **Description**: Reviewers were blocked with `403 Forbidden` when attempting to access decisions and discussions because `can_access_decision` only permitted the creator, Managers, and Administrators.
- **Steps to Reproduce**:
  1. An employee creates a decision.
  2. An approval is assigned to a Reviewer.
  3. The Reviewer attempts `GET /decisions/{id}` or `GET /decisions/{id}/detail` or `GET /decisions/{id}/comments`.
- **Expected Result**: The Reviewer can view decisions and discussion threads in their organization to evaluate them.
- **Actual Result**: `403 Forbidden - You do not have permission to view this decision`.
- **Severity**: High
- **Status**: Fixed
- **Fix**: Updated `can_access_decision` across `decisions.py`, `comments.py`, `threads.py`, and `meeting_notes.py` to include `UserRole.REVIEWER` while maintaining strict restrictions on `can_modify_decision` to creators, Managers, and Administrators.

---

### BUG-004
- **Module**: Approval Workflow & Version History
- **Description**: Completing an approval via `PATCH /approvals/{id}/status` updated the decision status to `Approved` or `Rejected` but did not snapshot a new `DecisionVersion`. Additionally, multi-level approvals were not handled (the first approval immediately approved the decision regardless of other pending approvals).
- **Steps to Reproduce**:
  1. Create a decision and assign 2 reviewers (multi-level).
  2. The first reviewer approves.
- **Expected Result**: Decision stays `Under Review` until all assigned reviewers approve. When final approval or rejection occurs, a new decision version snapshot is created.
- **Actual Result**: Decision was immediately marked `Approved` on first approval, and no version snapshot was generated.
- **Severity**: Medium
- **Status**: Fixed
- **Fix**: Updated `update_approval_status` in `app/routers/approvals.py` to count remaining pending approvals before marking `Approved`. Added `create_decision_version` call upon decision status transition.

---

### BUG-005
- **Module**: User Management & Authentication
- **Description**: Missing public user registration endpoint `POST /auth/register`. Only `POST /users` existed, which required an existing Administrator JWT token.
- **Steps to Reproduce**:
  1. Clean installation or public user onboarding.
  2. Attempt to register without an admin bearer token.
- **Expected Result**: `POST /auth/register` allows registering users with validation, password hashing, and returns `201 Created`.
- **Actual Result**: `401 Unauthorized` / `403 Forbidden` on `POST /users`.
- **Severity**: Medium
- **Status**: Fixed
- **Fix**: Implemented `POST /auth/register` in `app/routers/auth.py` accepting `UserCreate`, validating organization existence, duplicate email/employee ID, hashing passwords, logging security events, and returning `UserResponse`.

---

### BUG-006
- **Module**: Approval Workflow
- **Description**: In `create_approval`, any authenticated user could assign reviewers to any decision, and could assign users who do not have reviewer capabilities (e.g. regular employees).
- **Steps to Reproduce**:
  1. An employee calls `POST /approvals` on another user's decision.
  2. An employee assigns another employee as a reviewer.
- **Expected Result**: Only creator, manager, or admin can assign reviewers, and assigned reviewer must have `Reviewer`, `Manager`, or `Administrator` role.
- **Actual Result**: Unrestricted reviewer assignment was accepted.
- **Severity**: Medium
- **Status**: Fixed
- **Fix**: Added checks in `create_approval` verifying caller authorization (`decision.created_by == current_user.id or current_user.role in (UserRole.MANAGER, UserRole.ADMINISTRATOR)`) and reviewer role eligibility.

---

### BUG-007
- **Module**: Environment Configuration
- **Description**: Missing `.env.example` template file with placeholder values for deployment and developer setup.
- **Steps to Reproduce**: Inspect repository root for environment template.
- **Expected Result**: `.env.example` exists with non-sensitive placeholders.
- **Actual Result**: Only local `.env` existed.
- **Severity**: Low
- **Status**: Fixed
- **Fix**: Created `.env.example` with placeholders for database URL, JWT secret, algorithm, and token expiry.
