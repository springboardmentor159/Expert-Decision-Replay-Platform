import { useContext, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { AuthContext } from "../context/AuthContext";
import apiClient from "../api/apiClient";


function Dashboard() {
  const { user, loading: authLoading } =
    useContext(AuthContext);

  const [dashboardData, setDashboardData] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");


  const role = user?.role || "";


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
          /*
           * There is no dedicated reviewer dashboard
           * endpoint in the backend.
           *
           * Reviewer work is handled through the
           * approval/review workflow.
           */
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
          <p>Checking your session...</p>
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
        <div className="page-header">
          <div>
            <h1>Dashboard</h1>

            <p>
              Loading your dashboard...
            </p>
          </div>
        </div>

        <div className="card">
          <div className="loading-state">
            <p>
              Loading dashboard information...
            </p>
          </div>
        </div>
      </div>
    );
  }


  if (error) {
    return (
      <div className="page-container">
        <div className="page-header">
          <div>
            <h1>Dashboard</h1>

            <p>
              Welcome back,{" "}
              {user.name ||
                user.full_name ||
                user.email}
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

        <div className="page-header">
          <div>
            <h1>Reviewer Dashboard</h1>

            <p>
              Welcome back,{" "}
              {user.name ||
                user.full_name ||
                user.email}
              .
            </p>
          </div>
        </div>


        <div className="card">
          <div className="card-header">
            <div>
              <h2>Review Workspace</h2>

              <p>
                Review decisions assigned to you
                and complete approval actions.
              </p>
            </div>
          </div>


          <div className="dashboard-actions">

            <Link
              to="/approvals"
              className="primary-button"
            >
              View Assigned Reviews
            </Link>

            <Link
              to="/decisions"
              className="secondary-button"
            >
              View Decisions
            </Link>

          </div>
        </div>


        <div className="dashboard-grid">

          <div className="card">
            <h3>Assigned Reviews</h3>

            <p>
              View decisions currently assigned
              for review.
            </p>

            <Link
              to="/approvals"
              className="secondary-button"
            >
              Open Reviews
            </Link>
          </div>


          <div className="card">
            <h3>Knowledge Repository</h3>

            <p>
              Search previous organizational
              decisions.
            </p>

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
   * GENERIC DASHBOARD DATA EXTRACTION
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


  const totalDecisions = getValue(
    [
      "total_decisions",
      "total",
      "decision_count",
    ]
  );


  const draftDecisions = getValue(
    [
      "draft_decisions",
      "draft_count",
    ]
  );


  const approvedDecisions = getValue(
    [
      "approved_decisions",
      "approved_count",
    ]
  );


  const pendingDecisions = getValue(
    [
      "pending_decisions",
      "pending_count",
      "under_review_decisions",
    ]
  );


  const rejectedDecisions = getValue(
    [
      "rejected_decisions",
      "rejected_count",
    ]
  );


  /*
   * ========================================================
   * MAIN DASHBOARD
   * ========================================================
   */

  return (
    <div className="page-container">

      {/* =========================
          HEADER
      ========================== */}

      <div className="page-header">

        <div>
          <h1>
            {role} Dashboard
          </h1>

          <p>
            Welcome back,{" "}
            {user.name ||
              user.full_name ||
              user.email}
            .
          </p>
        </div>

        <div className="dashboard-header-actions">

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
              Create Decision
            </Link>
          )}

        </div>

      </div>


      {/* =========================
          STATISTICS
      ========================== */}

      <div className="dashboard-grid">

        <div className="card dashboard-stat-card">
          <div className="dashboard-stat-label">
            Total Decisions
          </div>

          <div className="dashboard-stat-value">
            {totalDecisions}
          </div>
        </div>


        <div className="card dashboard-stat-card">
          <div className="dashboard-stat-label">
            Draft Decisions
          </div>

          <div className="dashboard-stat-value">
            {draftDecisions}
          </div>
        </div>


        <div className="card dashboard-stat-card">
          <div className="dashboard-stat-label">
            Approved Decisions
          </div>

          <div className="dashboard-stat-value">
            {approvedDecisions}
          </div>
        </div>


        <div className="card dashboard-stat-card">
          <div className="dashboard-stat-label">
            Pending / Under Review
          </div>

          <div className="dashboard-stat-value">
            {pendingDecisions}
          </div>
        </div>


        <div className="card dashboard-stat-card">
          <div className="dashboard-stat-label">
            Rejected Decisions
          </div>

          <div className="dashboard-stat-value">
            {rejectedDecisions}
          </div>
        </div>

      </div>


      {/* =========================
          QUICK ACTIONS
      ========================== */}

      <div className="card">

        <div className="card-header">

          <div>
            <h2>Quick Actions</h2>

            <p>
              Access the most common decision
              management tasks.
            </p>
          </div>

        </div>


        <div className="dashboard-actions">

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
              Create Decision
            </Link>
          )}


          <Link
            to="/knowledge-repository"
            className="secondary-button"
          >
            Knowledge Repository
          </Link>


          {role === "Manager" && (
            <Link
              to="/approvals"
              className="secondary-button"
            >
              Pending Approvals
            </Link>
          )}


          {role === "Administrator" && (
            <Link
              to="/audit"
              className="secondary-button"
            >
              Audit Logs
            </Link>
          )}

        </div>

      </div>


      {/* =========================
          ROLE INFORMATION
      ========================== */}

      <div className="card">

        <div className="card-header">

          <div>
            <h2>
              Your Workspace
            </h2>

            <p>
              Available features based on
              your role.
            </p>
          </div>

        </div>


        <div className="dashboard-grid">

          <div>
            <h3>
              Decision Management
            </h3>

            <p>
              Create, view, edit, and explore
              organizational decisions.
            </p>

            <Link
              to="/decisions"
              className="secondary-button"
            >
              Open Decisions
            </Link>
          </div>


          <div>
            <h3>
              Knowledge Repository
            </h3>

            <p>
              Search and explore previous
              organizational decisions.
            </p>

            <Link
              to="/knowledge-repository"
              className="secondary-button"
            >
              Open Repository
            </Link>
          </div>


          {role === "Employee" && (
            <div>
              <h3>
                Discussions
              </h3>

              <p>
                Collaborate with other users
                around decision discussions.
              </p>

              <Link
                to="/decisions"
                className="secondary-button"
              >
                View Decisions
              </Link>
            </div>
          )}


          {role === "Manager" && (
            <div>
              <h3>
                Approvals
              </h3>

              <p>
                Manage the approval workflow
                for organizational decisions.
              </p>

              <Link
                to="/approvals"
                className="secondary-button"
              >
                Open Approvals
              </Link>
            </div>
          )}


          {role === "Administrator" && (
            <div>
              <h3>
                Administration
              </h3>

              <p>
                Manage users, audit information,
                reports, and system functions.
              </p>

              <Link
                to="/users"
                className="secondary-button"
              >
                Administration
              </Link>
            </div>
          )}

        </div>

      </div>

    </div>
  );
}


export default Dashboard;