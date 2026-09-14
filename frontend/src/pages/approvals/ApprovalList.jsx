import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  getApprovals,
  getPendingApprovals,
  approveApproval,
  rejectApproval,
} from "../../services/approvalService";

import { useAuth } from "../../context/AuthContext";

const ApprovalList = () => {
  const navigate = useNavigate();
  const { role } = useAuth();

  const [approvals, setApprovals] = useState([]);
  const [pendingApprovals, setPendingApprovals] =
    useState([]);

  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] =
    useState(null);

  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] =
    useState("");

  // =========================================================
  // LOAD APPROVALS
  // =========================================================

  useEffect(() => {
    loadApprovals();
  }, []);

  const loadApprovals = async () => {
    setLoading(true);
    setError("");

    try {
      const [allData, pendingData] =
        await Promise.all([
          getApprovals(),
          getPendingApprovals(),
        ]);

      setApprovals(
        Array.isArray(allData) ? allData : []
      );

      setPendingApprovals(
        Array.isArray(pendingData)
          ? pendingData
          : []
      );
    } catch (err) {
      console.error(
        "Failed to load approvals:",
        err
      );

      handleError(
        err,
        "Unable to load approval information."
      );
    } finally {
      setLoading(false);
    }
  };

  // =========================================================
  // APPROVE
  // =========================================================

  const handleApprove = async (approvalId) => {
    const confirmed = window.confirm(
      "Are you sure you want to approve this request?"
    );

    if (!confirmed) {
      return;
    }

    setActionLoading(approvalId);
    setError("");
    setSuccessMessage("");

    try {
      await approveApproval(approvalId);

      setSuccessMessage(
        "Approval completed successfully."
      );

      await loadApprovals();
    } catch (err) {
      console.error(
        "Failed to approve:",
        err
      );

      handleError(
        err,
        "Unable to approve this request."
      );
    } finally {
      setActionLoading(null);
    }
  };

  // =========================================================
  // REJECT
  // =========================================================

  const handleReject = async (approvalId) => {
    const confirmed = window.confirm(
      "Are you sure you want to reject this request?"
    );

    if (!confirmed) {
      return;
    }

    setActionLoading(approvalId);
    setError("");
    setSuccessMessage("");

    try {
      await rejectApproval(approvalId);

      setSuccessMessage(
        "Approval request rejected successfully."
      );

      await loadApprovals();
    } catch (err) {
      console.error(
        "Failed to reject:",
        err
      );

      handleError(
        err,
        "Unable to reject this request."
      );
    } finally {
      setActionLoading(null);
    }
  };

  // =========================================================
  // ERROR HANDLING
  // =========================================================

  const handleError = (err, defaultMessage) => {
    const status = err?.response?.status;

    if (status === 400) {
      setError(
        err.response?.data?.detail ||
          "Invalid approval request."
      );
    } else if (status === 401) {
      setError(
        "Your session has expired. Please log in again."
      );
    } else if (status === 403) {
      setError(
        "You do not have permission to perform this action."
      );
    } else if (status === 404) {
      setError(
        "The approval request was not found."
      );
    } else if (status === 422) {
      setError(
        "Please check the approval information."
      );
    } else if (status >= 500) {
      setError(
        "A server error occurred. Please try again."
      );
    } else if (!err?.response) {
      setError(
        "Unable to connect to the backend server."
      );
    } else {
      setError(
        err.response?.data?.detail ||
          defaultMessage
      );
    }
  };

  // =========================================================
  // HELPERS
  // =========================================================

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
    if (status === "Approved") {
      return "status-badge approved";
    }

    if (status === "Rejected") {
      return "status-badge rejected";
    }

    if (status === "Pending") {
      return "status-badge pending";
    }

    return "status-badge";
  };

  // =========================================================
  // LOADING
  // =========================================================

  if (loading) {
    return (
      <div className="approval-page">
        <div className="page-header">
          <div>
            <h1>Approval Workflow</h1>
            <p>
              Manage decision approval requests
            </p>
          </div>
        </div>

        <div className="approval-loading">
          Loading approvals...
        </div>
      </div>
    );
  }

  // =========================================================
  // UI
  // =========================================================

  return (
    <div className="approval-page">

      {/* HEADER */}

      <div className="page-header">
        <div>
          <h1>Approval Workflow</h1>
          <p>
            Review and manage decision approval requests
          </p>
        </div>

        <div className="approval-header-actions">

          {(role === "Manager" ||
            role === "Administrator") && (
            <button
              type="button"
              className="app-button primary"
              onClick={() =>
                navigate("/approvals/assign")
              }
            >
              Assign Approval
            </button>
          )}

          <button
            type="button"
            className="app-button secondary"
            onClick={loadApprovals}
          >
            Refresh
          </button>

        </div>
      </div>

      {/* ERROR */}

      {error && (
        <div className="alert alert-error">
          {error}
        </div>
      )}

      {/* SUCCESS */}

      {successMessage && (
        <div className="alert alert-success">
          {successMessage}
        </div>
      )}

      {/* =====================================================
          PENDING APPROVALS
          ===================================================== */}

      <section className="approval-section">

        <div className="approval-section-header">
          <div>
            <h2>Pending Approvals</h2>
            <p>
              Approval requests that are currently
              pending.
            </p>
          </div>

          <span className="approval-count">
            {pendingApprovals.length}
          </span>
        </div>

        <div className="approval-card">

          {pendingApprovals.length === 0 ? (
            <div className="approval-empty">
              <strong>
                No pending approvals
              </strong>

              <p>
                There are currently no pending
                approval requests.
              </p>
            </div>
          ) : (
            <div className="approval-table-wrapper">

              <table className="approval-table">

                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Decision ID</th>
                    <th>Assigned To</th>
                    <th>Approval Level</th>
                    <th>Status</th>
                    <th>Created</th>
                    <th>Actions</th>
                  </tr>
                </thead>

                <tbody>

                  {pendingApprovals.map(
                    (approval) => (
                      <tr key={approval.id}>

                        <td>
                          #{approval.id}
                        </td>

                        <td>
                          <button
                            type="button"
                            className="approval-decision-link"
                            onClick={() =>
                              navigate(
                                `/decisions/${approval.decision_id}`
                              )
                            }
                          >
                            Decision #
                            {approval.decision_id}
                          </button>
                        </td>

                        <td>
                          User #
                          {approval.assigned_to}
                        </td>

                        <td>
                          Level{" "}
                          {approval.approval_level}
                        </td>

                        <td>
                          <span
                            className={getStatusClass(
                              approval.status
                            )}
                          >
                            {approval.status}
                          </span>
                        </td>

                        <td>
                          {formatDate(
                            approval.created_at
                          )}
                        </td>

                        <td>
                          <div className="approval-actions">

                            <button
                              type="button"
                              className="app-button success-button"
                              disabled={
                                actionLoading ===
                                approval.id
                              }
                              onClick={() =>
                                handleApprove(
                                  approval.id
                                )
                              }
                            >
                              {actionLoading ===
                              approval.id
                                ? "Processing..."
                                : "Approve"}
                            </button>

                            <button
                              type="button"
                              className="app-button danger-button"
                              disabled={
                                actionLoading ===
                                approval.id
                              }
                              onClick={() =>
                                handleReject(
                                  approval.id
                                )
                              }
                            >
                              Reject
                            </button>

                          </div>
                        </td>

                      </tr>
                    )
                  )}

                </tbody>

              </table>

            </div>
          )}

        </div>

      </section>

      {/* =====================================================
          ALL APPROVALS
          ===================================================== */}

      <section className="approval-section">

        <div className="approval-section-header">
          <div>
            <h2>All Approvals</h2>
            <p>
              Complete approval workflow history.
            </p>
          </div>

          <span className="approval-count">
            {approvals.length}
          </span>
        </div>

        <div className="approval-card">

          {approvals.length === 0 ? (
            <div className="approval-empty">
              <strong>
                No approval records
              </strong>

              <p>
                Approval records will appear here.
              </p>
            </div>
          ) : (
            <div className="approval-table-wrapper">

              <table className="approval-table">

                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Decision ID</th>
                    <th>Assigned To</th>
                    <th>Level</th>
                    <th>Status</th>
                    <th>Created</th>
                    <th>Completed</th>
                  </tr>
                </thead>

                <tbody>

                  {approvals.map(
                    (approval) => (
                      <tr key={approval.id}>

                        <td>
                          #{approval.id}
                        </td>

                        <td>
                          <button
                            type="button"
                            className="approval-decision-link"
                            onClick={() =>
                              navigate(
                                `/decisions/${approval.decision_id}`
                              )
                            }
                          >
                            Decision #
                            {approval.decision_id}
                          </button>
                        </td>

                        <td>
                          User #
                          {approval.assigned_to}
                        </td>

                        <td>
                          Level{" "}
                          {approval.approval_level}
                        </td>

                        <td>
                          <span
                            className={getStatusClass(
                              approval.status
                            )}
                          >
                            {approval.status}
                          </span>
                        </td>

                        <td>
                          {formatDate(
                            approval.created_at
                          )}
                        </td>

                        <td>
                          {formatDate(
                            approval.completed_at
                          )}
                        </td>

                      </tr>
                    )
                  )}

                </tbody>

              </table>

            </div>
          )}

        </div>

      </section>

    </div>
  );
};

export default ApprovalList;