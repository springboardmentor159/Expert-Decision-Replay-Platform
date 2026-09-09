import { useEffect, useMemo, useState } from "react";

import { useAuth } from "../context/AuthContext";
import apiClient from "../api/apiClient";

const STATUS_LABELS = [
  ["draft", "Draft"],
  ["under_review", "Under Review"],
  ["approved", "Approved"],
  ["rejected", "Rejected"],
  ["archived", "Archived"],
];

function formatNumber(value) {
  const number = Number(value);

  if (Number.isNaN(number)) {
    return "0";
  }

  return number.toLocaleString();
}

function formatDate(value) {
  if (!value) {
    return "—";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return String(value);
  }

  return date.toLocaleString();
}

function getErrorMessage(error) {
  const status = error?.response?.status;
  const detail = error?.response?.data?.detail;

  if (status === 400) {
    return detail || "The analytics request is invalid.";
  }

  if (status === 401) {
    return "Your session has expired. Please log in again.";
  }

  if (status === 403) {
    return (
      detail ||
      "You do not have permission to view these analytics."
    );
  }

  if (status === 404) {
    return detail || "The analytics information was not found.";
  }

  if (status === 422) {
    return (
      detail ||
      "One or more analytics filter values are invalid."
    );
  }

  if (status >= 500) {
    return (
      "A server error occurred while loading analytics. " +
      "Please try again later."
    );
  }

  return (
    detail ||
    error?.message ||
    "Unable to load analytics."
  );
}

function extractActivity(data) {
  if (!data) {
    return {};
  }

  if (
    data.activity &&
    typeof data.activity === "object"
  ) {
    return data.activity;
  }

  return {};
}

function extractUsers(data) {
  if (!data) {
    return [];
  }

  if (Array.isArray(data.users)) {
    return data.users;
  }

  return [];
}

