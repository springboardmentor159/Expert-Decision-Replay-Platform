import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import apiClient from "../api/apiClient";
import {
  getDecisionApprovals,
  getApprovalErrorMessage,
} from "../api/approvalApi";

const formatDate = (value) => {
  if (!value) {
    return "—";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return String(value);
  }

  return date.toLocaleString();
};

const getStatusClass = (status) => {
  switch (status) {
    case "Pending":
      return "review-status review-status-pending";

    case "Approved":
      return "review-status review-status-approved";

    case "Rejected":
      return "review-status review-status-rejected";

    default:
      return "review-status";
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
    return (
      detail ||
      "The requested resource was not found."
    );
  }

  if (status === 422) {
    return (
      detail ||
      "The request contains invalid information."
    );
  }

  if (status >= 500) {
    return (
      "A server error occurred. Please try again later."
    );
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

  async function loadAssignedReviews() {
    try {
      setErrorMessage("");
      setLoading(true);

      const decisionsResponse =
        await apiClient.get(
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

      const approvalResults =
        await Promise.allSettled(
          decisionItems.map(
            (decision) =>
              getDecisionApprovals(
                decision.id
              )
          )
        );

      const allApprovals = [];

      approvalResults.forEach(
        (result) => {
          if (
            result.status !==
            "fulfilled"
          ) {
            return;
          }

          const data = result.value;

          const decisionApprovals =
            data?.approvals || [];

          decisionApprovals.forEach(
            (approval) => {
              allApprovals.push(
                approval
              );
            }
          );
        }
      );

      const uniqueApprovals =
        Array.from(
          new Map(
            allApprovals.map(
              (approval) => [
                approval.id,
                approval,
              ]
            )
          ).values()
        );

      setApprovals(
        uniqueApprovals
      );
    } catch (error) {
      console.error(
        "Failed to load assigned reviews:",
        error
      );

      setErrorMessage(
        getApprovalErrorMessage(
          error
        ) ||
          getErrorMessage(error)
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  useEffect(() => {
    loadAssignedReviews();
  }, []);

  async function handleRefresh() {
    setRefreshing(true);
    await loadAssignedReviews();
  }

  function getDecision(decisionId) {
    return decisions.find(
      (decision) =>
        decision.id === decisionId
    );
  }

  const reviewerApprovals =
    approvals.filter(
      (approval) =>
        approval.assigned_role ===
        "Reviewer"
    );

  const pendingApprovals =
    reviewerApprovals.filter(
      (approval) =>
        approval.status ===
        "Pending"
    );

  const completedApprovals =
    reviewerApprovals.filter(
      (approval) =>
        approval.status ===
          "Approved" ||
        approval.status ===
          "Rejected"
    );

  return (
    <>
      <style>
        {assignedReviewsStyles}
      </style>

      <div className="assigned-reviews-page">

        {/* HEADER */}
        <div className="assigned-reviews-header">

          <div>
            <span className="assigned-reviews-eyebrow">
              APPROVAL WORKFLOW
            </span>

            <h1>
              Assigned Reviews
            </h1>

            <p>
              Review decisions assigned to
              you and take the appropriate
              approval action.
            </p>
          </div>

          <button
            type="button"
            className="assigned-refresh-button"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            <span>↻</span>

            {refreshing
              ? "Refreshing..."
              : "Refresh"}
          </button>

        </div>

        {/* ERROR */}
        {errorMessage && (
          <div className="assigned-error">

            <div>
              <strong>
                Unable to load assigned
                reviews
              </strong>

              <p>
                {errorMessage}
              </p>
            </div>

            <button
              type="button"
              onClick={
                loadAssignedReviews
              }
            >
              Try Again
            </button>

          </div>
        )}

        {loading ? (
          <div className="assigned-loading">

            <div className="assigned-loading-icon">
              ◌
            </div>

            <h2>
              Loading assigned reviews...
            </h2>

            <p>
              Fetching your approval
              requests.
            </p>

          </div>
        ) : (
          <>

            {/* STATISTICS */}
            <div className="assigned-stat-grid">

              <div className="assigned-stat-card">

                <div className="assigned-stat-icon">
                  ▣
                </div>

                <div>
                  <span>
                    Assigned Reviews
                  </span>

                  <strong>
                    {
                      reviewerApprovals.length
                    }
                  </strong>

                  <small>
                    Reviewer assignments
                  </small>
                </div>

              </div>

              <div className="assigned-stat-card">

                <div className="assigned-stat-icon assigned-pending-icon">
                  ◷
                </div>

                <div>
                  <span>
                    Pending
                  </span>

                  <strong>
                    {
                      pendingApprovals.length
                    }
                  </strong>

                  <small>
                    Awaiting your review
                  </small>
                </div>

              </div>

              <div className="assigned-stat-card">

                <div className="assigned-stat-icon assigned-completed-icon">
                  ✓
                </div>

                <div>
                  <span>
                    Completed
                  </span>

                  <strong>
                    {
                      completedApprovals.length
                    }
                  </strong>

                  <small>
                    Reviewed requests
                  </small>
                </div>

              </div>

            </div>

            {/* EMPTY STATE */}
            {reviewerApprovals.length ===
            0 ? (
              <div className="assigned-empty">

                <div className="assigned-empty-icon">
                  ✓
                </div>

                <h2>
                  No Assigned Reviews
                </h2>

                <p>
                  You currently have no
                  Reviewer approval requests
                  assigned.
                </p>

                <Link
                  to="/decisions"
                  className="assigned-primary-button"
                >
                  View Decisions
                </Link>

              </div>
            ) : (

              /* REVIEW QUEUE */
              <div className="assigned-card">

                <div className="assigned-section-header">

                  <div className="assigned-section-icon">
                    ✓
                  </div>

                  <div>
                    <h2>
                      Review Queue
                    </h2>

                    <p>
                      Decisions assigned for
                      review are shown below.
                    </p>
                  </div>

                </div>

                <div className="assigned-table-wrapper">

                  <table className="assigned-table">

                    <thead>
                      <tr>
                        <th>
                          Decision
                        </th>

                        <th>
                          Approval ID
                        </th>

                        <th>
                          Role
                        </th>

                        <th>
                          Status
                        </th>

                        <th>
                          Assigned
                        </th>

                        <th>
                          Reviewed
                        </th>

                        <th>
                          Actions
                        </th>
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
                              key={
                                approval.id
                              }
                            >

                              <td>
                                <div className="assigned-decision-cell">

                                  <strong>
                                    {decision?.title ||
                                      `Decision #${approval.decision_id}`}
                                  </strong>

                                  {decision?.category && (
                                    <span>
                                      {
                                        decision.category
                                      }
                                    </span>
                                  )}

                                </div>
                              </td>

                              <td>
                                <span className="assigned-id">
                                  #{approval.id}
                                </span>
                              </td>

                              <td>
                                <span className="assigned-role">
                                  {approval.assigned_role ||
                                    "—"}
                                </span>
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
                                <span className="assigned-date">
                                  {formatDate(
                                    approval.assigned_at
                                  )}
                                </span>
                              </td>

                              <td>
                                <span className="assigned-date">
                                  {formatDate(
                                    approval.reviewed_at
                                  )}
                                </span>
                              </td>

                              <td>

                                <div className="assigned-actions">

                                  <Link
                                    to={`/decisions/${approval.decision_id}`}
                                    className="assigned-secondary-button"
                                  >
                                    View
                                  </Link>

                                  {approval.status ===
                                    "Pending" && (
                                    <Link
                                      to={`/approvals/${approval.id}`}
                                      className="assigned-primary-small-button"
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
    </>
  );
}

const assignedReviewsStyles = `
  .assigned-reviews-page {
    width: 100%;
    max-width: 1400px;
    margin: 0 auto;
    padding: 32px;
    box-sizing: border-box;
    background: #f8fafc;
  }

  .assigned-reviews-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 24px;
    margin-bottom: 28px;
  }

  .assigned-reviews-eyebrow {
    display: block;
    margin-bottom: 7px;
    color: #2563eb;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 0.14em;
  }

  .assigned-reviews-header h1 {
    margin: 0 0 7px;
    color: #0f172a;
    font-size: 32px;
    font-weight: 800;
    line-height: 1.2;
  }

  .assigned-reviews-header p {
    margin: 0;
    color: #64748b;
    font-size: 15px;
    line-height: 1.6;
  }

  .assigned-refresh-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    min-height: 44px;
    padding: 0 18px;
    border: 1px solid #cbd5e1;
    border-radius: 9px;
    background: #ffffff;
    color: #334155;
    font-family: inherit;
    font-size: 14px;
    font-weight: 700;
    cursor: pointer;
  }

  .assigned-refresh-button:hover {
    background: #f8fafc;
    border-color: #94a3b8;
  }

  .assigned-refresh-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .assigned-refresh-button span {
    font-size: 18px;
  }

  .assigned-stat-grid {
    display: grid;
    grid-template-columns:
      repeat(3, minmax(0, 1fr));
    gap: 16px;
    margin-bottom: 24px;
  }

  .assigned-stat-card {
    display: flex;
    align-items: center;
    gap: 15px;
    min-height: 122px;
    padding: 20px;
    box-sizing: border-box;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    background: #ffffff;
    box-shadow:
      0 2px 8px
      rgba(15, 23, 42, 0.04);
  }

  .assigned-stat-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    width: 46px;
    height: 46px;
    border-radius: 11px;
    background: #eff6ff;
    color: #2563eb;
    font-size: 20px;
    font-weight: 800;
  }

  .assigned-pending-icon {
    background: #fff7ed;
    color: #ea580c;
  }

  .assigned-completed-icon {
    background: #ecfdf5;
    color: #059669;
  }

  .assigned-stat-card span {
    display: block;
    margin-bottom: 5px;
    color: #64748b;
    font-size: 12px;
    font-weight: 700;
  }

  .assigned-stat-card strong {
    display: block;
    color: #0f172a;
    font-size: 27px;
    line-height: 1.2;
  }

  .assigned-stat-card small {
    display: block;
    margin-top: 4px;
    color: #94a3b8;
    font-size: 11px;
  }

  .assigned-card {
    margin-bottom: 24px;
    padding: 24px;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    background: #ffffff;
    box-shadow:
      0 2px 8px
      rgba(15, 23, 42, 0.04);
  }

  .assigned-section-header {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    margin-bottom: 22px;
  }

  .assigned-section-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    width: 42px;
    height: 42px;
    border-radius: 10px;
    background: #eff6ff;
    color: #2563eb;
    font-size: 18px;
    font-weight: 800;
  }

  .assigned-section-header h2 {
    margin: 0 0 5px;
    color: #0f172a;
    font-size: 20px;
  }

  .assigned-section-header p {
    margin: 0;
    color: #64748b;
    font-size: 14px;
    line-height: 1.5;
  }

  .assigned-table-wrapper {
    width: 100%;
    overflow-x: auto;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
  }

  .assigned-table {
    width: 100%;
    min-width: 1050px;
    border-collapse: collapse;
    background: #ffffff;
  }

  .assigned-table th {
    padding: 14px 16px;
    border-bottom: 1px solid #e2e8f0;
    background: #f8fafc;
    color: #64748b;
    font-size: 11px;
    font-weight: 800;
    text-align: left;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    white-space: nowrap;
  }

  .assigned-table td {
    padding: 16px;
    border-bottom: 1px solid #f1f5f9;
    color: #475569;
    font-size: 13px;
    vertical-align: middle;
  }

  .assigned-table tbody tr:last-child td {
    border-bottom: none;
  }

  .assigned-table tbody tr:hover {
    background: #f8fafc;
  }

  .assigned-decision-cell strong {
    display: block;
    max-width: 300px;
    color: #0f172a;
    font-size: 14px;
    line-height: 1.45;
  }

  .assigned-decision-cell span {
    display: block;
    margin-top: 5px;
    color: #94a3b8;
    font-size: 11px;
  }

  .assigned-id {
    display: inline-flex;
    padding: 5px 8px;
    border-radius: 6px;
    background: #f1f5f9;
    color: #475569;
    font-size: 12px;
    font-weight: 700;
  }

  .assigned-role {
    color: #475569;
    font-size: 12px;
    font-weight: 700;
  }

  .assigned-date {
    display: block;
    min-width: 135px;
    color: #64748b;
    font-size: 12px;
    line-height: 1.45;
  }

  .review-status {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 78px;
    min-height: 27px;
    padding: 0 9px;
    box-sizing: border-box;
    border-radius: 999px;
    background: #f1f5f9;
    color: #64748b;
    font-size: 11px;
    font-weight: 800;
  }

  .review-status-pending {
    background: #fff7ed;
    color: #c2410c;
  }

  .review-status-approved {
    background: #ecfdf5;
    color: #047857;
  }

  .review-status-rejected {
    background: #fef2f2;
    color: #b91c1c;
  }

  .assigned-actions {
    display: flex;
    align-items: center;
    gap: 7px;
    white-space: nowrap;
  }

  .assigned-secondary-button,
  .assigned-primary-small-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-height: 35px;
    padding: 0 12px;
    border-radius: 7px;
    font-family: inherit;
    font-size: 12px;
    font-weight: 700;
    text-decoration: none;
    box-sizing: border-box;
  }

  .assigned-secondary-button {
    border: 1px solid #cbd5e1;
    background: #ffffff;
    color: #334155;
  }

  .assigned-secondary-button:hover {
    background: #f8fafc;
  }

  .assigned-primary-small-button {
    border: 1px solid #2563eb;
    background: #2563eb;
    color: #ffffff;
  }

  .assigned-primary-small-button:hover {
    background: #1d4ed8;
  }

  .assigned-primary-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-height: 42px;
    padding: 0 17px;
    border-radius: 8px;
    background: #2563eb;
    color: #ffffff;
    font-size: 13px;
    font-weight: 700;
    text-decoration: none;
  }

  .assigned-primary-button:hover {
    background: #1d4ed8;
  }

  .assigned-empty {
    padding: 60px 24px;
    border: 1px dashed #cbd5e1;
    border-radius: 12px;
    background: #ffffff;
    text-align: center;
  }

  .assigned-empty-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 50px;
    height: 50px;
    margin: 0 auto 16px;
    border-radius: 50%;
    background: #ecfdf5;
    color: #059669;
    font-size: 21px;
    font-weight: 800;
  }

  .assigned-empty h2 {
    margin: 0 0 8px;
    color: #0f172a;
    font-size: 21px;
  }

  .assigned-empty p {
    max-width: 500px;
    margin: 0 auto 20px;
    color: #64748b;
    line-height: 1.6;
    font-size: 14px;
  }

  .assigned-error {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
    margin-bottom: 24px;
    padding: 16px 18px;
    border: 1px solid #fecaca;
    border-radius: 10px;
    background: #fef2f2;
  }

  .assigned-error strong {
    color: #991b1b;
    font-size: 14px;
  }

  .assigned-error p {
    margin: 4px 0 0;
    color: #b91c1c;
    font-size: 13px;
  }

  .assigned-error button {
    flex-shrink: 0;
    min-height: 38px;
    padding: 0 14px;
    border: 1px solid #fecaca;
    border-radius: 7px;
    background: #ffffff;
    color: #991b1b;
    font-family: inherit;
    font-size: 12px;
    font-weight: 700;
    cursor: pointer;
  }

  .assigned-loading {
    min-height: 400px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
  }

  .assigned-loading-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 52px;
    height: 52px;
    margin-bottom: 14px;
    border-radius: 50%;
    background: #eff6ff;
    color: #2563eb;
    font-size: 24px;
  }

  .assigned-loading h2 {
    margin: 0 0 7px;
    color: #0f172a;
    font-size: 19px;
  }

  .assigned-loading p {
    margin: 0;
    color: #64748b;
    font-size: 14px;
  }

  @media (max-width: 1000px) {
    .assigned-stat-grid {
      grid-template-columns:
        repeat(3, minmax(0, 1fr));
    }
  }

  @media (max-width: 800px) {
    .assigned-reviews-page {
      padding: 22px 16px;
    }

    .assigned-reviews-header {
      flex-direction: column;
      align-items: stretch;
    }

    .assigned-refresh-button {
      width: 100%;
    }

    .assigned-stat-grid {
      grid-template-columns: 1fr;
    }

    .assigned-card {
      padding: 18px;
    }
  }

  @media (max-width: 520px) {
    .assigned-reviews-page {
      padding: 18px 12px;
    }

    .assigned-reviews-header h1 {
      font-size: 26px;
    }

    .assigned-error {
      flex-direction: column;
      align-items: stretch;
    }

    .assigned-error button {
      width: 100%;
    }
  }
`;
