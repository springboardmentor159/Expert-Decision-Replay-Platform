import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import {
  ArrowLeft,
  CheckCircle2,
  XCircle,
  Clock3,
  FileText,
  User,
  ShieldCheck,
  AlertCircle,
  Loader2,
  MessageSquare,
} from "lucide-react";

import {
  getApproval,
  approveApproval,
  rejectApproval,
} from "../api/approvalApi";

function formatDate(value) {
  if (!value) {
    return "—";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "—";
  }

  return date.toLocaleString();
}

function getStatusClass(status) {
  switch (status) {
    case "Approved":
      return "approval-status approved";

    case "Rejected":
      return "approval-status rejected";

    case "Pending":
      return "approval-status pending";

    default:
      return "approval-status";
  }
}

function getErrorMessage(error, fallback) {
  const status = error?.response?.status;
  const detail = error?.response?.data?.detail;

  if (status === 400) {
    return (
      detail ||
      "This approval action is invalid."
    );
  }

  if (status === 401) {
    return "Your session has expired. Please log in again.";
  }

  if (status === 403) {
    return (
      detail ||
      "You do not have permission to review this approval."
    );
  }

  if (status === 404) {
    return (
      detail ||
      "The approval request was not found."
    );
  }

  if (status === 422) {
    if (Array.isArray(detail)) {
      return detail
        .map((item) => item.msg)
        .join(" ");
    }

    return (
      detail ||
      "The submitted information is invalid."
    );
  }

  if (status >= 500) {
    return "The server encountered an error. Please try again.";
  }

  return (
    detail ||
    error?.message ||
    fallback
  );
}

