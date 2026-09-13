import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import apiClient from "../api/apiClient";
import {
  getDecisionApprovals,
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
    return detail || "Invalid approval request.";
  }

  if (status === 401) {
    return "Your session has expired. Please log in again.";
  }

  if (status === 403) {
    return (
      detail ||
      "You do not have permission to view these approvals."
    );
  }

  if (status === 404) {
    return detail || "The requested resource was not found.";
  }

  if (status === 422) {
    return detail || "The request contains invalid information.";
  }

  if (status >= 500) {
    return "A server error occurred. Please try again later.";
  }

  return (
    detail ||
    error?.message ||
    "Unable to load assigned reviews."
  );
};

export default function AssignedReviews() {
  const [approvals, setApprovals] = useState([]);
  const [decisions, setDecisions] = useState([]);

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const [errorMessage, setErrorMessage] = useState("");

  const loadAssignedReviews = async () => {
    try {
      setErrorMessage("");
      setLoading(true);

      const decisionsResponse = await apiClient.get(
        "/decisions/",
        {
          params: {
            page: 1,
            page_size: 100,
          },
        }
      );

      const decisionItems =
        decisionsResponse?.data?.items ||
        decisionsResponse?.data?.decisions ||
        [];

      setDecisions(decisionItems);

      if (decisionItems.length === 0) {
        setApprovals([]);
        return;
      }

      const approvalResults = await Promise.allSettled(
        decisionItems.map((decision) =>
          getDecisionApprovals(decision.id)
        )
      );

      const allApprovals = [];

      approvalResults.forEach((result) => {
        if (result.status !== "fulfilled") {
          return;
        }

        const data = result.value;

        const decisionApprovals =
          data?.approvals || [];

        decisionApprovals.forEach((approval) => {
          allApprovals.push(approval);
        });
      });

      const uniqueApprovals = Array.from(
        new Map(
          allApprovals.map((approval) => [
            approval.id,
            approval,
          ])
        ).values()
      );

      setApprovals(uniqueApprovals);
    } catch (error) {
      setErrorMessage(
        getApprovalErrorMessage(error) ||
          getErrorMessage(error)
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadAssignedReviews();
  }, []);

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadAssignedReviews();
  };

  const getDecision = (decisionId) => {
    return decisions.find(
      (decision) => decision.id === decisionId
    );
  };

  const reviewerApprovals = approvals.filter(
    (approval) =>
      approval.assigned_role === "Reviewer"
  );

  const pendingApprovals =
    reviewerApprovals.filter(
      (approval) =>
        approval.status === "Pending"
    );

  const completedApprovals =
    reviewerApprovals.filter(
      (approval) =>
        approval.status === "Approved" ||
        approval.status === "Rejected"
    );

  return (
    <div className="page-container">

      <div className="page-header">

        <div>
          <h1>Assigned Reviews</h1>

          <p>
            Review decisions assigned to you and
            take the appropriate approval action.
          </p>
        </div>

        <button
          type="button"
          className="secondary-button"
          onClick={handleRefresh}
          disabled={refreshing}
        >
          {refreshing
            ? "Refreshing..."
            : "Refresh"}
        </button>

      </div>

      {errorMessage && (
        <div className="error-message">
          {errorMessage}
        </div>
      )}

      {loading ? (
        <div className="loading-state">
          Loading assigned reviews...
        </div>
      ) : (
        <>
          <div className="stats-grid">

            <div className="stat-card">
              <div className="stat-label">
                Assigned Reviews
              </div>

              <div className="stat-value">
                {reviewerApprovals.length}
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-label">
                Pending
              </div>

              <div className="stat-value">
                {pendingApprovals.length}
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-label">
                Completed
              </div>

              <div className="stat-value">
                {completedApprovals.length}
              </div>
            </div>

          </div>

          {reviewerApprovals.length === 0 ? (

            <div className="empty-state">

              <h2>No assigned reviews</h2>

              <p>
                You currently have no Reviewer
                approval requests assigned.
              </p>

            </div>

          ) : (

            <div className="card">

              <div className="section-header">

                <div>
                  <h2>Review Queue</h2>

                  <p>
                    Decisions requiring review are
                    shown below.
                  </p>
                </div>

              </div>

              <div className="table-container">

                <table className="data-table">

                  <thead>
                    <tr>
                      <th>Decision</th>
                      <th>Approval ID</th>
                      <th>Role</th>
                      <th>Status</th>
                      <th>Assigned</th>
                      <th>Reviewed</th>
                      <th>Action</th>
                    </tr>
                  </thead>

                  <tbody>

                    {reviewerApprovals.map(
                      (approval) => {

                        const decision =
                          getDecision(
                            approval.decision_id
                          );

                        return (
                          <tr
                            key={approval.id}
                          >

                            <td>
                              <strong>
                                {decision?.title ||
                                  `Decision #${approval.decision_id}`}
                              </strong>

                              {decision?.category && (
                                <small
                                  style={{
                                    display:
                                      "block",
                                    marginTop:
                                      "4px",
                                    opacity: 0.7,
                                  }}
                                >
                                  {decision.category}
                                </small>
                              )}
                            </td>

                            <td>
                              #{approval.id}
                            </td>

                            <td>
                              {approval.assigned_role ||
                                "—"}
                            </td>

                            <td>
                              <span
                                className={getStatusClass(
                                  approval.status
                                )}
                              >
                                {approval.status ||
                                  "Unknown"}
                              </span>
                            </td>

                            <td>
                              {formatDate(
                                approval.assigned_at
                              )}
                            </td>

                            <td>
                              {formatDate(
                                approval.reviewed_at
                              )}
                            </td>

                            <td>

                              <div
                                className="table-actions"
                              >

                                <Link
                                  to={`/decisions/${approval.decision_id}`}
                                  className="secondary-button"
                                >
                                  View
                                </Link>

                                {approval.status ===
                                  "Pending" && (
                                  <Link
                                    to={`/approvals/${approval.id}`}
                                    className="primary-button"
                                  >
                                    Review
                                  </Link>
                                )}

                              </div>

                            </td>

                          </tr>
                        );
                      }
                    )}

                  </tbody>

                </table>

              </div>

            </div>

          )}

        </>
      )}

    </div>
  );
}