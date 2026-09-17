import { useEffect, useState } from "react";
import api from "../services/api";

function Activity() {
  const [activities, setActivities] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadActivities = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await api.get("/activities");

      setActivities(
        Array.isArray(response.data) ? response.data : []
      );
    } catch (err) {
      console.error("Activity error:", err);

      setError(
        err.response?.data?.detail ||
          "Unable to load activity records."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadActivities();
  }, []);

  const filteredActivities = activities.filter((activity) => {
    const text = `
      ${activity.action || ""}
      ${activity.description || ""}
      ${activity.activity_type || ""}
      ${activity.user_id || ""}
      ${activity.entity_type || ""}
    `.toLowerCase();

    return text.includes(search.toLowerCase());
  });

  const formatDate = (date) => {
    if (!date) return "N/A";

    return new Date(date).toLocaleString();
  };

  if (loading) {
    return (
      <div className="page-container activity-page">
        <div className="page-header">
          <div>
            <h1>System Activity</h1>
            <p>
              Monitor recent activity across the platform.
            </p>
          </div>
        </div>

        <div className="empty-state">
          <h3>Loading activity...</h3>
          <p>
            Please wait while activity records are loading.
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-container activity-page">
        <div className="page-header">
          <div>
            <h1>System Activity</h1>
            <p>
              Monitor recent activity across the platform.
            </p>
          </div>
        </div>

        <div className="error-message">
          {error}
        </div>

        <button
          className="primary-button"
          onClick={loadActivities}
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="page-container activity-page">

      <div className="page-header">
        <div>
          <h1>System Activity</h1>
          <p>
            Monitor recent actions and activity across the
            organization.
          </p>
        </div>
      </div>

      <div className="dashboard-cards activity-stats">

        <div className="dashboard-card activity-stat-card">
          <div className="dashboard-card-label">
            Total Activities
          </div>

          <div className="dashboard-card-value">
            {activities.length}
          </div>

          <div className="dashboard-card-info">
            Recent activity records
          </div>
        </div>

        <div className="dashboard-card activity-stat-card">
          <div className="dashboard-card-label">
            Visible Records
          </div>

          <div className="dashboard-card-value">
            {filteredActivities.length}
          </div>

          <div className="dashboard-card-info">
            Matching current search
          </div>
        </div>

      </div>

      <div className="dashboard-section">

        <div className="section-heading">
          <div>
            <h2>Activity Monitor</h2>

            <span>
              Review recent system activity.
            </span>
          </div>
        </div>

        <div className="activity-search-row">

          <input
            type="text"
            className="form-input"
            placeholder="Search activity..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />

          <button
            className="secondary-button"
            onClick={() => setSearch("")}
          >
            Clear
          </button>

          <button
            className="primary-button"
            onClick={loadActivities}
          >
            Refresh
          </button>

        </div>

      </div>

      <div className="dashboard-section">

        <div className="section-heading">
          <div>
            <h2>Recent Activity</h2>

            <span>
              {filteredActivities.length}{" "}
              {filteredActivities.length === 1
                ? "record"
                : "records"}{" "}
              displayed
            </span>
          </div>
        </div>

        {filteredActivities.length === 0 ? (

          <div className="empty-state">
            <h3>No activity found</h3>

            <p>
              No activity records match your search.
            </p>
          </div>

        ) : (

          <div className="dashboard-table-container activity-table-container">

            <table className="dashboard-table">

              <thead>
                <tr>
                  <th>ID</th>
                  <th>User</th>
                  <th>Action</th>
                  <th>Entity</th>
                  <th>Description</th>
                  <th>Date & Time</th>
                </tr>
              </thead>

              <tbody>

                {filteredActivities.map((activity) => (

                  <tr key={activity.id}>

                    <td>
                      <strong>
                        #{activity.id}
                      </strong>
                    </td>

                    <td>
                      User #{activity.user_id ?? "N/A"}
                    </td>

                    <td>
                      <span className="activity-action-badge">
                        {activity.action ||
                          activity.activity_type ||
                          "Activity"}
                      </span>
                    </td>

                    <td>
                      {activity.entity_type || "N/A"}
                    </td>

                    <td>
                      {activity.description || "No description"}
                    </td>

                    <td>
                      {formatDate(activity.created_at)}
                    </td>

                  </tr>

                ))}

              </tbody>

            </table>

          </div>

        )}

      </div>

    </div>
  );
}

export default Activity;