import { useEffect, useState } from "react";
import api from "../services/api";
import { getStoredUser } from "../auth/authService";

function Dashboard() {
  const user = getStoredUser();
  const role = user?.role;

  const [users, setUsers] = useState([]);
  const [decisions, setDecisions] = useState([]);
  const [approvals, setApprovals] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      setError("");

      // Load decisions
      const decisionsResponse = await api.get("/decisions");

      const decisionData = Array.isArray(decisionsResponse.data)
        ? decisionsResponse.data
        : decisionsResponse.data.data || [];

      setDecisions(decisionData);

      // Load pending reviews for Reviewer
      if (role === "Reviewer") {
        const approvalsResponse = await api.get(
          "/approvals/pending"
        );

        const approvalData = Array.isArray(
          approvalsResponse.data
        )
          ? approvalsResponse.data
          : approvalsResponse.data.data || [];

        setApprovals(approvalData);
      }

      // Load users for HR / Admin / Manager
      if (
        role === "HR" ||
        role === "Administrator" ||
        role === "Manager"
      ) {
        const usersResponse = await api.get("/users");

        const userData = Array.isArray(usersResponse.data)
          ? usersResponse.data
          : usersResponse.data.data || [];

        setUsers(userData);
      }
    } catch (error) {
      console.error("Dashboard error:", error);

      if (error.response?.status === 401) {
        setError(
          "Your session has expired. Please login again."
        );
      } else if (error.response?.status === 403) {
        setError(
          "You are not authorized to view this information."
        );
      } else {
        setError(
          error.response?.data?.detail ||
            "Unable to load dashboard data."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  // Decision statistics
  const draftCount = decisions.filter(
    (decision) => decision.status === "Draft"
  ).length;

  const underReviewCount = decisions.filter(
    (decision) => decision.status === "Under Review"
  ).length;

  const approvedDecisionCount = decisions.filter(
    (decision) => decision.status === "Approved"
  ).length;

  const rejectedDecisionCount = decisions.filter(
    (decision) => decision.status === "Rejected"
  ).length;

  // User statistics
  const employeeCount = users.filter(
    (user) => user.role === "Employee"
  ).length;

  const reviewerCount = users.filter(
    (user) => user.role === "Reviewer"
  ).length;

  const managerCount = users.filter(
    (user) => user.role === "Manager"
  ).length;

  const hrCount = users.filter(
    (user) => user.role === "HR"
  ).length;

  const administratorCount = users.filter(
    (user) => user.role === "Administrator"
  ).length;

  // Loading
  if (loading) {
    return (
      <div className="dashboard-page">
        <h1>
          {role === "HR"
            ? "HR Dashboard"
            : role === "Reviewer"
            ? "Reviewer Dashboard"
            : role === "Manager"
            ? "Manager Dashboard"
            : role === "Administrator"
            ? "Administrator Dashboard"
            : "Employee Dashboard"}
        </h1>

        <p>Loading dashboard...</p>
      </div>
    );
  }

  // Error
  if (error) {
    return (
      <div className="dashboard-page">
        <h1>
          {role === "HR"
            ? "HR Dashboard"
            : role === "Reviewer"
            ? "Reviewer Dashboard"
            : role === "Manager"
            ? "Manager Dashboard"
            : role === "Administrator"
            ? "Administrator Dashboard"
            : "Employee Dashboard"}
        </h1>

        <div className="error-message">
          {error}
        </div>

        <button
          className="primary-btn"
          onClick={loadDashboard}
        >
          Try Again
        </button>
      </div>
    );
  }

  // =========================================================
  // HR DASHBOARD
  // =========================================================

  if (role === "HR") {
    return (
      <div className="dashboard-page">

        <div className="page-header">
          <div>
            <h1>HR Dashboard</h1>

            <p>
              Welcome back,{" "}
              <strong>
                {user?.email || "HR User"}
              </strong>
            </p>
          </div>
        </div>

        <h2 className="dashboard-section-title">
          Workforce Overview
        </h2>

        <div className="dashboard-cards">

          <div className="dashboard-card">
            <div className="dashboard-card-label">
              Total Users
            </div>

            <div className="dashboard-card-value">
              {users.length}
            </div>

            <div className="dashboard-card-info">
              Registered users
            </div>
          </div>

          <div className="dashboard-card">
            <div className="dashboard-card-label">
              Employees
            </div>

            <div className="dashboard-card-value">
              {employeeCount}
            </div>

            <div className="dashboard-card-info">
              Employee accounts
            </div>
          </div>

          <div className="dashboard-card">
            <div className="dashboard-card-label">
              Reviewers
            </div>

            <div className="dashboard-card-value">
              {reviewerCount}
            </div>

            <div className="dashboard-card-info">
              Reviewer accounts
            </div>
          </div>

          <div className="dashboard-card">
            <div className="dashboard-card-label">
              Managers
            </div>

            <div className="dashboard-card-value">
              {managerCount}
            </div>

            <div className="dashboard-card-info">
              Manager accounts
            </div>
          </div>

        </div>

        <h2 className="dashboard-section-title">
          Decision Overview
        </h2>

        <div className="dashboard-cards">

          <div className="dashboard-card">
            <div className="dashboard-card-label">
              Total Decisions
            </div>

            <div className="dashboard-card-value">
              {decisions.length}
            </div>

            <div className="dashboard-card-info">
              All decisions
            </div>
          </div>

          <div className="dashboard-card">
            <div className="dashboard-card-label">
              Draft
            </div>

            <div className="dashboard-card-value">
              {draftCount}
            </div>

            <div className="dashboard-card-info">
              Decisions in draft
            </div>
          </div>

          <div className="dashboard-card">
            <div className="dashboard-card-label">
              Under Review
            </div>

            <div className="dashboard-card-value">
              {underReviewCount}
            </div>

            <div className="dashboard-card-info">
              Awaiting review
            </div>
          </div>

          <div className="dashboard-card">
            <div className="dashboard-card-label">
              Approved
            </div>

            <div className="dashboard-card-value">
              {approvedDecisionCount}
            </div>

            <div className="dashboard-card-info">
              Approved decisions
            </div>
          </div>

        </div>

        <div className="dashboard-section">

          <div className="section-heading">
            <h2>Role Distribution</h2>
          </div>

          <div className="role-summary">

            <div>
              <strong>Employees</strong>
              <span>{employeeCount}</span>
            </div>

            <div>
              <strong>Reviewers</strong>
              <span>{reviewerCount}</span>
            </div>

            <div>
              <strong>Managers</strong>
              <span>{managerCount}</span>
            </div>

            <div>
              <strong>HR</strong>
              <span>{hrCount}</span>
            </div>

            <div>
              <strong>Administrators</strong>
              <span>{administratorCount}</span>
            </div>

          </div>

        </div>

      </div>
    );
  }

  // =========================================================
  // REVIEWER DASHBOARD
  // =========================================================

  if (role === "Reviewer") {
    const pendingReviewCount = approvals.length;

    return (
      <div className="dashboard-page">

        <div className="page-header">
          <div>
            <h1>Reviewer Dashboard</h1>

            <p>
              Welcome back,{" "}
              <strong>
                {user?.email || "Reviewer"}
              </strong>
            </p>
          </div>
        </div>

        <h2 className="dashboard-section-title">
          Review Overview
        </h2>

        <div className="dashboard-cards">

          <div className="dashboard-card">
            <div className="dashboard-card-label">
              Assigned Reviews
            </div>

            <div className="dashboard-card-value">
              {pendingReviewCount}
            </div>

            <div className="dashboard-card-info">
              Reviews assigned to you
            </div>
          </div>

          <div className="dashboard-card">
            <div className="dashboard-card-label">
              Pending Reviews
            </div>

            <div className="dashboard-card-value">
              {pendingReviewCount}
            </div>

            <div className="dashboard-card-info">
              Awaiting your action
            </div>
          </div>

          <div className="dashboard-card">
            <div className="dashboard-card-label">
              Approved Decisions
            </div>

            <div className="dashboard-card-value">
              {approvedDecisionCount}
            </div>

            <div className="dashboard-card-info">
              Approved decisions
            </div>
          </div>

          <div className="dashboard-card">
            <div className="dashboard-card-label">
              Rejected Decisions
            </div>

            <div className="dashboard-card-value">
              {rejectedDecisionCount}
            </div>

            <div className="dashboard-card-info">
              Rejected decisions
            </div>
          </div>

        </div>

        <div className="dashboard-section">

          <div className="section-heading">
            <h2>Pending Reviews</h2>

            <span>
              {pendingReviewCount} pending
            </span>
          </div>

          {approvals.length === 0 ? (
            <div className="empty-state">

              <h3>No Pending Reviews</h3>

              <p>
                You currently have no decisions waiting for review.
              </p>

            </div>
          ) : (
            <div className="dashboard-table-container">

              <table className="dashboard-table">

                <thead>
                  <tr>
                    <th>Approval ID</th>
                    <th>Decision ID</th>
                    <th>Status</th>
                    <th>Assigned</th>
                  </tr>
                </thead>

                <tbody>

                  {approvals.slice(0, 5).map(
                    (approval) => (
                      <tr key={approval.id}>

                        <td>
                          #{approval.id}
                        </td>

                        <td>
                          Decision #{approval.decision_id}
                        </td>

                        <td>
                          {approval.status}
                        </td>

                        <td>
                          {approval.created_at
                            ? new Date(
                                approval.created_at
                              ).toLocaleDateString()
                            : "N/A"}
                        </td>

                      </tr>
                    )
                  )}

                </tbody>

              </table>

            </div>
          )}

        </div>

      </div>
    );
  }
// =========================================================
  // MANAGER DASHBOARD
  // =========================================================

  if (role === "Manager") {
    return (
      <div className="dashboard-page">

        <div className="page-header">
          <div>
            <h1>Manager Dashboard</h1>

            <p>
              Welcome back,{" "}
              <strong>
                {user?.email || "Manager"}
              </strong>
            </p>
          </div>
        </div>

        <h2 className="dashboard-section-title">
          Team Overview
        </h2>

        <div className="dashboard-cards">

          <div className="dashboard-card">
            <div className="dashboard-card-label">
              Total Users
            </div>

            <div className="dashboard-card-value">
              {users.length}
            </div>

            <div className="dashboard-card-info">
              Users in the platform
            </div>
          </div>

          <div className="dashboard-card">
            <div className="dashboard-card-label">
              Employees
            </div>

            <div className="dashboard-card-value">
              {employeeCount}
            </div>

            <div className="dashboard-card-info">
              Employee accounts
            </div>
          </div>

          <div className="dashboard-card">
            <div className="dashboard-card-label">
              Reviewers
            </div>

            <div className="dashboard-card-value">
              {reviewerCount}
            </div>

            <div className="dashboard-card-info">
              Reviewer accounts
            </div>
          </div>

          <div className="dashboard-card">
            <div className="dashboard-card-label">
              Decisions
            </div>

            <div className="dashboard-card-value">
              {decisions.length}
            </div>

            <div className="dashboard-card-info">
              Team decisions
            </div>
          </div>

        </div>

        <h2 className="dashboard-section-title">
          Decision Overview
        </h2>

        <div className="dashboard-cards">

          <div className="dashboard-card">
            <div className="dashboard-card-label">
              Draft
            </div>

            <div className="dashboard-card-value">
              {draftCount}
            </div>

            <div className="dashboard-card-info">
              Decisions in draft
            </div>
          </div>

          <div className="dashboard-card">
            <div className="dashboard-card-label">
              Under Review
            </div>

            <div className="dashboard-card-value">
              {underReviewCount}
            </div>

            <div className="dashboard-card-info">
              Awaiting review
            </div>
          </div>

          <div className="dashboard-card">
            <div className="dashboard-card-label">
              Approved
            </div>

            <div className="dashboard-card-value">
              {approvedDecisionCount}
            </div>

            <div className="dashboard-card-info">
              Approved decisions
            </div>
          </div>

          <div className="dashboard-card">
            <div className="dashboard-card-label">
              Rejected
            </div>

            <div className="dashboard-card-value">
              {rejectedDecisionCount}
            </div>

            <div className="dashboard-card-info">
              Rejected decisions
            </div>
          </div>

        </div>

        <div className="dashboard-section">

          <div className="section-heading">
            <h2>Recent Team Decisions</h2>

            <span>
              {decisions.length} total
            </span>
          </div>

          {decisions.length === 0 ? (
            <div className="empty-state">

              <h3>No decisions available</h3>

              <p>
                There are currently no decisions to display.
              </p>

            </div>
          ) : (
            <div className="dashboard-table-container">

              <table className="dashboard-table">

                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Title</th>
                    <th>Category</th>
                    <th>Status</th>
                    <th>Created</th>
                  </tr>
                </thead>

                <tbody>

                  {decisions.slice(0, 5).map(
                    (decision) => (
                      <tr key={decision.id}>

                        <td>
                          #{decision.id}
                        </td>

                        <td>
                          {decision.title}
                        </td>

                        <td>
                          {decision.category || "N/A"}
                        </td>

                        <td>
                          {decision.status}
                        </td>

                        <td>
                          {decision.created_at
                            ? new Date(
                                decision.created_at
                              ).toLocaleDateString()
                            : "N/A"}
                        </td>

                      </tr>
                    )
                  )}

                </tbody>

              </table>

            </div>
          )}

        </div>

      </div>
    );
  }

  // =========================================================
  // ADMINISTRATOR DASHBOARD
  // =========================================================

  if (role === "Administrator") {
    return (
      <div className="dashboard-page">

        <div className="page-header">
          <div>
            <h1>Administrator Dashboard</h1>

            <p>
              Welcome back,{" "}
              <strong>
                {user?.email || "Administrator"}
              </strong>
            </p>
          </div>
        </div>

        <h2 className="dashboard-section-title">
          System Overview
        </h2>

        <div className="dashboard-cards">

          <div className="dashboard-card">
            <div className="dashboard-card-label">
              Total Users
            </div>

            <div className="dashboard-card-value">
              {users.length}
            </div>

            <div className="dashboard-card-info">
              Registered platform users
            </div>
          </div>

          <div className="dashboard-card">
            <div className="dashboard-card-label">
              Employees
            </div>

            <div className="dashboard-card-value">
              {employeeCount}
            </div>

            <div className="dashboard-card-info">
              Employee accounts
            </div>
          </div>

          <div className="dashboard-card">
            <div className="dashboard-card-label">
              Reviewers
            </div>

            <div className="dashboard-card-value">
              {reviewerCount}
            </div>

            <div className="dashboard-card-info">
              Reviewer accounts
            </div>
          </div>

          <div className="dashboard-card">
            <div className="dashboard-card-label">
              Managers
            </div>

            <div className="dashboard-card-value">
              {managerCount}
            </div>

            <div className="dashboard-card-info">
              Manager accounts
            </div>
          </div>

        </div>

        <h2 className="dashboard-section-title">
          Decision Statistics
        </h2>

        <div className="dashboard-cards">

          <div className="dashboard-card">
            <div className="dashboard-card-label">
              Total Decisions
            </div>

            <div className="dashboard-card-value">
              {decisions.length}
            </div>

            <div className="dashboard-card-info">
              Decisions in system
            </div>
          </div>

          <div className="dashboard-card">
            <div className="dashboard-card-label">
              Under Review
            </div>

            <div className="dashboard-card-value">
              {underReviewCount}
            </div>

            <div className="dashboard-card-info">
              Awaiting review
            </div>
          </div>

          <div className="dashboard-card">
            <div className="dashboard-card-label">
              Approved
            </div>

            <div className="dashboard-card-value">
              {approvedDecisionCount}
            </div>

            <div className="dashboard-card-info">
              Approved decisions
            </div>
          </div>

          <div className="dashboard-card">
            <div className="dashboard-card-label">
              Rejected
            </div>

            <div className="dashboard-card-value">
              {rejectedDecisionCount}
            </div>

            <div className="dashboard-card-info">
              Rejected decisions
            </div>
          </div>

        </div>

        <div className="dashboard-section">

          <div className="section-heading">
            <h2>Role Distribution</h2>
          </div>

          <div className="role-summary">

            <div>
              <strong>Employees</strong>
              <span>{employeeCount}</span>
            </div>

            <div>
              <strong>Reviewers</strong>
              <span>{reviewerCount}</span>
            </div>

            <div>
              <strong>Managers</strong>
              <span>{managerCount}</span>
            </div>

            <div>
              <strong>HR</strong>
              <span>{hrCount}</span>
            </div>

            <div>
              <strong>Administrators</strong>
              <span>{administratorCount}</span>
            </div>

          </div>

        </div>

      </div>
    );
  }

  // =========================================================
  // EMPLOYEE DASHBOARD
  // =========================================================

  return (
    <div className="dashboard-page">

      <div className="page-header">
        <div>
          <h1>Employee Dashboard</h1>

          <p>
            Welcome back,{" "}
            <strong>
              {user?.email || "Employee"}
            </strong>
          </p>
        </div>
      </div>

      <h2 className="dashboard-section-title">
        My Decision Overview
      </h2>

      <div className="dashboard-cards">

        <div className="dashboard-card">
          <div className="dashboard-card-label">
            My Decisions
          </div>

          <div className="dashboard-card-value">
            {decisions.length}
          </div>

          <div className="dashboard-card-info">
            Decisions created by you
          </div>
        </div>

        <div className="dashboard-card">
          <div className="dashboard-card-label">
            Draft
          </div>

          <div className="dashboard-card-value">
            {draftCount}
          </div>

          <div className="dashboard-card-info">
            Decisions in draft
          </div>
        </div>

        <div className="dashboard-card">
          <div className="dashboard-card-label">
            Under Review
          </div>

          <div className="dashboard-card-value">
            {underReviewCount}
          </div>

          <div className="dashboard-card-info">
            Awaiting review
          </div>
        </div>

        <div className="dashboard-card">
          <div className="dashboard-card-label">
            Approved
          </div>

          <div className="dashboard-card-value">
            {approvedDecisionCount}
          </div>

          <div className="dashboard-card-info">
            Approved decisions
          </div>
        </div>

      </div>

      <div className="dashboard-section">

        <div className="section-heading">
          <h2>Recent Decisions</h2>

          <span>
            {decisions.length} total
          </span>
        </div>

        {decisions.length === 0 ? (
          <div className="empty-state">

            <h3>No decisions available</h3>

            <p>
              You have not created any decisions yet.
            </p>

          </div>
        ) : (
          <div className="dashboard-table-container">

            <table className="dashboard-table">

              <thead>
                <tr>
                  <th>ID</th>
                  <th>Title</th>
                  <th>Category</th>
                  <th>Status</th>
                  <th>Created</th>
                </tr>
              </thead>

              <tbody>

                {decisions.slice(0, 5).map(
                  (decision) => (

                    <tr key={decision.id}>

                      <td>
                        #{decision.id}
                      </td>

                      <td>
                        {decision.title}
                      </td>

                      <td>
                        {decision.category || "N/A"}
                      </td>

                      <td>
                        {decision.status}
                      </td>

                      <td>
                        {decision.created_at
                          ? new Date(
                              decision.created_at
                            ).toLocaleDateString()
                          : "N/A"}
                      </td>

                    </tr>

                  )
                )}

              </tbody>

            </table>

          </div>
        )}

      </div>

    </div>
  );
}

export default Dashboard;