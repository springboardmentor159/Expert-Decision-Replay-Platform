import React, { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext";

import {
  getReviewerDashboard,
  getReviewerDecisions,
  getReviewerPendingReviews,
  getReviewerRecentActivities,
} from "../../services/dashboardService";

import PageHeader from "../../components/PageHeader";
import Button from "../../components/Button";
import Card from "../../components/Card";
import StatusBadge from "../../components/StatusBadge";
import Alert from "../../components/Alert";
import EmptyState from "../../components/EmptyState";

const ReviewerDashboard = () => {
  const { user } = useAuth();

  const [dashboard, setDashboard] = useState(null);
  const [decisions, setDecisions] = useState([]);
  const [pendingReviews, setPendingReviews] = useState([]);
  const [activities, setActivities] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadReviewerDashboard();
  }, []);

  const loadReviewerDashboard = async () => {
    try {
      setLoading(true);
      setError("");

      const [
        dashboardData,
        decisionsData,
        pendingReviewsData,
        activitiesData,
      ] = await Promise.all([
        getReviewerDashboard(),
        getReviewerDecisions(),
        getReviewerPendingReviews(),
        getReviewerRecentActivities(),
      ]);

      setDashboard(dashboardData || {});

      setDecisions(
        Array.isArray(decisionsData)
          ? decisionsData
          : decisionsData?.items ||
            decisionsData?.decisions ||
            []
      );

      setPendingReviews(
        Array.isArray(pendingReviewsData)
          ? pendingReviewsData
          : pendingReviewsData?.items ||
            pendingReviewsData?.approvals ||
            []
      );

      setActivities(
        Array.isArray(activitiesData)
          ? activitiesData
          : activitiesData?.items ||
            activitiesData?.activities ||
            []
      );
    } catch (err) {
      console.error("Reviewer dashboard error:", err);

      if (err.response) {
        const status = err.response.status;

        if (status === 401) {
          setError("Your session has expired. Please log in again.");
        } else if (status === 403) {
          setError(
            "You do not have permission to access the Reviewer Dashboard."
          );
        } else if (status === 404) {
          setError(
            "Reviewer dashboard service was not found. Please check the backend routes."
          );
        } else if (status === 422) {
          setError("Invalid request sent to the server.");
        } else if (status >= 500) {
          setError(
            "A server error occurred while loading the Reviewer Dashboard."
          );
        } else {
          setError(
            err.response.data?.detail ||
              "Unable to load the Reviewer Dashboard."
          );
        }
      } else if (err.request) {
        setError(
          "Unable to connect to the backend server. Please make sure FastAPI is running."
        );
      } else {
        setError("An unexpected error occurred.");
      }
    } finally {
      setLoading(false);
    }
  };

  const getStatusClass = (status) => {
    if (!status) return "";

    return status.toLowerCase().replace(/\s+/g, "-");
  };

  if (loading) {
    return (
      <div className="dashboard-page">
        <PageHeader
          title="Reviewer Dashboard"
          subtitle="Review assigned decisions and manage pending approvals"
        />

        <div className="dashboard-loading">
          <p>Loading Reviewer Dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-page">
      {/* ==============================
          PAGE HEADER
      ============================== */}
      <PageHeader
        title="Reviewer Dashboard"
        subtitle="Review assigned decisions and manage pending approvals"
      />

      {/* ==============================
          WELCOME SECTION
      ============================== */}
      <div className="dashboard-welcome">
        <div>
          <h2>
            Welcome, {user?.full_name || "Reviewer"}!
          </h2>

          <p>
            Review your assigned decisions, track pending reviews,
            and monitor your recent review activity.
          </p>
        </div>
      </div>

      {/* ==============================
          ERROR MESSAGE
      ============================== */}
      {error && (
        <Alert
          type="error"
          message={error}
        />
      )}

      {/* ==============================
          STATISTICS
      ============================== */}
      <div className="dashboard-stats">

        {/* Pending Reviews */}
        <Card className="dashboard-stat-card">
          <div className="stat-card-content">
            <div>
              <p className="stat-label">Pending Reviews</p>

              <h3 className="stat-value">
                {dashboard?.pending_reviews ?? pendingReviews.length}
              </h3>
            </div>

            <div className="stat-icon">
              🕒
            </div>
          </div>
        </Card>

        {/* Completed Reviews */}
        <Card className="dashboard-stat-card">
          <div className="stat-card-content">
            <div>
              <p className="stat-label">Completed Reviews</p>

              <h3 className="stat-value">
                {dashboard?.completed_reviews ?? 0}
              </h3>
            </div>

            <div className="stat-icon">
              ✅
            </div>
          </div>
        </Card>

        {/* Approved Reviews */}
        <Card className="dashboard-stat-card">
          <div className="stat-card-content">
            <div>
              <p className="stat-label">Approved</p>

              <h3 className="stat-value">
                {dashboard?.approved_reviews ?? 0}
              </h3>
            </div>

            <div className="stat-icon">
              👍
            </div>
          </div>
        </Card>

        {/* Total Assigned Reviews */}
        <Card className="dashboard-stat-card">
          <div className="stat-card-content">
            <div>
              <p className="stat-label">Total Assigned Reviews</p>

              <h3 className="stat-value">
                {dashboard?.total_reviews ?? decisions.length}
              </h3>
            </div>

            <div className="stat-icon">
              📋
            </div>
          </div>
        </Card>

      </div>

      {/* ==============================
          MAIN DASHBOARD GRID
      ============================== */}
      <div className="dashboard-grid">

        {/* ==============================
            PENDING REVIEWS
        ============================== */}
        <Card
          title="Pending Reviews"
          className="dashboard-card"
        >
          {pendingReviews.length === 0 ? (
            <EmptyState
              title="No Pending Reviews"
              message="You currently have no decisions waiting for your review."
            />
          ) : (
            <div className="dashboard-list">

              {pendingReviews.map((review) => (
                <div
                  key={review.approval_id}
                  className="dashboard-list-item"
                >
                  <div className="dashboard-list-content">

                    <h4>
                      Decision #{review.decision_id}
                    </h4>

                    <p>
                      Approval Level:{" "}
                      <strong>
                        {review.approval_level}
                      </strong>
                    </p>

                    <span className="dashboard-date">
                      Assigned on{" "}
                      {review.created_at
                        ? new Date(
                            review.created_at
                          ).toLocaleDateString()
                        : "N/A"}
                    </span>
                  </div>

                  <div className="dashboard-list-action">
                    <StatusBadge
                      status={review.status}
                    />
                  </div>
                </div>
              ))}

            </div>
          )}
        </Card>

        {/* ==============================
            RECENT ASSIGNED DECISIONS
        ============================== */}
        <Card
          title="Assigned Decisions"
          className="dashboard-card"
        >
          {decisions.length === 0 ? (
            <EmptyState
              title="No Assigned Decisions"
              message="No decisions have been assigned to you for review yet."
            />
          ) : (
            <div className="dashboard-list">

              {decisions.slice(0, 5).map((decision) => (
                <div
                  key={decision.id}
                  className="dashboard-list-item"
                >
                  <div className="dashboard-list-content">

                    <h4>
                      {decision.title}
                    </h4>

                    <p>
                      {decision.category || "No category"}
                    </p>

                    <span className="dashboard-date">
                      Updated{" "}
                      {decision.updated_at
                        ? new Date(
                            decision.updated_at
                          ).toLocaleDateString()
                        : "N/A"}
                    </span>
                  </div>

                  <div className="dashboard-list-action">
                    <StatusBadge
                      status={decision.status}
                    />
                  </div>
                </div>
              ))}

            </div>
          )}
        </Card>

        {/* ==============================
            RECENT ACTIVITY
        ============================== */}
        <Card
          title="Recent Activity"
          className="dashboard-card"
        >
          {activities.length === 0 ? (
            <EmptyState
              title="No Recent Activity"
              message="Your recent review activity will appear here."
            />
          ) : (
            <div className="dashboard-list">

              {activities.slice(0, 5).map((activity) => (
                <div
                  key={activity.id}
                  className="dashboard-list-item"
                >
                  <div className="dashboard-list-content">

                    <h4>
                      {activity.action ||
                        "Activity"}
                    </h4>

                    <p>
                      {activity.description ||
                        `${activity.entity_type || "System"} activity`}
                    </p>

                    <span className="dashboard-date">
                      {activity.created_at
                        ? new Date(
                            activity.created_at
                          ).toLocaleString()
                        : "N/A"}
                    </span>
                  </div>
                </div>
              ))}

            </div>
          )}
        </Card>

      </div>

      {/* ==============================
          QUICK ACTIONS
      ============================== */}
      <Card
        title="Reviewer Actions"
        className="dashboard-card quick-actions-card"
      >
        <div className="quick-actions">

          <Button
            onClick={() =>
              (window.location.href = "/approvals")
            }
          >
            Review Pending Approvals
          </Button>

          <Button
            onClick={() =>
              (window.location.href = "/decisions")
            }
          >
            View Decisions
          </Button>

          <Button
            onClick={() =>
              (window.location.href =
                "/repository")
            }
          >
            Knowledge Repository
          </Button>

          <Button
            onClick={() =>
              (window.location.href =
                "/profile")
            }
          >
            My Profile
          </Button>

        </div>
      </Card>
    </div>
  );
};

export default ReviewerDashboard;