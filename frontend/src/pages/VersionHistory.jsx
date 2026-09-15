import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../services/api";

function VersionHistory() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchHistory = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await api.get("/audit-logs/");

      const decisionHistory = response.data.filter(
        (log) =>
          Number(log.entity_id) === Number(id) ||
          Number(log.decision_id) === Number(id)
      );

      setHistory(decisionHistory);
    } catch (err) {
      console.error("Version history error:", err);

      if (err.response?.data?.detail) {
        setError(
          typeof err.response.data.detail === "string"
            ? err.response.data.detail
            : "Unable to load version history."
        );
      } else {
        setError("Unable to load version history.");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [id]);

  const getActionClass = (action) => {
    const value = String(action || "").toLowerCase();

    if (value.includes("create")) return "history-create";
    if (value.includes("update") || value.includes("edit")) {
      return "history-update";
    }
    if (value.includes("delete")) return "history-delete";
    if (value.includes("approve")) return "history-approve";

    return "history-default";
  };

  const getActionIcon = (action) => {
    const value = String(action || "").toLowerCase();

    if (value.includes("create")) return "+";
    if (value.includes("update") || value.includes("edit")) return "✎";
    if (value.includes("delete")) return "×";
    if (value.includes("approve")) return "✓";

    return "•";
  };

  return (
    <div className="history-page">

      {/* Header */}
      <div className="history-page-header">

        <div>
          <div className="page-breadcrumb">
            Decisions / Version History
          </div>

          <h1>Version History</h1>

          <p>
            Track changes and activities performed on Decision #{id}.
          </p>
        </div>

        <div className="history-header-actions">

          <div className="decision-id-badge">
            Decision #{id}
          </div>

          <button
            className="secondary-page-button"
            onClick={() => navigate(`/decisions/${id}`)}
          >
            ← Decision Details
          </button>

        </div>

      </div>

      {/* Summary */}
      <div className="history-summary">

        <div className="history-summary-card">

          <div className="history-summary-icon">
            ◷
          </div>

          <div>
            <span>Total Activities</span>
            <strong>{history.length}</strong>
          </div>

        </div>

        <div className="history-summary-card">

          <div className="history-summary-icon">
            ↻
          </div>

          <div>
            <span>Decision</span>
            <strong>#{id}</strong>
          </div>

        </div>

        <div className="history-summary-card">

          <div className="history-summary-icon">
            ✓
          </div>

          <div>
            <span>Tracking</span>
            <strong>Active</strong>
          </div>

        </div>

      </div>

      {/* Main History Card */}
      <div className="history-card">

        <div className="history-card-header">

          <div>
            <h2>Decision Timeline</h2>

            <p>
              A chronological record of changes and activities.
            </p>
          </div>

          <span className="history-count-badge">
            {history.length}{" "}
            {history.length === 1 ? "Activity" : "Activities"}
          </span>

        </div>

        {loading && (
          <div className="page-loading">
            <div className="loading-spinner"></div>
            <p>Loading decision history...</p>
          </div>
        )}

        {!loading && error && (
          <div className="history-error">

            <div className="history-error-icon">
              !
            </div>

            <h3>Unable to Load History</h3>

            <p>{error}</p>

          </div>
        )}

        {!loading && !error && history.length === 0 && (
          <div className="history-empty">

            <div className="history-empty-icon">
              ◷
            </div>

            <h3>No History Found</h3>

            <p>
              There are no recorded activities for this decision yet.
            </p>

          </div>
        )}

        {!loading && !error && history.length > 0 && (
          <div className="history-timeline">

            {history.map((log, index) => {

              const actionClass = getActionClass(log.action);

              return (
                <div className="history-item" key={log.id}>

                  <div className="history-marker-column">

                    <div
                      className={`history-marker ${actionClass}`}
                    >
                      {getActionIcon(log.action)}
                    </div>

                    {index < history.length - 1 && (
                      <div className="history-line"></div>
                    )}

                  </div>

                  <div className="history-content">

                    <div className="history-item-header">

                      <div>

                        <h3>
                          {log.action || "Activity"}
                        </h3>

                        <div className="history-meta">

                          <span>
                            User #{log.user_id || "—"}
                          </span>

                          <span>•</span>

                          <span>
                            {log.created_at
                              ? new Date(
                                  log.created_at
                                ).toLocaleString()
                              : "Date unavailable"}
                          </span>

                        </div>

                      </div>

                      <span className="history-log-id">
                        Log #{log.id}
                      </span>

                    </div>

                    <div className="history-details-grid">

                      <div className="history-detail">

                        <span>Entity</span>

                        <strong>
                          {log.entity_type || "—"}
                        </strong>

                      </div>

                      <div className="history-detail">

                        <span>Entity ID</span>

                        <strong>
                          {log.entity_id || "—"}
                        </strong>

                      </div>

                      <div className="history-detail">

                        <span>User ID</span>

                        <strong>
                          {log.user_id || "—"}
                        </strong>

                      </div>

                    </div>

                    <div className="history-change-box">

                      <span>Activity Details</span>

                      <p>
                        {log.details
                          ? typeof log.details === "object"
                            ? JSON.stringify(log.details)
                            : log.details
                          : "No additional details available."}
                      </p>

                    </div>

                  </div>

                </div>
              );
            })}

          </div>
        )}

      </div>

      {/* Bottom Navigation */}
      <div className="history-bottom-actions">

        <button
          className="secondary-page-button"
          onClick={() =>
            navigate(`/decisions/${id}/approvals`)
          }
        >
          ← Approval Workflow
        </button>

        <button
          className="primary-submit-button"
          onClick={() => navigate(`/decisions/${id}`)}
        >
          Decision Details
        </button>

      </div>

    </div>
  );
}

export default VersionHistory;