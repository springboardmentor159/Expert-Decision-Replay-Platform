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
    return "audit-created";
  }

  if (
    value.includes("update") ||
    value.includes("edit")
  ) {
    return "audit-updated";
  }

  if (
    value.includes("approve") ||
    value.includes("complete")
  ) {
    return "audit-approved";
  }

  if (
    value.includes("reject") ||
    value.includes("delete")
  ) {
    return "audit-rejected";
  }

  return "audit-default";
}

function getActionIcon(action: string) {
  const value = action.toLowerCase();

  if (value.includes("create")) {
    return <FileText size={18} />;
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
    return <XCircle size={18} />;
  }

  if (
    value.includes("update") ||
    value.includes("edit")
  ) {
    return <RefreshCw size={18} />;
  }

  if (value.includes("login")) {
    return <LogIn size={18} />;
  }

  if (value.includes("logout")) {
    return <LogOut size={18} />;
  }

  return <Activity size={18} />;
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
    <main className="dashboard-page">
      <header className="dashboard-header">
        <div>
          <p className="dashboard-eyebrow">
            Expert Decision Replay Platform
          </p>

          <h1>Audit & Activity</h1>

          <p className="dashboard-subtitle">
            Review platform activity, audit events,
            security events, and access logs.
          </p>
        </div>

        <div className="dashboard-user-actions">
          <div className="dashboard-user">
            <div className="dashboard-avatar">
              {user?.full_name
                ?.charAt(0)
                .toUpperCase()}
            </div>

            <div>
              <strong>{user?.full_name}</strong>
              <span>{user?.role}</span>
            </div>
          </div>
        </div>
      </header>

      <section className="dashboard-role-banner">
        <div className="role-icon">
          {isAdministrator ? (
            <ShieldCheck size={24} />
          ) : (
            <Activity size={24} />
          )}
        </div>

        <div>
          <strong>
            {isAdministrator
              ? "Administrator Audit Center"
              : "Activity Audit Trail"}
          </strong>

          <p>
            {isAdministrator
              ? "Monitor audit, security, and access events across the platform."
              : "Track actions performed across your decision workspace."}
          </p>
        </div>
      </section>

      {isAdministrator ? (
        <section className="dashboard-section">
          <div className="section-heading">
            <div>
              <h2>System Logs</h2>

              <p>
                Administrator-only audit, security,
                and access monitoring.
              </p>
            </div>

            <button
              className="secondary-button"
              onClick={handleRefresh}
              disabled={isLoading}
            >
              <RefreshCw size={17} />
              Refresh
            </button>
          </div>

          <div
            style={{
              display: "flex",
              gap: "10px",
              marginBottom: "20px",
              flexWrap: "wrap",
            }}
          >
            <button
              className={
                activeTab === "audit"
                  ? "primary-button"
                  : "secondary-button"
              }
              onClick={() => setActiveTab("audit")}
            >
              <ShieldCheck size={17} />
              Audit Logs
            </button>

            <button
              className={
                activeTab === "security"
                  ? "primary-button"
                  : "secondary-button"
              }
              onClick={() =>
                setActiveTab("security")
              }
            >
              <ShieldAlert size={17} />
              Security Logs
            </button>

            <button
              className={
                activeTab === "access"
                  ? "primary-button"
                  : "secondary-button"
              }
              onClick={() => setActiveTab("access")}
            >
              <Activity size={17} />
              Access Logs
            </button>
          </div>

          {isLoading ? (
            <div className="empty-state">
              <Clock3 size={32} />
              <p>Loading logs...</p>
            </div>
          ) : error ? (
            <div className="dashboard-error">
              <XCircle size={42} />

              <h2>Unable to load logs</h2>

              <p>{error}</p>

              <button onClick={handleRefresh}>
                Try Again
              </button>
            </div>
          ) : activeTab === "audit" ? (
            auditLogs.length === 0 ? (
              <div className="empty-state">
                <ShieldCheck size={40} />
                <p>No audit logs recorded yet.</p>
              </div>
            ) : (
              <div className="audit-list">
                {auditLogs.map((log) => (
                  <article
                    className="audit-card"
                    key={log.id}
                  >
                    <div
                      className={`audit-icon ${getActionClass(
                        log.action,
                      )}`}
                    >
                      {getActionIcon(log.action)}
                    </div>

                    <div className="audit-content">
                      <div className="audit-top">
                        <strong>{log.action}</strong>

                        <span className="audit-time">
                          {formatDateTime(
                            log.created_at,
                          )}
                        </span>
                      </div>

                      <p>{log.description}</p>

                      <div className="audit-meta">
                        <span>
                          User: {log.user_id ?? "—"}
                        </span>

                        <span>
                          Entity:{" "}
                          {log.entity_type || "—"}
                        </span>

                        <span>
                          ID: {log.entity_id ?? "—"}
                        </span>

                        <span>
                          IP: {log.ip_address ?? "—"}
                        </span>
                      </div>
                    </div>
                  </article>
                ))}
              </div>
            )
          ) : activeTab === "security" ? (
            securityLogs.length === 0 ? (
              <div className="empty-state">
                <ShieldAlert size={40} />
                <p>
                  No security logs recorded yet.
                </p>
              </div>
            ) : (
              <div className="audit-list">
                {securityLogs.map((log) => (
                  <article
                    className="audit-card"
                    key={log.id}
                  >
                    <div className="audit-icon audit-default">
                      {log.event_type
                        .toLowerCase()
                        .includes("login") ? (
                        <LogIn size={18} />
                      ) : (
                        <ShieldAlert size={18} />
                      )}
                    </div>

                    <div className="audit-content">
                      <div className="audit-top">
                        <strong>
                          {log.event_type}
                        </strong>

                        <span className="audit-time">
                          {formatDateTime(
                            log.created_at,
                          )}
                        </span>
                      </div>

                      <p>{log.description}</p>

                      <div className="audit-meta">
                        <span>
                          User: {log.user_id ?? "—"}
                        </span>

                        <span>
                          IP: {log.ip_address ?? "—"}
                        </span>
                      </div>
                    </div>
                  </article>
                ))}
              </div>
            )
          ) : accessLogs.length === 0 ? (
            <div className="empty-state">
              <Activity size={40} />
              <p>No access logs recorded yet.</p>
            </div>
          ) : (
            <div className="audit-list">
              {accessLogs.map((log) => (
                <article
                  className="audit-card"
                  key={log.id}
                >
                  <div className="audit-icon audit-default">
                    <Activity size={18} />
                  </div>

                  <div className="audit-content">
                    <div className="audit-top">
                      <strong>{log.action}</strong>

                      <span className="audit-time">
                        {formatDateTime(
                          log.created_at,
                        )}
                      </span>
                    </div>

                    <p>
                      {log.resource_type} resource
                      accessed.
                    </p>

                    <div className="audit-meta">
                      <span>
                        User: {log.user_id ?? "—"}
                      </span>

                      <span>
                        Resource:{" "}
                        {log.resource_type || "—"}
                      </span>

                      <span>
                        ID: {log.resource_id ?? "—"}
                      </span>

                      <span>
                        IP: {log.ip_address ?? "—"}
                      </span>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
      ) : (
        <section className="dashboard-section">
          <div className="section-heading">
            <div>
              <h2>Activity Log</h2>

              <p>
                Recent decision, alternative,
                discussion, and approval activities.
              </p>
            </div>

            <button
              className="secondary-button"
              onClick={handleRefresh}
              disabled={isLoading}
            >
              <RefreshCw size={17} />
              Refresh
            </button>
          </div>

          {isLoading ? (
            <div className="empty-state">
              <Clock3 size={32} />
              <p>Loading activity...</p>
            </div>
          ) : error ? (
            <div className="dashboard-error">
              <XCircle size={42} />

              <h2>Unable to load activity</h2>

              <p>{error}</p>

              <button onClick={handleRefresh}>
                Try Again
              </button>
            </div>
          ) : activities.length === 0 ? (
            <div className="empty-state">
              <Activity size={40} />

              <p>No activity recorded yet.</p>

              <span>
                Platform actions will appear here.
              </span>
            </div>
          ) : (
            <div className="audit-list">
              {activities.map((activity) => (
                <article
                  className="audit-card"
                  key={activity.id}
                >
                  <div
                    className={`audit-icon ${getActionClass(
                      activity.action,
                    )}`}
                  >
                    {getActionIcon(activity.action)}
                  </div>

                  <div className="audit-content">
                    <div className="audit-top">
                      <strong>
                        {activity.action}
                      </strong>

                      <span className="audit-time">
                        {formatDateTime(
                          activity.created_at,
                        )}
                      </span>
                    </div>

                    <p>{activity.description}</p>

                    <div className="audit-meta">
                      <span>
                        Entity:{" "}
                        {activity.entity_type || "—"}
                      </span>

                      <span>
                        ID:{" "}
                        {activity.entity_id ?? "—"}
                      </span>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
      )}

      <div className="audit-back-row">
        <button
          className="secondary-button"
          onClick={() => navigate("/dashboard")}
        >
          <ArrowLeft size={17} />
          Back to Dashboard
        </button>
      </div>
    </main>
  );
}