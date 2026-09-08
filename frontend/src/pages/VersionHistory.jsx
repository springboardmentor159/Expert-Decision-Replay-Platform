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

  return (
    <div>
      <h1>Version History & Timeline</h1>

      <p>
        <strong>Decision ID:</strong> {id}
      </p>

      <hr />

      {loading && <p>Loading history...</p>}

      {error && <p>{error}</p>}

      {!loading && !error && history.length === 0 && (
        <p>No history found for this decision.</p>
      )}

      {!loading && !error && history.length > 0 && (
        <>
          <h2>Decision Timeline</h2>

          <table border="1" cellPadding="10">
            <thead>
              <tr>
                <th>ID</th>
                <th>Action</th>
                <th>Entity</th>
                <th>Entity ID</th>
                <th>User ID</th>
                <th>Details</th>
                <th>Date</th>
              </tr>
            </thead>

            <tbody>
              {history.map((log) => (
                <tr key={log.id}>
                  <td>{log.id}</td>
                  <td>{log.action || "-"}</td>
                  <td>{log.entity_type || "-"}</td>
                  <td>{log.entity_id || "-"}</td>
                  <td>{log.user_id || "-"}</td>
                  <td>
                    {log.details
                      ? typeof log.details === "object"
                        ? JSON.stringify(log.details)
                        : log.details
                      : "-"}
                  </td>
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

      <button
        onClick={() => navigate(`/decisions/${id}`)}
      >
        Back to Decision
      </button>
    </div>
  );
}

export default VersionHistory;