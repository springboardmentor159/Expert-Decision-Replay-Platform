import { useEffect, useState } from "react";
import {
  Activity,
  ArrowLeft,
  CheckCircle2,
  Clock3,
  FileText,
  RefreshCw,
  ShieldCheck,
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

interface AuditDashboardData {
  recent_activities: DashboardActivity[];
  user_activity: DashboardActivity[];
}

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

  return <Activity size={18} />;
}

function getErrorMessage(error: unknown) {
  if (axios.isAxiosError(error)) {
    const status = error.response?.status;

    if (status === 401) {
      return "Your session has expired. Please sign in again.";
    }

    if (status === 403) {
      return "You do not have permission to view activity.";
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

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let isMounted = true;

    const loadInitialActivity = async () => {
      try {
        const response =
          await api.get<AuditDashboardData>("/dashboard");

        if (!isMounted) {
          return;
        }

        const data = response.data;

        const sourceActivities =
          user?.role === "Administrator" &&
          data.user_activity?.length
            ? data.user_activity
            : data.recent_activities ?? [];

        setActivities(sourceActivities);
        setError("");
      } catch (error: unknown) {
        if (!isMounted) {
          return;
        }

        setError(getErrorMessage(error));
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    loadInitialActivity();

    return () => {
      isMounted = false;
    };
  }, [user?.role]);

  const loadActivity = async () => {
    try {
      setIsLoading(true);
      setError("");

      const response =
        await api.get<AuditDashboardData>("/dashboard");

      const data = response.data;

      const sourceActivities =
        user?.role === "Administrator" &&
        data.user_activity?.length
          ? data.user_activity
          : data.recent_activities ?? [];

      setActivities(sourceActivities);
    } catch (error: unknown) {
      setError(getErrorMessage(error));
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefresh = () => {
    loadActivity();
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
            Review recent actions and platform activity.
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
          {user?.role === "Administrator" ? (
            <ShieldCheck size={24} />
          ) : (
            <Activity size={24} />
          )}
        </div>

        <div>
          <strong>Activity Audit Trail</strong>

          <p>
            Track actions performed across your
            decision workspace.
          </p>
        </div>
      </section>

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

                  <p>
                    {activity.description}
                  </p>

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

      <div className="audit-back-row">
        <button
          className="secondary-button"
          onClick={() =>
            navigate("/dashboard")
          }
        >
          <ArrowLeft size={17} />
          Back to Dashboard
        </button>
      </div>
    </main>
  );
}