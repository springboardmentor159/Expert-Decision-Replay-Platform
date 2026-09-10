import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Activity,
  ArrowRight,
  BarChart3,
  CheckCircle2,
  Clock3,
  FileText,
  Plus,
  RefreshCw,
  ShieldCheck,
  Users,
  XCircle,
} from "lucide-react";
import { Link } from "react-router-dom";

import Alert from "../components/Alert";
import Button from "../components/Button";
import { useAuth } from "../auth/AuthContext";
import api from "../services/api";
import "./DashboardPage.css";

interface ActivityItem {
  id: number;
  user_id?: number;
  action: string;
  entity_type: string;
  entity_id: number;
  description: string;
  created_at: string;
}

interface EmployeeDashboard {
  total_decisions: number;
  draft_decisions: number;
  under_review: number;
  approved_decisions: number;
  rejected_decisions: number;
  pending_reviews: number;
  recent_activities: ActivityItem[];
}

interface ManagerDashboard {
  department: string;
  total_decisions: number;
  draft_decisions: number;
  under_review: number;
  approved_decisions: number;
  rejected_decisions: number;
  pending_approvals: number;
  recent_team_activities: ActivityItem[];
}

interface AdminDashboard {
  total_users: number;
  total_decisions: number;
  draft_decisions: number;
  under_review: number;
  approved_decisions: number;
  rejected_decisions: number;
  recent_activities: ActivityItem[];
}

type DashboardData =
  | EmployeeDashboard
  | ManagerDashboard
  | AdminDashboard;

function formatDate(value: string) {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "Unknown date";
  }

  return date.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function formatRole(role: string) {
  return role
    .toLowerCase()
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

function getInitials(name: string) {
  return name
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part.charAt(0).toUpperCase())
    .join("");
}

function getErrorMessage(error: unknown) {
  const status = (
    error as {
      response?: {
        status?: number;
      };
    }
  )?.response?.status;

  if (status === 401) {
    return "Your session has expired. Please sign in again.";
  }

  if (status === 403) {
    return "You do not have permission to access this dashboard.";
  }

  if (status === 404) {
    return "Dashboard data was not found.";
  }

  if (status && status >= 500) {
    return "The server is temporarily unavailable. Please try again.";
  }

  return "Unable to load dashboard data. Please try again.";
}