export default function ReviewApproval() {
  const { approvalId } = useParams();
  const navigate = useNavigate();

  const [approval, setApproval] = useState(null);

  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [comments, setComments] = useState("");

  useEffect(() => {
    loadApproval();
  }, [approvalId]);

  async function loadApproval() {
    try {
      setLoading(true);
      setError("");
      setSuccess("");

      const data = await getApproval(
        approvalId
      );

      setApproval(data);

      setComments(
        data?.comments || ""
      );
    } catch (err) {
      console.error(
        "Failed to load approval:",
        err
      );

      setError(
        getErrorMessage(
          err,
          "Unable to load approval."
        )
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleApprove() {
    const confirmed = window.confirm(
      "Are you sure you want to approve this decision?"
    );

    if (!confirmed) {
      return;
    }

    try {
      setProcessing(true);
      setError("");
      setSuccess("");

      const result =
        await approveApproval(
          approvalId,
          {
            comments:
              comments.trim() || null,
          }
        );

      setApproval(
        result || {
          ...approval,
          status: "Approved",
          comments:
            comments.trim() || null,
        }
      );

      setSuccess(
        "Decision approved successfully."
      );
    } catch (err) {
      console.error(
        "Failed to approve decision:",
        err
      );

      setError(
        getErrorMessage(
          err,
          "Unable to approve this decision."
        )
      );
    } finally {
      setProcessing(false);
    }
  }

  async function handleReject() {
    const confirmed = window.confirm(
      "Are you sure you want to reject this decision?"
    );

    if (!confirmed) {
      return;
    }

    try {
      setProcessing(true);
      setError("");
      setSuccess("");

      const result =
        await rejectApproval(
          approvalId,
          {
            comments:
              comments.trim() || null,
          }
        );

      setApproval(
        result || {
          ...approval,
          status: "Rejected",
          comments:
            comments.trim() || null,
        }
      );

      setSuccess(
        "Decision rejected successfully."
      );
    } catch (err) {
      console.error(
        "Failed to reject decision:",
        err
      );

      setError(
        getErrorMessage(
          err,
          "Unable to reject this decision."
        )
      );
    } finally {
      setProcessing(false);
    }
  }

  if (loading) {
    return (
      <>
        <style>{styles}</style>

        <div className="review-page">
          <div className="review-loading">
            <Loader2
              size={26}
              className="review-spin"
            />

            <span>
              Loading approval...
            </span>
          </div>
        </div>
      </>
    );
  }

  if (error && !approval) {
    return (
      <>
        <style>{styles}</style>

        <div className="review-page">
          <div className="review-error-page">
            <div className="review-error-icon">
              <AlertCircle size={28} />
            </div>

            <h2>
              Unable to Load Approval
            </h2>

            <p>{error}</p>

            <div className="review-actions">
              <button
                type="button"
                className="review-primary"
                onClick={loadApproval}
              >
                Try Again
              </button>

              <Link
                to="/approvals"
                className="review-secondary"
              >
                <ArrowLeft size={15} />
                Back to Assigned Reviews
              </Link>
            </div>
          </div>
        </div>
      </>
    );
  }

  const status =
    approval?.status || "Pending";

  const isPending =
    status === "Pending";

  return (
    <>
      <style>{styles}</style>

      <div className="review-page">

        {/* HEADER */}
        <div className="review-header">
          <div>
            <Link
              to="/approvals"
              className="review-back"
            >
              <ArrowLeft size={15} />
              Back to Assigned Reviews
            </Link>

            <div className="review-eyebrow">
              Approval Workflow
            </div>

            <h1>
              Review Approval
            </h1>

            <p>
              Review the assigned decision and
              take the appropriate approval action.
            </p>
          </div>

          <div className="review-header-icon">
            <ShieldCheck size={28} />
          </div>
        </div>

        {/* ERROR */}
        {error && (
          <div className="review-alert error">
            <AlertCircle size={19} />

            <div>
              <strong>
                Action could not be completed
              </strong>

              <p>{error}</p>
            </div>
          </div>
        )}

        {/* SUCCESS */}
        {success && (
          <div className="review-alert success">
            <CheckCircle2 size={19} />

            <div>
              <strong>
                Action completed
              </strong>

              <p>{success}</p>
            </div>
          </div>
        )}

        {/* APPROVAL SUMMARY */}
        <div className="review-card review-summary">

          <div className="review-summary-top">
            <div className="review-summary-icon">
              <FileText size={23} />
            </div>

            <div className="review-summary-main">
              <div className="review-eyebrow">
                Decision Approval
              </div>

              <h2>
                Decision #
                {approval?.decision_id ??
                  "—"}
              </h2>

              <p>
                Approval #
                {approval?.id ??
                  approvalId}
              </p>
            </div>

            <span
              className={getStatusClass(
                status
              )}
            >
              {status}
            </span>
          </div>

          <div className="review-summary-grid">

            <div className="review-info">
              <span>
                <FileText size={14} />
                Decision ID
              </span>

              <strong>
                #
                {approval?.decision_id ??
                  "—"}
              </strong>
            </div>

            <div className="review-info">
              <span>
                <User size={14} />
                Assigned To
              </span>

              <strong>
                User{" "}
                {approval?.assigned_to ??
                  "—"}
              </strong>
            </div>

            <div className="review-info">
              <span>
                <ShieldCheck size={14} />
                Role
              </span>

              <strong>
                {approval?.assigned_role ||
                  "—"}
              </strong>
            </div>

            <div className="review-info">
              <span>
                <Clock3 size={14} />
                Assigned At
              </span>

              <strong>
                {formatDate(
                  approval?.assigned_at
                )}
              </strong>
            </div>

            <div className="review-info">
              <span>
                <User size={14} />
                Assigned By
              </span>

              <strong>
                User{" "}
                {approval?.assigned_by ??
                  "—"}
              </strong>
            </div>

            <div className="review-info">
              <span>
                <Clock3 size={14} />
                Reviewed At
              </span>

              <strong>
                {formatDate(
                  approval?.reviewed_at
                )}
              </strong>
            </div>

          </div>
        </div>

        {/* COMMENTS */}
        <div className="review-card">

          <div className="review-card-header">
            <div className="review-card-title-icon">
              <MessageSquare size={18} />
            </div>

            <div>
              <h2>
                Review Comments
              </h2>

              <p>
                Add your comments before
                approving or rejecting the
                decision.
              </p>
            </div>
          </div>

          <div className="review-card-body">

            <label
              htmlFor="approval-comments"
              className="review-label"
            >
              Comments
            </label>

            <textarea
              id="approval-comments"
              rows="6"
              value={comments}
              onChange={(event) =>
                setComments(
                  event.target.value
                )
              }
              disabled={
                processing ||
                !isPending
              }
              placeholder={
                isPending
                  ? "Enter your review comments..."
                  : "No further comments can be added because this approval has already been reviewed."
              }
            />

            <div className="review-comment-help">
              {isPending
                ? "Your comments will be stored with the approval decision."
                : "This approval has already been completed."}
            </div>
          </div>
        </div>

        {/* ACTIONS */}
        <div className="review-card review-action-card">

          <div>
            <h2>
              Approval Decision
            </h2>

            <p>
              {isPending
                ? "Choose whether to approve or reject this assigned decision."
                : `This approval has already been ${status.toLowerCase()}.`}
            </p>
          </div>

          {isPending ? (
            <div className="review-decision-buttons">

              <button
                type="button"
                className="review-reject"
                onClick={handleReject}
                disabled={processing}
              >
                {processing ? (
                  <Loader2
                    size={17}
                    className="review-spin"
                  />
                ) : (
                  <XCircle size={17} />
                )}

                {processing
                  ? "Processing..."
                  : "Reject"}
              </button>

              <button
                type="button"
                className="review-approve"
                onClick={handleApprove}
                disabled={processing}
              >
                {processing ? (
                  <Loader2
                    size={17}
                    className="review-spin"
                  />
                ) : (
                  <CheckCircle2 size={17} />
                )}

                {processing
                  ? "Processing..."
                  : "Approve"}
              </button>

            </div>
          ) : (
            <div className="review-completed">

              {status === "Approved" ? (
                <CheckCircle2 size={20} />
              ) : (
                <XCircle size={20} />
              )}

              <span>
                This approval is already{" "}
                <strong>
                  {status}
                </strong>
                .
              </span>

            </div>
          )}
        </div>

        {/* EXISTING COMMENTS */}
        {approval?.comments && (
          <div className="review-card">

            <div className="review-card-header">
              <div className="review-card-title-icon">
                <MessageSquare size={18} />
              </div>

              <div>
                <h2>
                  Existing Review Comments
                </h2>

                <p>
                  Comments stored with this
                  approval request.
                </p>
              </div>
            </div>

            <div className="review-card-body">
              <div className="review-existing-comment">
                {approval.comments}
              </div>
            </div>
          </div>
        )}

        {/* FOOTER */}
        <div className="review-footer">
          <Link
            to="/approvals"
            className="review-secondary"
          >
            <ArrowLeft size={15} />
            Back to Assigned Reviews
          </Link>

          {approval?.decision_id && (
            <Link
              to={`/decisions/${approval.decision_id}`}
              className="review-secondary"
            >
              <FileText size={15} />
              View Decision
            </Link>
          )}
        </div>

      </div>
    </>
  );
}

const styles = `
.review-page {
  width: 100%;
  max-width: 1100px;
  margin: 0 auto;
  padding: 5px 0 40px;
  box-sizing: border-box;
}

.review-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 24px;
}

.review-back {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 10px;
  color: #64748b;
  text-decoration: none;
  font-size: 13px;
  font-weight: 700;
}

.review-back:hover {
  color: #2563eb;
}

.review-eyebrow {
  color: #2563eb;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: .09em;
  text-transform: uppercase;
  margin-bottom: 5px;
}

.review-header h1 {
  margin: 0;
  color: #0f172a;
  font-size: 30px;
  line-height: 1.2;
}

.review-header p {
  margin: 7px 0 0;
  color: #64748b;
  font-size: 14px;
}

.review-header-icon {
  width: 54px;
  height: 54px;
  min-width: 54px;
  border-radius: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #eaf2ff;
  color: #2563eb;
}

.review-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  margin-bottom: 18px;
  box-shadow: 0 6px 22px rgba(15, 23, 42, .045);
  overflow: hidden;
}

.review-summary {
  padding: 0;
}

.review-summary-top {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 22px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.review-summary-icon {
  width: 48px;
  height: 48px;
  min-width: 48px;
  border-radius: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #dbeafe;
  color: #2563eb;
}

.review-summary-main {
  flex: 1;
  min-width: 0;
}

.review-summary-main .review-eyebrow {
  margin-bottom: 2px;
}

.review-summary-main h2 {
  margin: 0;
  color: #0f172a;
  font-size: 21px;
}

.review-summary-main p {
  margin: 4px 0 0;
  color: #64748b;
  font-size: 12px;
}

.approval-status {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 6px 11px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 800;
  white-space: nowrap;
}

.approval-status.approved {
  background: #dcfce7;
  color: #15803d;
}

.approval-status.rejected {
  background: #fee2e2;
  color: #b91c1c;
}

.approval-status.pending {
  background: #fef3c7;
  color: #b45309;
}

.review-summary-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0;
}

.review-info {
  padding: 18px 20px;
  border-right: 1px solid #e2e8f0;
  border-bottom: 1px solid #e2e8f0;
}

.review-info:nth-child(3n) {
  border-right: 0;
}

.review-info span {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
  color: #94a3b8;
  font-size: 11px;
  font-weight: 700;
}

.review-info strong {
  color: #334155;
  font-size: 13px;
}

.review-card-header {
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 19px 22px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.review-card-title-icon {
  width: 36px;
  height: 36px;
  min-width: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #dbeafe;
  color: #2563eb;
}

.review-card-header h2 {
  margin: 0;
  color: #0f172a;
  font-size: 17px;
}

.review-card-header p {
  margin: 4px 0 0;
  color: #64748b;
  font-size: 12px;
}

.review-card-body {
  padding: 22px;
}

.review-label {
  display: block;
  margin-bottom: 8px;
  color: #334155;
  font-size: 13px;
  font-weight: 750;
}

.review-card-body textarea {
  width: 100%;
  box-sizing: border-box;
  min-height: 130px;
  padding: 13px 14px;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  background: #ffffff;
  color: #0f172a;
  font-family: inherit;
  font-size: 13px;
  line-height: 1.6;
  resize: vertical;
  outline: none;
}

.review-card-body textarea:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, .1);
}

.review-card-body textarea:disabled {
  background: #f8fafc;
  cursor: not-allowed;
}

.review-comment-help {
  margin-top: 7px;
  color: #94a3b8;
  font-size: 11px;
}

.review-action-card {
  padding: 21px 22px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}

.review-action-card h2 {
  margin: 0;
  color: #0f172a;
  font-size: 17px;
}

.review-action-card p {
  margin: 5px 0 0;
  color: #64748b;
  font-size: 12px;
}

.review-decision-buttons {
  display: flex;
  gap: 10px;
  flex-shrink: 0;
}

.review-approve,
.review-reject,
.review-primary,
.review-secondary {
  min-height: 42px;
  padding: 0 15px;
  border-radius: 9px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  font-family: inherit;
  font-size: 12px;
  font-weight: 750;
  text-decoration: none;
  cursor: pointer;
  box-sizing: border-box;
}

.review-approve {
  border: 1px solid #16a34a;
  background: #16a34a;
  color: #ffffff;
}

.review-approve:hover:not(:disabled) {
  background: #15803d;
}

.review-reject {
  border: 1px solid #dc2626;
  background: #ffffff;
  color: #dc2626;
}

.review-reject:hover:not(:disabled) {
  background: #fef2f2;
}

.review-primary {
  border: 1px solid #2563eb;
  background: #2563eb;
  color: #ffffff;
}

.review-secondary {
  border: 1px solid #cbd5e1;
  background: #ffffff;
  color: #475569;
}

.review-secondary:hover {
  background: #f8fafc;
}

.review-approve:disabled,
.review-reject:disabled,
.review-primary:disabled {
  opacity: .55;
  cursor: not-allowed;
}

.review-completed {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 11px 14px;
  border-radius: 9px;
  background: #f8fafc;
  color: #475569;
  font-size: 12px;
}

.review-alert {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 14px 16px;
  margin-bottom: 18px;
  border-radius: 11px;
  font-size: 13px;
}

.review-alert strong {
  display: block;
  margin-bottom: 3px;
}

.review-alert p {
  margin: 0;
  line-height: 1.5;
}

.review-alert.error {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
}

.review-alert.success {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #166534;
}

.review-existing-comment {
  padding: 15px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: #f8fafc;
  color: #475569;
  font-size: 13px;
  line-height: 1.65;
  white-space: pre-wrap;
}

.review-footer {
  display: flex;
  justify-content: flex-start;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 4px;
}

.review-loading {
  min-height: 420px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #64748b;
  font-size: 14px;
}

.review-spin {
  animation: reviewSpin 1s linear infinite;
}

@keyframes reviewSpin {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
}

.review-error-page {
  min-height: 420px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.review-error-icon {
  width: 56px;
  height: 56px;
  border-radius: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fef2f2;
  color: #dc2626;
  margin-bottom: 12px;
}

.review-error-page h2 {
  margin: 0 0 6px;
  color: #0f172a;
  font-size: 20px;
}

.review-error-page p {
  margin: 0 0 18px;
  color: #64748b;
  font-size: 13px;
}

.review-actions {
  display: flex;
  gap: 9px;
  flex-wrap: wrap;
  justify-content: center;
}

@media (max-width: 800px) {
  .review-summary-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .review-info:nth-child(3n) {
    border-right: 1px solid #e2e8f0;
  }

  .review-info:nth-child(2n) {
    border-right: 0;
  }

  .review-action-card {
    align-items: flex-start;
    flex-direction: column;
  }

  .review-decision-buttons {
    width: 100%;
  }

  .review-decision-buttons button {
    flex: 1;
  }
}

@media (max-width: 560px) {
  .review-page {
    padding-bottom: 25px;
  }

  .review-header {
    flex-direction: column-reverse;
  }

  .review-header-icon {
    width: 45px;
    height: 45px;
    min-width: 45px;
  }

  .review-header h1 {
    font-size: 25px;
  }

  .review-summary-top {
    align-items: flex-start;
    flex-wrap: wrap;
  }

  .review-summary-grid {
    grid-template-columns: 1fr;
  }

  .review-info,
  .review-info:nth-child(2n),
  .review-info:nth-child(3n) {
    border-right: 0;
  }

  .review-decision-buttons {
    flex-direction: column;
  }

  .review-decision-buttons button {
    width: 100%;
  }

  .review-footer {
    flex-direction: column;
  }

  .review-footer a {
    width: 100%;
  }
}
`;
