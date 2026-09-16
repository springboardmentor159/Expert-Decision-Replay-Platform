import {
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";

import {
  Link,
} from "react-router-dom";

import {
  AlertCircle,
  ArrowRight,
  CheckCircle2,
  Clock3,
  FileCheck2,
  RefreshCw,
  ShieldCheck,
  XCircle,
} from "lucide-react";

import apiClient from "../api/apiClient";

import {
  AuthContext,
} from "../context/AuthContext";

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
    return value;
  }

  return date.toLocaleString();
};


const getStatusClass = (status) => {
  switch (status) {
    case "Pending":
      return "pa-status pa-status-pending";

    case "Approved":
      return "pa-status pa-status-approved";

    case "Rejected":
      return "pa-status pa-status-rejected";

    default:
      return "pa-status pa-status-default";
  }
};


const extractErrorMessage = (error) => {
  if (error?.response?.status === 401) {
    return (
      "Your session has expired. Please log in again."
    );
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
    return (
      "A server error occurred. Please try again later."
    );
  }

  return (
    error?.response?.data?.detail ||
    error?.message ||
    "Unable to load pending approvals."
  );
};


export default function PendingApprovals() {
  const { user } =
    useContext(AuthContext);

  const [approvals, setApprovals] =
    useState([]);

  const [decisions, setDecisions] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [refreshing, setRefreshing] =
    useState(false);

  const [errorMessage, setErrorMessage] =
    useState("");


  const loadPendingApprovals =
    useCallback(async () => {
      try {
        setErrorMessage("");

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

            const data =
              result.value;

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
          "Failed to load pending approvals:",
          error
        );

        setErrorMessage(
          getApprovalErrorMessage(
            error
          ) ||
          extractErrorMessage(
            error
          )
        );

      } finally {
        setLoading(false);
        setRefreshing(false);
      }
    }, []);


  useEffect(() => {
    loadPendingApprovals();
  }, [loadPendingApprovals]);


  const handleRefresh = async () => {
    setRefreshing(true);
    await loadPendingApprovals();
  };


  const currentUserId =
    Number(
      user?.id ??
      user?.user_id ??
      user?.sub
    );


  /*
   * Only approvals assigned to the
   * currently logged-in Manager
   * are displayed.
   */
  const managerApprovals =
    approvals.filter(
      (approval) =>
        approval.assigned_role ===
          "Manager" &&
        Number(
          approval.assigned_to
        ) === currentUserId
    );


  const pendingApprovals =
    managerApprovals.filter(
      (approval) =>
        approval.status ===
        "Pending"
    );


  const completedApprovals =
    managerApprovals.filter(
      (approval) =>
        approval.status ===
          "Approved" ||
        approval.status ===
          "Rejected"
    );


  const getDecision = (
    decisionId
  ) => {
    return decisions.find(
      (decision) =>
        decision.id ===
        decisionId
    );
  };


  return (
    <div className="pa-page">

      <style>{`
        .pa-page {
          max-width: 1200px;
          margin: 0 auto;
          padding: 5px 0 40px;
        }

        .pa-header {
          display: flex;
          align-items: flex-start;
          justify-content: space-between;
          gap: 20px;
          margin-bottom: 25px;
        }

        .pa-header-left {
          display: flex;
          align-items: flex-start;
          gap: 14px;
        }

        .pa-header-icon {
          width: 50px;
          height: 50px;
          min-width: 50px;
          border-radius: 14px;
          background: #eaf2ff;
          color: #2563eb;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .pa-eyebrow {
          margin-bottom: 5px;
          color: #64748b;
          font-size: 10px;
          font-weight: 800;
          letter-spacing: .1em;
          text-transform: uppercase;
        }

        .pa-header h1 {
          margin: 0;
          color: #0f172a;
          font-size: 29px;
          line-height: 1.2;
        }

        .pa-header p {
          margin: 7px 0 0;
          color: #64748b;
          font-size: 13px;
        }

        .pa-refresh {
          min-height: 42px;
          padding: 0 14px;
          border: 1px solid #cbd5e1;
          border-radius: 9px;
          background: #fff;
          color: #475569;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: 7px;
          font-family: inherit;
          font-size: 12px;
          font-weight: 750;
          cursor: pointer;
        }

        .pa-refresh:hover:not(:disabled) {
          background: #f8fafc;
          border-color: #94a3b8;
        }

        .pa-refresh:disabled {
          opacity: .55;
          cursor: not-allowed;
        }

        .pa-spin {
          animation: paSpin 1s linear infinite;
        }

        @keyframes paSpin {
          from {
            transform: rotate(0deg);
          }

          to {
            transform: rotate(360deg);
          }
        }

        .pa-error {
          display: flex;
          align-items: flex-start;
          gap: 11px;
          margin-bottom: 20px;
          padding: 14px 16px;
          border: 1px solid #fecaca;
          border-radius: 11px;
          background: #fef2f2;
          color: #991b1b;
        }

        .pa-error strong {
          display: block;
          margin-bottom: 3px;
          font-size: 12px;
        }

        .pa-error p {
          margin: 0;
          font-size: 12px;
          line-height: 1.5;
        }

        .pa-stats {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 15px;
          margin-bottom: 20px;
        }

        .pa-stat {
          position: relative;
          overflow: hidden;
          padding: 19px;
          border: 1px solid #e2e8f0;
          border-radius: 15px;
          background: #fff;
          box-shadow:
            0 5px 20px
            rgba(15,23,42,.04);
        }

        .pa-stat::after {
          content: "";
          position: absolute;
          right: -25px;
          top: -25px;
          width: 80px;
          height: 80px;
          border-radius: 50%;
          background: #f8fafc;
        }

        .pa-stat-top {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 10px;
        }

        .pa-stat-icon {
          width: 34px;
          height: 34px;
          border-radius: 9px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: #f1f5f9;
          color: #64748b;
        }

        .pa-stat-pending .pa-stat-icon {
          background: #fef3c7;
          color: #b45309;
        }

        .pa-stat-completed .pa-stat-icon {
          background: #dcfce7;
          color: #15803d;
        }

        .pa-stat-label {
          display: block;
          margin-top: 14px;
          color: #64748b;
          font-size: 11px;
          font-weight: 700;
        }

        .pa-stat-value {
          display: block;
          margin-top: 3px;
          color: #0f172a;
          font-size: 25px;
          line-height: 1.2;
        }

        .pa-card {
          overflow: hidden;
          border: 1px solid #e2e8f0;
          border-radius: 17px;
          background: #fff;
          box-shadow:
            0 7px 25px
            rgba(15,23,42,.05);
        }

        .pa-card-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 15px;
          padding: 20px 22px;
          border-bottom: 1px solid #e2e8f0;
          background: #f8fafc;
        }

        .pa-card-heading {
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .pa-card-icon {
          width: 36px;
          height: 36px;
          border-radius: 10px;
          background: #dbeafe;
          color: #2563eb;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .pa-card-header h2 {
          margin: 0;
          color: #0f172a;
          font-size: 17px;
        }

        .pa-card-header p {
          margin: 4px 0 0;
          color: #64748b;
          font-size: 11px;
        }

        .pa-queue-count {
          padding: 6px 10px;
          border-radius: 20px;
          background: #e2e8f0;
          color: #475569;
          font-size: 10px;
          font-weight: 750;
          white-space: nowrap;
        }

        .pa-table-wrapper {
          overflow-x: auto;
        }

        .pa-table {
          width: 100%;
          min-width: 850px;
          border-collapse: collapse;
        }

        .pa-table th {
          padding: 13px 15px;
          background: #fff;
          color: #64748b;
          font-size: 10px;
          font-weight: 800;
          letter-spacing: .05em;
          text-align: left;
          text-transform: uppercase;
          border-bottom: 1px solid #e2e8f0;
          white-space: nowrap;
        }

        .pa-table td {
          padding: 15px;
          color: #475569;
          font-size: 12px;
          vertical-align: middle;
          border-bottom: 1px solid #f1f5f9;
        }

        .pa-table tbody tr:hover {
          background: #f8fafc;
        }

        .pa-table tbody tr:last-child td {
          border-bottom: none;
        }

        .pa-decision {
          display: flex;
          flex-direction: column;
          gap: 4px;
          min-width: 190px;
        }

        .pa-decision strong {
          color: #0f172a;
          font-size: 13px;
          line-height: 1.4;
        }

        .pa-category {
          color: #94a3b8;
          font-size: 10px;
        }

        .pa-approval-id {
          color: #64748b;
          font-weight: 700;
        }

        .pa-status {
          display: inline-flex;
          align-items: center;
          padding: 5px 9px;
          border-radius: 20px;
          font-size: 10px;
          font-weight: 750;
          white-space: nowrap;
        }

        .pa-status-pending {
          background: #fef3c7;
          color: #92400e;
        }

        .pa-status-approved {
          background: #dcfce7;
          color: #166534;
        }

        .pa-status-rejected {
          background: #fee2e2;
          color: #991b1b;
        }

        .pa-status-default {
          background: #f1f5f9;
          color: #475569;
        }

        .pa-date {
          display: inline-flex;
          align-items: center;
          gap: 5px;
          white-space: nowrap;
          color: #64748b;
          font-size: 11px;
        }

        .pa-actions {
          display: flex;
          flex-wrap: wrap;
          gap: 7px;
          min-width: 170px;
        }

        .pa-action {
          min-height: 34px;
          padding: 0 10px;
          border-radius: 7px;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: 5px;
          text-decoration: none;
          font-size: 10px;
          font-weight: 750;
          white-space: nowrap;
        }

        .pa-action-secondary {
          border: 1px solid #cbd5e1;
          background: #fff;
          color: #475569;
        }

        .pa-action-secondary:hover {
          background: #f8fafc;
        }

        .pa-action-primary {
          border: 1px solid #2563eb;
          background: #2563eb;
          color: #fff;
        }

        .pa-action-primary:hover {
          background: #1d4ed8;
        }

        .pa-loading,
        .pa-empty {
          min-height: 300px;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 30px;
          text-align: center;
        }

        .pa-loading {
          gap: 11px;
          color: #64748b;
          font-size: 13px;
        }

        .pa-empty-icon {
          width: 55px;
          height: 55px;
          margin-bottom: 13px;
          border-radius: 15px;
          background: #f1f5f9;
          color: #64748b;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .pa-empty h3 {
          margin: 0 0 6px;
          color: #334155;
          font-size: 16px;
        }

        .pa-empty p {
          max-width: 420px;
          margin: 0;
          color: #94a3b8;
          font-size: 12px;
          line-height: 1.5;
        }

        @media (max-width: 750px) {
          .pa-header {
            flex-direction: column;
          }

          .pa-refresh {
            width: 100%;
          }

          .pa-stats {
            grid-template-columns: 1fr;
          }
        }

        @media (max-width: 500px) {
          .pa-header h1 {
            font-size: 24px;
          }

          .pa-header-left {
            gap: 10px;
          }

          .pa-header-icon {
            width: 44px;
            height: 44px;
            min-width: 44px;
          }
        }
      `}</style>


      {/* HEADER */}
      <div className="pa-header">

        <div className="pa-header-left">

          <div className="pa-header-icon">
            <FileCheck2 size={24} />
          </div>

          <div>

            <div className="pa-eyebrow">
              Manager Workspace
            </div>

            <h1>
              Pending Approvals
            </h1>

            <p>
              Review decisions awaiting
              your Manager approval.
            </p>

          </div>

        </div>


        <button
          type="button"
          className="pa-refresh"
          onClick={handleRefresh}
          disabled={
            refreshing ||
            loading
          }
        >
          <RefreshCw
            size={14}
            className={
              refreshing
                ? "pa-spin"
                : ""
            }
          />

          {refreshing
            ? "Refreshing..."
            : "Refresh"}
        </button>

      </div>


      {/* ERROR */}
      {errorMessage && (
        <div className="pa-error">

          <AlertCircle size={18} />

          <div>
            <strong>
              Unable to load approvals
            </strong>

            <p>
              {errorMessage}
            </p>
          </div>

        </div>
      )}


      {loading ? (
        <div className="pa-card">

          <div className="pa-loading">

            <RefreshCw
              size={24}
              className="pa-spin"
            />

            <span>
              Loading pending approvals...
            </span>

          </div>

        </div>
      ) : (
        <>

          {/* STATS */}
          <div className="pa-stats">

            <div className="pa-stat">

              <div className="pa-stat-top">
                <span className="pa-stat-label">
                  Total Approvals
                </span>

                <div className="pa-stat-icon">
                  <FileCheck2 size={17} />
                </div>
              </div>

              <strong className="pa-stat-value">
                {managerApprovals.length}
              </strong>

            </div>


            <div className="pa-stat pa-stat-pending">

              <div className="pa-stat-top">
                <span className="pa-stat-label">
                  Pending
                </span>

                <div className="pa-stat-icon">
                  <Clock3 size={17} />
                </div>
              </div>

              <strong className="pa-stat-value">
                {pendingApprovals.length}
              </strong>

            </div>


            <div className="pa-stat pa-stat-completed">

              <div className="pa-stat-top">
                <span className="pa-stat-label">
                  Completed
                </span>

                <div className="pa-stat-icon">
                  <CheckCircle2 size={17} />
                </div>
              </div>

              <strong className="pa-stat-value">
                {completedApprovals.length}
              </strong>

            </div>

          </div>


          {/* QUEUE */}
          {managerApprovals.length === 0 ? (
            <div className="pa-card">

              <div className="pa-empty">

                <div className="pa-empty-icon">
                  <ShieldCheck size={25} />
                </div>

                <h3>
                  No Manager approvals
                </h3>

                <p>
                  You currently have no
                  approval requests assigned
                  to you as a Manager.
                </p>

              </div>

            </div>
          ) : (
            <div className="pa-card">

              <div className="pa-card-header">

                <div className="pa-card-heading">

                  <div className="pa-card-icon">
                    <FileCheck2 size={18} />
                  </div>

                  <div>

                    <h2>
                      Approval Queue
                    </h2>

                    <p>
                      Decisions assigned to
                      you for Manager approval.
                    </p>

                  </div>

                </div>

                <span className="pa-queue-count">
                  {managerApprovals.length} Request
                  {managerApprovals.length === 1
                    ? ""
                    : "s"}
                </span>

              </div>


              <div className="pa-table-wrapper">

                <table className="pa-table">

                  <thead>
                    <tr>
                      <th>
                        Decision
                      </th>

                      <th>
                        Approval ID
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
                        Action
                      </th>
                    </tr>
                  </thead>


                  <tbody>

                    {managerApprovals.map(
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
                              <div className="pa-decision">

                                <strong>
                                  {decision?.title ||
                                    `Decision #${approval.decision_id}`}
                                </strong>

                                {decision?.category && (
                                  <span className="pa-category">
                                    {decision.category}
                                  </span>
                                )}

                              </div>
                            </td>


                            <td>
                              <span className="pa-approval-id">
                                #{approval.id}
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

                              <span className="pa-date">
                                <Clock3 size={12} />

                                {formatDate(
                                  approval.assigned_at
                                )}
                              </span>

                            </td>


                            <td>

                              <span className="pa-date">
                                <CheckCircle2 size={12} />

                                {formatDate(
                                  approval.reviewed_at
                                )}
                              </span>

                            </td>


                            <td>

                              <div className="pa-actions">

                                <Link
                                  to={`/decisions/${approval.decision_id}`}
                                  className="pa-action pa-action-secondary"
                                >
                                  View Decision
                                  <ArrowRight
                                    size={11}
                                  />
                                </Link>


                                <Link
                                  to={`/approvals/${approval.id}`}
                                  className={
                                    approval.status ===
                                    "Pending"
                                      ? "pa-action pa-action-primary"
                                      : "pa-action pa-action-secondary"
                                  }
                                >
                                  {approval.status ===
                                  "Pending"
                                    ? "Review"
                                    : "View Review"}

                                  {approval.status ===
                                    "Pending" ? (
                                    <ShieldCheck
                                      size={11}
                                    />
                                  ) : (
                                    <ArrowRight
                                      size={11}
                                    />
                                  )}
                                </Link>

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