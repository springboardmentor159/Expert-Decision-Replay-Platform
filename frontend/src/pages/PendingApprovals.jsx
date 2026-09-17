import { useEffect, useState } from "react";
import api from "../services/api";

function PendingApprovals() {
  const [approvals, setApprovals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadApprovals = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await api.get("/approvals/pending");

      const data = Array.isArray(response.data)
        ? response.data
        : response.data.data || [];

      setApprovals(data);
    } catch (err) {
      console.error("Pending approvals error:", err);

      setError(
        err.response?.data?.detail ||
          "Failed to load pending approvals."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadApprovals();
  }, []);

  return (
    <div className="page-container">

      <div className="page-header">
        <div>
          <h1>Pending Approvals</h1>
          <p>
            Review decisions currently waiting for approval.
          </p>
        </div>

        <button
          className="primary-btn"
          onClick={loadApprovals}
        >
          Refresh
        </button>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="table-card">

        {loading ? (
          <div className="loading-state">
            Loading pending approvals...
          </div>
        ) : approvals.length === 0 ? (
          <div className="empty-state">
            <h3>No Pending Approvals</h3>
            <p>
              There are currently no decisions waiting for approval.
            </p>
          </div>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Approval ID</th>
                  <th>Decision ID</th>
                  <th>Reviewer ID</th>
                  <th>Status</th>
                  <th>Created</th>
                </tr>
              </thead>

              <tbody>
                {approvals.map((approval) => (
                  <tr key={approval.id}>
                    <td>#{approval.id}</td>

                    <td>
                      Decision #{approval.decision_id}
                    </td>

                    <td>
                      User #{approval.reviewer_id}
                    </td>

                    <td>
                      <span className="role-badge">
                        {approval.status || "Pending"}
                      </span>
                    </td>

                    <td>
                      {approval.created_at
                        ? new Date(
                            approval.created_at
                          ).toLocaleString()
                        : "N/A"}
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

export default PendingApprovals;