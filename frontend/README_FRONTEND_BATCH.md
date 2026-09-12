# Expert Decision Replay Platform - Frontend Batch

Replace the existing `frontend/src` folder with this `src` folder.
Keep your existing `package.json`, `package-lock.json`, `node_modules`, `public`, and `vite.config.js`.

Also copy `.env.example` to `frontend/.env.example` if it is not already there.

This batch uses the existing Axios and React Router dependencies and connects to the existing FastAPI API.

Covered UI:
- JWT login/register
- Employee, Reviewer, Manager, Administrator role-based navigation
- Employee/Reviewer/Manager/Admin dashboards
- Decisions create/list/edit/status/details
- Decision information, rationale, tags
- Alternatives and comparison
- Comments
- Meeting notes
- Approvals
- Versions and decision history/timeline
- Repository/search/filter
- Activities
- Admin users
- Admin analytics
- Audit logs
- Reports and PDF/Excel download
- Loading, empty, validation and HTTP error states


## Self-check notes
- Approval actions use `approval_id` when the manager dashboard endpoint returns `approval_id` instead of `id`.
- Approval actions refresh the current page data instead of forcing a full browser reload.
- Alternative and meeting-note forms validate required values before sending requests.
- The frontend uses the existing backend API exactly where those endpoints exist. The current backend does not expose a separate knowledge-repository endpoint or a create-discussion-thread endpoint, so repository search is implemented over the decisions list and discussion is implemented with the available comments API.
- The current backend approval PATCH changes the approval record; it does not automatically change the decision status. The decision status therefore remains explicitly controllable through the existing decision-status endpoint.
- JWT is stored in `localStorage` because the current backend exposes a bearer-token API. For stronger XSS protection, the backend would need an HttpOnly cookie-based authentication design.

- Navigation also treats both `Admin` and `Administrator` JWT role values consistently.
