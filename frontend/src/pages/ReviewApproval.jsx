import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import apiClient from "../api/apiClient";
import { useAuth } from "../auth/AuthContext";

import {
  getApproval,
  approveApproval,
  rejectApproval,
  getApprovalErrorMessage,
} from "../api/approvalApi";

const formatDate = (value) => {
  if (!value) return "—";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString();
};

const getStatusClass = (status) => {
  switch (status) {
    case "Pending":
      return "status-badge status-pending";

    case "Approved":
      return "status-badge status-approved";

    case "Rejected":
      return "status-badge status-rejected";

    default:
      return "status-badge";
  }
};

const getErrorMessage = (error) => {
  const status = error?.response?.status;
  const detail = error?.response?.data?.detail;

  if (status === 400) {
    return detail || "This approval has already been reviewed.";
  }

  if (status === 401) {
    return "Your session has expired. Please log in again.";
  }

  if (status === 403) {
    return (
      detail ||
      "You are not authorized to perform this review."
    );
  }

  if (status === 404) {
    return detail || "Approval not found.";
  }

  if (status === 422) {
    return detail || "The review information is invalid.";
  }

  if (status >= 500) {
    return "A server error occurred. Please try again later.";
  }

  return (
    detail ||
    error?.message ||
    "Something went wrong while processing the review."
  );
};

