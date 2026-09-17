import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

function AssignedReviews() {
  const [approvals, setApprovals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const navigate = useNavigate();

  const loadApprovals = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await api.get("/approvals/pending");
      setApprovals(response.data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Failed to load assigned reviews"
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
          <h1>Assigned Reviews</h1>
          <p>
            Review decisions assigned to you for approval.
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
            Loading assigned reviews...
          </div>
        ) : approvals.length === 0 ? (
          <div className="empty-state">
            No pending reviews assigned to you.
          </div>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Approval ID</th>
                  <th>Decision ID</th>
                  <th>Status</th>
                  <th>Assigned Date</th>
                  <th>Action</th>
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
                      <span className="role-badge">
                        {approval.status}
                      </span>
                    </td>

                    <td>
                      {approval.created_at
                        ? new Date(
                            approval.created_at
                          ).toLocaleString()
                        : "—"}
                    </td>

                    <td>
                      <button
                        className="edit-btn"
                        onClick={() =>
                          navigate(
                            `/decisions/${approval.decision_id}`
                          )
                        }
                      >
                        Review
                      </button>
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

export default AssignedReviews;