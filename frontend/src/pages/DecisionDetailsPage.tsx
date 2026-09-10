import { useCallback, useEffect, useState } from "react";
import {
  ArrowLeft,
  CalendarDays,
  Clock3,
  Edit3,
  FileCheck2,
  FileText,
  GitCompare,
  History,
  MessageSquare,
  Tag,
  UserRound,
} from "lucide-react";
import { Link, useNavigate, useParams } from "react-router-dom";

import Alert from "../components/Alert";
import StatusBadge from "../components/StatusBadge";
import {
  getDecision,
  type Decision,
} from "../services/decisionService";
import "./DecisionDetailsPage.css";

export default function DecisionDetailsPage() {
  const { decisionId } = useParams<{ decisionId: string }>();
  const navigate = useNavigate();

  const [decision, setDecision] = useState<Decision | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  const loadDecision = useCallback(async () => {
    if (!decisionId) {
      setErrorMessage("Invalid decision identifier.");
      setIsLoading(false);
      return;
    }

    const numericDecisionId = Number(decisionId);

    if (
      !Number.isInteger(numericDecisionId) ||
      numericDecisionId <= 0
    ) {
      setErrorMessage("Invalid decision identifier.");
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setErrorMessage("");

    try {
      const data = await getDecision(numericDecisionId);
      setDecision(data);
    } catch (error: unknown) {
      const status = (
        error as {
          response?: {
            status?: number;
          };
        }
      )?.response?.status;

      if (status === 401) {
        setErrorMessage(
          "Your session has expired. Please sign in again.",
        );
      } else if (status === 403) {
        setErrorMessage(
          "You do not have permission to view this decision.",
        );
      } else if (status === 404) {
        setErrorMessage(
          "The requested decision was not found.",
        );
      } else if (status === 422) {
        setErrorMessage(
          "The decision identifier is not valid.",
        );
      } else if (status && status >= 500) {
        setErrorMessage(
          "The server is temporarily unavailable. Please try again.",
        );
      } else {
        setErrorMessage(
          "Unable to load the decision. Please try again.",
        );
      }
    } finally {
      setIsLoading(false);
    }
  }, [decisionId]);

  useEffect(() => {
    void loadDecision();
  }, [loadDecision]);

  function getStatusVariant(
    status: string,
  ): "success" | "danger" | "warning" | "neutral" {
    const normalizedStatus = status.toLowerCase();

    if (normalizedStatus === "approved") {
      return "success";
    }

    if (normalizedStatus === "rejected") {
      return "danger";
    }

    if (
      normalizedStatus === "pending review" ||
      normalizedStatus === "pending"
    ) {
      return "warning";
    }

    return "neutral";
  }

  function formatDate(value: string) {
    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
      return "—";
    }

    return date.toLocaleDateString(undefined, {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  }

  function formatDateTime(value: string) {
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

  if (isLoading) {
    return (
      <div className="decision-details-page">
        <div
          className="decision-details-loading"
          role="status"
          aria-live="polite"
        >
          <div className="decision-details-loading-spinner" />
          <span>Loading decision...</span>
        </div>
      </div>
    );
  }

  if (errorMessage) {
    return (
      <div className="decision-details-page">
        <div className="decision-details-error">
          <Alert variant="error">{errorMessage}</Alert>

          <button
            type="button"
            className="decision-details-secondary-button"
            onClick={() => navigate("/decisions")}
          >
            <ArrowLeft size={16} aria-hidden="true" />
            Back to Decisions
          </button>
        </div>
      </div>
    );
  }

  if (!decision) {
    return (
      <div className="decision-details-page">
        <Alert variant="info">
          No decision data is available.
        </Alert>
      </div>
    );
  }

  const hasTags = Boolean(decision.tags?.trim());

  return (
    <div className="decision-details-page">
      <header className="decision-details-header">
        <div>
          <Link
            to="/decisions"
            className="decision-details-back"
          >
            <ArrowLeft size={15} aria-hidden="true" />
            Back to Decisions
          </Link>

          <div className="decision-details-kicker">
            DECISION RECORD
          </div>

          <div className="decision-details-title-row">
            <h1>{decision.title}</h1>

            <StatusBadge
              variant={getStatusVariant(decision.status)}
            >
              {decision.status}
            </StatusBadge>
          </div>

          <p className="decision-details-intro">
            Review the recorded context and information for this
            organizational decision.
          </p>
        </div>
      </header>

      <div className="decision-details-layout">
        <main className="decision-details-main">
          <section className="decision-details-card">
            <div className="decision-details-card-header">
              <div className="decision-details-card-icon">
                <FileText
                  size={19}
                  strokeWidth={1.8}
                  aria-hidden="true"
                />
              </div>

              <div>
                <h2>Decision information</h2>
                <p>
                  Core information recorded for this decision.
                </p>
              </div>
            </div>

            <div className="decision-details-content">
              <div className="decision-details-info-grid">
                <div className="decision-details-info-item">
                  <span className="decision-details-info-label">
                    Category
                  </span>

                  <strong>{decision.category || "—"}</strong>
                </div>

                <div className="decision-details-info-item">
                  <span className="decision-details-info-label">
                    Status
                  </span>

                  <strong>{decision.status || "—"}</strong>
                </div>

                <div className="decision-details-info-item">
                  <span className="decision-details-info-label">
                    Created
                  </span>

                  <strong>
                    {formatDate(decision.created_at)}
                  </strong>
                </div>

                <div className="decision-details-info-item">
                  <span className="decision-details-info-label">
                    Last updated
                  </span>

                  <strong>
                    {formatDate(decision.updated_at)}
                  </strong>
                </div>
              </div>
            </div>
          </section>

          <section className="decision-details-card">
            <div className="decision-details-card-header">
              <div className="decision-details-card-icon">
                <FileText
                  size={19}
                  strokeWidth={1.8}
                  aria-hidden="true"
                />
              </div>

              <div>
                <h2>Problem statement</h2>
                <p>
                  The situation or problem that requires a decision.
                </p>
              </div>
            </div>

            <div className="decision-details-content">
              <p className="decision-details-problem">
                {decision.problem_statement ||
                  "No problem statement recorded."}
              </p>
            </div>
          </section>

          <section className="decision-details-card">
            <div className="decision-details-card-header">
              <div className="decision-details-card-icon">
                <Tag
                  size={19}
                  strokeWidth={1.8}
                  aria-hidden="true"
                />
              </div>

              <div>
                <h2>Tags</h2>
                <p>
                  Keywords associated with this decision.
                </p>
              </div>
            </div>

            <div className="decision-details-content">
              {hasTags ? (
                <div className="decision-details-tags">
                  {decision.tags
                    ?.split(",")
                    .map((tag) => tag.trim())
                    .filter(Boolean)
                    .map((tag) => (
                      <span
                        className="decision-details-tag"
                        key={tag}
                      >
                        {tag}
                      </span>
                    ))}
                </div>
              ) : (
                <p className="decision-details-empty">
                  No tags have been added to this decision.
                </p>
              )}
            </div>
          </section>
        </main>

        <aside className="decision-details-sidebar">
          <section className="decision-details-side-card">
            <div className="decision-details-side-heading">
              <span>RECORD DETAILS</span>
            </div>

            <div className="decision-details-meta">
              <div className="decision-details-meta-item">
                <span className="decision-details-meta-icon">
                  <UserRound
                    size={15}
                    aria-hidden="true"
                  />
                </span>

                <div>
                  <span>Created by</span>
                  <strong>User #{decision.created_by}</strong>
                </div>
              </div>

              <div className="decision-details-meta-item">
                <span className="decision-details-meta-icon">
                  <CalendarDays
                    size={15}
                    aria-hidden="true"
                  />
                </span>

                <div>
                  <span>Created</span>
                  <strong>
                    {formatDateTime(decision.created_at)}
                  </strong>
                </div>
              </div>

              <div className="decision-details-meta-item">
                <span className="decision-details-meta-icon">
                  <Clock3
                    size={15}
                    aria-hidden="true"
                  />
                </span>

                <div>
                  <span>Updated</span>
                  <strong>
                    {formatDateTime(decision.updated_at)}
                  </strong>
                </div>
              </div>
            </div>
          </section>

          <section className="decision-details-side-card">
            <div className="decision-details-side-heading">
              <span>AVAILABLE ACTIONS</span>
            </div>

            <div className="decision-details-actions">
              <button
                type="button"
                className="decision-details-action-button"
                onClick={() =>
                  navigate(`/decisions/${decision.id}/edit`)
                }
              >
                <Edit3 size={16} aria-hidden="true" />

                <span>
                  <strong>Edit Decision</strong>
                  <small>
                    Update the recorded decision information.
                  </small>
                </span>
              </button>

              <button
                type="button"
                className="decision-details-action-button"
                onClick={() =>
                  navigate(
                    `/decisions/${decision.id}/history`,
                  )
                }
              >
                <History size={16} aria-hidden="true" />

                <span>
                  <strong>Version History</strong>
                  <small>
                    Review previous versions of this decision.
                  </small>
                </span>
              </button>

              <button
                type="button"
                className="decision-details-action-button"
                onClick={() =>
                  navigate(
                    `/decisions/${decision.id}/alternatives`,
                  )
                }
              >
                <GitCompare size={16} aria-hidden="true" />

                <span>
                  <strong>Alternatives &amp; Comparison</strong>
                  <small>
                    Review and compare available decision alternatives.
                  </small>
                </span>
              </button>

              <button
                type="button"
                className="decision-details-action-button"
                onClick={() =>
                  navigate(
                    `/decisions/${decision.id}/comments`,
                  )
                }
              >
                <MessageSquare
                  size={16}
                  aria-hidden="true"
                />

                <span>
                  <strong>Discussion &amp; Comments</strong>
                  <small>
                    View and participate in the decision discussion.
                  </small>
                </span>
              </button>

              <button
                type="button"
                className="decision-details-action-button"
                onClick={() =>
                  navigate(
                    `/decisions/${decision.id}/approvals`,
                  )
                }
              >
                <FileCheck2
                  size={16}
                  aria-hidden="true"
                />

                <span>
                  <strong>Approval Workflow</strong>
                  <small>
                    Track reviewer assignments and approval progress.
                  </small>
                </span>
              </button>
            </div>
          </section>
        </aside>
      </div>
    </div>
  );
}