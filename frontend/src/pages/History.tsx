import { useEffect, useState } from "react";
import {
  ArrowLeft,
  History as HistoryIcon,
  Clock,
  User,
  GitBranch,
  FileText,
  Activity,
} from "lucide-react";
import { useNavigate, useParams } from "react-router-dom";

import api from "../services/api";

interface DecisionVersion {
  id: number;
  decision_id: number;
  version_number: number;
  title: string;
  problem_statement: string;
  description?: string | null;
  category: string;
  status: string;
  created_by: number;
  created_at: string;
}

interface AuditLog {
  id: number;
  user_id: number;
  action: string;
  description?: string | null;
  entity_type?: string | null;
  entity_id?: number | null;
  created_at: string;
}

interface HistoryResponse {
  decision_id: number;
  versions: DecisionVersion[];
  audit_logs: AuditLog[];
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

export default function History() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [history, setHistory] =
    useState<HistoryResponse | null>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const loadHistory = async () => {
    try {
      setIsLoading(true);
      setError("");

      const response = await api.get<HistoryResponse>(
        `/decisions/${id}/history`,
      );

      setHistory(response.data);
    } catch (err: any) {
      const status = err?.response?.status;

      if (status === 401) {
        setError(
          "Your session has expired. Please sign in again.",
        );
      } else if (status === 403) {
        setError(
          err?.response?.data?.detail ||
            "You do not have permission to view this history.",
        );
      } else if (status === 404) {
        setError("Decision not found.");
      } else if (status >= 500) {
        setError(
          "Server error. Please try again later.",
        );
      } else if (err?.request) {
        setError(
          "Unable to connect to the server. Make sure FastAPI is running.",
        );
      } else {
        setError("Unable to load decision history.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (id) {
      loadHistory();
    }
  }, [id]);

  return (
    <main className="decision-details-page">
      <header className="page-header">
        <div>
          <p className="page-eyebrow">
            Expert Decision Replay Platform
          </p>

          <h1>Decision History</h1>

          <p>
            Review the version history and timeline for
            Decision #{id}.
          </p>
        </div>

        <button
          className="secondary-button"
          onClick={() => navigate(`/decisions/${id}`)}
        >
          <ArrowLeft size={18} />
          Back to Decision
        </button>
      </header>

      {isLoading && (
        <section className="decision-details-card">
          <div className="decision-loading">
            <div className="loading-spinner" />
            <p>Loading decision history...</p>
          </div>
        </section>
      )}

      {!isLoading && error && (
        <section className="decision-details-card">
          <div className="decision-error" role="alert">
            <h2>Unable to load history</h2>

            <p>{error}</p>

            <div className="form-actions">
              <button
                className="secondary-button"
                onClick={() =>
                  navigate(`/decisions/${id}`)
                }
              >
                <ArrowLeft size={18} />
                Back to Decision
              </button>

              <button
                className="primary-button"
                onClick={loadHistory}
              >
                Try Again
              </button>
            </div>
          </div>
        </section>
      )}

      {!isLoading && !error && history && (
        <>
          <section className="decision-details-card">
            <div className="details-card-header">
              <div className="details-icon">
                <HistoryIcon size={24} />
              </div>

              <div>
                <h2>Version History</h2>

                <p>
                  Track every saved version of this
                  decision.
                </p>
              </div>
            </div>

            {history.versions.length === 0 ? (
              <div className="empty-state">
                <HistoryIcon size={40} />

                <h3>No Version History</h3>

                <p>
                  No versions are available for this
                  decision.
                </p>
              </div>
            ) : (
              <div className="history-timeline">
                {history.versions.map((version) => (
                  <div
                    className="history-item"
                    key={version.id}
                  >
                    <div className="history-icon">
                      <GitBranch size={20} />
                    </div>

                    <div className="history-content">
                      <div className="history-header">
                        <div>
                          <h3>
                            Version{" "}
                            {version.version_number}
                          </h3>

                          <span className="status-badge">
                            {version.status}
                          </span>
                        </div>

                        <span className="history-date">
                          <Clock size={15} />
                          {formatDate(
                            version.created_at,
                          )}
                        </span>
                      </div>

                      <div className="history-field">
                        <strong>Title:</strong>

                        <span>
                          {version.title}
                        </span>
                      </div>

                      <div className="history-field">
                        <strong>Category:</strong>

                        <span>
                          {version.category}
                        </span>
                      </div>

                      <div className="history-field">
                        <strong>
                          Problem Statement:
                        </strong>

                        <span>
                          {version.problem_statement}
                        </span>
                      </div>

                      <div className="history-user">
                        <User size={15} />

                        Created by User #
                        {version.created_by}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>

          <section className="decision-details-card">
            <div className="details-card-header">
              <div className="details-icon">
                <Activity size={24} />
              </div>

              <div>
                <h2>Decision Timeline & Audit</h2>

                <p>
                  Review important activities and
                  changes related to this decision.
                </p>
              </div>
            </div>

            {history.audit_logs.length === 0 ? (
              <div className="empty-state">
                <Activity size={40} />

                <h3>No Audit Activity</h3>

                <p>
                  No audit records are available for
                  this decision.
                </p>
              </div>
            ) : (
              <div className="history-timeline">
                {history.audit_logs.map((log) => (
                  <div
                    className="history-item"
                    key={log.id}
                  >
                    <div className="history-icon">
                      <FileText size={20} />
                    </div>

                    <div className="history-content">
                      <div className="history-header">
                        <div>
                          <h3>{log.action}</h3>
                        </div>

                        <span className="history-date">
                          <Clock size={15} />
                          {formatDate(
                            log.created_at,
                          )}
                        </span>
                      </div>

                      {log.description && (
                        <div className="history-field">
                          <strong>
                            Activity:
                          </strong>

                          <span>
                            {log.description}
                          </span>
                        </div>
                      )}

                      <div className="history-user">
                        <User size={15} />

                        User #{log.user_id}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        </>
      )}
    </main>
  );
}