import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import api from "../services/api";

function Dashboard() {
  const { user, logout } = useAuth();

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

  return (
    <div>
      <h1>Expert Decision Replay Platform</h1>

      <h2>Welcome to the Dashboard</h2>

      {user ? (
        <>
          <p>
            Welcome, <strong>{user.full_name}</strong>
          </p>

          <p>
            Role: <strong>{role}</strong>
          </p>

          {role === "Employee" && (
            <div>
              <h3>Employee Dashboard</h3>
              <p>Create and manage your decisions.</p>
              <p>View decision history and participate in discussions.</p>
            </div>
          )}

          {role === "Reviewer" && (
            <div>
              <h3>Reviewer Dashboard</h3>
              <p>Review submitted decisions.</p>
              <p>Provide feedback and request changes.</p>
            </div>
          )}

          {role === "Manager" && (
            <div>
              <h3>Manager Dashboard</h3>
              <p>Review decisions awaiting approval.</p>
              <p>Approve or reject decisions.</p>
            </div>
          )}

          {role === "Administrator" && (
            <div>
              <h3>Administrator Dashboard</h3>
              <p>
                Manage users, decisions, reports and system activities.
              </p>
            </div>
          )}

          <hr />

          {/* Decision Statistics */}
          <h3>Decision Statistics</h3>

          {loading ? (
            <p>Loading statistics...</p>
          ) : error ? (
            <p>{error}</p>
          ) : (
            <div>
              <p>
                <strong>Total Decisions:</strong>{" "}
                {stats.total_decisions}
              </p>

              <p>
                <strong>Draft Decisions:</strong>{" "}
                {stats.draft_decisions}
              </p>

              <p>
                <strong>Under Review:</strong>{" "}
                {stats.under_review}
              </p>

              <p>
                <strong>Approved Decisions:</strong>{" "}
                {stats.approved_decisions}
              </p>

              <p>
                <strong>Rejected Decisions:</strong>{" "}
                {stats.rejected_decisions}
              </p>
            </div>
          )}

          <hr />

          {/* My Decisions */}
          <h3>My Decisions</h3>

          {decisionsLoading ? (
            <p>Loading your decisions...</p>
          ) : decisionsError ? (
            <p>{decisionsError}</p>
          ) : myDecisions.length === 0 ? (
            <p>You have not created any decisions yet.</p>
          ) : (
            <table border="1" cellPadding="10">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Title</th>
                  <th>Category</th>
                  <th>Status</th>
                  <th>Created At</th>
                </tr>
              </thead>

              <tbody>
                {myDecisions.map((decision) => (
                  <tr key={decision.id}>
                    <td>{decision.id}</td>
                    <td>{decision.title}</td>
                    <td>{decision.category}</td>
                    <td>{decision.status}</td>
                    <td>
                      {decision.created_at
                        ? new Date(
                            decision.created_at
                          ).toLocaleString()
                        : "-"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          <hr />

          {/* Recent Activities */}
          <h3>Recent Activities</h3>

          {activitiesLoading ? (
            <p>Loading recent activities...</p>
          ) : activitiesError ? (
            <p>{activitiesError}</p>
          ) : recentActivities.length === 0 ? (
            <p>No recent activities found.</p>
          ) : (
            <table border="1" cellPadding="10">
              <thead>
                <tr>
                  <th>Activity</th>
                  <th>Entity</th>
                  <th>Entity ID</th>
                  <th>Date</th>
                </tr>
              </thead>

              <tbody>
                {recentActivities.map((activity) => (
                  <tr key={activity.id}>
                    <td>
                      {activity.action ||
                        activity.activity_type ||
                        "-"}
                    </td>

                    <td>
                      {activity.entity_type || "-"}
                    </td>

                    <td>
                      {activity.entity_id || "-"}
                    </td>

                    <td>
                      {activity.created_at
                        ? new Date(
                            activity.created_at
                          ).toLocaleString()
                        : "-"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </>
      ) : (
        <p>Loading user information...</p>
      )}

      <br />

      <button onClick={logout}>Logout</button>
    </div>
  );
}

export default Dashboard;