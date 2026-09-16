import { useContext, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { AuthContext } from "../context/AuthContext";
import apiClient from "../api/apiClient";

function Dashboard() {
  const {
    user,
    loading: authLoading,
  } = useContext(AuthContext);

  const [dashboardData, setDashboardData] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const role = user?.role || "";

  const displayName =
    user?.name ||
    user?.full_name ||
    user?.email ||
    "User";

  const getErrorMessage = (requestError) => {
    const status =
      requestError?.response?.status;

    const detail =
      requestError?.response?.data?.detail;

    if (status === 400) {
      return (
        detail ||
        "The dashboard request is invalid."
      );
    }

    if (status === 401) {
      return (
        "Your session has expired. Please log in again."
      );
    }

    if (status === 403) {
      return (
        detail ||
        "You do not have permission to access this dashboard."
      );
    }

    if (status === 404) {
      return (
        detail ||
        "The dashboard information could not be found."
      );
    }

    if (status === 422) {
      return (
        detail ||
        "The dashboard request contains invalid information."
      );
    }

    if (status >= 500) {
      return (
        "A server error occurred while loading the dashboard."
      );
    }

    return (
      detail ||
      requestError?.message ||
      "Unable to load the dashboard."
    );
  };

  useEffect(() => {
    if (authLoading || !user) {
      return;
    }

    const loadDashboard = async () => {
      setLoading(true);
      setError("");

      try {
        let endpoint = "";

        if (role === "Employee") {
          endpoint = "/dashboard/employee";
        } else if (role === "Manager") {
          endpoint = "/dashboard/manager";
        } else if (role === "Administrator") {
          endpoint = "/dashboard/admin";
        } else if (role === "Reviewer") {
          setDashboardData({
            reviewer: true,
          });

          setLoading(false);
          return;
        } else {
          throw new Error(
            "Your account does not have a recognized role."
          );
        }

        const response =
          await apiClient.get(endpoint);

        setDashboardData(response.data);
      } catch (requestError) {
        console.error(
          "Dashboard loading failed:",
          requestError
        );

        setDashboardData(null);

        setError(
          getErrorMessage(requestError)
        );
      } finally {
        setLoading(false);
      }
    };

    loadDashboard();
  }, [
    authLoading,
    user,
    role,
  ]);

  if (authLoading) {
    return (
      <div className="page-container">
        <div className="loading-state">
          Checking your session...
        </div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  if (loading) {
    return (
      <div className="page-container">
        <div className="dashboard-welcome">
          <div>
            <div className="dashboard-eyebrow">
              EXPERT DECISION REPLAY
            </div>

            <h1>Dashboard</h1>

            <p>
              Preparing your decision workspace...
            </p>
          </div>
        </div>

        <div className="dashboard-loading-card">
          <div className="loading-state">
            Loading dashboard information...
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-container">
        <div className="dashboard-welcome">
          <div>
            <div className="dashboard-eyebrow">
              EXPERT DECISION REPLAY
            </div>

            <h1>Dashboard</h1>

            <p>
              Welcome back, {displayName}.
            </p>
          </div>
        </div>

        <div className="error-message">
          <strong>
            Unable to load dashboard
          </strong>

          <p>{error}</p>

          <button
            type="button"
            className="secondary-button"
            onClick={() =>
              window.location.reload()
            }
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  /*
   * ========================================================
   * REVIEWER DASHBOARD
   * ========================================================
   */

  if (role === "Reviewer") {
    return (
      <div className="page-container">

        <div className="dashboard-welcome">

          <div>
            <div className="dashboard-eyebrow">
              REVIEW WORKSPACE
            </div>

            <h1>
              Welcome, {displayName}
            </h1>

            <p>
              Review assigned decisions and
              complete approval actions.
            </p>
          </div>

          <div className="dashboard-role-badge">
            REVIEWER
          </div>

        </div>

        <div className="dashboard-feature-grid">

          <div className="dashboard-feature-card dashboard-feature-primary">

            <div className="feature-icon">
              ✓
            </div>

            <div>
              <h2>
                Assigned Reviews
              </h2>

              <p>
                Review decisions assigned to
                you and complete approval
                actions.
              </p>
            </div>

            <Link
              to="/approvals"
              className="primary-button"
            >
              Open Reviews
            </Link>

          </div>

          <div className="dashboard-feature-card">

            <div className="feature-icon">
              ▣
            </div>

            <div>
              <h2>
                Decision Library
              </h2>

              <p>
                Browse decisions and inspect
                their complete context.
              </p>
            </div>

            <Link
              to="/decisions"
              className="secondary-button"
            >
              View Decisions
            </Link>

          </div>

          <div className="dashboard-feature-card">

            <div className="feature-icon">
              ◌
            </div>

            <div>
              <h2>
                Discussions
              </h2>

              <p>
                Participate in discussions and
                review decision comments.
              </p>
            </div>

            <Link
              to="/discussions"
              className="secondary-button"
            >
              Open Discussions
            </Link>

          </div>

          <div className="dashboard-feature-card">

            <div className="feature-icon">
              ▤
            </div>

            <div>
              <h2>
                Knowledge Repository
              </h2>

              <p>
                Search previous organizational
                decisions.
              </p>
            </div>

            <Link
              to="/knowledge-repository"
              className="secondary-button"
            >
              Browse Repository
            </Link>

          </div>

        </div>

      </div>
    );
  }

  /*
   * ========================================================
   * DASHBOARD DATA
   * ========================================================
   */

  const data =
    dashboardData || {};

  const getValue = (
    keys,
    fallback = 0
  ) => {
    for (const key of keys) {
      if (
        data[key] !== undefined &&
        data[key] !== null
      ) {
        return data[key];
      }
    }

    return fallback;
  };

  const totalDecisions = getValue([
    "total_decisions",
    "total",
    "decision_count",
  ]);

  const draftDecisions = getValue([
    "draft_decisions",
    "draft_count",
  ]);

  const approvedDecisions = getValue([
    "approved_decisions",
    "approved_count",
  ]);

  const pendingDecisions = getValue([
    "pending_decisions",
    "pending_count",
    "under_review_decisions",
  ]);

  const rejectedDecisions = getValue([
    "rejected_decisions",
    "rejected_count",
  ]);

  /*
   * ========================================================
   * STATUS PERCENTAGES
   * ========================================================
   */

  const getPercentage = (value) => {
    const total = Number(totalDecisions);

    if (!total || total <= 0) {
      return 0;
    }

    return Math.min(
      100,
      Math.round(
        (Number(value) / total) * 100
      )
    );
  };

  const draftPercentage =
    getPercentage(draftDecisions);

  const approvedPercentage =
    getPercentage(approvedDecisions);

  const pendingPercentage =
    getPercentage(pendingDecisions);

  const rejectedPercentage =
    getPercentage(rejectedDecisions);

  /*
   * ========================================================
   * STAT CARD
   * ========================================================
   */

  const StatCard = ({
    icon,
    label,
    value,
    description,
    className = "",
  }) => {
    return (
      <div
        className={`dashboard-stat-card ${className}`}
      >
        <div className="dashboard-stat-top">

          <div className="dashboard-stat-icon">
            {icon}
          </div>

        </div>

        <div className="dashboard-stat-value">
          {value}
        </div>

        <div className="dashboard-stat-label">
          {label}
        </div>

        <div className="dashboard-stat-description">
          {description}
        </div>
      </div>
    );
  };

  return (
    <div className="page-container">

      {/* ==================================================
          WELCOME HEADER
      =================================================== */}

      <div className="dashboard-welcome">

        <div>
          <div className="dashboard-eyebrow">
            EXPERT DECISION REPLAY
          </div>

          <h1>
            Welcome back, {displayName}
          </h1>

          <p>
            Here's an overview of your
            decision management workspace.
          </p>
        </div>

        <div className="dashboard-header-actions">

          <div className="dashboard-role-badge">
            {role.toUpperCase()}
          </div>

          <Link
            to="/decisions"
            className="secondary-button"
          >
            View Decisions
          </Link>

          {role === "Employee" && (
            <Link
              to="/decisions/create"
              className="primary-button"
            >
              + Create Decision
            </Link>
          )}

        </div>

      </div>


      {/* ==================================================
          STATISTICS
      =================================================== */}

      <div className="dashboard-stats-grid">

        <StatCard
          icon="▣"
          label="Total Decisions"
          value={totalDecisions}
          description="Decisions tracked"
          className="stat-blue"
        />

        <StatCard
          icon="○"
          label="Draft Decisions"
          value={draftDecisions}
          description="Currently being prepared"
          className="stat-slate"
        />

        <StatCard
          icon="✓"
          label="Approved Decisions"
          value={approvedDecisions}
          description="Successfully approved"
          className="stat-green"
        />

        <StatCard
          icon="◷"
          label="Under Review"
          value={pendingDecisions}
          description="Awaiting review or action"
          className="stat-orange"
        />

        <StatCard
          icon="!"
          label="Rejected Decisions"
          value={rejectedDecisions}
          description="Decisions requiring attention"
          className="stat-red"
        />

      </div>


      {/* ==================================================
          MAIN DASHBOARD GRID
      =================================================== */}

      <div className="dashboard-content-grid">

        {/* ---------- Decision Overview ---------- */}

        <div className="dashboard-panel">

          <div className="dashboard-panel-header">

            <div>
              <h2>
                Decision Overview
              </h2>

              <p>
                Current distribution of decisions
              </p>
            </div>

            <Link
              to="/decisions"
              className="text-link"
            >
              View all →
            </Link>

          </div>


          <div className="decision-overview">

            <div className="overview-row">

              <div className="overview-label">
                <span className="status-dot dot-green" />
                Approved
              </div>

              <strong>
                {approvedDecisions}
              </strong>

              <div className="overview-bar">
                <div
                  className="overview-fill fill-green"
                  style={{
                    width:
                      `${approvedPercentage}%`,
                  }}
                />
              </div>

            </div>


            <div className="overview-row">

              <div className="overview-label">
                <span className="status-dot dot-blue" />
                Under Review
              </div>

              <strong>
                {pendingDecisions}
              </strong>

              <div className="overview-bar">
                <div
                  className="overview-fill fill-blue"
                  style={{
                    width:
                      `${pendingPercentage}%`,
                  }}
                />
              </div>

            </div>


            <div className="overview-row">

              <div className="overview-label">
                <span className="status-dot dot-slate" />
                Draft
              </div>

              <strong>
                {draftDecisions}
              </strong>

              <div className="overview-bar">
                <div
                  className="overview-fill fill-slate"
                  style={{
                    width:
                      `${draftPercentage}%`,
                  }}
                />
              </div>

            </div>


            <div className="overview-row">

              <div className="overview-label">
                <span className="status-dot dot-red" />
                Rejected
              </div>

              <strong>
                {rejectedDecisions}
              </strong>

              <div className="overview-bar">
                <div
                  className="overview-fill fill-red"
                  style={{
                    width:
                      `${rejectedPercentage}%`,
                  }}
                />
              </div>

            </div>

          </div>

        </div>


        {/* ---------- Quick Actions ---------- */}

        <div className="dashboard-panel">

          <div className="dashboard-panel-header">

            <div>
              <h2>
                Quick Actions
              </h2>

              <p>
                Frequently used features
              </p>
            </div>

          </div>


          <div className="quick-actions-list">

            {role === "Employee" && (
              <Link
                to="/decisions/create"
                className="quick-action"
              >
                <span className="quick-action-icon">
                  +
                </span>

                <span>
                  <strong>
                    Create Decision
                  </strong>

                  <small>
                    Start a new decision
                  </small>
                </span>

                <span className="quick-action-arrow">
                  →
                </span>
              </Link>
            )}

            <Link
              to="/decisions"
              className="quick-action"
            >
              <span className="quick-action-icon">
                ▣
              </span>

              <span>
                <strong>
                  View Decisions
                </strong>

                <small>
                  Browse decision records
                </small>
              </span>

              <span className="quick-action-arrow">
                →
              </span>
            </Link>


            <Link
              to="/knowledge-repository"
              className="quick-action"
            >
              <span className="quick-action-icon">
                ▤
              </span>

              <span>
                <strong>
                  Knowledge Repository
                </strong>

                <small>
                  Search previous decisions
                </small>
              </span>

              <span className="quick-action-arrow">
                →
              </span>
            </Link>


            {role === "Manager" && (
              <Link
                to="/approvals"
                className="quick-action"
              >
                <span className="quick-action-icon">
                  ✓
                </span>

                <span>
                  <strong>
                    Pending Approvals
                  </strong>

                  <small>
                    Review approval requests
                  </small>
                </span>

                <span className="quick-action-arrow">
                  →
                </span>
              </Link>
            )}


            {role === "Reviewer" && (
              <Link
                to="/approvals"
                className="quick-action"
              >
                <span className="quick-action-icon">
                  ✓
                </span>

                <span>
                  <strong>
                    Assigned Reviews
                  </strong>

                  <small>
                    Complete assigned reviews
                  </small>
                </span>

                <span className="quick-action-arrow">
                  →
                </span>
              </Link>
            )}


            {role === "Administrator" && (
              <Link
                to="/users"
                className="quick-action"
              >
                <span className="quick-action-icon">
                  ♙
                </span>

                <span>
                  <strong>
                    User Management
                  </strong>

                  <small>
                    Manage platform users
                  </small>
                </span>

                <span className="quick-action-arrow">
                  →
                </span>
              </Link>
            )}

          </div>

        </div>

      </div>


      {/* ==================================================
          WORKSPACE SECTION
      =================================================== */}

      <div className="dashboard-workspace">

        <div className="dashboard-panel workspace-main">

          <div className="dashboard-panel-header">

            <div>
              <h2>
                Decision Management
              </h2>

              <p>
                Manage and explore the complete
                decision lifecycle.
              </p>
            </div>

          </div>


          <div className="workspace-feature-grid">

            <div className="workspace-feature">

              <div className="workspace-feature-icon">
                01
              </div>

              <div>
                <h3>
                  Evaluate Alternatives
                </h3>

                <p>
                  Compare options using cost,
                  feasibility, risk, pros and cons.
                </p>

                <Link
                  to="/decisions"
                  className="text-link"
                >
                  Explore decisions →
                </Link>
              </div>

            </div>


            <div className="workspace-feature">

              <div className="workspace-feature-icon">
                02
              </div>

              <div>
                <h3>
                  Review & Approve
                </h3>

                <p>
                  Track reviews and approval
                  actions through the workflow.
                </p>

                <Link
                  to="/approvals"
                  className="text-link"
                >
                  Open approvals →
                </Link>
              </div>

            </div>


            <div className="workspace-feature">

              <div className="workspace-feature-icon">
                03
              </div>

              <div>
                <h3>
                  Replay Decision History
                </h3>

                <p>
                  Understand how decisions changed
                  through versions, timeline and audit.
                </p>

                <Link
                  to="/decisions"
                  className="text-link"
                >
                  View history →
                </Link>

              </div>

            </div>

          </div>

        </div>


        {/* ---------- Admin / Manager Panel ---------- */}

        {(role === "Administrator" ||
          role === "Manager") && (
          <div className="dashboard-panel workspace-side">

            <div className="dashboard-panel-header">

              <div>
                <h2>
                  Management
                </h2>

                <p>
                  Administrative tools
                </p>
              </div>

            </div>


            {role === "Administrator" && (
              <>
                <Link
                  to="/users"
                  className="management-link"
                >
                  <span>
                    ♙
                  </span>

                  <div>
                    <strong>
                      User Management
                    </strong>

                    <small>
                      Manage platform accounts
                    </small>
                  </div>
                </Link>

                <Link
                  to="/audit"
                  className="management-link"
                >
                  <span>
                    ◫
                  </span>

                  <div>
                    <strong>
                      Audit Logs
                    </strong>

                    <small>
                      Review system activity
                    </small>
                  </div>
                </Link>

                <Link
                  to="/reports"
                  className="management-link"
                >
                  <span>
                    ▤
                  </span>

                  <div>
                    <strong>
                      Reports
                    </strong>

                    <small>
                      Generate platform reports
                    </small>
                  </div>
                </Link>
              </>
            )}


            {role === "Manager" && (
              <>
                <Link
                  to="/approvals"
                  className="management-link"
                >
                  <span>
                    ✓
                  </span>

                  <div>
                    <strong>
                      Pending Approvals
                    </strong>

                    <small>
                      Manage approval workflow
                    </small>
                  </div>
                </Link>

                <Link
                  to="/analytics"
                  className="management-link"
                >
                  <span>
                    ▥
                  </span>

                  <div>
                    <strong>
                      Decision Analytics
                    </strong>

                    <small>
                      Review decision statistics
                    </small>
                  </div>
                </Link>

                <Link
                  to="/reports"
                  className="management-link"
                >
                  <span>
                    ▤
                  </span>

                  <div>
                    <strong>
                      Reports
                    </strong>

                    <small>
                      Generate team reports
                    </small>
                  </div>
                </Link>
              </>
            )}

          </div>
        )}

      </div>


      {/* ==================================================
          FOOTER
      =================================================== */}

      <div className="dashboard-footer-note">
        <span>
          ●
        </span>

        <span>
          Decision Replay Platform
        </span>

        <span className="footer-separator">
          •
        </span>

        <span>
          {role} Workspace
        </span>
      </div>

    </div>
  );
}

export default Dashboard;