import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";
import { useAuth } from "../context/AuthContext";
import "./Dashboard.css";

function Dashboard() {
  const navigate = useNavigate();
  const { logout } = useAuth();

  const [decisions, setDecisions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchDecisions();
  }, []);

  const fetchDecisions = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await api.get("/decisions");

      setDecisions(response.data);
    } catch (err) {
      console.error("Error fetching decisions:", err);
      setError("Unable to load decisions. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const getStatus = (decision) => {
    if (decision.status) {
      return decision.status;
    }

    return "Pending";
  };

  const getStatusClass = (status) => {
    const formattedStatus = status.toLowerCase();

    if (
      formattedStatus.includes("approved") ||
      formattedStatus.includes("completed")
    ) {
      return "status-approved";
    }

    if (
      formattedStatus.includes("rejected") ||
      formattedStatus.includes("cancelled")
    ) {
      return "status-rejected";
    }

    if (
      formattedStatus.includes("review") ||
      formattedStatus.includes("progress")
    ) {
      return "status-review";
    }

    return "status-pending";
  };

  const totalDecisions = decisions.length;

  const approvedDecisions = decisions.filter((decision) => {
    const status = getStatus(decision).toLowerCase();

    return (
      status.includes("approved") || status.includes("completed")
    );
  }).length;

  const pendingDecisions = decisions.filter((decision) => {
    const status = getStatus(decision).toLowerCase();

    return (
      status.includes("pending") ||
      status.includes("review") ||
      status.includes("progress")
    );
  }).length;

  const rejectedDecisions = decisions.filter((decision) => {
    const status = getStatus(decision).toLowerCase();

    return (
      status.includes("rejected") || status.includes("cancelled")
    );
  }).length;

  const handleCreateDecision = () => {
    navigate("/create-decision");
  };

  const handleOpenDecision = (decisionId) => {
    navigate(`/decisions/${decisionId}`);
  };

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="dashboard-container">
      {/* Header Section */}
      <div className="dashboard-header">
        <div>
          <p className="dashboard-subtitle">Welcome back</p>

          <h1 className="dashboard-title">Decision Dashboard</h1>

          <p className="dashboard-description">
            Manage, review and track your important decisions.
          </p>
        </div>

        <div className="dashboard-header-actions">
          <button
            className="create-decision-button"
            onClick={handleCreateDecision}
          >
            + Create Decision
          </button>

          <button
            className="logout-button"
            onClick={handleLogout}
          >
            Logout
          </button>
        </div>
      </div>

      {/* Statistics Section */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon total-icon">📋</div>

          <div>
            <p className="stat-label">Total Decisions</p>
            <h2 className="stat-value">{totalDecisions}</h2>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon approved-icon">✓</div>

          <div>
            <p className="stat-label">Approved</p>
            <h2 className="stat-value">{approvedDecisions}</h2>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon pending-icon">⏳</div>

          <div>
            <p className="stat-label">Pending</p>
            <h2 className="stat-value">{pendingDecisions}</h2>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon rejected-icon">✕</div>

          <div>
            <p className="stat-label">Rejected</p>
            <h2 className="stat-value">{rejectedDecisions}</h2>
          </div>
        </div>
      </div>

      {/* Decisions Section */}
      <div className="decisions-section">
        <div className="section-header">
          <div>
            <h2 className="section-title">Recent Decisions</h2>

            <p className="section-description">
              View and manage your decision records.
            </p>
          </div>

          <button
            className="refresh-button"
            onClick={fetchDecisions}
            disabled={loading}
          >
            ↻ Refresh
          </button>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="message-card">
            <p>Loading decisions...</p>
          </div>
        )}

        {/* Error State */}
        {!loading && error && (
          <div className="message-card error-message">
            <p>{error}</p>

            <button
              className="retry-button"
              onClick={fetchDecisions}
            >
              Try Again
            </button>
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && decisions.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">📂</div>

            <h3>No decisions found</h3>

            <p>
              You have not created any decisions yet. Create your first
              decision to get started.
            </p>

            <button
              className="create-decision-button"
              onClick={handleCreateDecision}
            >
              + Create Your First Decision
            </button>
          </div>
        )}

        {/* Decision Cards */}
        {!loading && !error && decisions.length > 0 && (
          <div className="decisions-grid">
            {decisions.map((decision) => {
              const status = getStatus(decision);

              return (
                <div
                  className="decision-card"
                  key={decision.id}
                  onClick={() => handleOpenDecision(decision.id)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" || event.key === " ") {
                      handleOpenDecision(decision.id);
                    }
                  }}
                >
                  <div className="decision-card-top">
                    <span className="decision-id">
                      Decision #{decision.id}
                    </span>

                    <span
                      className={`status-badge ${getStatusClass(status)}`}
                    >
                      {status}
                    </span>
                  </div>

                  <h3 className="decision-card-title">
                    {decision.title || "Untitled Decision"}
                  </h3>

                  <p className="decision-card-description">
                    {decision.problem_statement ||
                      decision.description ||
                      "No description available."}
                  </p>

                  <div className="decision-card-footer">
                    <span className="decision-category">
                      {decision.category || "General"}
                    </span>

                    <span className="view-details">
                      View Details →
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;