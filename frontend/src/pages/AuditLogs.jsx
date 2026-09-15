import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

function AuditLogs() {
  const navigate = useNavigate();

  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [searchText, setSearchText] = useState("");
  const [actionFilter, setActionFilter] = useState("");

  const fetchAuditLogs = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await api.get("/audit-logs/");

      setLogs(response.data);
    } catch (err) {
      console.error("Audit logs error:", err);

      if (err.response?.data?.detail) {
        setError(
          typeof err.response.data.detail === "string"
            ? err.response.data.detail
            : "Unable to load audit logs."
        );
      } else {
        setError("Unable to load audit logs.");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAuditLogs();
  }, []);

  const actionOptions = useMemo(() => {
    const actions = logs
      .map((log) => log.action)
      .filter(Boolean);

    return [...new Set(actions)];
  }, [logs]);

  const filteredLogs = useMemo(() => {
    const search = searchText.trim().toLowerCase();

    return logs.filter((log) => {
      const matchesSearch =
        !search ||
        String(log.id || "").toLowerCase().includes(search) ||
        String(log.action || "").toLowerCase().includes(search) ||
        String(log.entity_type || "").toLowerCase().includes(search) ||
        String(log.entity_id || "").toLowerCase().includes(search) ||
        String(log.user_id || "").toLowerCase().includes(search);

      const matchesAction =
        !actionFilter || log.action === actionFilter;

      return matchesSearch && matchesAction;
    });
  }, [logs, searchText, actionFilter]);

  const getActionClass = (action) => {
    const value = String(action || "").toLowerCase();

    if (value.includes("create")) return "audit-create";
    if (value.includes("update") || value.includes("edit")) {
      return "audit-update";
    }
    if (value.includes("delete")) return "audit-delete";
    if (value.includes("approve")) return "audit-approve";

    return "audit-default";
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
    <div className="audit-page">

      {/* Header */}
      <div className="audit-header">

        <div>
          <div className="page-breadcrumb">
            Administration / Audit Logs
          </div>

          <h1>Audit & Activity Logs</h1>

          <p>
            Monitor activities and changes recorded across the platform.
          </p>
        </div>

        <div className="audit-header-actions">

          <button
            className="audit-refresh-button"
            onClick={fetchAuditLogs}
            disabled={loading}
          >
            ↻ {loading ? "Refreshing..." : "Refresh"}
          </button>

          <button
            className="secondary-page-button"
            onClick={() => navigate("/dashboard")}
          >
            ← Dashboard
          </button>

        </div>

      </div>

      {/* Summary */}
      <div className="audit-summary">

        <div className="audit-summary-card">
          <div className="audit-summary-icon">◉</div>

          <div>
            <span>Total Activities</span>
            <strong>{logs.length}</strong>
          </div>
        </div>

        <div className="audit-summary-card">
          <div className="audit-summary-icon">⌕</div>

          <div>
            <span>Showing</span>
            <strong>{filteredLogs.length}</strong>
          </div>
        </div>

        <div className="audit-summary-card">
          <div className="audit-summary-icon">✓</div>

          <div>
            <span>Audit Tracking</span>
            <strong>Active</strong>
          </div>
        </div>

      </div>

      {/* Filters */}
      <div className="audit-filter-card">

        <div className="audit-filter-heading">

          <div>
            <h2>Activity Search</h2>

            <p>
              Search logs by action, entity or user.
            </p>
          </div>

          <span className="audit-count">
            {filteredLogs.length} Results
          </span>

        </div>

        <div className="audit-filters">

          <div className="audit-search">

            <span>⌕</span>

            <input
              type="text"
              value={searchText}
              onChange={(e) =>
                setSearchText(e.target.value)
              }
              placeholder="Search audit logs..."
            />

          </div>

          <select
            value={actionFilter}
            onChange={(e) =>
              setActionFilter(e.target.value)
            }
          >
            <option value="">All Actions</option>

            {actionOptions.map((action) => (
              <option key={action} value={action}>
                {action}
              </option>
            ))}

          </select>

          <button
            className="audit-clear-button"
            onClick={() => {
              setSearchText("");
              setActionFilter("");
            }}
          >
            Clear
          </button>

        </div>

      </div>

      {/* Activity History */}
      <div className="audit-results-card">

        <div className="audit-results-header">

          <div>
            <h2>Activity History</h2>

            <p>
              Recorded system activities and decision changes.
            </p>
          </div>

          <div className="audit-secure-label">
            ● Audit Tracking
          </div>

        </div>

        {loading && (
          <div className="audit-loading">
            <div className="loading-spinner"></div>
            <p>Loading audit activities...</p>
          </div>
        )}

        {!loading && error && (
          <div className="audit-error">

            <div className="audit-error-icon">!</div>

            <h3>Unable to Load Audit Logs</h3>

            <p>{error}</p>

            <button
              className="audit-retry-button"
              onClick={fetchAuditLogs}
            >
              Try Again
            </button>

          </div>
        )}

        {!loading &&
          !error &&
          filteredLogs.length === 0 && (
            <div className="audit-empty">

              <div className="audit-empty-icon">
                ◉
              </div>

              <h3>No Audit Activities Found</h3>

              <p>
                No activities match the current search or filter.
              </p>

            </div>
          )}

        {!loading &&
          !error &&
          filteredLogs.length > 0 && (

            <div className="audit-table-wrapper">

              <table className="audit-table">

                <thead>
                  <tr>
                    <th>Activity</th>
                    <th>Entity</th>
                    <th>Entity ID</th>
                    <th>User</th>
                    <th>Date & Time</th>
                  </tr>
                </thead>

                <tbody>

                  {filteredLogs.map((log) => (

                    <tr key={log.id}>

                      <td>

                        <div className="audit-action-cell">

                          <div
                            className={`audit-action-icon ${getActionClass(
                              log.action
                            )}`}
                          >
                            {getActionIcon(log.action)}
                          </div>

                          <div>
                            <strong>
                              {log.action || "Activity"}
                            </strong>

                            <span>
                              Log #{log.id}
                            </span>
                          </div>

                        </div>

                      </td>

                      <td>
                        <span className="audit-entity">
                          {log.entity_type || "—"}
                        </span>
                      </td>

                      <td>
                        <span className="audit-id">
                          {log.entity_id || "—"}
                        </span>
                      </td>

                      <td>
                        <span className="audit-user">
                          User #{log.user_id || "—"}
                        </span>
                      </td>

                      <td>
                        <span className="audit-date">
                          {log.created_at
                            ? new Date(
                                log.created_at
                              ).toLocaleString()
                            : "—"}
                        </span>
                      </td>

                    </tr>

                  ))}

                </tbody>

              </table>

            </div>

          )}

      </div>

    </div>
  );
}

export default AuditLogs;