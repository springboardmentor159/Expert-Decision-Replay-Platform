import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import apiClient from "../api/apiClient";
import { useAuth } from "../auth/AuthContext";

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

const extractErrorMessage = (error) => {
  if (error?.response?.status === 401) {
    return "Your session has expired. Please log in again.";
  }

  if (error?.response?.status === 403) {
    return (
      error?.response?.data?.detail ||
      "You do not have permission to view these approvals."
    );
  }

  if (error?.response?.status === 404) {
    return (
      error?.response?.data?.detail ||
      "The requested resource was not found."
    );
  }

  if (error?.response?.status === 422) {
    return (
      error?.response?.data?.detail ||
      "The request contains invalid information."
    );
  }

  if (error?.response?.status >= 500) {
    return "A server error occurred. Please try again later.";
  }

  return (
    error?.response?.data?.detail ||
    error?.message ||
    "Unable to load pending approvals."
  );
};

export default function PendingApprovals() {
  const { user } = useAuth();

  const [approvals, setApprovals] = useState([]);
  const [decisions, setDecisions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const loadPendingApprovals = async () => {
    try {
      setErrorMessage("");

      const decisionsResponse = await apiClient.get("/decisions/", {
        params: {
          page: 1,
          page_size: 100,
        },
      });

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
      console.error(
        "Failed to load pending approvals:",
        error
      );

      setErrorMessage(
        getApprovalErrorMessage(error) ||
          extractErrorMessage(error)
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadPendingApprovals();
  }, []);

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadPendingApprovals();
  };

  const currentUserId = Number(
    user?.id ??
      user?.user_id ??
      user?.sub
  );

  /*
   * Only approvals assigned to the currently logged-in
   * Manager are displayed.
   */
  const managerApprovals = approvals.filter(
    (approval) =>
      approval.assigned_role === "Manager" &&
      Number(approval.assigned_to) === currentUserId
  );

  const pendingApprovals = managerApprovals.filter(
    (approval) =>
      approval.status === "Pending"
  );

  const completedApprovals = managerApprovals.filter(
    (approval) =>
      approval.status === "Approved" ||
      approval.status === "Rejected"
  );

  const getDecision = (decisionId) => {
    return decisions.find(
      (decision) => decision.id === decisionId
    );
  };

  return (
    <div className="dashboard-page">
      <div className="page-header">
        <div>
          <h1>Pending Approvals</h1>

          <p className="page-subtitle">
            Review decisions awaiting your Manager approval.
          </p>
        </div>

        <button
          type="button"
          className="secondary-button"
          onClick={handleRefresh}
          disabled={refreshing}
        >
          {refreshing ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      {errorMessage && (
        <div className="error-message">
          {errorMessage}
        </div>
      )}

      {loading ? (
        <div className="loading-state">
          Loading pending approvals...
        </div>
      ) : (
        <>
          <div className="dashboard-stats">
            <div className="stat-card">
              <span className="stat-label">
                Total Approvals
              </span>

              <strong className="stat-value">
                {managerApprovals.length}
              </strong>
            </div>

            <div className="stat-card">
              <span className="stat-label">
                Pending
              </span>

              <strong className="stat-value">
                {pendingApprovals.length}
              </strong>
            </div>

            <div className="stat-card">
              <span className="stat-label">
                Completed
              </span>

              <strong className="stat-value">
                {completedApprovals.length}
              </strong>
            </div>
          </div>

          {managerApprovals.length === 0 ? (
            <div className="empty-state">
              <h3>No Manager approvals</h3>

              <p>
                You currently have no approval requests
                assigned to you as a Manager.
              </p>
            </div>
          ) : (
            <div className="content-card">
              <div className="section-header">
                <div>
                  <h2>Approval Queue</h2>

                  <p>
                    Decisions assigned to you for Manager
                    approval are shown below.
                  </p>
                </div>
              </div>

              <div className="table-container">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Decision</th>
                      <th>Approval ID</th>
                      <th>Status</th>
                      <th>Assigned</th>
                      <th>Reviewed</th>
                      <th>Action</th>
                    </tr>
                  </thead>

                  <tbody>
                    {managerApprovals.map((approval) => {
                      const decision = getDecision(
                        approval.decision_id
                      );

                      return (
                        <tr key={approval.id}>
                          <td>
                            <div>
                              <strong>
                                {decision?.title ||
                                  `Decision #${approval.decision_id}`}
                              </strong>

                              {decision?.category && (
                                <small
                                  style={{
                                    display: "block",
                                    marginTop: "4px",
                                    opacity: 0.7,
                                  }}
                                >
                                  {decision.category}
                                </small>
                              )}
                            </div>
                          </td>

                          <td>
                            #{approval.id}
                          </td>

                          <td>
                            <span
                              className={getStatusClass(
                                approval.status
                              )}
                            >
                              {approval.status || "Unknown"}
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
                              style={{
                                display: "flex",
                                gap: "8px",
                                flexWrap: "wrap",
                              }}
                            >
                              <Link
                                to={`/decisions/${approval.decision_id}`}
                                className="secondary-button"
                              >
                                View Decision
                              </Link>

                              <Link
                                to={`/approvals/${approval.id}`}
                                className={
                                  approval.status ===
                                  "Pending"
                                    ? "primary-button"
                                    : "secondary-button"
                                }
                              >
                                {approval.status ===
                                "Pending"
                                  ? "Review"
                                  : "View Review"}
                              </Link>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
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
