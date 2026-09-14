import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../../context/AuthContext";
import {
  getEmployeeDashboard,
  getEmployeeDecisions,
  getEmployeePendingReviews,
  getEmployeeRecentActivities,
} from "../../services/dashboardService";

import PageHeader from "../../components/PageHeader";
import Button from "../../components/Button";
import Card from "../../components/Card";
import StatusBadge from "../../components/StatusBadge";
import Alert from "../../components/Alert";
import EmptyState from "../../components/EmptyState";

const EmployeeDashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [dashboard, setDashboard] = useState(null);
  const [decisions, setDecisions] = useState([]);
  const [pendingReviews, setPendingReviews] = useState([]);
  const [activities, setActivities] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // --------------------------------------------------
  // LOAD DASHBOARD DATA
  // --------------------------------------------------
  const loadDashboard = async () => {
    try {
      setLoading(true);
      setError("");

      const [
        dashboardData,
        decisionsData,
        pendingReviewsData,
        activitiesData,
      ] = await Promise.all([
        getEmployeeDashboard(),
        getEmployeeDecisions(),
        getEmployeePendingReviews(),
        getEmployeeRecentActivities(),
      ]);

      setDashboard(dashboardData);

      setDecisions(
        Array.isArray(decisionsData)
          ? decisionsData
          : decisionsData?.decisions || []
      );

      setPendingReviews(
        Array.isArray(pendingReviewsData)
          ? pendingReviewsData
          : pendingReviewsData?.pending_reviews || []
      );

      setActivities(
        Array.isArray(activitiesData)
          ? activitiesData
          : activitiesData?.activities || []
      );
    } catch (err) {
      console.error("Failed to load employee dashboard:", err);

      const status = err.response?.status;

      if (status === 401) {
        setError("Your session has expired. Please login again.");
      } else if (status === 403) {
        setError(
          "You are not authorized to view the employee dashboard."
        );
      } else if (status === 404) {
        setError("Employee dashboard endpoint was not found.");
      } else if (status === 422) {
        setError("Invalid dashboard request.");
      } else if (status >= 500) {
        setError("Server error. Please try again later.");
      } else if (err.request) {
        setError(
          "Unable to connect to the backend. Please make sure FastAPI is running."
        );
      } else {
        setError("Unable to load dashboard data.");
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
  // GET VALUE WITH FALLBACK
  // --------------------------------------------------
  const getValue = (possibleValues, fallback = 0) => {
    for (const value of possibleValues) {
      if (value !== undefined && value !== null) {
        return value;
      }
    }

    return fallback;
  };

  // --------------------------------------------------
  // STATISTICS
  // --------------------------------------------------
  const totalDecisions = getValue(
    [
      dashboard?.total_decisions,
      dashboard?.my_decisions,
      dashboard?.total,
    ],
    decisions.length
  );

  const draftCount = getValue(
    [
      dashboard?.draft_count,
      dashboard?.drafts,
    ],
    decisions.filter(
      (decision) => decision.status === "Draft"
    ).length
  );

  const underReviewCount = getValue(
    [
      dashboard?.under_review_count,
      dashboard?.under_review,
      dashboard?.pending_review,
    ],
    decisions.filter(
      (decision) => decision.status === "Under Review"
    ).length
  );

  const approvedCount = getValue(
    [
      dashboard?.approved_count,
      dashboard?.approved,
    ],
    decisions.filter(
      (decision) => decision.status === "Approved"
    ).length
  );

  // --------------------------------------------------
  // RECENT DATA
  // --------------------------------------------------
  const recentDecisions = decisions.slice(0, 5);
  const recentActivities = activities.slice(0, 5);

  // --------------------------------------------------
  // LOADING
  // --------------------------------------------------
  if (loading) {
    return (
      <div className="dashboard-page">
        <PageHeader
          title="Employee Dashboard"
          subtitle="Manage your decisions and track their progress"
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
        title="Employee Dashboard"
        subtitle="Manage your decisions and track their progress"
        action={
          <Button
            variant="primary"
            onClick={() => navigate("/decisions/create")}
          >
            + Create Decision
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
            Welcome, {user?.full_name || "Employee"} 👋
          </h2>

          <p>
            Here's an overview of your decisions and recent activity.
          </p>
        </div>

        <div className="dashboard-user-info">
          <span>{user?.role || "Employee"}</span>
          <small>{user?.email || ""}</small>
        </div>
      </div>

      {/* =====================================================
          STATISTICS
      ===================================================== */}

      <div className="dashboard-stats">

        {/* MY DECISIONS */}

        <div className="dashboard-stat-card">
          <div className="stat-icon">
            ▣
          </div>

          <div>
            <span className="stat-label">
              My Decisions
            </span>

            <strong className="stat-value">
              {totalDecisions}
            </strong>
          </div>
        </div>

        {/* DRAFTS */}

        <div className="dashboard-stat-card">
          <div className="stat-icon">
            ◷
          </div>

          <div>
            <span className="stat-label">
              Drafts
            </span>

            <strong className="stat-value">
              {draftCount}
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

      </div>

      {/* =====================================================
          MAIN DASHBOARD GRID
      ===================================================== */}

      <div className="dashboard-grid">

        {/* ===================================================
            RECENT DECISIONS
        =================================================== */}

        <Card
          title="Recent Decisions"
          className="dashboard-card"
        >

          {recentDecisions.length === 0 ? (

            <EmptyState
              title="No decisions found"
              message="You haven't created any decisions yet."
              action={
                <Button
                  variant="primary"
                  onClick={() => navigate("/decisions/create")}
                >
                  Create Decision
                </Button>
              }
            />

          ) : (

            <div className="dashboard-list">

              {recentDecisions.map((decision) => (

                <button
                  key={decision.id}
                  className="dashboard-list-item"
                  onClick={() =>
                    navigate(`/decisions/${decision.id}`)
                  }
                >

                  <div className="dashboard-list-main">

                    <strong>
                      {decision.title || "Untitled Decision"}
                    </strong>

                    <span>
                      {decision.category || "No category"}
                    </span>

                  </div>

                  <StatusBadge
                    status={decision.status}
                  />

                </button>

              ))}

            </div>

          )}

          {recentDecisions.length > 0 && (
            <div className="dashboard-card-footer">

              <Button
                variant="secondary"
                onClick={() => navigate("/decisions")}
              >
                View All Decisions
              </Button>

            </div>
          )}

        </Card>

        {/* ===================================================
            PENDING REVIEWS
        =================================================== */}

        <Card
          title="Pending Reviews"
          className="dashboard-card"
        >

          {pendingReviews.length === 0 ? (

            <EmptyState
              title="No pending reviews"
              message="You currently have no pending review items."
            />

          ) : (

            <div className="dashboard-list">

              {pendingReviews.slice(0, 5).map((item, index) => (

                <button
                  key={item.id || index}
                  className="dashboard-list-item"
                  onClick={() =>
                    item.decision_id
                      ? navigate(
                          `/decisions/${item.decision_id}`
                        )
                      : null
                  }
                >

                  <div className="dashboard-list-main">

                    <strong>
                      {item.title ||
                        item.decision_title ||
                        `Review #${item.id || index + 1}`}
                    </strong>

                    <span>
                      {item.approval_level
                        ? `Approval Level ${item.approval_level}`
                        : "Pending review"}
                    </span>

                  </div>

                  <span className="pending-label">
                    Pending
                  </span>

                </button>

              ))}

            </div>

          )}

        </Card>

      </div>

      {/* =====================================================
          RECENT ACTIVITY
      ===================================================== */}

      <Card
        title="Recent Activity"
        className="dashboard-card"
      >

        {recentActivities.length === 0 ? (

          <EmptyState
            title="No recent activity"
            message="Your recent decision activity will appear here."
          />

        ) : (

          <div className="activity-list">

            {recentActivities.map((activity, index) => (

              <div
                className="activity-item"
                key={activity.id || index}
              >

                <div className="activity-dot">
                  ●
                </div>

                <div className="activity-content">

                  <strong>
                    {activity.activity_type ||
                      activity.type ||
                      "Activity"}
                  </strong>

                  <p>
                    {activity.description ||
                      activity.message ||
                      "Decision activity recorded."}
                  </p>

                  <span>
                    {activity.created_at
                      ? new Date(
                          activity.created_at
                        ).toLocaleString()
                      : ""}
                  </span>

                </div>

              </div>

            ))}

          </div>

        )}

      </Card>

      {/* =====================================================
          QUICK ACTIONS
      ===================================================== */}

      <Card
        title="Quick Actions"
        className="dashboard-card"
      >

        <div className="quick-actions">

          {/* CREATE DECISION */}

          <Button
            variant="primary"
            onClick={() => navigate("/decisions/create")}
          >
            + Create Decision
          </Button>

          {/* KNOWLEDGE REPOSITORY */}

          <Button
            variant="secondary"
            onClick={() => navigate("/repository")}
          >
            Knowledge Repository
          </Button>

          {/* MY DECISIONS */}

          <Button
            variant="secondary"
            onClick={() => navigate("/decisions")}
          >
            My Decisions
          </Button>

          {/* REPORTS */}

          <Button
            variant="secondary"
            onClick={() => navigate("/reports")}
          >
            Reports
          </Button>

        </div>

      </Card>

    </div>
  );
};

export default EmployeeDashboard;