export default function ReviewApproval() {
  const { approvalId } = useParams();
  const navigate = useNavigate();

  const { user } = useAuth();

  const [approval, setApproval] = useState(null);
  const [decision, setDecision] = useState(null);

  const [comments, setComments] = useState("");

  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);

  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  /*
   * Determine where the user should return after
   * completing or cancelling the approval review.
   *
   * Reviewer:
   *   /approvals
   *
   * Manager:
   *   /manager/pending-approvals
   */
  const getApprovalQueuePath = () => {
    if (user?.role === "Manager") {
      return "/manager/pending-approvals";
    }

    return "/approvals";
  };

  const getApprovalQueueLabel = () => {
    if (user?.role === "Manager") {
      return "Pending Approvals";
    }

    return "Assigned Reviews";
  };

  const loadApproval = async () => {
    try {
      setLoading(true);
      setErrorMessage("");

      const approvalData = await getApproval(approvalId);

      setApproval(approvalData);

      /*
       * Load the related decision so the Reviewer or Manager
       * can understand what they are reviewing.
       */
      try {
        const decisionResponse = await apiClient.get(
          `/decisions/${approvalData.decision_id}`
        );

        setDecision(
          decisionResponse?.data?.decision ||
            decisionResponse?.data
        );
      } catch (decisionError) {
        /*
         * The approval itself can still be displayed even
         * if the related decision cannot be loaded.
         */
        console.warn(
          "Unable to load related decision:",
          decisionError
        );
      }

      /*
       * If the approval already contains comments,
       * display them in the review field.
       */
      setComments(approvalData.comments || "");
    } catch (error) {
      console.error(
        "Failed to load approval:",
        error
      );

      setErrorMessage(
        getApprovalErrorMessage(error) ||
          getErrorMessage(error)
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadApproval();
  }, [approvalId]);

  const handleApprove = async () => {
    const confirmed = window.confirm(
      "Are you sure you want to approve this decision?"
    );

    if (!confirmed) {
      return;
    }

    try {
      setProcessing(true);
      setErrorMessage("");
      setSuccessMessage("");

      const response = await approveApproval(
        approvalId,
        comments
      );

      setSuccessMessage(
        response?.message ||
          "Approval completed successfully."
      );

      if (response?.approval) {
        setApproval(response.approval);
      }

      /*
       * Return to the correct approval queue based on
       * the logged-in user's role.
       */
      setTimeout(() => {
        navigate(getApprovalQueuePath());
      }, 1000);
    } catch (error) {
      console.error(
        "Failed to approve:",
        error
      );

      setErrorMessage(
        getApprovalErrorMessage(error) ||
          getErrorMessage(error)
      );
    } finally {
      setProcessing(false);
    }
  };

  const handleReject = async () => {
    const trimmedComments = comments.trim();

    if (!trimmedComments) {
      setErrorMessage(
        "Please provide a reason or review comment before rejecting the decision."
      );

      return;
    }

    const confirmed = window.confirm(
      "Are you sure you want to reject this decision?"
    );

    if (!confirmed) {
      return;
    }

    try {
      setProcessing(true);
      setErrorMessage("");
      setSuccessMessage("");

      const response = await rejectApproval(
        approvalId,
        comments
      );

      setSuccessMessage(
        response?.message ||
          "Decision rejected successfully."
      );

      if (response?.approval) {
        setApproval(response.approval);
      }

      setTimeout(() => {
        navigate(getApprovalQueuePath());
      }, 1000);
    } catch (error) {
      console.error(
        "Failed to reject:",
        error
      );

      setErrorMessage(
        getApprovalErrorMessage(error) ||
          getErrorMessage(error)
      );
    } finally {
      setProcessing(false);
    }
  };

  if (loading) {
    return (
      <div className="dashboard-page">
        <div className="loading-state">
          Loading approval details...
        </div>
      </div>
    );
  }

  if (!approval) {
    return (
      <div className="dashboard-page">
        <div className="error-message">
          {errorMessage || "Approval not found."}
        </div>

        <Link
          to={getApprovalQueuePath()}
          className="secondary-button"
        >
          Back to {getApprovalQueueLabel()}
        </Link>
      </div>
    );
  }

  const isPending =
    approval.status === "Pending";

  return (
    <div className="dashboard-page">
      <div className="page-header">
        <div>
          <h1>Review Approval</h1>

          <p className="page-subtitle">
            Review the decision and complete the
            assigned approval action.
          </p>
        </div>

        <Link
          to={getApprovalQueuePath()}
          className="secondary-button"
        >
          ← {getApprovalQueueLabel()}
        </Link>
      </div>

      {errorMessage && (
        <div className="error-message">
          {errorMessage}
        </div>
      )}

      {successMessage && (
        <div className="success-message">
          {successMessage}
        </div>
      )}

      <div className="dashboard-grid">
        <div className="content-card">
          <div className="section-header">
            <div>
              <h2>Approval Information</h2>

              <p>
                Details of the current approval request.
              </p>
            </div>

            <span
              className={getStatusClass(
                approval.status
              )}
            >
              {approval.status || "Unknown"}
            </span>
          </div>

          <div className="details-grid">
            <div className="detail-item">
              <span className="detail-label">
                Approval ID
              </span>

              <strong>
                #{approval.id}
              </strong>
            </div>

            <div className="detail-item">
              <span className="detail-label">
                Decision ID
              </span>

              <strong>
                #{approval.decision_id}
              </strong>
            </div>

            <div className="detail-item">
              <span className="detail-label">
                Assigned Role
              </span>

              <strong>
                {approval.assigned_role || "—"}
              </strong>
            </div>

            <div className="detail-item">
              <span className="detail-label">
                Assigned User
              </span>

              <strong>
                User #{approval.assigned_to}
              </strong>
            </div>

            <div className="detail-item">
              <span className="detail-label">
                Assigned By
              </span>

              <strong>
                User #{approval.assigned_by}
              </strong>
            </div>

            <div className="detail-item">
              <span className="detail-label">
                Assigned At
              </span>

              <strong>
                {formatDate(
                  approval.assigned_at
                )}
              </strong>
            </div>

            <div className="detail-item">
              <span className="detail-label">
                Reviewed At
              </span>

              <strong>
                {formatDate(
                  approval.reviewed_at
                )}
              </strong>
            </div>
          </div>
        </div>

        <div className="content-card">
          <div className="section-header">
            <div>
              <h2>Decision</h2>

              <p>
                Information related to the decision
                being reviewed.
              </p>
            </div>
          </div>

          {decision ? (
            <div>
              <h3>
                {decision.title ||
                  `Decision #${approval.decision_id}`}
              </h3>

              {decision.category && (
                <p>
                  <strong>Category:</strong>{" "}
                  {decision.category}
                </p>
              )}

              {decision.status && (
                <p>
                  <strong>Status:</strong>{" "}
                  {typeof decision.status === "string"
                    ? decision.status
                    : decision.status?.value}
                </p>
              )}

              {decision.problem_statement && (
                <div className="decision-description">
                  <h4>
                    Problem Statement
                  </h4>

                  <p>
                    {decision.problem_statement}
                  </p>
                </div>
              )}

              <Link
                to={`/decisions/${approval.decision_id}`}
                className="secondary-button"
              >
                View Full Decision
              </Link>
            </div>
          ) : (
            <div className="empty-state">
              <p>
                Decision information could not be
                loaded.
              </p>

              <Link
                to={`/decisions/${approval.decision_id}`}
                className="secondary-button"
              >
                Open Decision
              </Link>
            </div>
          )}
        </div>
      </div>

      <div className="content-card">
        <div className="section-header">
          <div>
            <h2>Review Comments</h2>

            <p>
              Add comments explaining your review
              decision.
            </p>
          </div>
        </div>

        {approval.comments &&
          !isPending && (
            <div className="existing-comment">
              <strong>
                Previous Review Comment
              </strong>

              <p>
                {approval.comments}
              </p>
            </div>
          )}

        <textarea
          className="form-textarea"
          rows="6"
          value={comments}
          onChange={(event) =>
            setComments(event.target.value)
          }
          placeholder={
            isPending
              ? "Enter your review comments..."
              : "This approval has already been reviewed."
          }
          disabled={
            !isPending || processing
          }
        />

        {isPending ? (
          <div
            style={{
              display: "flex",
              gap: "12px",
              marginTop: "20px",
              flexWrap: "wrap",
            }}
          >
            <button
              type="button"
              className="primary-button"
              onClick={handleApprove}
              disabled={processing}
            >
              {processing
                ? "Processing..."
                : "✓ Approve Decision"}
            </button>

            <button
              type="button"
              className="danger-button"
              onClick={handleReject}
              disabled={processing}
            >
              {processing
                ? "Processing..."
                : "✕ Reject Decision"}
            </button>

            <Link
              to={getApprovalQueuePath()}
              className="secondary-button"
            >
              Cancel
            </Link>
          </div>
        ) : (
          <div className="review-completed">
            <strong>
              This approval has already been reviewed.
            </strong>

            <p>
              Current status:{" "}
              <span
                className={getStatusClass(
                  approval.status
                )}
              >
                {approval.status}
              </span>
            </p>

            <Link
              to={getApprovalQueuePath()}
              className="secondary-button"
            >
              Back to {getApprovalQueueLabel()}
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}