import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

function AuditLogs() {
  const navigate = useNavigate();

  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

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

  return (
    <div>
      <h1>Audit & Activity Logs</h1>

      <p>
        View the activities and changes recorded in the system.
      </p>

      <hr />

      {loading && <p>Loading audit logs...</p>}

      {error && <p>{error}</p>}

      {!loading && !error && logs.length === 0 && (
        <p>No audit activities found.</p>
      )}

      {!loading && !error && logs.length > 0 && (
        <>
          <h2>Activity History</h2>

          <table border="1" cellPadding="10">
            <thead>
              <tr>
                <th>ID</th>
                <th>Action</th>
                <th>Entity Type</th>
                <th>Entity ID</th>
                <th>User ID</th>
                <th>Date</th>
              </tr>
            </thead>

            <tbody>
              {logs.map((log) => (
                <tr key={log.id}>
                  <td>{log.id}</td>
                  <td>{log.action || "-"}</td>
                  <td>{log.entity_type || "-"}</td>
                  <td>{log.entity_id || "-"}</td>
                  <td>{log.user_id || "-"}</td>
                  <td>
                    {log.created_at
                      ? new Date(
                          log.created_at
                        ).toLocaleString()
                      : "-"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}

      <br />

      <button onClick={fetchAuditLogs}>
        Refresh
      </button>

      <button
        onClick={() => navigate("/dashboard")}
        style={{ marginLeft: "10px" }}
      >
        Back to Dashboard
      </button>
    </div>
  );
}

export default AuditLogs;