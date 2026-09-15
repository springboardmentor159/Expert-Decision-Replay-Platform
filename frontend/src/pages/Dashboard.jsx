import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import api from "../services/api";

function Dashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const role = user?.role || "Employee";

  const [stats, setStats] = useState({
    total_decisions: 0,
    draft_decisions: 0,
    under_review: 0,
    approved_decisions: 0,
    rejected_decisions: 0,
  });

  const [myDecisions, setMyDecisions] = useState([]);
  const [recentActivities, setRecentActivities] = useState([]);

  const [loading, setLoading] = useState(true);
  const [decisionsLoading, setDecisionsLoading] = useState(true);
  const [activitiesLoading, setActivitiesLoading] = useState(true);

  const [error, setError] = useState("");
  const [decisionsError, setDecisionsError] = useState("");
  const [activitiesError, setActivitiesError] = useState("");

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const response = await api.get("/dashboard/employee");

        setStats({
          total_decisions: response.data.total_decisions || 0,
          draft_decisions: response.data.draft_decisions || 0,
          under_review: response.data.under_review || 0,
          approved_decisions: response.data.approved_decisions || 0,
          rejected_decisions: response.data.rejected_decisions || 0,
        });
      } catch (err) {
        console.error("Dashboard error:", err);
        setError("Unable to load dashboard statistics.");
      } finally {
        setLoading(false);
      }
    };

    const fetchMyDecisions = async () => {
      try {
        const response = await api.get("/dashboard/employee/decisions");
        setMyDecisions(response.data);
      } catch (err) {
        console.error("My decisions error:", err);
        setDecisionsError("Unable to load your decisions.");
      } finally {
        setDecisionsLoading(false);
      }
    };

    const fetchRecentActivities = async () => {
      try {
        const response = await api.get(
          "/dashboard/employee/recent-activities"
        );

        setRecentActivities(response.data);
      } catch (err) {
        console.error("Recent activities error:", err);
        setActivitiesError("Unable to load recent activities.");
      } finally {
        setActivitiesLoading(false);
      }
    };

    fetchDashboard();
    fetchMyDecisions();
    fetchRecentActivities();
  }, []);

  const statCards = [
    {
      title: "Total Decisions",
      value: stats.total_decisions,
      icon: "▣",
      className: "blue",
    },
    {
      title: "Draft Decisions",
      value: stats.draft_decisions,
      icon: "✎",
      className: "orange",
    },
    {
      title: "Under Review",
      value: stats.under_review,
      icon: "◷",
      className: "purple",
    },
    {
      title: "Approved",
      value: stats.approved_decisions,
      icon: "✓",
      className: "green",
    },
  ];

  return (
    <div className="dashboard-page">

      {/* PAGE HEADING */}

      <div className="dashboard-heading">
        <div>
          <p className="page-label">OVERVIEW</p>

          <h1>Good evening, {user?.full_name || "Ramya"} 👋</h1>

          <p className="dashboard-subtitle">
            Here's what's happening with your decisions today.
          </p>
        </div>

        <button
          className="primary-button"
          onClick={() => navigate("/decisions/create")}
        >
          <span>+</span>
          Create Decision
        </button>
      </div>


      {/* STATISTICS */}

      {loading ? (
        <div className="loading-card">
          Loading dashboard statistics...
        </div>
      ) : error ? (
        <div className="error-card">
          {error}
        </div>
      ) : (
        <div className="stats-grid">

          {statCards.map((card) => (
            <div className="stat-card" key={card.title}>

              <div className={`stat-icon ${card.className}`}>
                {card.icon}
              </div>

              <div className="stat-content">
                <p>{card.title}</p>
                <h2>{card.value}</h2>
              </div>

            </div>
          ))}

        </div>
      )}


      {/* MAIN GRID */}

      <div className="dashboard-grid">

        {/* MY DECISIONS */}

        <div className="dashboard-card decisions-card">

          <div className="card-header">

            <div>
              <h2>My Decisions</h2>
              <p>Recently created and updated decisions</p>
            </div>

            <button
              className="text-button"
              onClick={() => navigate("/decisions")}
            >
              View All →
            </button>

          </div>

          {decisionsLoading ? (
            <div className="empty-state">
              Loading your decisions...
            </div>
          ) : decisionsError ? (
            <div className="error-state">
              {decisionsError}
            </div>
          ) : myDecisions.length === 0 ? (

            <div className="empty-state">

              <div className="empty-icon">
                ▣
              </div>

              <h3>No decisions yet</h3>

              <p>
                Create your first decision to get started.
              </p>

              <button
                className="secondary-button"
                onClick={() => navigate("/decisions/create")}
              >
                Create Decision
              </button>

            </div>

          ) : (

            <div className="decision-table-wrapper">

              <table className="modern-table">

                <thead>
                  <tr>
                    <th>Decision</th>
                    <th>Category</th>
                    <th>Status</th>
                    <th>Created</th>
                  </tr>
                </thead>

                <tbody>

                  {myDecisions.slice(0, 5).map((decision) => (

                    <tr
                      key={decision.id}
                      onClick={() =>
                        navigate(`/decisions/${decision.id}`)
                      }
                      className="clickable-row"
                    >

                      <td>
                        <div className="decision-name">
                          <div className="decision-avatar">
                            {decision.title
                              ? decision.title.charAt(0).toUpperCase()
                              : "D"}
                          </div>

                          <div>
                            <strong>
                              {decision.title}
                            </strong>

                            <span>
                              Decision #{decision.id}
                            </span>
                          </div>
                        </div>
                      </td>

                      <td>
                        {decision.category || "-"}
                      </td>

                      <td>
                        <span
                          className={`status-badge ${String(
                            decision.status || ""
                          )
                            .toLowerCase()
                            .replace(/\s+/g, "-")}`}
                        >
                          {decision.status || "Unknown"}
                        </span>
                      </td>

                      <td>
                        {decision.created_at
                          ? new Date(
                              decision.created_at
                            ).toLocaleDateString()
                          : "-"}
                      </td>

                    </tr>

                  ))}

                </tbody>

              </table>

            </div>

          )}

        </div>


        {/* RIGHT SIDE */}

        <div className="right-dashboard-column">

          {/* QUICK ACTIONS */}

          <div className="dashboard-card quick-card">

            <div className="card-header">

              <div>
                <h2>Quick Actions</h2>
                <p>Common tasks</p>
              </div>

            </div>

            <button
              className="quick-action"
              onClick={() => navigate("/decisions/create")}
            >
              <span className="quick-icon blue">
                +
              </span>

              <div>
                <strong>Create Decision</strong>
                <small>Start a new decision</small>
              </div>

              <span className="arrow">→</span>
            </button>

            <button
              className="quick-action"
              onClick={() => navigate("/knowledge")}
            >
              <span className="quick-icon purple">
                ▤
              </span>

              <div>
                <strong>Knowledge Repository</strong>
                <small>Explore past decisions</small>
              </div>

              <span className="arrow">→</span>
            </button>

            <button
              className="quick-action"
              onClick={() => navigate("/reports")}
            >
              <span className="quick-icon green">
                ▥
              </span>

              <div>
                <strong>View Reports</strong>
                <small>Analyze decision data</small>
              </div>

              <span className="arrow">→</span>
            </button>

          </div>


          {/* ROLE CARD */}

          <div className="role-card">

            <div className="role-card-icon">
              ◉
            </div>

            <div>
              <span>Your Role</span>
              <strong>{role}</strong>
            </div>

          </div>

        </div>

      </div>


      {/* RECENT ACTIVITY */}

      <div className="dashboard-card activity-card">

        <div className="card-header">

          <div>
            <h2>Recent Activity</h2>
            <p>Your latest activity on the platform</p>
          </div>

          <button
            className="text-button"
            onClick={() => navigate("/audit-logs")}
          >
            View Audit Logs →
          </button>

        </div>

        {activitiesLoading ? (

          <div className="empty-state">
            Loading recent activities...
          </div>

        ) : activitiesError ? (

          <div className="error-state">
            {activitiesError}
          </div>

        ) : recentActivities.length === 0 ? (

          <div className="empty-state">
            <div className="empty-icon">◷</div>
            <h3>No recent activity</h3>
            <p>Your platform activity will appear here.</p>
          </div>

        ) : (

          <div className="activity-list">

            {recentActivities.slice(0, 5).map((activity) => (

              <div
                className="activity-item"
                key={activity.id}
              >

                <div className="activity-icon">
                  ✓
                </div>

                <div className="activity-content">

                  <strong>
                    {activity.action ||
                      activity.activity_type ||
                      "Activity"}
                  </strong>

                  <span>
                    {activity.entity_type || "Decision"}
                    {activity.entity_id
                      ? ` #${activity.entity_id}`
                      : ""}
                  </span>

                </div>

                <time>
                  {activity.created_at
                    ? new Date(
                        activity.created_at
                      ).toLocaleString()
                    : "-"}
                </time>

              </div>

            ))}

          </div>

        )}

      </div>

    </div>
  );
}

export default Dashboard;