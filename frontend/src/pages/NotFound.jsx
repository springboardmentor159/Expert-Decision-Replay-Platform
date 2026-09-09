import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="state-block error-state">
      <p className="empty-title">404 — Page not found</p>
      <Link className="btn btn-secondary btn-sm" to="/dashboard">
        Back to dashboard
      </Link>
    </div>
  );
}