function StatCard({
  title,
  value,
  description,
}) {
  return (
    <div className="card stat-card">
      <div className="stat-card-content">
        <div>
          <p className="stat-label">
            {title}
          </p>

          <h2 className="stat-value">
            {formatNumber(value)}
          </h2>

          {description && (
            <p className="stat-description">
              {description}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

function StatusCard({
  label,
  value,
}) {
  return (
    <div className="card">
      <p className="stat-label">
        {label}
      </p>

      <h2 className="stat-value">
        {formatNumber(value)}
      </h2>
    </div>
  );
}

export default function Analytics() {
  const { user } = useAuth();

  const [managerStatistics, setManagerStatistics] =
    useState(null);

  const [adminAnalytics, setAdminAnalytics] =
    useState(null);

  const [decisionActivity, setDecisionActivity] =
    useState({});

  const [approvalStatistics, setApprovalStatistics] =
    useState(null);

  const [userActivity, setUserActivity] =
    useState(null);

  const [startDate, setStartDate] =
    useState("");

  const [endDate, setEndDate] =
    useState("");

  const [activityDays, setActivityDays] =
    useState(30);

  const [loading, setLoading] =
    useState(true);

  const [errorMessage, setErrorMessage] =
    useState("");

  const [refreshing, setRefreshing] =
    useState(false);

  const isAdmin =
    user?.role === "Administrator";

  const isManager =
    user?.role === "Manager";

  const decisionStatistics = useMemo(() => {
    if (isAdmin) {
      return (
        adminAnalytics?.decision_statistics ||
        {}
      );
    }

    return managerStatistics || {};
  }, [
    isAdmin,
    adminAnalytics,
    managerStatistics,
  ]);

  async function loadAnalytics() {
    try {
      setLoading(true);
      setErrorMessage("");

      if (isManager) {
        const response = await apiClient.get(
          "/dashboard/manager/statistics"
        );

        setManagerStatistics(
          response.data
        );

        return;
      }

      if (isAdmin) {
        const params = {};

        if (startDate) {
          params.start_date =
            `${startDate}T00:00:00`;
        }

        if (endDate) {
          params.end_date =
            `${endDate}T23:59:59`;
        }

        const [
          analyticsResponse,
          activityResponse,
          approvalResponse,
          userActivityResponse,
        ] = await Promise.all([
          apiClient.get(
            "/dashboard/admin/analytics",
            { params }
          ),

          apiClient.get(
            "/dashboard/admin/decision-activity",
            { params }
          ),

          apiClient.get(
            "/dashboard/admin/approval-statistics"
          ),

          apiClient.get(
            "/dashboard/admin/user-activity",
            {
              params: {
                days: activityDays,
              },
            }
          ),
        ]);

        setAdminAnalytics(
          analyticsResponse.data
        );

        setDecisionActivity(
          extractActivity(
            activityResponse.data
          )
        );

        setApprovalStatistics(
          approvalResponse.data
        );

        setUserActivity(
          userActivityResponse.data
        );

        return;
      }

      setErrorMessage(
        "Analytics are currently available for Manager and Administrator roles."
      );
    } catch (error) {
      console.error(
        "Failed to load analytics:",
        error
      );

      setErrorMessage(
        getErrorMessage(error)
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  useEffect(() => {
    loadAnalytics();
  }, [
    isAdmin,
    isManager,
    startDate,
    endDate,
    activityDays,
  ]);

  async function refreshAnalytics() {
    setRefreshing(true);
    await loadAnalytics();
  }

  function validateDates() {
    if (
      startDate &&
      endDate &&
      startDate > endDate
    ) {
      return "Start date cannot be after end date.";
    }

    return "";
  }

  function handleStartDateChange(event) {
    const value = event.target.value;

    setStartDate(value);

    if (
      endDate &&
      value &&
      value > endDate
    ) {
      setErrorMessage(
        "Start date cannot be after end date."
      );
    } else {
      setErrorMessage("");
    }
  }

  function handleEndDateChange(event) {
    const value = event.target.value;

    setEndDate(value);

    if (
      startDate &&
      value &&
      startDate > value
    ) {
      setErrorMessage(
        "Start date cannot be after end date."
      );
    } else {
      setErrorMessage("");
    }
  }

  function resetFilters() {
    setStartDate("");
    setEndDate("");
    setActivityDays(30);
    setErrorMessage("");
  }

  const activityEntries =
    Object.entries(decisionActivity || {});

  const activeUsers =
    userActivity?.active_users ?? 0;

  const totalUsers =
    adminAnalytics?.total_users ?? 0;

  const usersByRole =
    adminAnalytics?.user_statistics
      ?.users_by_role ||
    adminAnalytics?.users_by_role ||
    {};

  if (loading) {
    return (
      <div className="page-container">
        <div className="loading-state">
          Loading analytics...
        </div>
      </div>
    );
  }

  if (
    !isAdmin &&
    !isManager
  ) {
    return (
      <div className="page-container">
        <div className="page-header">
          <div>
            <h1>Decision Analytics</h1>

            <p>
              Analyze decision activity,
              trends, and organizational
              decision data.
            </p>
          </div>
        </div>

        <div className="card">
          <div className="empty-state">
            <h2>Analytics Not Available</h2>

            <p>
              This analytics workspace is
              currently available to
              Managers and Administrators.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1>Decision Analytics</h1>

          <p>
            {isAdmin
              ? "Organization-wide decision analytics and activity."
              : "Team-level decision statistics and performance."}
          </p>
        </div>

        <div className="page-actions">
          <button
            type="button"
            className="button secondary"
            onClick={refreshAnalytics}
            disabled={refreshing}
          >
            {refreshing
              ? "Refreshing..."
              : "Refresh"}
          </button>
        </div>
      </div>

      {errorMessage && (
        <div className="card">
          <div className="error-state">
            <h2>
              Unable to load analytics
            </h2>

            <p>
              {errorMessage}
            </p>

            <button
              type="button"
              className="button"
              onClick={loadAnalytics}
            >
              Try Again
            </button>
          </div>
        </div>
      )}

      {isAdmin && (
        <div className="card">
          <div className="section-header">
            <div>
              <h2>Analytics Filters</h2>

              <p>
                Filter organization-wide
                decision analytics by creation
                date.
              </p>
            </div>
          </div>

          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="analyticsStartDate">
                Start Date
              </label>

              <input
                id="analyticsStartDate"
                type="date"
                value={startDate}
                onChange={
                  handleStartDateChange
                }
              />
            </div>

            <div className="form-group">
              <label htmlFor="analyticsEndDate">
                End Date
              </label>

              <input
                id="analyticsEndDate"
                type="date"
                value={endDate}
                onChange={
                  handleEndDateChange
                }
              />
            </div>

            <div className="form-group">
              <label htmlFor="activityDays">
                User Activity Period
              </label>

              <select
                id="activityDays"
                value={activityDays}
                onChange={(event) =>
                  setActivityDays(
                    Number(
                      event.target.value
                    )
                  )
                }
              >
                <option value={7}>
                  Last 7 days
                </option>

                <option value={30}>
                  Last 30 days
                </option>

                <option value={90}>
                  Last 90 days
                </option>

                <option value={180}>
                  Last 180 days
                </option>

                <option value={365}>
                  Last 365 days
                </option>
              </select>
            </div>
          </div>

          <div className="page-actions">
            <button
              type="button"
              className="button secondary"
              onClick={resetFilters}
            >
              Reset Filters
            </button>
          </div>
        </div>
      )}

      <div className="section-header">
        <div>
          <h2>Decision Overview</h2>

          <p>
            Current decision distribution
            from the backend.
          </p>
        </div>
      </div>

      <div className="stats-grid">
        <StatCard
          title="Total Decisions"
          value={
            isAdmin
              ? adminAnalytics?.total_decisions
              : managerStatistics?.total_decisions
          }
          description={
            isAdmin
              ? "Organization-wide"
              : "Your team"
          }
        />

        {STATUS_LABELS.map(
          ([key, label]) => (
            <StatusCard
              key={key}
              label={label}
              value={
                decisionStatistics?.[key] ??
                0
              }
            />
          )
        )}
      </div>

      {isAdmin && (
        <>
          <div className="section-header">
            <div>
              <h2>
                Organization Overview
              </h2>

              <p>
                User and approval statistics
                returned by the analytics APIs.
              </p>
            </div>
          </div>

          <div className="stats-grid">
            <StatCard
              title="Total Users"
              value={totalUsers}
              description="Registered platform users"
            />

            <StatCard
              title="Active Users"
              value={activeUsers}
              description={`Activity in the last ${userActivity?.period_days ?? activityDays} days`}
            />

            <StatCard
              title="Total Approvals"
              value={
                approvalStatistics?.total_approvals ??
                adminAnalytics?.approval_statistics
                  ?.total_approvals ??
                0
              }
              description="Approval records"
            />

            <StatCard
              title="Completion Rate"
              value={
                approvalStatistics?.completion_rate ??
                adminAnalytics?.approval_statistics
                  ?.completion_rate ??
                0
              }
              description="Percent completed"
            />
          </div>
        </>
      )}

      {isAdmin && (
        <div className="card">
          <div className="section-header">
            <div>
              <h2>Users by Role</h2>

              <p>
                Distribution of registered
                users across platform roles.
              </p>
            </div>
          </div>

          {Object.keys(usersByRole).length ===
          0 ? (
            <div className="empty-state">
              <p>
                No role statistics are
                available.
              </p>
            </div>
          ) : (
            <div className="table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Role</th>
                    <th>User Count</th>
                  </tr>
                </thead>

                <tbody>
                  {Object.entries(
                    usersByRole
                  ).map(
                    ([role, count]) => (
                      <tr key={role}>
                        <td>{role}</td>
                        <td>
                          {formatNumber(
                            count
                          )}
                        </td>
                      </tr>
                    )
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {isAdmin && (
        <div className="card">
          <div className="section-header">
            <div>
              <h2>
                Decision Creation Activity
              </h2>

              <p>
                Number of decisions created
                per day for the selected
                period.
              </p>
            </div>
          </div>

          {activityEntries.length ===
          0 ? (
            <div className="empty-state">
              <h3>
                No Activity Data
              </h3>

              <p>
                No decision creation
                activity was returned for
                the selected period.
              </p>
            </div>
          ) : (
            <div className="table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>
                      Decisions Created
                    </th>
                  </tr>
                </thead>

                <tbody>
                  {activityEntries.map(
                    ([date, count]) => (
                      <tr key={date}>
                        <td>{date}</td>

                        <td>
                          {formatNumber(
                            count
                          )}
                        </td>
                      </tr>
                    )
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {isAdmin && (
        <div className="card">
          <div className="section-header">
            <div>
              <h2>
                Active User Activity
              </h2>

              <p>
                Users ranked by recorded
                activity in the selected
                period.
              </p>
            </div>
          </div>

          {extractUsers(
            userActivity
          ).length === 0 ? (
            <div className="empty-state">
              <p>
                No active-user activity is
                available for this period.
              </p>
            </div>
          ) : (
            <div className="table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>User ID</th>
                    <th>Name</th>
                    <th>Email</th>
                    <th>
                      Activity Count
                    </th>
                    <th>
                      Last Activity
                    </th>
                  </tr>
                </thead>

                <tbody>
                  {extractUsers(
                    userActivity
                  ).map((item) => (
                    <tr
                      key={
                        item.user_id
                      }
                    >
                      <td>
                        #{item.user_id}
                      </td>

                      <td>
                        {item.full_name ||
                          "—"}
                      </td>

                      <td>
                        {item.email ||
                          "—"}
                      </td>

                      <td>
                        {formatNumber(
                          item.activity_count
                        )}
                      </td>

                      <td>
                        {formatDate(
                          item.last_activity
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {isAdmin &&
        approvalStatistics?.message && (
          <div className="card">
            <div className="empty-state">
              <h3>
                Approval Statistics
              </h3>

              <p>
                {approvalStatistics.message}
              </p>
            </div>
          </div>
        )}
    </div>
  );
}