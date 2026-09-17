import { useEffect, useState } from "react";
import api from "../services/api";

function AuditLogs() {
  const [logs, setLogs] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadLogs = async () => {
    try {
      setLoading(true);
      setError("");

      // Use your existing activity endpoint
      const response = await api.get("/activities");
      setLogs(response.data);
    } catch (err) {
      setError(
        err.response?.data?.detail || "Failed to load audit logs"
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLogs();
  }, []);

  const filteredLogs = logs.filter((log) => {
    const text = search.toLowerCase();

    return (
      log.action?.toLowerCase().includes(text) ||
      log.description?.toLowerCase().includes(text) ||
      String(log.user_id || "").includes(text)
    );
  });

  return (
    <div className="page-container">

      <div className="page-header">
        <div>
          <h1>Audit Logs</h1>
          <p>
            Monitor user activities and system actions across the platform.
          </p>
        </div>

        <button className="primary-btn" onClick={loadLogs}>
          Refresh
        </button>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="filter-bar">
        <input
          type="text"
          placeholder="Search audit logs..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      <div className="table-card">

        {loading ? (
          <div className="loading-state">
            Loading audit logs...
          </div>
        ) : filteredLogs.length === 0 ? (
          <div className="empty-state">
            No audit logs found.
          </div>
        ) : (
          <div className="table-wrapper">

            <table>
              <thead>
                <tr>
                  <th>User ID</th>
                  <th>Action</th>
                  <th>Description</th>
                  <th>Date & Time</th>
                </tr>
              </thead>

              <tbody>
                {filteredLogs.map((log) => (
                  <tr key={log.id}>

                    <td>
                      #{log.user_id ?? "—"}
                    </td>

                    <td>
                      <span className="role-badge">
                        {log.action || "Activity"}
                      </span>
                    </td>

                    <td>
                      {log.description || "No description"}
                    </td>

                    <td>
                      {log.created_at
                        ? new Date(log.created_at).toLocaleString()
                        : "—"}
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