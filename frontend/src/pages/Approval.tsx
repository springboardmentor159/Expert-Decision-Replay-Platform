import { useEffect, useState, type FormEvent } from "react";
import {
  ArrowLeft,
  CheckCircle,
  ClipboardCheck,
  RefreshCw,
  Save,
  XCircle,
} from "lucide-react";
import { useNavigate, useParams } from "react-router-dom";

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
    } catch (err: any) {
      const status = err?.response?.status;

      if (status === 401) {
        setError(
          "Your session has expired. Please sign in again.",
        );
      } else if (status === 403) {
        setError(
          "Only Reviewers and Managers can view pending approvals.",
        );
      } else if (status === 404) {
        setError("Approval information not found.");
      } else if (status >= 500) {
        setError(
          "Server error. Please try again later.",
        );
      } else if (err?.request) {
        setError(
          "Unable to connect to the server. Make sure FastAPI is running.",
        );
      } else {
        setError("Unable to load approvals.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const loadUsers = async () => {
    try {
      const response = await api.get<User[]>("/users");

      setUsers(response.data);
    } catch {
      setUsers([]);
    }
  };

  useEffect(() => {
    loadApprovals();
    loadUsers();
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
        approval_level: Number(form.approval_level),
      });

      setForm(emptyForm);

      await loadApprovals();
    } catch (err: any) {
      const status = err?.response?.status;
      const detail = err?.response?.data?.detail;

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
          detail || "Decision or assigned user not found.",
        );
      } else if (status === 409) {
        setFormError(
          "A pending approval already exists at this level.",
        );
      } else if (status === 422) {
        setFormError(
          detail || "Please check the approval details.",
        );
      } else if (status >= 500) {
        setFormError(
          "Server error. Please try again later.",
        );
      } else if (err?.request) {
        setFormError(
          "Unable to connect to the server.",
        );
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

      await api.patch(`/approvals/${approvalId}`, {
        status: action,
      });

      await loadApprovals();
    } catch (err: any) {
      const status = err?.response?.status;
      const detail = err?.response?.data?.detail;

      if (status === 400) {
        setError(
          detail || "This approval cannot be completed.",
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
      } else if (status >= 500) {
        setError(
          "Server error. Please try again later.",
        );
      } else if (err?.request) {
        setError(
          "Unable to connect to the server.",
        );
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
    return level === 1 ? "Reviewer" : "Manager";
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
    <main className="decision-details-page">
      <header className="page-header">
        <div>
          <p className="page-eyebrow">
            Expert Decision Replay Platform
          </p>

          <h1>Approval Workflow</h1>

          <p>
            Manage approval stages for Decision #{id}.
          </p>
        </div>

        <button
          className="secondary-button"
          onClick={() =>
            navigate(`/decisions/${id}`)
          }
        >
          <ArrowLeft size={18} />
          Back to Decision
        </button>
      </header>

      {error && (
        <section
          className="decision-error"
          role="alert"
        >
          <strong>Approval Error</strong>
          <p>{error}</p>

          <button onClick={loadApprovals}>
            <RefreshCw size={17} />
            Try Again
          </button>
        </section>
      )}

      <section className="decision-details-card">
        <div className="details-card-header">
          <div className="details-icon">
            <ClipboardCheck size={22} />
          </div>

          <div>
            <h2>Approval Workflow</h2>

            <p>
              Reviewer approval is required before final
              Manager approval.
            </p>
          </div>
        </div>

        <div className="workspace-grid">
          <div className="workspace-item">
            <h3>Level 1</h3>

            <p>
              Reviewer reviews and approves the decision.
            </p>

            <span>Reviewer Approval</span>
          </div>

          <div className="workspace-item">
            <h3>Level 2</h3>

            <p>
              Manager provides the final approval.
            </p>

            <span>Manager Approval</span>
          </div>
        </div>
      </section>

      <section className="alternative-form-card">
        <div className="details-card-header">
          <div className="details-icon">
            <Save size={22} />
          </div>

          <div>
            <h2>Assign Approval</h2>

            <p>
              Assign the next approval stage to a
              Reviewer or Manager.
            </p>
          </div>
        </div>

        <form
          onSubmit={handleAssign}
          className="alternative-form"
        >
          <div className="form-group">
            <label htmlFor="approval_level">
              Approval Level
            </label>

            <select
              id="approval_level"
              name="approval_level"
              value={form.approval_level}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  approval_level: event.target.value,
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

          <div className="form-group">
            <label htmlFor="assigned_reviewer_id">
              Assign To
            </label>

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
                    form.approval_level === "1"
                  ) {
                    return user.role === "Reviewer";
                  }

                  return user.role === "Manager";
                })
                .map((user) => (
                  <option
                    key={user.id}
                    value={user.id}
                  >
                    {user.full_name} - {user.role} #
                    {user.id}
                  </option>
                ))}
            </select>
          </div>

          {formError && (
            <div
              className="auth-error"
              role="alert"
            >
              {formError}
            </div>
          )}

          <div className="form-actions">
            <button
              type="submit"
              className="primary-button"
              disabled={isSubmitting}
            >
              <Save size={18} />

              {isSubmitting
                ? "Assigning..."
                : "Assign Approval"}
            </button>
          </div>
        </form>
      </section>

      <section className="alternative-list-section">
        <div className="page-section-header">
          <div>
            <h2>Pending Approvals</h2>

            <p>
              {approvals.length} pending approval
              {approvals.length === 1
                ? ""
                : "s"} for this decision.
            </p>
          </div>

          <button
            className="secondary-button"
            onClick={loadApprovals}
          >
            <RefreshCw size={17} />
            Refresh
          </button>
        </div>

        {isLoading ? (
          <section className="decision-loading">
            <div className="loading-spinner" />

            <p>Loading approvals...</p>
          </section>
        ) : approvals.length === 0 ? (
          <section className="decision-empty">
            <ClipboardCheck size={42} />

            <h2>No pending approvals</h2>

            <p>
              There are currently no pending approvals for
              this decision.
            </p>
          </section>
        ) : (
          <div className="alternative-grid">
            {approvals.map((approval) => (
              <article
                key={approval.id}
                className="alternative-card"
              >
                <div className="alternative-card-header">
                  <div>
                    <h3>
                      {getLevelName(
                        approval.approval_level,
                      )}{" "}
                      Approval
                    </h3>

                    <span>
                      Approval #{approval.id}
                    </span>
                  </div>

                  <span className="status-badge under-review">
                    {approval.status}
                  </span>
                </div>

                <div className="alternative-metrics">
                  <div>
                    <span>Decision</span>

                    <strong>
                      #{approval.decision_id}
                    </strong>
                  </div>

                  <div>
                    <span>Assigned To</span>

                    <strong>
                      {getUserName(
                        approval.assigned_reviewer_id,
                      )}
                    </strong>
                  </div>

                  <div>
                    <span>Level</span>

                    <strong>
                      {approval.approval_level}
                    </strong>
                  </div>

                  <div>
                    <span>Created</span>

                    <strong>
                      {formatDate(
                        approval.created_at,
                      )}
                    </strong>
                  </div>
                </div>

                <div className="form-actions">
                  <button
                    className="primary-button"
                    onClick={() =>
                      handleAction(
                        approval.id,
                        "Approved",
                      )
                    }
                    disabled={
                      actionId === approval.id
                    }
                  >
                    <CheckCircle size={17} />

                    {actionId === approval.id
                      ? "Processing..."
                      : "Approve"}
                  </button>

                  <button
                    className="danger-button"
                    onClick={() =>
                      handleAction(
                        approval.id,
                        "Rejected",
                      )
                    }
                    disabled={
                      actionId === approval.id
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