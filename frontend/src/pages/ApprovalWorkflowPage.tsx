import { useCallback, useEffect, useState } from "react";
import {
  ArrowLeft,
  CheckCircle2,
  Clock3,
  FileCheck2,
  UserRound,
  XCircle,
} from "lucide-react";
import { useNavigate, useParams } from "react-router-dom";

import Alert from "../components/Alert";
import Button from "../components/Button";
import StatusBadge from "../components/StatusBadge";
import { useAuth } from "../auth/AuthContext";
import {
  getApprovals,
  updateApproval,
  type Approval,
} from "../services/approvalService";
import "./ApprovalWorkflowPage.css";

function getErrorStatus(error: unknown): number | undefined {
  return (
    error as {
      response?: {
        status?: number;
      };
    }
  )?.response?.status;
}

function getErrorMessage(
  error: unknown,
  action: string,
): string {
  const status = getErrorStatus(error);

  if (status === 401) {
    return "Your session has expired. Please sign in again.";
  }

  if (status === 403) {
    return "You do not have permission to access this approval workflow.";
  }

  if (status === 404) {
    return "The requested approval or decision was not found.";
  }

  if (status === 422) {
    return "The approval information is not valid.";
  }

  if (status && status >= 500) {
    return "The server is temporarily unavailable. Please try again.";
  }

  return `Unable to ${action}. Please try again.`;
}

function getStatusVariant(
  status: string,
): "success" | "danger" | "warning" | "neutral" {
  const normalized = status.toLowerCase();

  if (normalized === "approved") {
    return "success";
  }

  if (normalized === "rejected") {
    return "danger";
  }

  if (
    normalized === "pending" ||
    normalized === "under review"
  ) {
    return "warning";
  }

  return "neutral";
}

