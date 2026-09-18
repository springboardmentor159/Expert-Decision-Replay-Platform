import { useCallback, useEffect, useMemo, useState, type FormEvent } from "react";
import {
  ArrowLeft,
  CheckCircle2,
  Clock3,
  FileCheck2,
  Plus,
  ShieldCheck,
  UserRound,
  X,
  XCircle,
} from "lucide-react";
import { useNavigate, useParams } from "react-router-dom";
import Alert from "../components/Alert";
import Button from "../components/Button";
import StatusBadge from "../components/StatusBadge";
import { useAuth } from "../auth/AuthContext";
import {
  getApprovals,
  createApproval,
  updateApproval,
  type Approval,
} from "../services/approvalService";
import { getUsers, type PlatformUser } from "../services/userService";
import "./ApprovalWorkflowPage.css";

function getError(error: unknown, fallback: string) {
  const response = (
    error as {
      response?: {
        status?: number;
        data?: { detail?: string };
      };
    }
  )?.response;

  if (response?.status === 401) {
    return "Your session has expired. Please sign in again.";
  }

  if (response?.status === 403) {
    return (
      response.data?.detail ||
      "You do not have permission to perform this action."
    );
  }

  if (response?.status === 404) {
    return "The requested decision or approval was not found.";
  }

  if (response?.status === 409) {
    return response.data?.detail || "That approval stage already exists.";
  }

  if (response?.status === 422) {
    return response.data?.detail || "Please check the approval information.";
  }

  if (response?.status && response.status >= 500) {
    return "The server is temporarily unavailable. Please try again.";
  }

  return response?.data?.detail || fallback;
}

function formatDate(value: string | null) {
  if (!value) return "—";

  const date = new Date(value);

  return Number.isNaN(date.getTime())
    ? "—"
    : date.toLocaleString(undefined, {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "numeric",
        minute: "2-digit",
      });
}

function variant(
  status: string
): "success" | "danger" | "warning" | "neutral" {
  const value = status.toLowerCase();

  if (value === "approved") return "success";
  if (value === "rejected") return "danger";
  if (value === "pending" || value === "under review") return "warning";

  return "neutral";
}

