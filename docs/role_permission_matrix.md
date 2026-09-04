# Role Permission Matrix

This document defines the Role-Based Access Control (RBAC) matrix for the **Expert Decision Replay Platform** as verified in Sprint 13.

## Permission Matrix

| Feature / Action | Employee | Reviewer | Manager | Administrator |
|---|---|---|---|---|
| **Create Decision** | ✓ | According to rules | According to rules | ✓ |
| **Review Decision** | - | ✓ | ✓ | ✓ |
| **Approve / Reject** | - | ✓ | ✓ | ✓ |
| **Audit Logs (System-wide)** | Restricted (403) | Restricted (403) | Restricted (403) | ✓ |
| **User Management** | - (403) | - (403) | Restricted (Org users only) | ✓ (All users) |
| **Organization Reports** | Restricted (403) | Restricted (403) | Restricted (403) | ✓ |

---

## Detailed Role Responsibilities

### 1. Employee
- **Decisions**: Can create decisions within their organization. Can view, update, add alternatives to, and submit their own decisions.
- **Discussions**: Can view discussions and add comments/threads on their own decisions.
- **Approvals**: Cannot perform approval/rejection actions. Cannot be assigned as a reviewer.
- **Dashboards**: Access to personal `/dashboard/employee` (my decisions, pending reviews, recent activities).
- **Restrictions**: Cannot access `/audit-logs`, `/security-logs`, `/access-logs`, system analytics, or admin dashboard.

### 2. Reviewer
- **Decisions**: Can view decisions in their organization that are assigned for review or under review.
- **Discussions**: Can view discussion threads, comments, and meeting notes, and contribute feedback.
- **Approvals**: Can view assigned reviews (`/approvals/my`) and perform approval or rejection (`PATCH /approvals/{id}/status`).
- **Restrictions**: Cannot arbitrarily edit decision title, problem statement, or alternatives created by others. Cannot access organization audit logs or system admin dashboard.

### 3. Manager
- **Decisions**: Can view all decisions within their organization. Can modify decisions when necessary.
- **Approvals**: Can assign reviewers, view team approvals, and approve/reject decision approvals.
- **Users**: Can view profiles of users within their own organization.
- **Dashboards**: Access to `/dashboard/manager` (team decisions, pending approvals, team statistics).
- **Reports**: Access to decision, approval, and their department team reports. Restricted from organization-wide audit logs.

### 4. Administrator
- **Decisions**: Unrestricted access across the organization to view, modify, and manage decisions.
- **User Management**: Full CRUD access (`POST /users`, `GET /users`, `PUT /users/{id}`, `DELETE /users/{id}`) across all organizations.
- **Audit & Compliance**: Exclusive access to `/audit-logs`, `/security-logs`, `/access-logs`, and audit reports.
- **Dashboards & Analytics**: Access to `/dashboard/admin`, system analytics, and organization-level reports.
