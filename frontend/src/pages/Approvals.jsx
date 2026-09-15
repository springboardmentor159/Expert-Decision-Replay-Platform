import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../services/api";

function Approvals() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [approvals, setApprovals] = useState([]);

  const [reviewerId, setReviewerId] = useState("");
  const [approvalLevel, setApprovalLevel] = useState("");

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const fetchApprovals = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await api.get("/approvals/");

      const decisionApprovals = response.data.filter(
        (approval) => approval.decision_id === Number(id)
      );

      setApprovals(decisionApprovals);
    } catch (err) {
      console.error("Approvals error:", err);
      setError("Unable to load approvals.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApprovals();
  }, [id]);

  const handleCreateApproval = async (e) => {
    e.preventDefault();

    setError("");
    setMessage("");

    if (!reviewerId) {
      setError("Reviewer ID is required.");
      return;
    }

    if (!approvalLevel) {
      setError("Approval level is required.");
      return;
    }

    setSaving(true);

    try {
      const response = await api.post("/approvals/", {
        decision_id: Number(id),
        reviewer_id: Number(reviewerId),
        approval_level: Number(approvalLevel),
      });

      setApprovals((current) => [...current, response.data]);

      setReviewerId("");
      setApprovalLevel("");

      setMessage("Approval request created successfully.");
    } catch (err) {
      console.error("Create approval error:", err);

      if (err.response?.data?.detail) {
        setError(
          typeof err.response.data.detail === "string"
            ? err.response.data.detail
            : "Unable to create approval."
        );
      } else {
        setError("Unable to create approval.");
      }
    } finally {
      setSaving(false);
    }
  };

  const handleApprovalUpdate = async (approvalId, newStatus) => {
    setError("");
    setMessage("");

    try {
      const response = await api.put(`/approvals/${approvalId}`, {
        status: newStatus,
      });

      setApprovals((current) =>
        current.map((approval) =>
          approval.id === approvalId ? response.data : approval
        )
      );

      setMessage(
        `Decision ${newStatus.toLowerCase()} successfully.`
      );
    } catch (err) {
      console.error("Approval update error:", err);

      if (err.response?.data?.detail) {
        setError(
          typeof err.response.data.detail === "string"
            ? err.response.data.detail
            : "Unable to update approval."
        );
      } else {
        setError("Unable to update approval.");
      }
    }
  };

  const pendingCount = approvals.filter(
    (approval) => approval.status === "Pending"
  ).length;

  const approvedCount = approvals.filter(
    (approval) => approval.status === "Approved"
  ).length;

  const rejectedCount = approvals.filter(
    (approval) => approval.status === "Rejected"
  ).length;

  const getStatusClass = (status) => {
    if (status === "Approved") return "approved";
    if (status === "Rejected") return "rejected";
    return "pending";
  };

  return (
    <div className="approvals-page">

      {/* Header */}
      <div className="approvals-page-header">
        <div>
          <div className="page-breadcrumb">
            Decisions / Approval Workflow
          </div>

          <h1>Approval Workflow</h1>

          <p>
            Manage reviewers and track the approval progress for
            Decision #{id}.
          </p>
        </div>

        <div className="approval-header-actions">
          <span className="decision-id-badge">
            Decision #{id}
          </span>

          <button
            className="secondary-page-button"
            onClick={() => navigate(`/decisions/${id}`)}
          >
            ← Decision Details
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="approval-summary">

        <div className="approval-summary-card">
          <div className="approval-summary-icon">◉</div>

          <div>
            <span>Total Requests</span>
            <strong>{approvals.length}</strong>
          </div>
        </div>

        <div className="approval-summary-card">
          <div className="approval-summary-icon pending-icon">
            ⏳
          </div>

          <div>
            <span>Pending</span>
            <strong>{pendingCount}</strong>
          </div>
        </div>

        <div className="approval-summary-card">
          <div className="approval-summary-icon approved-icon">
            ✓
          </div>

          <div>
            <span>Approved</span>
            <strong>{approvedCount}</strong>
          </div>
        </div>

        <div className="approval-summary-card">
          <div className="approval-summary-icon rejected-icon">
            !
          </div>

          <div>
            <span>Rejected</span>
            <strong>{rejectedCount}</strong>
          </div>
        </div>

      </div>

      {/* Create Approval */}
      <div className="approval-create-card">

        <div className="approval-card-heading">
          <div className="approval-heading-icon">
            +
          </div>

          <div>
            <h2>Create Approval Request</h2>
            <p>
              Assign this decision to a reviewer for evaluation.
            </p>
          </div>
        </div>

        <form onSubmit={handleCreateApproval}>

          <div className="approval-form-grid">

            <div className="form-field">
              <label>Reviewer ID</label>

              <input
                type="number"
                min="1"
                value={reviewerId}
                onChange={(e) => setReviewerId(e.target.value)}
                placeholder="Enter reviewer user ID"
              />

              <small>
                Enter the user ID of the reviewer.
              </small>
            </div>

            <div className="form-field">
              <label>Approval Level</label>

              <select
                value={approvalLevel}
                onChange={(e) => setApprovalLevel(e.target.value)}
              >
                <option value="">
                  Select Approval Level
                </option>

                <option value="1">Level 1</option>
                <option value="2">Level 2</option>
                <option value="3">Level 3</option>
              </select>

              <small>
                Select the required approval stage.
              </small>
            </div>

            <div className="approval-submit-wrapper">
              <button
                type="submit"
                className="primary-submit-button"
                disabled={saving}
              >
                {saving
                  ? "Creating..."
                  : "Create Approval Request"}
              </button>
            </div>

          </div>

        </form>

      </div>

      {/* Messages */}
      {message && (
        <div className="success-message">
          <span>✓</span>
          {message}
        </div>
      )}

      {error && (
        <div className="error-message">
          <span>!</span>
          {error}
        </div>
      )}

      {/* Workflow */}
      <div className="approval-workflow-card">

        <div className="approval-list-header">
          <div>
            <h2>Approval Progress</h2>

            <p>
              Reviewers assigned to evaluate this decision.
            </p>
          </div>

          <span className="approval-count-badge">
            {approvals.length}{" "}
            {approvals.length === 1 ? "Request" : "Requests"}
          </span>
        </div>

        {loading ? (
          <div className="page-loading">
            <div className="loading-spinner"></div>
            <p>Loading approval workflow...</p>
          </div>
        ) : approvals.length === 0 ? (
          <div className="approval-empty">

            <div className="approval-empty-icon">
              ✓
            </div>

            <h3>No Approval Requests</h3>

            <p>
              Create an approval request above to start the
              review workflow for this decision.
            </p>

          </div>
        ) : (
          <div className="approval-list">

            {approvals.map((approval, index) => (
              <div className="approval-item" key={approval.id}>

                <div className="approval-step">

                  <div className="approval-step-number">
                    {index + 1}
                  </div>

                  {index < approvals.length - 1 && (
                    <div className="approval-step-line"></div>
                  )}

                </div>

                <div className="approval-details">

                  <div className="approval-item-top">

                    <div>
                      <h3>
                        Approval Level {approval.approval_level}
                      </h3>

                      <p>
                        Reviewer #{approval.reviewer_id}
                      </p>
                    </div>

                    <span
                      className={`approval-status ${getStatusClass(
                        approval.status
                      )}`}
                    >
                      {approval.status}
                    </span>

                  </div>

                  <div className="approval-info-grid">

                    <div>
                      <span>Approval ID</span>
                      <strong>#{approval.id}</strong>
                    </div>

                    <div>
                      <span>Reviewer</span>
                      <strong>
                        User #{approval.reviewer_id}
                      </strong>
                    </div>

                    <div>
                      <span>Assigned At</span>
                      <strong>
                        {approval.assigned_at
                          ? new Date(
                              approval.assigned_at
                            ).toLocaleString()
                          : "—"}
                      </strong>
                    </div>

                    <div>
                      <span>Completed At</span>
                      <strong>
                        {approval.completed_at
                          ? new Date(
                              approval.completed_at
                            ).toLocaleString()
                          : "Pending"}
                      </strong>
                    </div>

                  </div>

                  {approval.status === "Pending" && (
                    <div className="approval-actions">

                      <button
                        className="approve-button"
                        onClick={() =>
                          handleApprovalUpdate(
                            approval.id,
                            "Approved"
                          )
                        }
                      >
                        ✓ Approve
                      </button>

                      <button
                        className="reject-button"
                        onClick={() =>
                          handleApprovalUpdate(
                            approval.id,
                            "Rejected"
                          )
                        }
                      >
                        ✕ Reject
                      </button>

                    </div>
                  )}

                  {approval.status !== "Pending" && (
                    <div className="approval-completed-note">
                      {approval.status === "Approved"
                        ? "✓ This approval request has been approved."
                        : "✕ This approval request has been rejected."}
                    </div>
                  )}

                </div>

              </div>
            ))}

          </div>
        )}

      </div>

      {/* Bottom Navigation */}
      <div className="approval-bottom-actions">

        <button
          className="secondary-page-button"
          onClick={() =>
            navigate(`/decisions/${id}/comments`)
          }
        >
          ← Discussions
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

export default Approvals;