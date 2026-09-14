import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../../context/AuthContext";

import {
  getManagerDashboard,
  getManagerTeamDecisions,
  getManagerPendingApprovals,
  getManagerStatistics,
} from "../../services/dashboardService";

import PageHeader from "../../components/PageHeader";
import Button from "../../components/Button";
import Card from "../../components/Card";
import StatusBadge from "../../components/StatusBadge";
import Alert from "../../components/Alert";
import EmptyState from "../../components/EmptyState";

const ManagerDashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [summary, setSummary] = useState(null);
  const [teamDecisions, setTeamDecisions] = useState([]);
  const [pendingApprovals, setPendingApprovals] = useState([]);
  const [statistics, setStatistics] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // --------------------------------------------------
  // LOAD MANAGER DASHBOARD DATA
  // --------------------------------------------------

  const loadDashboard = async () => {
    try {
      setLoading(true);
      setError("");

      const [
        summaryData,
        decisionsData,
        approvalsData,
        statisticsData,
      ] = await Promise.all([
        getManagerDashboard(),
        getManagerTeamDecisions(),
        getManagerPendingApprovals(),
        getManagerStatistics(),
      ]);

      // ----------------------------------------------
      // SUMMARY
      // ----------------------------------------------

      setSummary(summaryData || {});

      // ----------------------------------------------
      // TEAM DECISIONS
      // ----------------------------------------------

      setTeamDecisions(
        Array.isArray(decisionsData)
          ? decisionsData
          : decisionsData?.decisions ||
              decisionsData?.items ||
              []
      );

      // ----------------------------------------------
      // PENDING APPROVALS
      // ----------------------------------------------

      setPendingApprovals(
        Array.isArray(approvalsData)
          ? approvalsData
          : approvalsData?.approvals ||
              approvalsData?.items ||
              approvalsData?.pending_approvals ||
              []
      );

      // ----------------------------------------------
      // STATISTICS
      // ----------------------------------------------

      setStatistics(statisticsData || {});
    } catch (err) {
      console.error(
        "Failed to load manager dashboard:",
        err
      );

      const status = err.response?.status;

      if (status === 401) {
        setError(
          "Your session has expired. Please login again."
        );
      } else if (status === 403) {
        setError(
          "You are not authorized to view the manager dashboard."
        );
      } else if (status === 404) {
        setError(
          "Manager dashboard endpoint was not found."
        );
      } else if (status === 422) {
        setError("Invalid dashboard request.");
      } else if (status >= 500) {
        setError(
          "Server error. Please try again later."
        );
      } else if (err.request) {
        setError(
          "Unable to connect to the backend. Please make sure FastAPI is running."
        );
      } else {
        setError(
          "Unable to load manager dashboard."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  // --------------------------------------------------
  // INITIAL LOAD
  // --------------------------------------------------

  useEffect(() => {
    loadDashboard();
  }, []);

  // --------------------------------------------------
  // DATE FORMATTER
  // --------------------------------------------------

  const formatDate = (dateValue) => {
    if (!dateValue) {
      return "";
    }

    const date = new Date(dateValue);

    if (Number.isNaN(date.getTime())) {
      return dateValue;
    }

    return date.toLocaleString();
  };

  // --------------------------------------------------
  // STATISTICS
  // --------------------------------------------------

  const teamDecisionCount =
    summary?.team_decisions ??
    statistics?.total_decisions ??
    teamDecisions.length;

  const pendingApprovalCount =
    summary?.pending_approvals ??
    statistics?.pending_approvals ??
    pendingApprovals.length;

  const approvedCount =
    summary?.approved_decisions ??
    statistics?.approved_decisions ??
    teamDecisions.filter(
      (decision) => decision.status === "Approved"
    ).length;

  const rejectedCount =
    summary?.rejected_decisions ??
    statistics?.rejected_decisions ??
    teamDecisions.filter(
      (decision) => decision.status === "Rejected"
    ).length;

  const underReviewCount =
    summary?.under_review ??
    statistics?.under_review ??
    teamDecisions.filter(
      (decision) => decision.status === "Under Review"
    ).length;

  const draftCount =
    summary?.draft_decisions ??
    statistics?.draft_decisions ??
    teamDecisions.filter(
      (decision) => decision.status === "Draft"
    ).length;

  const archivedCount =
    summary?.archived_decisions ??
    statistics?.archived_decisions ??
    teamDecisions.filter(
      (decision) => decision.status === "Archived"
    ).length;

  // --------------------------------------------------
  // RECENT DATA
  // --------------------------------------------------

  const recentDecisions = teamDecisions.slice(0, 5);
  const recentApprovals = pendingApprovals.slice(0, 5);

  // --------------------------------------------------
  // LOADING
  // --------------------------------------------------

  if (loading) {
    return (
      <div className="dashboard-page">
        <PageHeader
          title="Manager Dashboard"
          subtitle="Manage team decisions, approvals and performance"
        />

        <div className="dashboard-loading">
          <div className="loading-spinner"></div>
          <p>Loading dashboard...</p>
        </div>
      </div>
    );
  }

  // --------------------------------------------------
  // MAIN DASHBOARD
  // --------------------------------------------------

  return (
    <div className="dashboard-page">

      {/* =====================================================
          PAGE HEADER
      ===================================================== */}

      <PageHeader
        title="Manager Dashboard"
        subtitle="Manage team decisions, approvals and performance"
        action={
          <Button
            variant="primary"
            onClick={() => navigate("/approvals")}
          >
            View Approvals
          </Button>
        }
      />

      {/* =====================================================
          ERROR
      ===================================================== */}

      {error && (
        <Alert
          message={error}
          type="error"
          onClose={() => setError("")}
        />
      )}

      {/* =====================================================
          WELCOME
      ===================================================== */}

      <div className="dashboard-welcome">
        <div>
          <h2>
            Welcome, {user?.full_name || "Manager"} 👋
          </h2>

          <p>
            Here's an overview of your team's decisions,
            approvals and current progress.
          </p>
        </div>

        <div className="dashboard-user-info">
          <span>{user?.role || "Manager"}</span>
          <small>{user?.email || ""}</small>
        </div>
      </div>

      {/* =====================================================
          STATISTICS
      ===================================================== */}

      <div className="dashboard-stats">

        {/* TEAM DECISIONS */}

        <div className="dashboard-stat-card">
          <div className="stat-icon">
            ▣
          </div>

          <div>
            <span className="stat-label">
              Team Decisions
            </span>

            <strong className="stat-value">
              {teamDecisionCount}
            </strong>
          </div>
        </div>

        {/* PENDING APPROVALS */}

        <div className="dashboard-stat-card">
          <div className="stat-icon">
            ◷
          </div>

          <div>
            <span className="stat-label">
              Pending Approvals
            </span>

            <strong className="stat-value">
              {pendingApprovalCount}
            </strong>
          </div>
        </div>

        {/* APPROVED */}

        <div className="dashboard-stat-card">
          <div className="stat-icon">
            ✓
          </div>

          <div>
            <span className="stat-label">
              Approved
            </span>

            <strong className="stat-value">
              {approvedCount}
            </strong>
          </div>
        </div>

        {/* REJECTED */}

        <div className="dashboard-stat-card">
          <div className="stat-icon">
            ✕
          </div>

          <div>
            <span className="stat-label">
              Rejected
            </span>

            <strong className="stat-value">
              {rejectedCount}
            </strong>
          </div>
        </div>

      </div>

      {/* =====================================================
          MAIN DASHBOARD GRID
      ===================================================== */}

      <div className="dashboard-grid">

        {/* ===================================================
            TEAM DECISIONS
        =================================================== */}

        <Card
          title="Team Decisions"
          className="dashboard-card"
        >

          {recentDecisions.length === 0 ? (

            <EmptyState
              title="No team decisions found"
              message="There are currently no decisions available for your team."
            />

          ) : (

            <div className="dashboard-list">

              {recentDecisions.map((decision) => (

                <button
                  key={decision.id}
                  className="dashboard-list-item"
                  onClick={() =>
                    navigate(
                      `/decisions/${decision.id}`
                    )
                  }
                >

                  <div className="dashboard-list-main">

                    <strong>
                      {decision.title ||
                        "Untitled Decision"}
                    </strong>

                    <span>
                      {decision.category ||
                        "No category"}
                    </span>

                  </div>

                  <StatusBadge
                    status={
                      decision.status || "Draft"
                    }
                  />

                </button>

              ))}

            </div>

          )}

          {teamDecisions.length > 0 && (
            <div className="dashboard-card-footer">

              <Button
                variant="secondary"
                onClick={() =>
                  navigate("/decisions")
                }
              >
                View All Decisions
              </Button>

            </div>
          )}

        </Card>

        {/* ===================================================
            PENDING APPROVALS
        =================================================== */}

        <Card
          title="Pending Approvals"
          className="dashboard-card"
        >

          {recentApprovals.length === 0 ? (

            <EmptyState
              title="No pending approvals"
              message="There are currently no pending approval requests."
            />

          ) : (

            <div className="dashboard-list">

              {recentApprovals.map(
                (approval, index) => {

                  const approvalId =
                    approval.id ||
                    approval.approval_id ||
                    index + 1;

                  const decisionId =
                    approval.decision_id;

                  return (
                    <button
                      key={approvalId}
                      className="dashboard-list-item"
                      onClick={() =>
                        decisionId
                          ? navigate(
                              `/decisions/${decisionId}`
                            )
                          : navigate(
                              "/approvals"
                            )
                      }
                    >

                      <div className="dashboard-list-main">

                        <strong>
                          {approval.decision_title ||
                            approval.title ||
                            `Approval #${approvalId}`}
                        </strong>

                        <span>
                          {decisionId
                            ? `Decision #${decisionId}`
                            : approval.approval_level
                            ? `Approval Level ${approval.approval_level}`
                            : "Pending approval"}
                        </span>

                        {approval.created_at && (
                          <small>
                            {formatDate(
                              approval.created_at
                            )}
                          </small>
                        )}

                      </div>

                      <StatusBadge
                        status={
                          approval.status ||
                          "Pending"
                        }
                      />

                    </button>
                  );
                }
              )}

            </div>

          )}

          {pendingApprovals.length > 0 && (
            <div className="dashboard-card-footer">

              <Button
                variant="secondary"
                onClick={() =>
                  navigate("/approvals")
                }
              >
                View All Approvals
              </Button>

            </div>
          )}

        </Card>

      </div>

      {/* =====================================================
          DECISION STATISTICS
      ===================================================== */}

      <Card
        title="Decision Statistics"
        className="dashboard-card"
      >

        <div className="dashboard-stats">

          {/* APPROVED */}

          <div className="dashboard-stat-card">
            <div className="stat-icon">
              ✓
            </div>

            <div>
              <span className="stat-label">
                Approved
              </span>

              <strong className="stat-value">
                {approvedCount}
              </strong>
            </div>
          </div>

          {/* REJECTED */}

          <div className="dashboard-stat-card">
            <div className="stat-icon">
              ✕
            </div>

            <div>
              <span className="stat-label">
                Rejected
              </span>

              <strong className="stat-value">
                {rejectedCount}
              </strong>
            </div>
          </div>

          {/* UNDER REVIEW */}

          <div className="dashboard-stat-card">
            <div className="stat-icon">
              ↻
            </div>

            <div>
              <span className="stat-label">
                Under Review
              </span>

              <strong className="stat-value">
                {underReviewCount}
              </strong>
            </div>
          </div>

          {/* DRAFT */}

          <div className="dashboard-stat-card">
            <div className="stat-icon">
              ◷
            </div>

            <div>
              <span className="stat-label">
                Draft
              </span>

              <strong className="stat-value">
                {draftCount}
              </strong>
            </div>
          </div>

        </div>

        <div className="dashboard-stats">

          {/* ARCHIVED */}

          <div className="dashboard-stat-card">
            <div className="stat-icon">
              ▤
            </div>

            <div>
              <span className="stat-label">
                Archived
              </span>

              <strong className="stat-value">
                {archivedCount}
              </strong>
            </div>
          </div>

          {/* TOTAL */}

          <div className="dashboard-stat-card">
            <div className="stat-icon">
              ▣
            </div>

            <div>
              <span className="stat-label">
                Total Decisions
              </span>

              <strong className="stat-value">
                {teamDecisionCount}
              </strong>
            </div>
          </div>

        </div>

      </Card>

      {/* =====================================================
          QUICK ACTIONS
      ===================================================== */}

      <Card
        title="Quick Actions"
        className="dashboard-card"
      >

        <div className="quick-actions">

          {/* TEAMS */}

          <Button
            variant="primary"
            onClick={() =>
              navigate("/teams")
            }
          >
            Manage Teams
          </Button>

          {/* APPROVALS */}

          <Button
            variant="secondary"
            onClick={() =>
              navigate("/approvals")
            }
          >
            View Approvals
          </Button>

          {/* DECISIONS */}

          <Button
            variant="secondary"
            onClick={() =>
              navigate("/decisions")
            }
          >
            View Decisions
          </Button>

          {/* KNOWLEDGE REPOSITORY */}

          <Button
            variant="secondary"
            onClick={() =>
              navigate("/repository")
            }
          >
            Knowledge Repository
          </Button>

          {/* REPORTS */}

          <Button
            variant="secondary"
            onClick={() =>
              navigate("/reports")
            }
          >
            Reports
          </Button>

        </div>

      </Card>

    </div>
  );
};

export default ManagerDashboard;