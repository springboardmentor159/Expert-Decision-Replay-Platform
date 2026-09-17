import { useEffect, useState } from "react";
import {
  ArrowLeft,
  History as HistoryIcon,
  Clock,
  User,
  GitBranch,
  FileText,
  Activity,
  RefreshCw,
  CalendarDays,
  Layers3,
} from "lucide-react";
import { useNavigate, useParams } from "react-router-dom";
import { isAxiosError } from "axios";

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

function getStatusClass(status: string) {
  return status.toLowerCase().replace(/\s+/g, "-");
}

export default function History() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [history, setHistory] =
    useState<HistoryResponse | null>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  /*
   * Used by Refresh and Try Again buttons.
   * The API endpoint and response handling are unchanged.
   */
  const loadHistory = async () => {
    try {
      setIsLoading(true);
      setError("");

      const response = await api.get<HistoryResponse>(
        `/decisions/${id}/history`,
      );

      setHistory(response.data);
    } catch (err: unknown) {
      if (isAxiosError(err)) {
        const status = err.response?.status;

        if (status === 401) {
          setError(
            "Your session has expired. Please sign in again.",
          );
        } else if (status === 403) {
          setError(
            err.response?.data?.detail ||
              "You do not have permission to view this history.",
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
          setError("Unable to load decision history.");
        }
      } else {
        setError("Unable to load decision history.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  /*
   * Initial history loading.
   *
   * Kept separate from loadHistory() so the effect does not
   * directly call a function containing synchronous state
   * updates.
   */
  useEffect(() => {
    let isMounted = true;

    const loadInitialHistory = async () => {
      if (!id) {
        if (isMounted) {
          setError("Invalid decision ID.");
          setIsLoading(false);
        }

        return;
      }

      try {
        if (isMounted) {
          setIsLoading(true);
          setError("");
        }

        const response = await api.get<HistoryResponse>(
          `/decisions/${id}/history`,
        );

        if (isMounted) {
          setHistory(response.data);
        }
      } catch (err: unknown) {
        if (!isMounted) {
          return;
        }

        if (isAxiosError(err)) {
          const status = err.response?.status;

          if (status === 401) {
            setError(
              "Your session has expired. Please sign in again.",
            );
          } else if (status === 403) {
            setError(
              err.response?.data?.detail ||
                "You do not have permission to view this history.",
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
            setError("Unable to load decision history.");
          }
        } else {
          setError("Unable to load decision history.");
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    void loadInitialHistory();

    return () => {
      isMounted = false;
    };
  }, [id]);

  return (
    <main className="history-page">
      {/* PAGE HEADER */}
      <header className="history-page-header">
        <div className="history-heading-area">
          <div className="history-heading-icon">
            <HistoryIcon size={24} />
          </div>

          <div>
            <p className="history-eyebrow">
              Expert Decision Replay Platform
            </p>

            <h1>Decision History</h1>

            <p className="history-subtitle">
              Review versions, changes, and audit activity
              for Decision #{id}.
            </p>
          </div>
        </div>

        <div className="history-toolbar">
          <button
            type="button"
            className="history-refresh-button"
            onClick={() => {
              void loadHistory();
            }}
            disabled={isLoading}
            title="Refresh history"
          >
            <RefreshCw
              size={17}
              className={
                isLoading
                  ? "history-spin"
                  : ""
              }
            />

            Refresh
          </button>

          <button
            type="button"
            className="history-back-button"
            onClick={() =>
              navigate(`/decisions/${id}`)
            }
          >
            <ArrowLeft size={18} />
            Back to Decision
          </button>
        </div>
      </header>

      {/* LOADING */}
      {isLoading && (
        <section className="history-state-card">
          <div className="history-loading">
            <div className="history-spinner" />

            <div>
              <h3>Loading decision history</h3>

              <p>
                Retrieving versions and audit activity...
              </p>
            </div>
          </div>
        </section>
      )}

      {/* ERROR */}
      {!isLoading && error && (
        <section className="history-state-card history-error-card">
          <div className="history-state-icon history-error-icon">
            <Activity size={24} />
          </div>

          <div className="history-state-content">
            <p className="history-state-eyebrow">
              History unavailable
            </p>

            <h2>Unable to load history</h2>

            <p>{error}</p>

            <div className="history-error-actions">
              <button
                type="button"
                className="history-secondary-button"
                onClick={() =>
                  navigate(`/decisions/${id}`)
                }
              >
                <ArrowLeft size={17} />
                Back to Decision
              </button>

              <button
                type="button"
                className="history-primary-button"
                onClick={() => {
                  void loadHistory();
                }}
              >
                <RefreshCw size={17} />
                Try Again
              </button>
            </div>
          </div>
        </section>
      )}

      {/* MAIN CONTENT */}
      {!isLoading && !error && history && (
        <>
          {/* SUMMARY */}
          <section className="history-summary-grid">
            <div className="history-summary-card">
              <div className="history-summary-icon">
                <GitBranch size={19} />
              </div>

              <div>
                <span>Versions</span>

                <strong>
                  {history.versions.length}
                </strong>
              </div>
            </div>

            <div className="history-summary-card">
              <div className="history-summary-icon">
                <Activity size={19} />
              </div>

              <div>
                <span>Audit Activities</span>

                <strong>
                  {history.audit_logs.length}
                </strong>
              </div>
            </div>

            <div className="history-summary-card">
              <div className="history-summary-icon">
                <Layers3 size={19} />
              </div>

              <div>
                <span>Decision</span>

                <strong>
                  #{history.decision_id}
                </strong>
              </div>
            </div>
          </section>

          {/* VERSION HISTORY */}
          <section className="history-section-card">
            <div className="history-section-header">
              <div className="history-section-title">
                <div className="history-section-icon">
                  <HistoryIcon size={21} />
                </div>

                <div>
                  <h2>Version History</h2>

                  <p>
                    Track every saved version of this
                    decision.
                  </p>
                </div>
              </div>

              <div className="history-section-count">
                {history.versions.length}{" "}
                {history.versions.length === 1
                  ? "version"
                  : "versions"}
              </div>
            </div>

            {history.versions.length === 0 ? (
              <div className="history-empty-state">
                <div className="history-empty-icon">
                  <HistoryIcon size={30} />
                </div>

                <h3>No Version History</h3>

                <p>
                  No versions are available for this
                  decision.
                </p>
              </div>
            ) : (
              <div className="history-version-timeline">
                {history.versions.map(
                  (version, index) => (
                    <article
                      className="history-version-item"
                      key={version.id}
                    >
                      <div className="history-version-rail">
                        <div className="history-version-node">
                          <GitBranch size={17} />
                        </div>

                        {index !==
                          history.versions.length - 1 && (
                          <div className="history-version-line" />
                        )}
                      </div>

                      <div className="history-version-card">
                        <div className="history-version-top">
                          <div className="history-version-title">
                            <div className="history-version-number">
                              Version{" "}
                              {version.version_number}
                            </div>

                            <span
                              className={`history-status-badge ${getStatusClass(
                                version.status,
                              )}`}
                            >
                              <span className="history-status-dot" />

                              {version.status}
                            </span>
                          </div>

                          <div className="history-version-date">
                            <Clock size={15} />

                            {formatDate(
                              version.created_at,
                            )}
                          </div>
                        </div>

                        <div className="history-version-divider" />

                        <div className="history-version-fields">
                          <div className="history-detail-field">
                            <div className="history-field-label">
                              <FileText size={15} />
                              Title
                            </div>

                            <div className="history-field-value">
                              {version.title}
                            </div>
                          </div>

                          <div className="history-detail-field">
                            <div className="history-field-label">
                              <Layers3 size={15} />
                              Category
                            </div>

                            <div className="history-field-value">
                              <span className="history-category-chip">
                                {version.category}
                              </span>
                            </div>
                          </div>

                          <div className="history-detail-field history-full-field">
                            <div className="history-field-label">
                              <FileText size={15} />
                              Problem Statement
                            </div>

                            <div className="history-problem-value">
                              {version.problem_statement}
                            </div>
                          </div>
                        </div>

                        <div className="history-version-footer">
                          <div className="history-created-by">
                            <div className="history-user-avatar">
                              <User size={14} />
                            </div>

                            <span>
                              Created by User #
                              {version.created_by}
                            </span>
                          </div>

                          <div className="history-created-date">
                            <CalendarDays size={14} />

                            {formatDate(
                              version.created_at,
                            )}
                          </div>
                        </div>
                      </div>
                    </article>
                  ),
                )}
              </div>
            )}
          </section>

          {/* AUDIT TIMELINE */}
          <section className="history-section-card">
            <div className="history-section-header">
              <div className="history-section-title">
                <div className="history-section-icon">
                  <Activity size={21} />
                </div>

                <div>
                  <h2>Decision Timeline & Audit</h2>

                  <p>
                    Review important activities and
                    changes related to this decision.
                  </p>
                </div>
              </div>

              <div className="history-section-count">
                {history.audit_logs.length}{" "}
                {history.audit_logs.length === 1
                  ? "activity"
                  : "activities"}
              </div>
            </div>

            {history.audit_logs.length === 0 ? (
              <div className="history-empty-state">
                <div className="history-empty-icon">
                  <Activity size={30} />
                </div>

                <h3>No Audit Activity</h3>

                <p>
                  No audit records are available for this
                  decision.
                </p>
              </div>
            ) : (
              <div className="history-audit-timeline">
                {history.audit_logs.map(
                  (log, index) => (
                    <article
                      className="history-audit-item"
                      key={log.id}
                    >
                      <div className="history-audit-rail">
                        <div className="history-audit-node">
                          <FileText size={16} />
                        </div>

                        {index !==
                          history.audit_logs.length - 1 && (
                          <div className="history-audit-line" />
                        )}
                      </div>

                      <div className="history-audit-card">
                        <div className="history-audit-header">
                          <div>
                            <p className="history-audit-eyebrow">
                              Decision activity
                            </p>

                            <h3>{log.action}</h3>
                          </div>

                          <div className="history-audit-date">
                            <Clock size={15} />

                            {formatDate(
                              log.created_at,
                            )}
                          </div>
                        </div>

                        {log.description && (
                          <div className="history-audit-description">
                            <span>Activity</span>

                            <p>
                              {log.description}
                            </p>
                          </div>
                        )}

                        <div className="history-audit-footer">
                          <div className="history-created-by">
                            <div className="history-user-avatar">
                              <User size={14} />
                            </div>

                            <span>
                              User #{log.user_id}
                            </span>
                          </div>

                          {log.entity_type && (
                            <span className="history-entity-chip">
                              {log.entity_type}
                            </span>
                          )}
                        </div>
                      </div>
                    </article>
                  ),
                )}
              </div>
            )}
          </section>
        </>
      )}
    </main>
  );
}