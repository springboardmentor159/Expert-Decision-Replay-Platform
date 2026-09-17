import { useEffect, useState } from "react";
import {
  Activity,
  ArrowLeft,
  CheckCircle2,
  Clock3,
  FileText,
  RefreshCw,
  ShieldCheck,
  ShieldAlert,
  LogIn,
  LogOut,
  XCircle,
  Trash2,
  Edit3,
  Plus,
  LockKeyhole,
  UserRound,
  Database,
} from "lucide-react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

import api from "../services/api";
import { useAuth } from "../context/useAuth";

interface DashboardActivity {
  id: number;
  action: string;
  entity_type: string;
  entity_id: number | null;
  description: string;
  created_at: string;
}

interface AuditLog {
  id: number;
  user_id: number | null;
  action: string;
  entity_type: string;
  entity_id: number | null;
  description: string;
  ip_address: string | null;
  request_method?: string | null;
  endpoint?: string | null;
  old_value?: Record<string, unknown> | null;
  new_value?: Record<string, unknown> | null;
  created_at: string;
}

interface SecurityLog {
  id: number;
  user_id: number | null;
  event_type: string;
  description: string;
  ip_address: string | null;
  created_at: string;
}

interface AccessLog {
  id: number;
  user_id: number | null;
  resource_type: string;
  resource_id: number | null;
  action: string;
  ip_address: string | null;
  created_at: string;
}

interface AuditDashboardData {
  recent_activities: DashboardActivity[];
  user_activity: DashboardActivity[];
}

type AdminTab = "audit" | "security" | "access";

