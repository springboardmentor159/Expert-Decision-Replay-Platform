import {
  useCallback,
  useEffect,
  useState,
  type CSSProperties,
} from "react";
import {
  ArrowLeft,
  Calendar,
  FileText,
  History,
  MessageSquare,
  GitBranch,
  CheckCircle2,
  Edit,
} from "lucide-react";
import { useNavigate, useParams } from "react-router-dom";
import { isAxiosError } from "axios";

import api from "../services/api";

interface Decision {
  id: number;
  title: string;
  problem_statement: string;
  category: string;
  status: string;
  created_by: number;
  created_at: string;
  updated_at: string;
}

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

export default function DecisionDetails() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [decision, setDecision] = useState<Decision | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const loadDecision = useCallback(async () => {
    if (!id) {
      setError("Invalid decision ID.");
      setIsLoading(false);
      return;
    }

    try {
      setError("");

      const response = await api.get<Decision>(
        `/decisions/${id}`,
      );

      setDecision(response.data);
    } catch (err: unknown) {
      if (isAxiosError(err)) {
        const status = err.response?.status;

        if (status === 401) {
          setError(
            "Your session has expired. Please sign in again.",
          );
        } else if (status === 403) {
          setError(
            "You do not have permission to view this decision.",
          );
        } else if (status === 404) {
          setError("Decision not found.");
        } else if (status && status >= 500) {
          setError(
            "Server error. Please try again later.",
          );
        } else if (err.request) {
          setError(
            "Unable to connect to the server. Make sure FastAPI is running.",
          );
        } else {
          setError("Unable to load the decision.");
        }
      } else {
        setError("Unable to load the decision.");
      }
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    // Intentionally load decision data when the URL ID changes.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void loadDecision();
  }, [loadDecision]);

  const backButtonStyle: CSSProperties = {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "8px",
    padding: "10px 18px",
    minWidth: "165px",
    minHeight: "42px",
    border: "1px solid #cbd5e1",
    borderRadius: "8px",
    backgroundColor: "#ffffff",
    color: "#1e293b",
    fontWeight: 600,
    fontSize: "14px",
    cursor: "pointer",
  };

  const editButtonStyle: CSSProperties = {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "8px",
    padding: "10px 20px",
    minWidth: "165px",
    minHeight: "42px",
    border: "none",
    borderRadius: "8px",
    backgroundColor: "#2563eb",
    color: "#ffffff",
    fontWeight: 600,
    fontSize: "14px",
    cursor: "pointer",
    boxShadow: "0 2px 6px rgba(0, 0, 0, 0.15)",
  };

  const retryButtonStyle: CSSProperties = {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "8px",
    padding: "10px 20px",
    minWidth: "120px",
    minHeight: "42px",
    border: "none",
    borderRadius: "8px",
    backgroundColor: "#2563eb",
    color: "#ffffff",
    fontWeight: 600,
    fontSize: "14px",
    cursor: "pointer",
  };

  if (isLoading) {
    return (
      <main className="decision-loading">
        <div className="loading-spinner" />
        <p>Loading decision...</p>
      </main>
    );
  }

  if (error) {
    return (
      <main className="decision-page">
        <section className="decision-error" role="alert">
          <h2>Unable to load decision</h2>

          <p>{error}</p>

          <div className="form-actions">
            <button
              type="button"
              className="secondary-button"
              style={backButtonStyle}
              onClick={() => navigate("/decisions")}
            >
              <ArrowLeft size={18} />
              Back to Decisions
            </button>

            <button
              type="button"
              className="primary-button"
              style={retryButtonStyle}
              onClick={() => {
                setIsLoading(true);
                void loadDecision();
              }}
            >
              Try Again
            </button>
          </div>
        </section>
      </main>
    );
  }

  if (!decision) {
    return null;
  }

  return (
    <main className="decision-details-page">
      <header className="page-header">
        <div>
          <p className="page-eyebrow">
            Expert Decision Replay Platform
          </p>

          <h1>{decision.title}</h1>

          <p>Decision #{decision.id}</p>
        </div>

        <div className="form-actions">
          <button
            type="button"
            className="secondary-button"
            style={backButtonStyle}
            onClick={() => navigate("/decisions")}
          >
            <ArrowLeft size={18} />
            Back to Decisions
          </button>

          <button
            type="button"
            className="primary-button"
            style={editButtonStyle}
            onClick={() =>
              navigate(`/decisions/${decision.id}/edit`)
            }
          >
            <Edit size={18} />
            Edit Decision
          </button>
        </div>
      </header>

      <section className="decision-details-card">
        <div className="details-card-header">
          <div className="details-icon">
            <FileText size={24} />
          </div>

          <div>
            <h2>Decision Information</h2>

            <p>
              Review the information and current status of
              this decision.
            </p>
          </div>
        </div>

        <div className="decision-info-grid">
          <div className="info-item">
            <span className="info-label">
              Decision ID
            </span>

            <strong>#{decision.id}</strong>
          </div>

          <div className="info-item">
            <span className="info-label">
              Category
            </span>

            <strong>{decision.category}</strong>
          </div>

          <div className="info-item">
            <span className="info-label">
              Status
            </span>

            <span
              className={`status-badge ${getStatusClass(
                decision.status,
              )}`}
            >
              {decision.status}
            </span>
          </div>

          <div className="info-item">
            <span className="info-label">
              Created By
            </span>

            <strong>
              User #{decision.created_by}
            </strong>
          </div>

          <div className="info-item">
            <span className="info-label">
              Created
            </span>

            <strong>
              <Calendar size={16} />
              {formatDate(decision.created_at)}
            </strong>
          </div>

          <div className="info-item">
            <span className="info-label">
              Last Updated
            </span>

            <strong>
              <Calendar size={16} />
              {formatDate(decision.updated_at)}
            </strong>
          </div>
        </div>

        <div className="details-section">
          <h3>Problem Statement</h3>

          <div className="problem-statement">
            {decision.problem_statement}
          </div>
        </div>
      </section>

      <section className="decision-details-card">
        <div className="details-card-header">
          <div className="details-icon">
            <GitBranch size={22} />
          </div>

          <div>
            <h2>Decision Workspace</h2>

            <p>
              Explore the complete decision lifecycle.
            </p>
          </div>
        </div>

        <div className="workspace-grid">
          <div
            className="workspace-item"
            onClick={() =>
              navigate(
                `/decisions/${decision.id}/alternatives`,
              )
            }
            role="button"
            tabIndex={0}
            onKeyDown={(event) => {
              if (
                event.key === "Enter" ||
                event.key === " "
              ) {
                navigate(
                  `/decisions/${decision.id}/alternatives`,
                );
              }
            }}
          >
            <FileText size={22} />

            <h3>Alternatives</h3>

            <p>
              Compare possible solutions for this decision.
            </p>

            <span>
              Open Alternative Analysis →
            </span>
          </div>

          <div
            className="workspace-item"
            onClick={() =>
              navigate(
                `/decisions/${decision.id}/discussion`,
              )
            }
            role="button"
            tabIndex={0}
            onKeyDown={(event) => {
              if (
                event.key === "Enter" ||
                event.key === " "
              ) {
                navigate(
                  `/decisions/${decision.id}/discussion`,
                );
              }
            }}
          >
            <MessageSquare size={22} />

            <h3>Discussion</h3>

            <p>
              Review comments and decision discussions.
            </p>

            <span>
              Open Discussion →
            </span>
          </div>

          <div
            className="workspace-item"
            onClick={() =>
              navigate(
                `/decisions/${decision.id}/approval`,
              )
            }
            role="button"
            tabIndex={0}
            onKeyDown={(event) => {
              if (
                event.key === "Enter" ||
                event.key === " "
              ) {
                navigate(
                  `/decisions/${decision.id}/approval`,
                );
              }
            }}
          >
            <CheckCircle2 size={22} />

            <h3>Approval</h3>

            <p>
              Track the decision approval workflow.
            </p>

            <span>
              Open Approval Workflow →
            </span>
          </div>

          <div
            className="workspace-item"
            onClick={() =>
              navigate(
                `/decisions/${decision.id}/history`,
              )
            }
            role="button"
            tabIndex={0}
            onKeyDown={(event) => {
              if (
                event.key === "Enter" ||
                event.key === " "
              ) {
                navigate(
                  `/decisions/${decision.id}/history`,
                );
              }
            }}
          >
            <History size={22} />

            <h3>History</h3>

            <p>
              Review versions and the decision timeline.
            </p>

            <span>
              Open Version History →
            </span>
          </div>
        </div>
      </section>
    </main>
  );
}