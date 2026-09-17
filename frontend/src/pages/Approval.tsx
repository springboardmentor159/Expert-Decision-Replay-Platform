import {
  useEffect,
  useState,
  type CSSProperties,
  type FormEvent,
} from "react";
import {
  ArrowLeft,
  CheckCircle,
  ClipboardCheck,
  RefreshCw,
  Save,
  XCircle,
  UserCheck,
  ShieldCheck,
  Clock3,
  GitBranch,
} from "lucide-react";
import { useNavigate, useParams } from "react-router-dom";
import { isAxiosError } from "axios";

import api from "../services/api";

interface Approval {
  id: number;
  decision_id: number;
  assigned_reviewer_id: number;
  approval_level: number;
  status: string;
  created_at: string;
  completed_at: string | null;
}

interface User {
  id: number;
  full_name: string;
  email: string;
  role: string;
}

const emptyForm = {
  assigned_reviewer_id: "",
  approval_level: "1",
};

function formatDate(dateString: string) {
  return new Date(dateString).toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function getStatusClass(status: string) {
  return status.toLowerCase().replace(/\s+/g, "-");
}

export default function Approval() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [form, setForm] = useState(emptyForm);

  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [actionId, setActionId] = useState<number | null>(null);

  const [error, setError] = useState("");
  const [formError, setFormError] = useState("");

  const backButtonStyle: CSSProperties = {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "8px",
    padding: "10px 18px",
    minHeight: "42px",
    border: "1px solid #cbd5e1",
    borderRadius: "9px",
    backgroundColor: "#ffffff",
    color: "#1e293b",
    fontWeight: 600,
    fontSize: "14px",
    cursor: "pointer",
  };

  const primaryButtonStyle: CSSProperties = {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "8px",
    padding: "11px 20px",
    minHeight: "44px",
    border: "none",
    borderRadius: "9px",
    backgroundColor: "#2563eb",
    color: "#ffffff",
    fontWeight: 600,
    fontSize: "14px",
    cursor: isSubmitting ? "not-allowed" : "pointer",
    boxShadow: "0 3px 8px rgba(37, 99, 235, 0.18)",
    opacity: isSubmitting ? 0.7 : 1,
  };

  const refreshButtonStyle: CSSProperties = {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "8px",
    padding: "9px 16px",
    minHeight: "40px",
    border: "1px solid #cbd5e1",
    borderRadius: "9px",
    backgroundColor: "#ffffff",
    color: "#334155",
    fontWeight: 600,
    fontSize: "14px",
    cursor: "pointer",
  };

  const retryButtonStyle: CSSProperties = {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "8px",
    padding: "10px 20px",
    minHeight: "42px",
    border: "none",
    borderRadius: "9px",
    backgroundColor: "#2563eb",
    color: "#ffffff",
    fontWeight: 600,
    fontSize: "14px",
    cursor: "pointer",
  };

  const approveButtonStyle: CSSProperties = {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "8px",
    padding: "10px 18px",
    minHeight: "40px",
    border: "none",
    borderRadius: "9px",
    backgroundColor: "#15803d",
    color: "#ffffff",
    fontWeight: 600,
    fontSize: "14px",
    cursor: "pointer",
  };

  const rejectButtonStyle: CSSProperties = {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "8px",
    padding: "10px 18px",
    minHeight: "40px",
    border: "1px solid #fecaca",
    borderRadius: "9px",
    backgroundColor: "#fff1f2",
    color: "#b91c1c",
    fontWeight: 600,
    fontSize: "14px",
    cursor: "pointer",
  };

  const loadApprovals = async () => {
    try {
      setIsLoading(true);
      setError("");

      const response = await api.get<Approval[]>(
        "/approvals/pending",
      );

      if (id) {
        const decisionApprovals = response.data.filter(
          (approval) =>
            approval.decision_id === Number(id),
        );

        setApprovals(decisionApprovals);
      } else {
        setApprovals(response.data);
      }
    } catch (err: unknown) {
      if (isAxiosError(err)) {
        const status = err.response?.status;

        if (status === 401) {
          setError(
            "Your session has expired. Please sign in again.",
          );
        } else if (status === 403) {
          setError(
            "Only Reviewers and Managers can view pending approvals.",
          );
        } else if (status === 404) {
          setError(
            "Approval information not found.",
          );
        } else if (status && status >= 500) {
          setError(
            "Server error. Please try again later.",
          );
        } else if (err.request) {
          setError(
            "Unable to connect to the server. Make sure FastAPI is running.",
          );
        } else {
          setError("Unable to load approvals.");
        }
      } else {
        setError("Unable to load approvals.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const loadUsers = async () => {
    try {
      const response =
        await api.get<User[]>("/users");

      setUsers(response.data);
    } catch {
      setUsers([]);
    }
  };

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void loadApprovals();
      void loadUsers();
    }, 0);

    return () => {
      window.clearTimeout(timer);
    };
  }, [id]);

  const handleAssign = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();

    setFormError("");

    if (!id) {
      setFormError("Invalid decision ID.");
      return;
    }

    if (!form.assigned_reviewer_id) {
      setFormError(
        "Please select a user for the approval.",
      );
      return;
    }

    try {
      setIsSubmitting(true);

      await api.post("/approvals", {
        decision_id: Number(id),
        assigned_reviewer_id: Number(
          form.assigned_reviewer_id,
        ),
        approval_level: Number(
          form.approval_level,
        ),
      });

      setForm(emptyForm);

      await loadApprovals();
    } catch (err: unknown) {
      if (isAxiosError(err)) {
        const status = err.response?.status;
        const detail =
          err.response?.data?.detail;

        if (status === 400) {
          setFormError(
            detail ||
              "The approval assignment is not valid.",
          );
        } else if (status === 403) {
          setFormError(
            "Only Managers or Administrators can assign approvals.",
          );
        } else if (status === 404) {
          setFormError(
            detail ||
              "Decision or assigned user not found.",
          );
        } else if (status === 409) {
          setFormError(
            "A pending approval already exists at this level.",
          );
        } else if (status === 422) {
          setFormError(
            detail ||
              "Please check the approval details.",
          );
        } else if (
          status &&
          status >= 500
        ) {
          setFormError(
            "Server error. Please try again later.",
          );
        } else if (err.request) {
          setFormError(
            "Unable to connect to the server.",
          );
        } else {
          setFormError(
            "Unable to assign the approval.",
          );
        }
      } else {
        setFormError(
          "Unable to assign the approval.",
        );
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleAction = async (
    approvalId: number,
    action: "Approved" | "Rejected",
  ) => {
    const message =
      action === "Approved"
        ? "Are you sure you want to approve this decision?"
        : "Are you sure you want to reject this decision?";

    if (!window.confirm(message)) {
      return;
    }

    try {
      setActionId(approvalId);
      setError("");

      await api.patch(
        `/approvals/${approvalId}`,
        {
          status: action,
        },
      );

      await loadApprovals();
    } catch (err: unknown) {
      if (isAxiosError(err)) {
        const status =
          err.response?.status;
        const detail =
          err.response?.data?.detail;

        if (status === 400) {
          setError(
            detail ||
              "This approval cannot be completed.",
          );
        } else if (status === 403) {
          setError(
            detail ||
              "You are not authorized to complete this approval.",
          );
        } else if (status === 404) {
          setError("Approval not found.");
        } else if (status === 409) {
          setError(
            detail ||
              "This approval cannot be completed because the required workflow step is not finished.",
          );
        } else if (
          status &&
          status >= 500
        ) {
          setError(
            "Server error. Please try again later.",
          );
        } else if (err.request) {
          setError(
            "Unable to connect to the server.",
          );
        } else {
          setError(
            "Unable to complete the approval.",
          );
        }
      } else {
        setError(
          "Unable to complete the approval.",
        );
      }
    } finally {
      setActionId(null);
    }
  };

  const getLevelName = (level: number) => {
    return level === 1
      ? "Reviewer"
      : "Manager";
  };

  const getUserName = (userId: number) => {
    const user = users.find(
      (item) => item.id === userId,
    );

    return user
      ? `${user.full_name} (#${user.id})`
      : `User #${userId}`;
  };

  return (
    <main className="approval-page">
      <header className="approval-header">
        <div className="approval-heading">
          <div className="approval-heading-icon">
            <ClipboardCheck size={25} />
          </div>

          <div>
            <p className="approval-eyebrow">
              Expert Decision Replay Platform
            </p>

            <h1>Approval Workflow</h1>

            <p className="approval-subtitle">
              Manage approval stages for Decision #{id}.
            </p>
          </div>
        </div>

        <button
          type="button"
          className="approval-back-button"
          style={backButtonStyle}
          onClick={() =>
            navigate(`/decisions/${id}`)
          }
        >
          <ArrowLeft size={17} />
          Back to Decision
        </button>
      </header>

      {error && (
        <section
          className="approval-error"
          role="alert"
        >
          <div className="approval-error-content">
            <div className="approval-error-icon">
              <XCircle size={20} />
            </div>

            <div>
              <strong>Approval Error</strong>
              <p>{error}</p>
            </div>
          </div>

          <button
            type="button"
            className="approval-retry-button"
            style={retryButtonStyle}
            onClick={() => {
              void loadApprovals();
            }}
          >
            <RefreshCw size={16} />
            Try Again
          </button>
        </section>
      )}

      <section className="approval-workflow-card">
        <div className="approval-section-header">
          <div className="approval-section-icon">
            <GitBranch size={21} />
          </div>

          <div>
            <span className="approval-section-label">
              GOVERNANCE FLOW
            </span>

            <h2>Approval Workflow</h2>

            <p>
              Reviewer approval is required before final Manager approval.
            </p>
          </div>
        </div>

        <div className="approval-stepper">
          <div className="approval-step">
            <div className="approval-step-marker">
              <UserCheck size={21} />
            </div>

            <div className="approval-step-content">
              <span className="approval-step-number">
                LEVEL 1
              </span>

              <h3>Reviewer Approval</h3>

              <p>
                Reviewer reviews and approves the decision.
              </p>

              <span className="approval-step-role">
                Reviewer
              </span>
            </div>
          </div>

          <div className="approval-step-line" />

          <div className="approval-step">
            <div className="approval-step-marker">
              <ShieldCheck size={21} />
            </div>

            <div className="approval-step-content">
              <span className="approval-step-number">
                LEVEL 2
              </span>

              <h3>Manager Approval</h3>

              <p>
                Manager provides the final approval.
              </p>

              <span className="approval-step-role">
                Manager
              </span>
            </div>
          </div>
        </div>
      </section>

      <section className="approval-assign-card">
        <div className="approval-section-header">
          <div className="approval-section-icon">
            <Save size={21} />
          </div>

          <div>
            <span className="approval-section-label">
              WORKFLOW CONTROL
            </span>

            <h2>Assign Approval</h2>

            <p>
              Assign the next approval stage to a Reviewer or Manager.
            </p>
          </div>
        </div>

        <form
          onSubmit={handleAssign}
          className="approval-form"
        >
          <div className="approval-form-grid">
            <div className="approval-field">
              <label htmlFor="approval_level">
                Approval Level
              </label>

              <span className="approval-field-help">
                Select which stage should be assigned.
              </span>

              <select
                id="approval_level"
                name="approval_level"
                value={form.approval_level}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    approval_level:
                      event.target.value,
                    assigned_reviewer_id:
                      "",
                  }))
                }
                disabled={isSubmitting}
              >
                <option value="1">
                  Level 1 - Reviewer
                </option>

                <option value="2">
                  Level 2 - Manager
                </option>
              </select>
            </div>

            <div className="approval-field">
              <label htmlFor="assigned_reviewer_id">
                Assign To
              </label>

              <span className="approval-field-help">
                Choose an authorized user for this stage.
              </span>

              <select
                id="assigned_reviewer_id"
                name="assigned_reviewer_id"
                value={form.assigned_reviewer_id}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    assigned_reviewer_id:
                      event.target.value,
                  }))
                }
                disabled={isSubmitting}
              >
                <option value="">
                  Select a user
                </option>

                {users
                  .filter((user) => {
                    if (
                      form.approval_level ===
                      "1"
                    ) {
                      return (
                        user.role ===
                        "Reviewer"
                      );
                    }

                    return (
                      user.role ===
                      "Manager"
                    );
                  })
                  .map((user) => (
                    <option
                      key={user.id}
                      value={user.id}
                    >
                      {user.full_name} -{" "}
                      {user.role} #
                      {user.id}
                    </option>
                  ))}
              </select>
            </div>
          </div>

          {formError && (
            <div
              className="approval-form-error"
              role="alert"
            >
              <XCircle size={18} />
              <span>{formError}</span>
            </div>
          )}

          <div className="approval-form-footer">
            <p>
              Assigning an approval creates the next workflow task for the selected user.
            </p>

            <button
              type="submit"
              className="approval-assign-button"
              style={primaryButtonStyle}
              disabled={isSubmitting}
            >
              <Save size={17} />

              {isSubmitting
                ? "Assigning..."
                : "Assign Approval"}
            </button>
          </div>
        </form>
      </section>

      <section className="approval-pending-section">
        <div className="approval-pending-header">
          <div>
            <span className="approval-section-label">
              ACTION REQUIRED
            </span>

            <h2>Pending Approvals</h2>

            <p>
              {approvals.length} pending approval
              {approvals.length === 1
                ? ""
                : "s"} for this decision.
            </p>
          </div>

          <button
            type="button"
            className="approval-refresh-button"
            style={refreshButtonStyle}
            onClick={() => {
              void loadApprovals();
            }}
          >
            <RefreshCw size={16} />
            Refresh
          </button>
        </div>

        {isLoading ? (
          <section className="approval-state-card">
            <div className="loading-spinner" />

            <h3>Loading approvals...</h3>

            <p>
              Retrieving the current approval workflow.
            </p>
          </section>
        ) : approvals.length === 0 ? (
          <section className="approval-state-card approval-empty-state">
            <div className="approval-empty-icon">
              <ClipboardCheck size={30} />
            </div>

            <h3>No pending approvals</h3>

            <p>
              There are currently no pending approvals for this decision.
            </p>
          </section>
        ) : (
          <div className="approval-card-grid">
            {approvals.map((approval) => (
              <article
                key={approval.id}
                className="approval-card"
              >
                <div className="approval-card-top">
                  <div className="approval-card-title">
                    <div className="approval-card-icon">
                      {approval.approval_level ===
                      1 ? (
                        <UserCheck size={19} />
                      ) : (
                        <ShieldCheck size={19} />
                      )}
                    </div>

                    <div>
                      <span>
                        Level{" "}
                        {approval.approval_level}
                      </span>

                      <h3>
                        {getLevelName(
                          approval.approval_level,
                        )}{" "}
                        Approval
                      </h3>
                    </div>
                  </div>

                  <span
                    className={`approval-status-badge ${getStatusClass(
                      approval.status,
                    )}`}
                  >
                    {approval.status}
                  </span>
                </div>

                <div className="approval-card-divider" />

                <div className="approval-meta-grid">
                  <div className="approval-meta-item">
                    <span>Decision</span>
                    <strong>
                      #{approval.decision_id}
                    </strong>
                  </div>

                  <div className="approval-meta-item">
                    <span>Assigned To</span>
                    <strong>
                      {getUserName(
                        approval.assigned_reviewer_id,
                      )}
                    </strong>
                  </div>

                  <div className="approval-meta-item">
                    <span>Approval Level</span>
                    <strong>
                      Level{" "}
                      {approval.approval_level}
                    </strong>
                  </div>

                  <div className="approval-meta-item">
                    <span>Created</span>
                    <strong>
                      <Clock3 size={14} />
                      {formatDate(
                        approval.created_at,
                      )}
                    </strong>
                  </div>
                </div>

                <div className="approval-card-actions">
                  <button
                    type="button"
                    className="approval-action-approve"
                    style={approveButtonStyle}
                    onClick={() =>
                      void handleAction(
                        approval.id,
                        "Approved",
                      )
                    }
                    disabled={
                      actionId ===
                      approval.id
                    }
                  >
                    <CheckCircle size={17} />

                    {actionId ===
                    approval.id
                      ? "Processing..."
                      : "Approve"}
                  </button>

                  <button
                    type="button"
                    className="approval-action-reject"
                    style={rejectButtonStyle}
                    onClick={() =>
                      void handleAction(
                        approval.id,
                        "Rejected",
                      )
                    }
                    disabled={
                      actionId ===
                      approval.id
                    }
                  >
                    <XCircle size={17} />
                    Reject
                  </button>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}