function formatDateTime(dateString?: string) {
  if (!dateString) {
    return "—";
  }

  return new Date(dateString).toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function getActionClass(action: string) {
  const value = action.toLowerCase();

  if (value.includes("create")) {
    return "audit-action-create";
  }

  if (
    value.includes("update") ||
    value.includes("edit")
  ) {
    return "audit-action-update";
  }

  if (
    value.includes("approve") ||
    value.includes("complete")
  ) {
    return "audit-action-approve";
  }

  if (
    value.includes("reject") ||
    value.includes("delete")
  ) {
    return "audit-action-delete";
  }

  if (value.includes("status")) {
    return "audit-action-status";
  }

  return "audit-action-default";
}

function getActionIcon(action: string) {
  const value = action.toLowerCase();

  if (value.includes("create")) {
    return <Plus size={18} />;
  }

  if (
    value.includes("approve") ||
    value.includes("complete")
  ) {
    return <CheckCircle2 size={18} />;
  }

  if (
    value.includes("reject") ||
    value.includes("delete")
  ) {
    return value.includes("delete") ? (
      <Trash2 size={18} />
    ) : (
      <XCircle size={18} />
    );
  }

  if (
    value.includes("update") ||
    value.includes("edit")
  ) {
    return <Edit3 size={18} />;
  }

  if (value.includes("login")) {
    return <LogIn size={18} />;
  }

  if (value.includes("logout")) {
    return <LogOut size={18} />;
  }

  if (value.includes("status")) {
    return <Activity size={18} />;
  }

  return <FileText size={18} />;
}

function getErrorMessage(error: unknown) {
  if (axios.isAxiosError(error)) {
    const status = error.response?.status;

    if (status === 401) {
      return "Your session has expired. Please sign in again.";
    }

    if (status === 403) {
      return "You do not have permission to view this information.";
    }

    if (status === 404) {
      return "The requested audit information was not found.";
    }

    if (status && status >= 500) {
      return "Server error. Please try again later.";
    }

    if (error.request && !error.response) {
      return "Unable to connect to the server. Make sure the FastAPI backend is running.";
    }
  }

  return "Unable to load audit activity.";
}

function getTabLabel(tab: AdminTab) {
  if (tab === "audit") {
    return "Audit Logs";
  }

  if (tab === "security") {
    return "Security Logs";
  }

  return "Access Logs";
}

function getSecurityIcon(eventType: string) {
  const value = eventType.toLowerCase();

  if (value.includes("login")) {
    return <LogIn size={18} />;
  }

  if (value.includes("logout")) {
    return <LogOut size={18} />;
  }

  return <ShieldAlert size={18} />;
}

export default function AuditActivity() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [activities, setActivities] = useState<
    DashboardActivity[]
  >([]);

  const [auditLogs, setAuditLogs] = useState<AuditLog[]>(
    [],
  );

  const [securityLogs, setSecurityLogs] = useState<
    SecurityLog[]
  >([]);

  const [accessLogs, setAccessLogs] = useState<
    AccessLog[]
  >([]);

  const [activeTab, setActiveTab] =
    useState<AdminTab>("audit");

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const isAdministrator =
    user?.role === "Administrator";

  const loadAdminLogs = async (tab: AdminTab) => {
    try {
      setIsLoading(true);
      setError("");

      if (tab === "audit") {
        const response =
          await api.get<AuditLog[]>("/audit-logs");

        setAuditLogs(response.data);
      } else if (tab === "security") {
        const response =
          await api.get<SecurityLog[]>(
            "/security-logs",
          );

        setSecurityLogs(response.data);
      } else {
        const response =
          await api.get<AccessLog[]>(
            "/access-logs",
          );

        setAccessLogs(response.data);
      }
    } catch (error: unknown) {
      setError(getErrorMessage(error));
    } finally {
      setIsLoading(false);
    }
  };

  const loadUserActivity = async () => {
    try {
      setIsLoading(true);
      setError("");

      const response =
        await api.get<AuditDashboardData>("/dashboard");

      setActivities(
        response.data.recent_activities ?? [],
      );
    } catch (error: unknown) {
      setError(getErrorMessage(error));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const timer = window.setTimeout(() => {
      if (isAdministrator) {
        void loadAdminLogs(activeTab);
      } else {
        void loadUserActivity();
      }
    }, 0);

    return () => {
      window.clearTimeout(timer);
    };
  }, [isAdministrator, activeTab]);

  const handleRefresh = () => {
    if (isAdministrator) {
      void loadAdminLogs(activeTab);
    } else {
      void loadUserActivity();
    }
  };

  return (
    <main className="audit-page">
      <div className="audit-page-container">

        {/* PAGE HEADER */}

        <header className="audit-page-header">
          <div className="audit-heading-area">

            <div className="audit-heading-icon">
              <Activity size={25} />
            </div>

            <div>
              <p className="audit-eyebrow">
                Expert Decision Replay Platform
              </p>

              <h1>Audit &amp; Activity</h1>

              <p className="audit-subtitle">
                Review platform activity, audit events,
                security events, and access logs.
              </p>
            </div>

          </div>

          <div className="audit-user-panel">
            <div className="audit-user-avatar">
              {user?.full_name
                ?.charAt(0)
                .toUpperCase()}
            </div>

            <div className="audit-user-info">
              <strong>
                {user?.full_name}
              </strong>

              <span>
                {user?.role}
              </span>
            </div>
          </div>
        </header>

        {/* ADMIN / USER CONTEXT */}

        <section className="audit-context-card">

          <div className="audit-context-icon">
            {isAdministrator ? (
              <ShieldCheck size={24} />
            ) : (
              <Activity size={24} />
            )}
          </div>

          <div className="audit-context-content">
            <div className="audit-context-heading">
              <span className="audit-context-label">
                {isAdministrator
                  ? "ADMINISTRATOR AUDIT CENTER"
                  : "ACTIVITY AUDIT TRAIL"}
              </span>

              <span className="audit-live-indicator">
                <span />
                Live Platform Records
              </span>
            </div>

            <h2>
              {isAdministrator
                ? "System Governance & Monitoring"
                : "Your Workspace Activity"}
            </h2>

            <p>
              {isAdministrator
                ? "Monitor audit, security, and access events across the platform."
                : "Track actions performed across your decision workspace."}
            </p>
          </div>

        </section>

        {/* ADMINISTRATOR LOGS */}

        {isAdministrator ? (
          <section className="audit-system-section">

            <div className="audit-section-header">

              <div>
                <div className="audit-section-title-row">
                  <div className="audit-section-title-icon">
                    <Database size={19} />
                  </div>

                  <div>
                    <h2>
                      System Logs
                    </h2>

                    <p>
                      Administrator-only audit,
                      security, and access monitoring.
                    </p>
                  </div>
                </div>
              </div>

              <button
                type="button"
                className="audit-refresh-button"
                onClick={handleRefresh}
                disabled={isLoading}
              >
                <RefreshCw
                  size={17}
                  className={
                    isLoading
                      ? "audit-spin"
                      : ""
                  }
                />

                Refresh
              </button>

            </div>

            {/* TABS */}

            <div className="audit-tabs">

              <button
                type="button"
                className={`audit-tab ${
                  activeTab === "audit"
                    ? "active"
                    : ""
                }`}
                onClick={() =>
                  setActiveTab("audit")
                }
              >
                <ShieldCheck size={17} />

                <span>
                  Audit Logs
                </span>

                {activeTab === "audit" && (
                  <span className="audit-tab-active-dot" />
                )}
              </button>

              <button
                type="button"
                className={`audit-tab ${
                  activeTab === "security"
                    ? "active"
                    : ""
                }`}
                onClick={() =>
                  setActiveTab("security")
                }
              >
                <ShieldAlert size={17} />

                <span>
                  Security Logs
                </span>

                {activeTab === "security" && (
                  <span className="audit-tab-active-dot" />
                )}
              </button>

              <button
                type="button"
                className={`audit-tab ${
                  activeTab === "access"
                    ? "active"
                    : ""
                }`}
                onClick={() =>
                  setActiveTab("access")
                }
              >
                <LockKeyhole size={17} />

                <span>
                  Access Logs
                </span>

                {activeTab === "access" && (
                  <span className="audit-tab-active-dot" />
                )}
              </button>

            </div>

            {/* TAB CONTENT */}

            <div className="audit-log-surface">

              <div className="audit-log-surface-header">
                <div>
                  <span className="audit-surface-eyebrow">
                    SYSTEM MONITORING
                  </span>

                  <h3>
                    {getTabLabel(activeTab)}
                  </h3>
                </div>

                <div className="audit-record-status">
                  <span />
                  Monitoring
                </div>
              </div>

              {isLoading ? (
                <div className="audit-loading-state">
                  <div className="audit-loading-icon">
                    <Clock3 size={27} />
                  </div>

                  <h3>
                    Loading logs
                  </h3>

                  <p>
                    Retrieving the latest
                    platform records...
                  </p>
                </div>
              ) : error ? (
                <div className="audit-error-state">
                  <div className="audit-error-icon">
                    <XCircle size={26} />
                  </div>

                  <h3>
                    Unable to load logs
                  </h3>

                  <p>{error}</p>

                  <button
                    type="button"
                    onClick={handleRefresh}
                  >
                    <RefreshCw size={16} />
                    Try Again
                  </button>
                </div>
              ) : activeTab === "audit" ? (
                auditLogs.length === 0 ? (
                  <div className="audit-empty-state">
                    <div className="audit-empty-icon">
                      <ShieldCheck size={28} />
                    </div>

                    <h3>
                      No audit events
                    </h3>

                    <p>
                      Audit events will appear
                      here when platform actions
                      are recorded.
                    </p>
                  </div>
                ) : (
                  <div className="audit-timeline">

                    {auditLogs.map((log) => (
                      <article
                        className="audit-event"
                        key={log.id}
                      >
                        <div className="audit-event-rail">
                          <div
                            className={`audit-event-icon ${getActionClass(
                              log.action,
                            )}`}
                          >
                            {getActionIcon(
                              log.action,
                            )}
                          </div>

                          <span className="audit-event-line" />
                        </div>

                        <div className="audit-event-card">

                          <div className="audit-event-header">

                            <div className="audit-event-title">
                              <span
                                className={`audit-action-badge ${getActionClass(
                                  log.action,
                                )}`}
                              >
                                {log.action}
                              </span>

                              <span className="audit-event-time">
                                <Clock3 size={14} />
                                {formatDateTime(
                                  log.created_at,
                                )}
                              </span>
                            </div>

                            <span className="audit-event-number">
                              #{log.id}
                            </span>

                          </div>

                          <p className="audit-event-description">
                            {log.description}
                          </p>

                          <div className="audit-event-meta">

                            <span className="audit-meta-item">
                              <UserRound size={14} />
                              User{" "}
                              <strong>
                                {log.user_id ?? "—"}
                              </strong>
                            </span>

                            <span className="audit-meta-item">
                              <Database size={14} />
                              Entity{" "}
                              <strong>
                                {log.entity_type ||
                                  "—"}
                              </strong>
                            </span>

                            <span className="audit-meta-item">
                              ID{" "}
                              <strong>
                                {log.entity_id ??
                                  "—"}
                              </strong>
                            </span>

                            <span className="audit-meta-item">
                              IP{" "}
                              <strong>
                                {log.ip_address ??
                                  "—"}
                              </strong>
                            </span>

                          </div>

                        </div>
                      </article>
                    ))}

                  </div>
                )
              ) : activeTab === "security" ? (
                securityLogs.length === 0 ? (
                  <div className="audit-empty-state">
                    <div className="audit-empty-icon security">
                      <ShieldAlert size={28} />
                    </div>

                    <h3>
                      No security events
                    </h3>

                    <p>
                      Security events will appear
                      here when they are recorded.
                    </p>
                  </div>
                ) : (
                  <div className="audit-timeline">

                    {securityLogs.map((log) => (
                      <article
                        className="audit-event"
                        key={log.id}
                      >
                        <div className="audit-event-rail">
                          <div className="audit-event-icon audit-action-security">
                            {getSecurityIcon(
                              log.event_type,
                            )}
                          </div>

                          <span className="audit-event-line" />
                        </div>

                        <div className="audit-event-card">

                          <div className="audit-event-header">

                            <div className="audit-event-title">
                              <span className="audit-action-badge audit-action-security">
                                {log.event_type}
                              </span>

                              <span className="audit-event-time">
                                <Clock3 size={14} />
                                {formatDateTime(
                                  log.created_at,
                                )}
                              </span>
                            </div>

                            <span className="audit-event-number">
                              #{log.id}
                            </span>

                          </div>

                          <p className="audit-event-description">
                            {log.description}
                          </p>

                          <div className="audit-event-meta">

                            <span className="audit-meta-item">
                              <UserRound size={14} />
                              User{" "}
                              <strong>
                                {log.user_id ?? "—"}
                              </strong>
                            </span>

                            <span className="audit-meta-item">
                              IP{" "}
                              <strong>
                                {log.ip_address ??
                                  "—"}
                              </strong>
                            </span>

                          </div>

                        </div>
                      </article>
                    ))}

                  </div>
                )
              ) : accessLogs.length === 0 ? (
                <div className="audit-empty-state">
                  <div className="audit-empty-icon access">
                    <LockKeyhole size={28} />
                  </div>

                  <h3>
                    No access events
                  </h3>

                  <p>
                    Resource access events will
                    appear here when recorded.
                  </p>
                </div>
              ) : (
                <div className="audit-timeline">

                  {accessLogs.map((log) => (
                    <article
                      className="audit-event"
                      key={log.id}
                    >
                      <div className="audit-event-rail">
                        <div className="audit-event-icon audit-action-access">
                          <LockKeyhole size={18} />
                        </div>

                        <span className="audit-event-line" />
                      </div>

                      <div className="audit-event-card">

                        <div className="audit-event-header">

                          <div className="audit-event-title">
                            <span className="audit-action-badge audit-action-access">
                              {log.action}
                            </span>

                            <span className="audit-event-time">
                              <Clock3 size={14} />
                              {formatDateTime(
                                log.created_at,
                              )}
                            </span>
                          </div>

                          <span className="audit-event-number">
                            #{log.id}
                          </span>

                        </div>

                        <p className="audit-event-description">
                          {log.resource_type} resource
                          accessed.
                        </p>

                        <div className="audit-event-meta">

                          <span className="audit-meta-item">
                            <UserRound size={14} />
                            User{" "}
                            <strong>
                              {log.user_id ?? "—"}
                            </strong>
                          </span>

                          <span className="audit-meta-item">
                            Resource{" "}
                            <strong>
                              {log.resource_type ||
                                "—"}
                            </strong>
                          </span>

                          <span className="audit-meta-item">
                            ID{" "}
                            <strong>
                              {log.resource_id ??
                                "—"}
                            </strong>
                          </span>

                          <span className="audit-meta-item">
                            IP{" "}
                            <strong>
                              {log.ip_address ??
                                "—"}
                            </strong>
                          </span>

                        </div>

                      </div>
                    </article>
                  ))}

                </div>
              )}

            </div>
          </section>
        ) : (
          /* NON-ADMIN ACTIVITY */

          <section className="audit-system-section">

            <div className="audit-section-header">

              <div className="audit-section-title-row">
                <div className="audit-section-title-icon">
                  <Activity size={19} />
                </div>

                <div>
                  <h2>
                    Activity Log
                  </h2>

                  <p>
                    Recent decision, alternative,
                    discussion, and approval
                    activities.
                  </p>
                </div>
              </div>

              <button
                type="button"
                className="audit-refresh-button"
                onClick={handleRefresh}
                disabled={isLoading}
              >
                <RefreshCw
                  size={17}
                  className={
                    isLoading
                      ? "audit-spin"
                      : ""
                  }
                />

                Refresh
              </button>

            </div>

            <div className="audit-log-surface">

              <div className="audit-log-surface-header">
                <div>
                  <span className="audit-surface-eyebrow">
                    WORKSPACE ACTIVITY
                  </span>

                  <h3>
                    Recent Activity
                  </h3>
                </div>

                <div className="audit-record-status">
                  <span />
                  Activity Tracking
                </div>
              </div>

              {isLoading ? (
                <div className="audit-loading-state">
                  <div className="audit-loading-icon">
                    <Clock3 size={27} />
                  </div>

                  <h3>
                    Loading activity
                  </h3>

                  <p>
                    Retrieving your latest
                    workspace activity...
                  </p>
                </div>
              ) : error ? (
                <div className="audit-error-state">
                  <div className="audit-error-icon">
                    <XCircle size={26} />
                  </div>

                  <h3>
                    Unable to load activity
                  </h3>

                  <p>{error}</p>

                  <button
                    type="button"
                    onClick={handleRefresh}
                  >
                    <RefreshCw size={16} />
                    Try Again
                  </button>
                </div>
              ) : activities.length === 0 ? (
                <div className="audit-empty-state">
                  <div className="audit-empty-icon">
                    <Activity size={28} />
                  </div>

                  <h3>
                    No activity recorded
                  </h3>

                  <p>
                    Platform actions will appear
                    here as you work with decisions.
                  </p>
                </div>
              ) : (
                <div className="audit-timeline">

                  {activities.map((activity) => (
                    <article
                      className="audit-event"
                      key={activity.id}
                    >
                      <div className="audit-event-rail">
                        <div
                          className={`audit-event-icon ${getActionClass(
                            activity.action,
                          )}`}
                        >
                          {getActionIcon(
                            activity.action,
                          )}
                        </div>

                        <span className="audit-event-line" />
                      </div>

                      <div className="audit-event-card">

                        <div className="audit-event-header">

                          <div className="audit-event-title">
                            <span
                              className={`audit-action-badge ${getActionClass(
                                activity.action,
                              )}`}
                            >
                              {activity.action}
                            </span>

                            <span className="audit-event-time">
                              <Clock3 size={14} />
                              {formatDateTime(
                                activity.created_at,
                              )}
                            </span>
                          </div>

                          <span className="audit-event-number">
                            #{activity.id}
                          </span>

                        </div>

                        <p className="audit-event-description">
                          {activity.description}
                        </p>

                        <div className="audit-event-meta">

                          <span className="audit-meta-item">
                            <Database size={14} />
                            Entity{" "}
                            <strong>
                              {activity.entity_type ||
                                "—"}
                            </strong>
                          </span>

                          <span className="audit-meta-item">
                            ID{" "}
                            <strong>
                              {activity.entity_id ??
                                "—"}
                            </strong>
                          </span>

                        </div>

                      </div>
                    </article>
                  ))}

                </div>
              )}

            </div>
          </section>
        )}

        {/* BACK */}

        <div className="audit-back-row">
          <button
            type="button"
            className="audit-back-button"
            onClick={() =>
              navigate("/dashboard")
            }
          >
            <ArrowLeft size={17} />
            Back to Dashboard
          </button>
        </div>

      </div>
    </main>
  );
}