export default function DashboardPage() {
  const { user } = useAuth();

  const [data, setData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  const role = String(user?.role ?? "").toLowerCase();

  const endpoint = useMemo(() => {
    if (role === "employee") {
      return "/dashboard/employee";
    }

    if (role === "manager") {
      return "/dashboard/manager";
    }

    if (role === "administrator") {
      return "/dashboard/admin";
    }

    return null;
  }, [role]);

  const loadDashboard = useCallback(async () => {
    if (!endpoint) {
      setErrorMessage(
        "No dashboard is currently available for your role.",
      );
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setErrorMessage("");

    try {
      const response = await api.get<DashboardData>(endpoint);
      setData(response.data);
    } catch (error: unknown) {
      setErrorMessage(getErrorMessage(error));
    } finally {
      setIsLoading(false);
    }
  }, [endpoint]);

  useEffect(() => {
    void loadDashboard();
  }, [loadDashboard]);

  if (isLoading) {
    return (
      <div className="dashboard-page">
        <div
          className="dashboard-loading"
          role="status"
          aria-live="polite"
        >
          <div className="dashboard-spinner" />
          <span>Loading your workspace...</span>
        </div>
      </div>
    );
  }

  if (errorMessage) {
    return (
      <div className="dashboard-page">
        <Alert variant="error">
          {errorMessage}
        </Alert>

        <div className="dashboard-retry">
          <Button
            variant="secondary"
            onClick={() => void loadDashboard()}
          >
            <RefreshCw size={15} aria-hidden="true" />
            Retry
          </Button>
        </div>
      </div>
    );
  }

  if (!data || !user) {
    return (
      <div className="dashboard-page">
        <Alert variant="info">
          No dashboard data is available.
        </Alert>
      </div>
    );
  }

  const firstName =
    user.full_name?.trim().split(/\s+/)[0] || "there";

  const isManager =
    role === "manager" &&
    "pending_approvals" in data;

  const isAdmin =
    role === "administrator" &&
    "total_users" in data;

  const activities =
    "recent_team_activities" in data
      ? data.recent_team_activities
      : data.recent_activities;

  const pendingValue =
    "pending_approvals" in data
      ? data.pending_approvals
      : "pending_reviews" in data
        ? data.pending_reviews
        : data.under_review;

  const pendingLabel =
    "pending_approvals" in data
      ? "Pending approvals"
      : "pending_reviews" in data
        ? "Pending reviews"
        : "Under review";

  const pendingDescription =
    "pending_approvals" in data
      ? "Waiting for your attention"
      : "pending_reviews" in data
        ? "Reviews requiring attention"
        : "Decisions currently in review";

  const statusTotal =
    data.draft_decisions +
    data.under_review +
    data.approved_decisions +
    data.rejected_decisions;

  const draftPercent =
    statusTotal > 0
      ? Math.round(
          (data.draft_decisions / statusTotal) * 100,
        )
      : 0;

  const reviewPercent =
    statusTotal > 0
      ? Math.round(
          (data.under_review / statusTotal) * 100,
        )
      : 0;

  const approvedPercent =
    statusTotal > 0
      ? Math.round(
          (data.approved_decisions / statusTotal) * 100,
        )
      : 0;

  const rejectedPercent =
    statusTotal > 0
      ? Math.round(
          (data.rejected_decisions / statusTotal) * 100,
        )
      : 0;

  return (
    <div className="dashboard-page">
      {/* HEADER */}
      <header className="dashboard-header">
        <div className="dashboard-header-copy">
          <div className="dashboard-kicker">
            <span className="dashboard-kicker-dot" />
            Workspace overview
          </div>

          <h1>
            Welcome back, {firstName}
          </h1>

          <p>
            Monitor decisions, approvals, and
            organizational knowledge from one place.
          </p>

          {isManager && (
            <div className="dashboard-scope">
              <ShieldCheck
                size={14}
                aria-hidden="true"
              />
              <span>Department</span>
              <strong>{data.department}</strong>
            </div>
          )}
        </div>

        <div className="dashboard-header-actions">
          <div className="dashboard-identity">
            <div className="dashboard-identity-avatar">
              {getInitials(user.full_name || "User")}
            </div>

            <div className="dashboard-identity-content">
              <strong>{user.full_name}</strong>
              <span>
                {user.designation ||
                  formatRole(String(user.role))}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* COMMAND BAR */}
      <section className="dashboard-command-bar">
        <div>
          <span className="dashboard-command-label">
            Decision workspace
          </span>

          <h2>
            Manage your decision lifecycle
          </h2>
        </div>

        <div className="dashboard-command-actions">
          <Link
            to="/decisions"
            className="dashboard-button dashboard-button-secondary"
          >
            <FileText size={16} aria-hidden="true" />
            View decisions
          </Link>

          <Link
            to="/decisions/new"
            className="dashboard-button dashboard-button-primary"
          >
            <Plus size={17} aria-hidden="true" />
            New decision
          </Link>
        </div>
      </section>

      {/* KPI CARDS */}
      <section
        className="dashboard-kpi-grid"
        aria-label="Decision metrics"
      >
        <article className="dashboard-kpi-card dashboard-kpi-card-blue">
          <div className="dashboard-kpi-top">
            <span className="dashboard-kpi-label">
              Total decisions
            </span>

            <span className="dashboard-kpi-icon dashboard-kpi-blue">
              <FileText size={17} />
            </span>
          </div>

          <strong className="dashboard-kpi-value">
            {data.total_decisions}
          </strong>

          <span className="dashboard-kpi-meta">
            Decision records
          </span>
        </article>

        <article className="dashboard-kpi-card dashboard-kpi-card-amber">
          <div className="dashboard-kpi-top">
            <span className="dashboard-kpi-label">
              {pendingLabel}
            </span>

            <span className="dashboard-kpi-icon dashboard-kpi-amber">
              <Clock3 size={17} />
            </span>
          </div>

          <strong className="dashboard-kpi-value">
            {pendingValue}
          </strong>

          <span className="dashboard-kpi-meta">
            {pendingDescription}
          </span>
        </article>

        <article className="dashboard-kpi-card dashboard-kpi-card-green">
          <div className="dashboard-kpi-top">
            <span className="dashboard-kpi-label">
              Approved
            </span>

            <span className="dashboard-kpi-icon dashboard-kpi-green">
              <CheckCircle2 size={17} />
            </span>
          </div>

          <strong className="dashboard-kpi-value">
            {data.approved_decisions}
          </strong>

          <span className="dashboard-kpi-meta">
            Completed decisions
          </span>
        </article>

        <article
          className={`dashboard-kpi-card ${
            isAdmin
              ? "dashboard-kpi-card-purple"
              : "dashboard-kpi-card-red"
          }`}
        >
          <div className="dashboard-kpi-top">
            <span className="dashboard-kpi-label">
              {isAdmin ? "Total users" : "Rejected"}
            </span>

            <span
              className={`dashboard-kpi-icon ${
                isAdmin
                  ? "dashboard-kpi-purple"
                  : "dashboard-kpi-red"
              }`}
            >
              {isAdmin ? (
                <Users size={17} />
              ) : (
                <XCircle size={17} />
              )}
            </span>
          </div>

          <strong className="dashboard-kpi-value">
            {isAdmin
              ? data.total_users
              : data.rejected_decisions}
          </strong>

          <span className="dashboard-kpi-meta">
            {isAdmin
              ? "Registered platform users"
              : "Decisions requiring review"}
          </span>
        </article>
      </section>

      {/* ANALYTICS + ACTIVITY */}
      <section className="dashboard-main-grid">
        <article className="dashboard-surface dashboard-health-surface">
          <div className="dashboard-surface-header">
            <div>
              <span className="dashboard-surface-eyebrow">
                Analytics
              </span>

              <h2>Decision health</h2>

              <p>
                Current distribution across your
                decision records.
              </p>
            </div>

            <span className="dashboard-surface-icon dashboard-icon-purple">
              <BarChart3 size={18} />
            </span>
          </div>

          <div className="dashboard-health">
            <div className="dashboard-health-summary">
              <div className="dashboard-health-total-ring">
                <strong>{statusTotal}</strong>
                <span>Total</span>
              </div>

              <div>
                <strong className="dashboard-health-summary-title">
                  Decision portfolio
                </strong>

                <span>
                  Current lifecycle status
                </span>
              </div>
            </div>

            <div className="dashboard-health-bars">
              <div className="dashboard-health-bar">
                <div className="dashboard-health-label">
                  <span>
                    <i className="dashboard-dot dashboard-dot-draft" />
                    Draft
                  </span>

                  <strong>{draftPercent}%</strong>
                </div>

                <div className="dashboard-progress">
                  <span
                    className="dashboard-progress-draft"
                    style={{
                      width: `${draftPercent}%`,
                    }}
                  />
                </div>

                <small>
                  {data.draft_decisions} decisions
                </small>
              </div>

              <div className="dashboard-health-bar">
                <div className="dashboard-health-label">
                  <span>
                    <i className="dashboard-dot dashboard-dot-review" />
                    Under review
                  </span>

                  <strong>{reviewPercent}%</strong>
                </div>

                <div className="dashboard-progress">
                  <span
                    className="dashboard-progress-review"
                    style={{
                      width: `${reviewPercent}%`,
                    }}
                  />
                </div>

                <small>
                  {data.under_review} decisions
                </small>
              </div>

              <div className="dashboard-health-bar">
                <div className="dashboard-health-label">
                  <span>
                    <i className="dashboard-dot dashboard-dot-approved" />
                    Approved
                  </span>

                  <strong>{approvedPercent}%</strong>
                </div>

                <div className="dashboard-progress">
                  <span
                    className="dashboard-progress-approved"
                    style={{
                      width: `${approvedPercent}%`,
                    }}
                  />
                </div>

                <small>
                  {data.approved_decisions} decisions
                </small>
              </div>

              <div className="dashboard-health-bar">
                <div className="dashboard-health-label">
                  <span>
                    <i className="dashboard-dot dashboard-dot-rejected" />
                    Rejected
                  </span>

                  <strong>{rejectedPercent}%</strong>
                </div>

                <div className="dashboard-progress">
                  <span
                    className="dashboard-progress-rejected"
                    style={{
                      width: `${rejectedPercent}%`,
                    }}
                  />
                </div>

                <small>
                  {data.rejected_decisions} decisions
                </small>
              </div>
            </div>
          </div>
        </article>

        <article className="dashboard-surface dashboard-activity-surface">
          <div className="dashboard-surface-header">
            <div>
              <span className="dashboard-surface-eyebrow">
                Activity
              </span>

              <h2>Recent activity</h2>

              <p>
                {isManager
                  ? "Latest activity from your department."
                  : "Your latest platform activity."}
              </p>
            </div>

            <span className="dashboard-surface-icon dashboard-icon-blue">
              <Activity size={18} />
            </span>
          </div>

          {activities.length === 0 ? (
            <div className="dashboard-empty">
              <Activity size={18} />
              <span>No recent activity.</span>
            </div>
          ) : (
            <div className="dashboard-activity-list">
              {activities
                .slice(0, 4)
                .map((activity) => (
                  <div
                    className="dashboard-activity-row"
                    key={activity.id}
                  >
                    <div className="dashboard-activity-marker">
                      <span />
                    </div>

                    <div className="dashboard-activity-body">
                      <strong>
                        {activity.description}
                      </strong>

                      <span>
                        {activity.entity_type} #
                        {activity.entity_id}
                        <b>•</b>
                        {formatDate(activity.created_at)}
                      </span>
                    </div>

                    <span className="dashboard-activity-action">
                      {activity.action}
                    </span>
                  </div>
                ))}
            </div>
          )}

          {activities.length > 0 && (
            <Link
              to="/activity"
              className="dashboard-view-all"
            >
              View all activity
              <ArrowRight size={15} />
            </Link>
          )}
        </article>
      </section>

      {/* WORKSPACE CARD */}
      <section className="dashboard-workspace-card">
        <div className="dashboard-workspace-icon">
          <ShieldCheck size={20} />
        </div>

        <div className="dashboard-workspace-content">
          <span className="dashboard-surface-eyebrow">
            {formatRole(String(user.role))}
            workspace
          </span>

          <h2>Your decision workspace</h2>

          <p>
            Search, review, create, and manage
            decisions from one central workspace.
          </p>
        </div>

        <Link
          to="/decisions"
          className="dashboard-workspace-link"
        >
          Open workspace
          <ArrowRight size={16} />
        </Link>
      </section>
    </div>
  );
}