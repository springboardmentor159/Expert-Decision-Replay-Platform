import {
  useEffect,
  useState,
  type ReactNode,
} from "react";

import {
  Activity,
  BarChart3,
  CheckCircle2,
  Clock3,
  FileText,
  LogOut,
  ShieldCheck,
  Users,
  XCircle,
} from "lucide-react";

import { useNavigate } from "react-router-dom";

import axios from "axios";

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

interface DecisionItem {
  id: number;
  title: string;
  category: string;
  status: string;
  created_at?: string;
  updated_at?: string;
  created_by?: number;
}

interface ApprovalItem {
  id: number;
  decision_id: number;
  approval_level: number;
  status: string;
  created_at: string;
}

interface DashboardData {
  role: string;
  my_decisions: DecisionItem[];
  pending_reviews: DecisionItem[];
  recent_activities: DashboardActivity[];
  team_decisions: DecisionItem[];
  pending_approvals: ApprovalItem[];
  decision_statistics: Record<string, number>;
  system_analytics: Record<string, number>;
  user_activity: DashboardActivity[];
  organization_reports: {
    decision_statistics?: Record<string, number>;
    total_users?: number;
    total_decisions?: number;
    total_approvals?: number;
  };
}

function formatDate(dateString?: string) {
  if (!dateString) {
    return "—";
  }

  return new Date(dateString).toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function getStatusClass(status: string) {
  return status.toLowerCase().replace(/\s+/g, "-");
}

export default function Dashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [dashboard, setDashboard] =
    useState<DashboardData | null>(null);

  const [isLoading, setIsLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  useEffect(() => {
    let isMounted = true;

    const loadDashboard = async () => {
      try {
        const response =
          await api.get<DashboardData>("/dashboard");

        if (!isMounted) {
          return;
        }

        setDashboard(response.data);
        setError("");
      } catch (err: unknown) {
        if (!isMounted) {
          return;
        }

        if (axios.isAxiosError(err)) {
          const status =
            err.response?.status;

          if (status === 401) {
            setError(
              "Your session has expired. Please sign in again.",
            );
          } else if (status === 403) {
            setError(
              "You do not have permission to view this dashboard.",
            );
          } else if (
            status !== undefined &&
            status >= 500
          ) {
            setError(
              "Server error. Please try again later.",
            );
          } else if (err.request) {
            setError(
              "Unable to connect to the server. Make sure the FastAPI backend is running.",
            );
          } else {
            setError(
              "Unable to load dashboard data.",
            );
          }
        } else {
          setError(
            "Unable to load dashboard data.",
          );
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    loadDashboard();

    return () => {
      isMounted = false;
    };
  }, []);

  const handleLogout = async () => {
    await logout();

    navigate("/login", {
      replace: true,
    });
  };

  if (isLoading) {
    return (
      <main className="dashboard-page">
        <div className="dashboard-loading">
          <div className="loading-spinner" />

          <p>
            Loading dashboard...
          </p>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="dashboard-page">
        <div className="dashboard-error">
          <XCircle size={42} />

          <h2>
            Unable to load dashboard
          </h2>

          <p>{error}</p>

          <button
            onClick={() =>
              window.location.reload()
            }
          >
            Try Again
          </button>
        </div>
      </main>
    );
  }

  if (!dashboard || !user) {
    return null;
  }

  const role = dashboard.role;

  return (
    <main className="dashboard-page">
      <header className="dashboard-header">
        <div>
          <p className="dashboard-eyebrow">
            Expert Decision Replay Platform
          </p>

          <h1>
            Welcome, {user.full_name}
          </h1>

          <p className="dashboard-subtitle">
            Here's what's happening with your
            decisions today.
          </p>
        </div>

        <div className="dashboard-user-actions">
          <div className="dashboard-user">
            <div className="dashboard-avatar">
              {user.full_name
                .charAt(0)
                .toUpperCase()}
            </div>

            <div>
              <strong>
                {user.full_name}
              </strong>

              <span>{role}</span>
            </div>
          </div>

          <button
            className="logout-button"
            onClick={handleLogout}
            title="Logout"
          >
            <LogOut size={18} />

            Logout
          </button>
        </div>
      </header>

      <section className="dashboard-role-banner">
        <div className="role-icon">
          {role === "Administrator" ? (
            <ShieldCheck size={24} />
          ) : role === "Manager" ? (
            <Users size={24} />
          ) : (
            <FileText size={24} />
          )}
        </div>

        <div>
          <strong>
            {role} Dashboard
          </strong>

          <p>
            {role === "Employee"
              ? "Track your decisions and review status."
              : role === "Reviewer"
                ? "Review decisions and monitor recent activity."
                : role === "Manager"
                  ? "Monitor team decisions and pending approvals."
                  : "Monitor organization-wide decisions and activity."}
          </p>
        </div>
      </section>

      {role === "Employee" && (
        <>
          <section className="dashboard-section">
            <div className="section-heading">
              <div>
                <h2>
                  My Decisions
                </h2>

                <p>
                  Decisions created by you.
                </p>
              </div>

              <span className="section-count">
                {dashboard.my_decisions.length}
              </span>
            </div>

            <div className="decision-grid">
              {dashboard.my_decisions.length ===
              0 ? (
                <div className="empty-state">
                  <FileText size={32} />

                  <p>
                    No decisions created yet.
                  </p>
                </div>
              ) : (
                dashboard.my_decisions.map(
                  (decision) => (
                    <article
                      className="decision-card"
                      key={decision.id}
                    >
                      <div className="decision-card-top">
                        <span className="decision-category">
                          {decision.category}
                        </span>

                        <span
                          className={`status-badge ${getStatusClass(
                            decision.status,
                          )}`}
                        >
                          {decision.status}
                        </span>
                      </div>

                      <h3>
                        {decision.title}
                      </h3>

                      <p>
                        Created{" "}
                        {formatDate(
                          decision.created_at,
                        )}
                      </p>
                    </article>
                  ),
                )
              )}
            </div>
          </section>

          <section className="dashboard-section">
            <div className="section-heading">
              <div>
                <h2>
                  Pending Reviews
                </h2>

                <p>
                  Your decisions currently under review.
                </p>
              </div>

              <Clock3 size={22} />
            </div>

            <div className="simple-list">
              {dashboard.pending_reviews.length ===
              0 ? (
                <div className="empty-state">
                  <CheckCircle2 size={32} />

                  <p>
                    No pending reviews.
                  </p>
                </div>
              ) : (
                dashboard.pending_reviews.map(
                  (decision) => (
                    <div
                      className="list-row"
                      key={decision.id}
                    >
                      <div>
                        <strong>
                          {decision.title}
                        </strong>

                        <span>
                          {decision.category}
                        </span>
                      </div>

                      <div className="list-row-right">
                        <span className="status-badge under-review">
                          {decision.status}
                        </span>

                        <small>
                          {formatDate(
                            decision.updated_at,
                          )}
                        </small>
                      </div>
                    </div>
                  ),
                )
              )}
            </div>
          </section>
        </>
      )}

      {role === "Reviewer" && (
        <section className="dashboard-section">
          <div className="section-heading">
            <div>
              <h2>
                Pending Reviews
              </h2>

              <p>
                Decisions requiring your attention.
              </p>
            </div>

            <Clock3 size={22} />
          </div>

          <div className="simple-list">
            {dashboard.pending_reviews.length ===
            0 ? (
              <div className="empty-state">
                <CheckCircle2 size={32} />

                <p>
                  No pending reviews.
                </p>
              </div>
            ) : (
              dashboard.pending_reviews.map(
                (decision) => (
                  <div
                    className="list-row"
                    key={decision.id}
                  >
                    <div>
                      <strong>
                        {decision.title}
                      </strong>

                      <span>
                        {decision.category}
                      </span>
                    </div>

                    <span className="status-badge under-review">
                      {decision.status}
                    </span>
                  </div>
                ),
              )
            )}
          </div>
        </section>
      )}

      {role === "Manager" && (
        <>
          <section className="stats-grid">
            <StatCard
              icon={<FileText size={22} />}
              title="Draft"
              value={
                dashboard
                  .decision_statistics["Draft"] ??
                0
              }
            />

            <StatCard
              icon={<Clock3 size={22} />}
              title="Under Review"
              value={
                dashboard
                  .decision_statistics[
                    "Under Review"
                  ] ?? 0
              }
            />

            <StatCard
              icon={<CheckCircle2 size={22} />}
              title="Approved"
              value={
                dashboard
                  .decision_statistics[
                    "Approved"
                  ] ?? 0
              }
            />

            <StatCard
              icon={<XCircle size={22} />}
              title="Rejected"
              value={
                dashboard
                  .decision_statistics[
                    "Rejected"
                  ] ?? 0
              }
            />
          </section>

          <section className="dashboard-section">
            <div className="section-heading">
              <div>
                <h2>
                  Team Decisions
                </h2>

                <p>
                  Recent decisions from your department.
                </p>
              </div>
            </div>

            <div className="decision-grid">
              {dashboard.team_decisions.length ===
              0 ? (
                <div className="empty-state">
                  <FileText size={32} />

                  <p>
                    No team decisions found.
                  </p>
                </div>
              ) : (
                dashboard.team_decisions.map(
                  (decision) => (
                    <article
                      className="decision-card"
                      key={decision.id}
                    >
                      <div className="decision-card-top">
                        <span className="decision-category">
                          {decision.category}
                        </span>

                        <span
                          className={`status-badge ${getStatusClass(
                            decision.status,
                          )}`}
                        >
                          {decision.status}
                        </span>
                      </div>

                      <h3>
                        {decision.title}
                      </h3>

                      <p>
                        Created{" "}
                        {formatDate(
                          decision.created_at,
                        )}
                      </p>
                    </article>
                  ),
                )
              )}
            </div>
          </section>

          <section className="dashboard-section">
            <div className="section-heading">
              <div>
                <h2>
                  Pending Approvals
                </h2>

                <p>
                  Approvals assigned to you.
                </p>
              </div>
            </div>

            <div className="simple-list">
              {dashboard.pending_approvals.length ===
              0 ? (
                <div className="empty-state">
                  <CheckCircle2 size={32} />

                  <p>
                    No pending approvals.
                  </p>
                </div>
              ) : (
                dashboard.pending_approvals.map(
                  (approval) => (
                    <div
                      className="list-row"
                      key={approval.id}
                    >
                      <div>
                        <strong>
                          Decision #
                          {approval.decision_id}
                        </strong>

                        <span>
                          Approval Level{" "}
                          {approval.approval_level}
                        </span>
                      </div>

                      <span className="status-badge pending">
                        {approval.status}
                      </span>
                    </div>
                  ),
                )
              )}
            </div>
          </section>
        </>
      )}

      {role === "Administrator" && (
        <>
          <section className="stats-grid">
            <StatCard
              icon={<Users size={22} />}
              title="Total Users"
              value={
                dashboard
                  .system_analytics
                  .total_users ?? 0
              }
            />

            <StatCard
              icon={<FileText size={22} />}
              title="Total Decisions"
              value={
                dashboard
                  .system_analytics
                  .total_decisions ?? 0
              }
            />

            <StatCard
              icon={<BarChart3 size={22} />}
              title="Total Approvals"
              value={
                dashboard
                  .system_analytics
                  .total_approvals ?? 0
              }
            />

            <StatCard
              icon={<Clock3 size={22} />}
              title="Pending Approvals"
              value={
                dashboard
                  .system_analytics
                  .pending_approvals ?? 0
              }
            />
          </section>

          <section className="dashboard-section">
            <div className="section-heading">
              <div>
                <h2>
                  Organization Reports
                </h2>

                <p>
                  Decision statistics across the organization.
                </p>
              </div>

              <BarChart3 size={22} />
            </div>

            <div className="stats-grid compact">
              {Object.entries(
                dashboard
                  .organization_reports
                  .decision_statistics ?? {},
              ).map(([status, count]) => (
                <StatCard
                  key={status}
                  icon={
                    <Activity size={20} />
                  }
                  title={status}
                  value={count}
                />
              ))}
            </div>
          </section>

          <section className="dashboard-section">
            <div className="section-heading">
              <div>
                <h2>
                  User Activity
                </h2>

                <p>
                  Recent activity across the organization.
                </p>
              </div>

              <Activity size={22} />
            </div>

            <div className="simple-list">
              {dashboard.user_activity.length ===
              0 ? (
                <div className="empty-state">
                  <Activity size={32} />

                  <p>
                    No recent activity.
                  </p>
                </div>
              ) : (
                dashboard.user_activity.map(
                  (activity) => (
                    <div
                      className="list-row"
                      key={activity.id}
                    >
                      <div>
                        <strong>
                          {activity.action}
                        </strong>

                        <span>
                          {activity.description}
                        </span>
                      </div>

                      <small>
                        {formatDate(
                          activity.created_at,
                        )}
                      </small>
                    </div>
                  ),
                )
              )}
            </div>
          </section>
        </>
      )}

      <section className="dashboard-section">
        <div className="section-heading">
          <div>
            <h2>
              Recent Activity
            </h2>

            <p>
              Your latest platform activity.
            </p>
          </div>

          <Activity size={22} />
        </div>

        <div className="simple-list">
          {dashboard.recent_activities.length ===
          0 ? (
            <div className="empty-state">
              <Activity size={32} />

              <p>
                No recent activity yet.
              </p>
            </div>
          ) : (
            dashboard.recent_activities.map(
              (activity) => (
                <div
                  className="list-row"
                  key={activity.id}
                >
                  <div>
                    <strong>
                      {activity.action}
                    </strong>

                    <span>
                      {activity.description}
                    </span>
                  </div>

                  <small>
                    {formatDate(
                      activity.created_at,
                    )}
                  </small>
                </div>
              ),
            )
          )}
        </div>
      </section>
    </main>
  );
}

interface StatCardProps {
  icon: ReactNode;
  title: string;
  value: number;
}

function StatCard({
  icon,
  title,
  value,
}: StatCardProps) {
  return (
    <article className="stat-card">
      <div className="stat-icon">
        {icon}
      </div>

      <div>
        <span>
          {title}
        </span>

        <strong>
          {value}
        </strong>
      </div>
    </article>
  );
}