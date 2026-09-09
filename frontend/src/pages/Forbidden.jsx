import { Link } from "react-router-dom";

export default function Forbidden() {
  return (
    <div className="state-block error-state">
      <p className="empty-title">403 — Access denied</p>
      <p>You do not have permission to view this page.</p>
      <Link className="btn btn-secondary btn-sm" to="/dashboard">
        Back to dashboard
      </Link>
    </div>
  );
}