function formatDateTime(value: string | null): string {
  if (!value) {
    return "—";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "—";
  }

  return date.toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

export default function ApprovalWorkflowPage() {
  const { decisionId } = useParams<{ decisionId: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [updatingId, setUpdatingId] = useState<number | null>(
    null,
  );
  const [pageError, setPageError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const numericDecisionId = Number(decisionId);

  const loadApprovals = useCallback(async () => {
    if (
      !decisionId ||
      !Number.isInteger(numericDecisionId) ||
      numericDecisionId <= 0
    ) {
      setPageError("Invalid decision identifier.");
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setPageError("");

    try {
      const data = await getApprovals({
        decision_id: numericDecisionId,
      });

      setApprovals(data);
    } catch (error: unknown) {
      setPageError(
        getErrorMessage(error, "load the approval workflow"),
      );
    } finally {
      setIsLoading(false);
    }
  }, [decisionId, numericDecisionId]);

  useEffect(() => {
    void loadApprovals();
  }, [loadApprovals]);

  const canUpdateApproval =
    user?.role === "reviewer" ||
    user?.role === "manager" ||
    user?.role === "administrator";

  async function handleStatusUpdate(
    approval: Approval,
    status: string,
  ) {
    setUpdatingId(approval.id);
    setPageError("");
    setSuccessMessage("");

    try {
      const updatedApproval = await updateApproval(
        approval.id,
        {
          status,
        },
      );

      setApprovals((current) =>
        current.map((item) =>
          item.id === updatedApproval.id
            ? updatedApproval
            : item,
        ),
      );

      setSuccessMessage(
        `Approval marked as ${status.toLowerCase()}.`,
      );
    } catch (error: unknown) {
      setPageError(
        getErrorMessage(error, "update the approval"),
      );
    } finally {
      setUpdatingId(null);
    }
  }

  const approvedCount = approvals.filter(
    (approval) =>
      approval.status.toLowerCase() === "approved",
  ).length;

  const rejectedCount = approvals.filter(
    (approval) =>
      approval.status.toLowerCase() === "rejected",
  ).length;

  const pendingCount = approvals.filter((approval) => {
    const status = approval.status.toLowerCase();

    return (
      status === "pending" ||
      status === "under review"
    );
  }).length;

  if (
    !decisionId ||
    !Number.isInteger(numericDecisionId) ||
    numericDecisionId <= 0
  ) {
    return (
      <div className="approval-workflow-page">
        <div className="approval-workflow-error">
          <Alert variant="error">
            Invalid decision identifier.
          </Alert>

          <Button
            variant="secondary"
            onClick={() => navigate("/decisions")}
          >
            <ArrowLeft size={16} aria-hidden="true" />
            Back to Decisions
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="approval-workflow-page">
      <header className="approval-workflow-header">
        <div>
          <button
            type="button"
            className="approval-back-button"
            onClick={() =>
              navigate(`/decisions/${numericDecisionId}`)
            }
          >
            <ArrowLeft size={15} aria-hidden="true" />
            Back to Decision
          </button>

          <div className="approval-kicker">
            DECISION GOVERNANCE
          </div>

          <div className="approval-title-row">
            <div className="approval-title-icon">
              <FileCheck2
                size={23}
                aria-hidden="true"
              />
            </div>

            <div>
              <h1>Approval Workflow</h1>
              <p>
                Track reviewer assignments and approval progress
                for this decision.
              </p>
            </div>
          </div>
        </div>

        <div className="approval-decision-chip">
          Decision #{numericDecisionId}
        </div>
      </header>

      {pageError && (
        <div className="approval-alert">
          <Alert variant="error">{pageError}</Alert>
        </div>
      )}

      {successMessage && (
        <div className="approval-alert">
          <Alert variant="success">
            {successMessage}
          </Alert>
        </div>
      )}

      <section className="approval-summary">
        <div className="approval-summary-card">
          <div className="approval-summary-icon">
            <FileCheck2 size={18} aria-hidden="true" />
          </div>

          <div>
            <span>Total approvals</span>
            <strong>{approvals.length}</strong>
          </div>
        </div>

        <div className="approval-summary-card">
          <div className="approval-summary-icon approval-summary-success">
            <CheckCircle2 size={18} aria-hidden="true" />
          </div>

          <div>
            <span>Approved</span>
            <strong>{approvedCount}</strong>
          </div>
        </div>

        <div className="approval-summary-card">
          <div className="approval-summary-icon approval-summary-warning">
            <Clock3 size={18} aria-hidden="true" />
          </div>

          <div>
            <span>Pending</span>
            <strong>{pendingCount}</strong>
          </div>
        </div>

        <div className="approval-summary-card">
          <div className="approval-summary-icon approval-summary-danger">
            <XCircle size={18} aria-hidden="true" />
          </div>

          <div>
            <span>Rejected</span>
            <strong>{rejectedCount}</strong>
          </div>
        </div>
      </section>

      <section className="approval-workflow-card">
        <div className="approval-card-header">
          <div>
            <h2>Approval stages</h2>
            <p>
              Review the assigned approval levels and their
              current status.
            </p>
          </div>
        </div>

        {isLoading ? (
          <div
            className="approval-loading"
            role="status"
            aria-live="polite"
          >
            <div className="approval-spinner" />
            <span>Loading approval workflow...</span>
          </div>
        ) : approvals.length === 0 ? (
          <div className="approval-empty">
            <div className="approval-empty-icon">
              <FileCheck2 size={24} aria-hidden="true" />
            </div>

            <h3>No approval stages found</h3>

            <p>
              No approval assignments have been created for
              this decision yet.
            </p>
          </div>
        ) : (
          <div className="approval-list">
            {approvals.map((approval, index) => {
              const normalizedStatus =
                approval.status.toLowerCase();

              const isUpdating =
                updatingId === approval.id;

              return (
                <article
                  className="approval-item"
                  key={approval.id}
                >
                  <div className="approval-level">
                    <span>{index + 1}</span>
                  </div>

                  <div className="approval-content">
                    <div className="approval-main-row">
                      <div>
                        <div className="approval-stage-label">
                          APPROVAL LEVEL{" "}
                          {approval.approval_level}
                        </div>

                        <h3>
                          Reviewer #{approval.reviewer_id}
                        </h3>
                      </div>

                      <StatusBadge
                        variant={getStatusVariant(
                          approval.status,
                        )}
                      >
                        {approval.status}
                      </StatusBadge>
                    </div>

                    <div className="approval-meta">
                      <span>
                        <UserRound
                          size={14}
                          aria-hidden="true"
                        />
                        Reviewer #{approval.reviewer_id}
                      </span>

                      <span>
                        <Clock3
                          size={14}
                          aria-hidden="true"
                        />
                        Assigned{" "}
                        {formatDateTime(
                          approval.assigned_at,
                        )}
                      </span>

                      {approval.completed_at && (
                        <span>
                          <CheckCircle2
                            size={14}
                            aria-hidden="true"
                          />
                          Completed{" "}
                          {formatDateTime(
                            approval.completed_at,
                          )}
                        </span>
                      )}
                    </div>

                    {canUpdateApproval &&
                      normalizedStatus !== "approved" &&
                      normalizedStatus !== "rejected" && (
                        <div className="approval-actions">
                          <Button
                            onClick={() =>
                              void handleStatusUpdate(
                                approval,
                                "Approved",
                              )
                            }
                            disabled={isUpdating}
                          >
                            <CheckCircle2
                              size={15}
                              aria-hidden="true"
                            />
                            {isUpdating
                              ? "Updating..."
                              : "Approve"}
                          </Button>

                          <Button
                            variant="danger"
                            onClick={() =>
                              void handleStatusUpdate(
                                approval,
                                "Rejected",
                              )
                            }
                            disabled={isUpdating}
                          >
                            <XCircle
                              size={15}
                              aria-hidden="true"
                            />
                            Reject
                          </Button>
                        </div>
                      )}
                  </div>
                </article>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}