export default function ApprovalWorkflowPage() {
  const { decisionId } = useParams<{ decisionId: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();

  const id = Number(decisionId);

  const canAssign =
    user?.role === "manager" || user?.role === "administrator";

  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [users, setUsers] = useState<PlatformUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [updating, setUpdating] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [showAssign, setShowAssign] = useState(false);
  const [reviewerId, setReviewerId] = useState("");
  const [level, setLevel] = useState("1");

  const load = useCallback(async () => {
    if (!Number.isInteger(id) || id <= 0) {
      setError("Invalid decision identifier.");
      setLoading(false);
      return;
    }

    setLoading(true);
    setError("");

    try {
      setApprovals(await getApprovals({ decision_id: id }));
    } catch (e) {
      setError(
        getError(e, "Unable to load the approval workflow.")
      );
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    if (!canAssign) return;

    void getUsers()
      .then(setUsers)
      .catch(() => setUsers([]));
  }, [canAssign]);

  // Only actual Reviewer accounts can be selected for an approval stage.
  // Manager and Administrator approvals are handled through their own
  // authorized actions rather than being assigned as reviewers.
  const eligibleUsers = useMemo(
    () => users.filter((item) => item.role === "Reviewer"),
    [users]
  );

  const approved = approvals.filter(
    (item) => item.status.toLowerCase() === "approved"
  ).length;

  const rejected = approvals.filter(
    (item) => item.status.toLowerCase() === "rejected"
  ).length;

  const pending = approvals.filter((item) =>
    ["pending", "under review"].includes(item.status.toLowerCase())
  ).length;

  async function assign(event: FormEvent) {
    event.preventDefault();

    setError("");
    setNotice("");

    if (!reviewerId) {
      setError("Select a reviewer for the approval stage.");
      return;
    }

    setSaving(true);

    try {
      const created = await createApproval({
        decision_id: id,
        reviewer_id: Number(reviewerId),
        approval_level: Number(level),
        status: "Pending",
      });

      setApprovals((items) =>
        [...items, created].sort(
          (a, b) => a.approval_level - b.approval_level
        )
      );

      setShowAssign(false);
      setReviewerId("");
      setLevel("1");

      setNotice(
        `Approval level ${created.approval_level} assigned successfully.`
      );
    } catch (e) {
      setError(
        getError(e, "Unable to assign the approval stage.")
      );
    } finally {
      setSaving(false);
    }
  }

  async function changeStatus(
    approval: Approval,
    status: "Under Review" | "Approved" | "Rejected"
  ) {
    if (
      !window.confirm(
        `Mark approval level ${approval.approval_level} as ${status}?`
      )
    ) {
      return;
    }

    setUpdating(approval.id);
    setError("");
    setNotice("");

    try {
      const updated = await updateApproval(approval.id, { status });

      setApprovals((items) =>
        items.map((item) =>
          item.id === updated.id ? updated : item
        )
      );

      setNotice(
        `Approval level ${approval.approval_level} marked ${status.toLowerCase()}.`
      );
    } catch (e) {
      setError(
        getError(e, "Unable to update the approval.")
      );
    } finally {
      setUpdating(null);
    }
  }

  if (!Number.isInteger(id) || id <= 0) {
    return (
      <div className="approval-workflow-page">
        <Alert variant="error">
          Invalid decision identifier.
        </Alert>
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
            onClick={() => navigate(`/decisions/${id}`)}
          >
            <ArrowLeft size={15} />
            Back to Decision
          </button>

          <span className="approval-kicker">
            DECISION GOVERNANCE
          </span>

          <div className="approval-title-row">
            <div className="approval-title-icon">
              <FileCheck2 size={23} />
            </div>

            <div>
              <h1>Approval workflow</h1>
              <p>
                Assign, review, and complete the approval stages
                for this decision.
              </p>
            </div>
          </div>
        </div>

        <span className="approval-decision-chip">
          Decision #{id}
        </span>
      </header>

      {error && (
        <div className="approval-alert">
          <Alert variant="error">{error}</Alert>
        </div>
      )}

      {notice && (
        <div className="approval-alert">
          <Alert variant="success">{notice}</Alert>
        </div>
      )}

      <section className="approval-summary">
        <div className="approval-summary-card">
          <FileCheck2 size={18} />
          <div>
            <span>Total stages</span>
            <strong>{approvals.length}</strong>
          </div>
        </div>

        <div className="approval-summary-card">
          <CheckCircle2
            className="approval-summary-success"
            size={18}
          />
          <div>
            <span>Approved</span>
            <strong>{approved}</strong>
          </div>
        </div>

        <div className="approval-summary-card">
          <Clock3
            className="approval-summary-warning"
            size={18}
          />
          <div>
            <span>Pending</span>
            <strong>{pending}</strong>
          </div>
        </div>

        <div className="approval-summary-card">
          <XCircle
            className="approval-summary-danger"
            size={18}
          />
          <div>
            <span>Rejected</span>
            <strong>{rejected}</strong>
          </div>
        </div>
      </section>

      <section className="approval-workflow-card">
        <div className="approval-card-header">
          <div>
            <h2>Approval stages</h2>
            <p>
              Each stage is assigned to a reviewer or manager and
              tracked independently.
            </p>
          </div>

          {canAssign && (
            <Button
              onClick={() => {
                setShowAssign(true);
                setError("");
              }}
            >
              <Plus size={16} />
              Assign stage
            </Button>
          )}
        </div>

        {loading ? (
          <div className="approval-loading">
            <div className="approval-spinner" />
            Loading approval workflow...
          </div>
        ) : approvals.length === 0 ? (
          <div className="approval-empty">
            <FileCheck2 size={28} />

            <h3>No approval stages yet</h3>

            <p>
              {canAssign
                ? "Assign a reviewer to start the review workflow."
                : "A manager has not assigned an approval stage to this decision yet."}
            </p>

            {canAssign && (
              <Button onClick={() => setShowAssign(true)}>
                <Plus size={15} />
                Assign first stage
              </Button>
            )}
          </div>
        ) : (
          <div className="approval-list">
            {approvals.map((approval, index) => {
              const assignedUser = users.find(
                (item) => item.id === approval.reviewer_id
              );

              const isUpdating =
                updating === approval.id;

              const isAssignedReviewer =
                user?.id === approval.reviewer_id;

              const canAct =
                (user?.role === "reviewer" &&
                  isAssignedReviewer) ||
                user?.role === "manager" ||
                user?.role === "administrator";

              return (
                <article
                  className="approval-item"
                  key={approval.id}
                >
                  <div className="approval-level">
                    <span>{approval.approval_level}</span>
                  </div>

                  <div className="approval-content">
                    <div className="approval-stage-top">
                      <div>
                        <span className="approval-stage-label">
                          STAGE {index + 1}
                        </span>

                        <h3>
                          Approval level{" "}
                          {approval.approval_level}
                        </h3>
                      </div>

                      <StatusBadge
                        variant={variant(approval.status)}
                      >
                        {approval.status}
                      </StatusBadge>
                    </div>

                    <div className="approval-meta-grid">
                      <div>
                        <UserRound size={15} />
                        <span>Assigned reviewer</span>
                        <strong>
                          {assignedUser?.full_name ||
                            `User #${approval.reviewer_id}`}
                        </strong>
                      </div>

                      <div>
                        <ShieldCheck size={15} />
                        <span>Role</span>
                        <strong>
                          {assignedUser?.role || "Reviewer"}
                        </strong>
                      </div>

                      <div>
                        <Clock3 size={15} />
                        <span>Assigned</span>
                        <strong>
                          {formatDate(
                            approval.assigned_at
                          )}
                        </strong>
                      </div>

                      <div>
                        <CheckCircle2 size={15} />
                        <span>Completed</span>
                        <strong>
                          {formatDate(
                            approval.completed_at
                          )}
                        </strong>
                      </div>
                    </div>

                    {canAct &&
                      ["Pending", "Under Review"].includes(
                        approval.status
                      ) && (
                        <div className="approval-actions">
                          {user?.role === "reviewer" &&
                            approval.status === "Pending" && (
                              <Button
                                variant="secondary"
                                disabled={isUpdating}
                                onClick={() =>
                                  void changeStatus(
                                    approval,
                                    "Under Review"
                                  )
                                }
                              >
                                {isUpdating
                                  ? "Updating..."
                                  : "Start review"}
                              </Button>
                            )}

                          <Button
                            disabled={isUpdating}
                            onClick={() =>
                              void changeStatus(
                                approval,
                                "Approved"
                              )
                            }
                          >
                            {isUpdating
                              ? "Updating..."
                              : "Approve"}
                          </Button>

                          <Button
                            variant="danger"
                            disabled={isUpdating}
                            onClick={() =>
                              void changeStatus(
                                approval,
                                "Rejected"
                              )
                            }
                          >
                            {isUpdating
                              ? "Updating..."
                              : "Reject"}
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

      {showAssign && (
        <div
          className="approval-modal-backdrop"
          onMouseDown={(e) => {
            if (e.currentTarget === e.target) {
              setShowAssign(false);
            }
          }}
        >
          <section
            className="approval-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="assign-title"
          >
            <div className="approval-modal-header">
              <div>
                <span className="approval-kicker">
                  WORKFLOW SETUP
                </span>

                <h2 id="assign-title">
                  Assign approval stage
                </h2>
              </div>

              <button
                type="button"
                onClick={() => setShowAssign(false)}
                aria-label="Close"
              >
                <X size={18} />
              </button>
            </div>

            <form
              onSubmit={assign}
              className="approval-assign-form"
            >
              <label>
                Approval level

                <select
                  value={level}
                  onChange={(e) =>
                    setLevel(e.target.value)
                  }
                >
                  <option value="1">
                    Level 1 — Reviewer
                  </option>

                  <option value="2">
                    Level 2 — Manager / final approval
                  </option>
                </select>
              </label>

              <label>
                Reviewer

                <select
                  value={reviewerId}
                  onChange={(e) =>
                    setReviewerId(e.target.value)
                  }
                  required
                >
                  <option value="">
                    Select a reviewer
                  </option>

                  {eligibleUsers.map((item) => (
                    <option
                      key={item.id}
                      value={item.id}
                    >
                      {item.full_name} — {item.role}
                      {item.department
                        ? ` · ${item.department}`
                        : ""}
                    </option>
                  ))}
                </select>
              </label>

              {eligibleUsers.length === 0 && (
                <p>
                  No eligible Reviewer accounts are
                  available in your permitted user scope.
                </p>
              )}

              <p>
                Assigning a stage creates a tracked
                approval record and makes it available to
                the selected reviewer.
              </p>

              <div className="approval-modal-actions">
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => setShowAssign(false)}
                >
                  Cancel
                </Button>

                <Button
                  type="submit"
                  disabled={
                    saving || eligibleUsers.length === 0
                  }
                >
                  {saving
                    ? "Assigning..."
                    : "Assign stage"}
                </Button>
              </div>
            </form>
          </section>
        </div>
      )}
    </div>
  );
}