import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

function ReviewActions() {
  const [approvals, setApprovals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [processingId, setProcessingId] = useState(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

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
          "Failed to load review actions"
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadApprovals();
  }, []);

  const handleApprove = async (approvalId) => {
    const confirmed = window.confirm(
      "Are you sure you want to approve this decision?"
    );

    if (!confirmed) return;

    try {
      setProcessingId(approvalId);
      setError("");
      setSuccess("");

      await api.patch(
        `/approvals/${approvalId}/approve`
      );

      setSuccess("Decision approved successfully.");

      await loadApprovals();
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Failed to approve decision"
      );
    } finally {
      setProcessingId(null);
    }
  };

  const handleReject = async (approvalId) => {
    const confirmed = window.confirm(
      "Are you sure you want to reject this decision?"
    );

    if (!confirmed) return;

    try {
      setProcessingId(approvalId);
      setError("");
      setSuccess("");

      await api.patch(
        `/approvals/${approvalId}/reject`
      );

      setSuccess("Decision rejected successfully.");

      await loadApprovals();
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Failed to reject decision"
      );
    } finally {
      setProcessingId(null);
    }
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1>Review Actions</h1>
          <p>
            Review pending decisions and take approval actions.
          </p>
        </div>

        <button
          className="primary-btn"
          onClick={loadApprovals}
          disabled={loading}
        >
          Refresh
        </button>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {success && (
        <div className="success-message">
          {success}
        </div>
      )}

      <div className="table-card">
        {loading ? (
          <div className="loading-state">
            Loading review actions...
          </div>
        ) : approvals.length === 0 ? (
          <div className="empty-state">
            <h3>No Pending Reviews</h3>
            <p>
              There are currently no decisions waiting for your review.
            </p>
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
                  <th>Decision</th>
                  <th>Actions</th>
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
                        View
                      </button>
                    </td>

                    <td>
                      <button
                        className="primary-btn"
                        onClick={() =>
                          handleApprove(approval.id)
                        }
                        disabled={
                          processingId === approval.id
                        }
                      >
                        {processingId === approval.id
                          ? "Processing..."
                          : "Approve"}
                      </button>

                      <button
                        className="delete-btn"
                        onClick={() =>
                          handleReject(approval.id)
                        }
                        disabled={
                          processingId === approval.id
                        }
                      >
                        Reject
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

export default ReviewActions;