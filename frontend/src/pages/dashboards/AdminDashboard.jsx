import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

import axiosClient from "../../api/axiosClient";

import PageHeader from "../../components/PageHeader";
import Button from "../../components/Button";
import Card from "../../components/Card";
import StatusBadge from "../../components/StatusBadge";
import Alert from "../../components/Alert";


const AdminDashboard = () => {
  const { user, role } = useAuth();
  const navigate = useNavigate();

  const [users, setUsers] = useState([]);
  const [decisions, setDecisions] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");


  // =========================================================
  // LOAD ADMIN DASHBOARD DATA
  // =========================================================

  const loadDashboard = async () => {
    try {
      setLoading(true);
      setError("");

      const [
        usersResponse,
        decisionsResponse,
        auditResponse,
      ] = await Promise.all([
        axiosClient.get("/users"),
        axiosClient.get("/decisions", {
          params: {
            page: 1,
            limit: 100,
          },
        }),
        axiosClient.get("/audit-logs", {
          params: {
            page: 1,
            page_size: 10,
          },
        }),
      ]);


      // -------------------------------------------------------
      // USERS
      // -------------------------------------------------------

      const usersData = usersResponse.data;

      if (Array.isArray(usersData)) {
        setUsers(usersData);
      } else if (Array.isArray(usersData?.items)) {
        setUsers(usersData.items);
      } else if (Array.isArray(usersData?.users)) {
        setUsers(usersData.users);
      } else {
        setUsers([]);
      }


      // -------------------------------------------------------
      // DECISIONS
      // -------------------------------------------------------

      const decisionsData = decisionsResponse.data;

      if (Array.isArray(decisionsData)) {
        setDecisions(decisionsData);
      } else if (
        Array.isArray(decisionsData?.items)
      ) {
        setDecisions(decisionsData.items);
      } else if (
        Array.isArray(decisionsData?.decisions)
      ) {
        setDecisions(decisionsData.decisions);
      } else {
        setDecisions([]);
      }


      // -------------------------------------------------------
      // AUDIT LOGS
      // -------------------------------------------------------

      const auditData = auditResponse.data;

      if (Array.isArray(auditData)) {
        setAuditLogs(auditData);
      } else if (
        Array.isArray(auditData?.items)
      ) {
        setAuditLogs(auditData.items);
      } else if (
        Array.isArray(auditData?.logs)
      ) {
        setAuditLogs(auditData.logs);
      } else {
        setAuditLogs([]);
      }

    } catch (err) {
      console.error(
        "Admin dashboard error:",
        err
      );

      if (err.response?.status === 401) {
        setError(
          "You are not authenticated."
        );
      } else if (err.response?.status === 403) {
        setError(
          "You do not have permission to access the administrator dashboard."
        );
      } else if (err.response?.status === 404) {
        setError(
          "One of the dashboard services was not found."
        );
      } else if (err.response?.status === 422) {
        setError(
          "Invalid dashboard request."
        );
      } else if (err.response?.status === 500) {
        setError(
          "Server error. Please try again later."
        );
      } else if (!err.response) {
        setError(
          "Unable to connect to the backend server."
        );
      } else {
        setError(
          "Failed to load administrator dashboard."
        );
      }

    } finally {
      setLoading(false);
    }
  };


  useEffect(() => {
    loadDashboard();
  }, []);


  // =========================================================
  // CALCULATE STATISTICS
  // =========================================================

  const totalUsers = users.length;

  const activeUsers = users.filter(
    (item) =>
      item.is_active !== false &&
      item.active !== false
  ).length;


  const totalDecisions = decisions.length;

  const pendingDecisions = decisions.filter(
    (item) =>
      item.status === "Draft" ||
      item.status === "Under Review"
  ).length;


  const approvedDecisions = decisions.filter(
    (item) =>
      item.status === "Approved"
  ).length;


  const rejectedDecisions = decisions.filter(
    (item) =>
      item.status === "Rejected"
  ).length;


  const archivedDecisions = decisions.filter(
    (item) =>
      item.status === "Archived"
  ).length;


  const recentDecisions = decisions
    .slice()
    .sort(
      (a, b) =>
        new Date(
          b.created_at || 0
        ) -
        new Date(
          a.created_at || 0
        )
    )
    .slice(0, 5);


  // =========================================================
  // LOADING
  // =========================================================

  if (loading) {
    return (
      <div className="dashboard-page">

        <PageHeader
          title="Administrator Dashboard"
          subtitle="System overview and administration"
        />

        <Card>
          <p>Loading dashboard...</p>
        </Card>

      </div>
    );
  }


  // =========================================================
  // PAGE
  // =========================================================

  return (
    <div className="dashboard-page admin-dashboard">

      {/* PAGE HEADER */}

      <PageHeader
        title="Administrator Dashboard"
        subtitle="System overview and administration"
      />


      {/* WELCOME */}

      <div className="dashboard-welcome">

        <h2>
          Welcome,{" "}
          {user?.full_name ||
            user?.name ||
            "Administrator"}
        </h2>

        <p>
          Monitor users, decisions, approvals
          and system activity.
        </p>

      </div>


      {/* ERROR */}

      {error && (
        <Alert type="error">
          {error}
        </Alert>
      )}


      {/* =====================================================
          STAT CARDS
      ===================================================== */}

      <div className="dashboard-stats">

        <Card>

          <div className="stat-card">

            <div className="stat-label">
              Total Users
            </div>

            <div className="stat-value">
              {totalUsers}
            </div>

          </div>

        </Card>


        <Card>

          <div className="stat-card">

            <div className="stat-label">
              Active Users
            </div>

            <div className="stat-value">
              {activeUsers}
            </div>

          </div>

        </Card>


        <Card>

          <div className="stat-card">

            <div className="stat-label">
              Total Decisions
            </div>

            <div className="stat-value">
              {totalDecisions}
            </div>

          </div>

        </Card>


        <Card>

          <div className="stat-card">

            <div className="stat-label">
              Pending Decisions
            </div>

            <div className="stat-value">
              {pendingDecisions}
            </div>

          </div>

        </Card>

      </div>


      {/* =====================================================
          MAIN GRID
      ===================================================== */}

      <div className="dashboard-grid">


        {/* ---------------------------------------------------
            DECISION STATISTICS
        --------------------------------------------------- */}

        <Card>

          <div className="dashboard-card-header">

            <div>

              <h2>
                Decision Statistics
              </h2>

              <p>
                Current decision status overview.
              </p>

            </div>

          </div>


          <div className="admin-decision-stats">

            <div className="admin-stat-row">

              <span>
                Approved
              </span>

              <strong>
                {approvedDecisions}
              </strong>

            </div>


            <div className="admin-stat-row">

              <span>
                Rejected
              </span>

              <strong>
                {rejectedDecisions}
              </strong>

            </div>


            <div className="admin-stat-row">

              <span>
                Pending
              </span>

              <strong>
                {pendingDecisions}
              </strong>

            </div>


            <div className="admin-stat-row">

              <span>
                Archived
              </span>

              <strong>
                {archivedDecisions}
              </strong>

            </div>

          </div>


          <div className="dashboard-card-actions">

            <Button
              onClick={() =>
                navigate("/decisions")
              }
            >
              View Decisions
            </Button>

          </div>

        </Card>


        {/* ---------------------------------------------------
            SYSTEM ACTIVITY
        --------------------------------------------------- */}

        <Card>

          <div className="dashboard-card-header">

            <div>

              <h2>
                Recent System Activity
              </h2>

              <p>
                Latest audit activity.
              </p>

            </div>

          </div>


          {auditLogs.length === 0 ? (

            <div className="dashboard-empty">

              <p>
                No recent activity available.
              </p>

            </div>

          ) : (

            <div className="admin-activity-list">

              {auditLogs
                .slice(0, 5)
                .map((log, index) => (

                  <div
                    className="admin-activity-item"
                    key={
                      log.id || index
                    }
                  >

                    <div>

                      <strong>
                        {log.action ||
                          log.activity_type ||
                          "System Activity"}
                      </strong>

                      <p>
                        {log.description ||
                          log.entity_type ||
                          "System activity recorded"}
                      </p>

                    </div>


                    <span>

                      {log.created_at
                        ? new Date(
                            log.created_at
                          ).toLocaleString()
                        : "-"}

                    </span>

                  </div>

                ))}

            </div>

          )}


          <div className="dashboard-card-actions">

            <Button
              onClick={() =>
                navigate("/audit")
              }
            >
              View Audit Logs
            </Button>

          </div>

        </Card>


        {/* ---------------------------------------------------
            RECENT DECISIONS
        --------------------------------------------------- */}

        <Card>

          <div className="dashboard-card-header">

            <div>

              <h2>
                Recent Decisions
              </h2>

              <p>
                Recently created decisions.
              </p>

            </div>

          </div>


          {recentDecisions.length === 0 ? (

            <div className="dashboard-empty">

              <p>
                No decisions available.
              </p>

            </div>

          ) : (

            <div className="dashboard-table-wrapper">

              <table className="dashboard-table">

                <thead>

                  <tr>

                    <th>
                      Title
                    </th>

                    <th>
                      Category
                    </th>

                    <th>
                      Status
                    </th>

                  </tr>

                </thead>


                <tbody>

                  {recentDecisions.map(
                    (decision) => (

                      <tr
                        key={decision.id}
                        onClick={() =>
                          navigate(
                            `/decisions/${decision.id}`
                          )
                        }
                        className="dashboard-clickable-row"
                      >

                        <td>
                          {decision.title}
                        </td>

                        <td>
                          {decision.category ||
                            "-"}
                        </td>

                        <td>

                          <StatusBadge
                            status={
                              decision.status
                            }
                          />

                        </td>

                      </tr>

                    )
                  )}

                </tbody>

              </table>

            </div>

          )}


          <div className="dashboard-card-actions">

            <Button
              onClick={() =>
                navigate("/decisions")
              }
            >
              Manage Decisions
            </Button>

          </div>

        </Card>


        {/* ---------------------------------------------------
            ADMIN ACTIONS
        --------------------------------------------------- */}

        <Card>

          <div className="dashboard-card-header">

            <div>

              <h2>
                Administration
              </h2>

              <p>
                Manage platform resources.
              </p>

            </div>

          </div>


          <div className="admin-actions">

            <Button
              onClick={() =>
                navigate("/teams")
              }
            >
              Manage Teams
            </Button>


            <Button
              onClick={() =>
                navigate("/approvals")
              }
            >
              Manage Approvals
            </Button>


            <Button
              onClick={() =>
                navigate("/repository")
              }
            >
              Knowledge Repository
            </Button>


            <Button
              onClick={() =>
                navigate("/reports")
              }
            >
              Reports
            </Button>


            <Button
              onClick={() =>
                navigate("/audit")
              }
            >
              Audit Logs
            </Button>

          </div>

        </Card>

      </div>

    </div>
  );
};


export default AdminDashboard;