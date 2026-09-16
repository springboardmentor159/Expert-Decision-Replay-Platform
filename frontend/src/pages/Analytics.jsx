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
    return (
      detail ||
      "The analytics information was not found."
    );
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
    <div className="analytics-stat-card">
      <div className="analytics-stat-icon">
        {title === "Total Decisions" && "▣"}
        {title === "Draft" && "◌"}
        {title === "Under Review" && "◷"}
        {title === "Approved" && "✓"}
        {title === "Rejected" && "×"}
        {title === "Archived" && "▤"}
        {title === "Total Users" && "♙"}
        {title === "Active Users" && "●"}
        {title === "Total Approvals" && "✓"}
        {title === "Completion Rate" && "%"}
      </div>

      <div className="analytics-stat-content">
        <span className="analytics-stat-label">
          {title}
        </span>

        <strong className="analytics-stat-value">
          {formatNumber(value)}
          {title === "Completion Rate" ? "%" : ""}
        </strong>

        {description && (
          <span className="analytics-stat-description">
            {description}
          </span>
        )}
      </div>
    </div>
  );
}

function StatusCard({
  label,
  value,
}) {
  return (
    <div className="analytics-status-card">
      <div className="analytics-status-top">
        <span>{label}</span>
      </div>

      <strong>
        {formatNumber(value)}
      </strong>

      <small>
        Decisions
      </small>
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
    Object.entries(
      decisionActivity || {}
    );

  const activeUsers =
    userActivity?.active_users ?? 0;

  const totalUsers =
    adminAnalytics?.total_users ?? 0;

  const usersByRole =
    adminAnalytics?.user_statistics
      ?.users_by_role ||
    adminAnalytics?.users_by_role ||
    {};

  const totalApprovals =
    approvalStatistics?.total_approvals ??
    adminAnalytics?.approval_statistics
      ?.total_approvals ??
    0;

  const completionRate =
    approvalStatistics?.completion_rate ??
    adminAnalytics?.approval_statistics
      ?.completion_rate ??
    0;

  if (loading) {
    return (
      <div className="analytics-page">
        <style>
          {analyticsStyles}
        </style>

        <div className="analytics-loading">
          <div className="analytics-loading-icon">
            ◌
          </div>

          <h2>
            Loading analytics...
          </h2>

          <p>
            Preparing your decision analytics
            dashboard.
          </p>
        </div>
      </div>
    );
  }

  if (
    !isAdmin &&
    !isManager
  ) {
    return (
      <>
        <style>
          {analyticsStyles}
        </style>

        <div className="analytics-page">

          <div className="analytics-page-header">
            <div>
              <span className="analytics-eyebrow">
                ANALYTICS & REPORTING
              </span>

              <h1>
                Decision Analytics
              </h1>

              <p>
                Analyze decision activity,
                trends, and organizational
                decision data.
              </p>
            </div>
          </div>

          <div className="analytics-empty-card">
            <div className="analytics-empty-icon">
              ◫
            </div>

            <h2>
              Analytics Not Available
            </h2>

            <p>
              This analytics workspace is
              currently available to Managers
              and Administrators.
            </p>
          </div>

        </div>
      </>
    );
  }

  return (
    <>
      <style>
        {analyticsStyles}
      </style>

      <div className="analytics-page">

        {/* HEADER */}
        <div className="analytics-page-header">

          <div>
            <span className="analytics-eyebrow">
              ANALYTICS & REPORTING
            </span>

            <h1>
              Decision Analytics
            </h1>

            <p>
              {isAdmin
                ? "Organization-wide decision analytics and activity."
                : "Team-level decision statistics and performance."}
            </p>
          </div>

          <button
            type="button"
            className="analytics-refresh-button"
            onClick={refreshAnalytics}
            disabled={refreshing}
          >
            <span>
              ↻
            </span>

            {refreshing
              ? "Refreshing..."
              : "Refresh"}
          </button>

        </div>

        {/* ERROR */}
        {errorMessage && (
          <div className="analytics-error">
            <div>
              <strong>
                Unable to load analytics
              </strong>

              <p>
                {errorMessage}
              </p>
            </div>

            <button
              type="button"
              onClick={loadAnalytics}
            >
              Try Again
            </button>
          </div>
        )}

        {/* ADMIN FILTERS */}
        {isAdmin && (
          <div className="analytics-card">

            <div className="analytics-section-header">
              <div className="analytics-section-icon">
                ⚙
              </div>

              <div>
                <h2>
                  Analytics Filters
                </h2>

                <p>
                  Filter organization-wide
                  analytics by date and user
                  activity period.
                </p>
              </div>
            </div>

            <div className="analytics-filter-grid">

              <div className="analytics-field">
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

              <div className="analytics-field">
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

              <div className="analytics-field">
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

            <div className="analytics-filter-actions">
              <button
                type="button"
                className="analytics-secondary-button"
                onClick={resetFilters}
              >
                Reset Filters
              </button>
            </div>

          </div>
        )}

        {/* DECISION OVERVIEW */}
        <div className="analytics-section-title">
          <div>
            <span className="analytics-eyebrow">
              DECISION METRICS
            </span>

            <h2>
              Decision Overview
            </h2>

            <p>
              Current decision distribution
              returned by the backend.
            </p>
          </div>
        </div>

        <div className="analytics-stat-grid">

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
                  decisionStatistics?.[
                    key
                  ] ?? 0
                }
              />
            )
          )}

        </div>

        {/* ORGANIZATION OVERVIEW */}
        {isAdmin && (
          <>
            <div className="analytics-section-title">
              <div>
                <span className="analytics-eyebrow">
                  ORGANIZATION
                </span>

                <h2>
                  Organization Overview
                </h2>

                <p>
                  User and approval statistics
                  returned by the analytics
                  APIs.
                </p>
              </div>
            </div>

            <div className="analytics-stat-grid analytics-four-columns">

              <StatCard
                title="Total Users"
                value={totalUsers}
                description="Registered platform users"
              />

              <StatCard
                title="Active Users"
                value={activeUsers}
                description={`Activity in the last ${
                  userActivity?.period_days ??
                  activityDays
                } days`}
              />

              <StatCard
                title="Total Approvals"
                value={totalApprovals}
                description="Approval records"
              />

              <StatCard
                title="Completion Rate"
                value={completionRate}
                description="Percent completed"
              />

            </div>
          </>
        )}

        {/* USERS BY ROLE */}
        {isAdmin && (
          <div className="analytics-card">

            <div className="analytics-section-header">
              <div className="analytics-section-icon">
                ♙
              </div>

              <div>
                <h2>
                  Users by Role
                </h2>

                <p>
                  Distribution of registered
                  users across platform roles.
                </p>
              </div>
            </div>

            {Object.keys(usersByRole).length ===
            0 ? (
              <div className="analytics-empty">
                <p>
                  No role statistics are
                  available.
                </p>
              </div>
            ) : (
              <div className="analytics-role-grid">
                {Object.entries(
                  usersByRole
                ).map(
                  ([role, count]) => (
                    <div
                      key={role}
                      className="analytics-role-card"
                    >
                      <div className="analytics-role-icon">
                        {role
                          .charAt(0)
                          .toUpperCase()}
                      </div>

                      <div>
                        <span>
                          {role}
                        </span>

                        <strong>
                          {formatNumber(
                            count
                          )}
                        </strong>

                        <small>
                          Users
                        </small>
                      </div>
                    </div>
                  )
                )}
              </div>
            )}

          </div>
        )}

        {/* DECISION CREATION ACTIVITY */}
        {isAdmin && (
          <div className="analytics-card">

            <div className="analytics-section-header">
              <div className="analytics-section-icon">
                ◷
              </div>

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
              <div className="analytics-empty">
                <div className="analytics-empty-icon">
                  ◌
                </div>

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
              <div className="analytics-table-wrapper">
                <table className="analytics-table">

                  <thead>
                    <tr>
                      <th>
                        Date
                      </th>

                      <th>
                        Decisions Created
                      </th>
                    </tr>
                  </thead>

                  <tbody>
                    {activityEntries.map(
                      ([date, count]) => (
                        <tr key={date}>
                          <td>
                            {date}
                          </td>

                          <td>
                            <span className="analytics-number-badge">
                              {formatNumber(
                                count
                              )}
                            </span>
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

        {/* ACTIVE USERS */}
        {isAdmin && (
          <div className="analytics-card">

            <div className="analytics-section-header">
              <div className="analytics-section-icon">
                ●
              </div>

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
              <div className="analytics-empty">
                <p>
                  No active-user activity is
                  available for this period.
                </p>
              </div>
            ) : (
              <div className="analytics-table-wrapper">
                <table className="analytics-table">

                  <thead>
                    <tr>
                      <th>
                        User ID
                      </th>

                      <th>
                        Name
                      </th>

                      <th>
                        Email
                      </th>

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
                          <span className="analytics-id-badge">
                            #{item.user_id}
                          </span>
                        </td>

                        <td className="analytics-name-cell">
                          {item.full_name ||
                            "—"}
                        </td>

                        <td>
                          {item.email ||
                            "—"}
                        </td>

                        <td>
                          <span className="analytics-number-badge">
                            {formatNumber(
                              item.activity_count
                            )}
                          </span>
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

        {/* APPROVAL MESSAGE */}
        {isAdmin &&
          approvalStatistics?.message && (
            <div className="analytics-card">

              <div className="analytics-empty">
                <div className="analytics-empty-icon">
                  ✓
                </div>

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
    </>
  );
}

const analyticsStyles = `
  .analytics-page {
    width: 100%;
    max-width: 1400px;
    margin: 0 auto;
    padding: 32px;
    box-sizing: border-box;
    background: #f8fafc;
  }

  .analytics-page-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 24px;
    margin-bottom: 28px;
  }

  .analytics-eyebrow {
    display: block;
    margin-bottom: 7px;
    color: #2563eb;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 0.14em;
  }

  .analytics-page-header h1 {
    margin: 0 0 7px;
    color: #0f172a;
    font-size: 32px;
    font-weight: 800;
    line-height: 1.2;
  }

  .analytics-page-header p {
    margin: 0;
    color: #64748b;
    font-size: 15px;
    line-height: 1.6;
  }

  .analytics-refresh-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    min-height: 44px;
    padding: 0 18px;
    border: 1px solid #cbd5e1;
    border-radius: 9px;
    background: #ffffff;
    color: #334155;
    font-family: inherit;
    font-size: 14px;
    font-weight: 700;
    cursor: pointer;
  }

  .analytics-refresh-button:hover {
    background: #f8fafc;
    border-color: #94a3b8;
  }

  .analytics-refresh-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .analytics-refresh-button span {
    font-size: 18px;
  }

  .analytics-card {
    margin-bottom: 24px;
    padding: 24px;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    background: #ffffff;
    box-shadow:
      0 2px 8px rgba(15, 23, 42, 0.04);
    box-sizing: border-box;
  }

  .analytics-section-header {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    margin-bottom: 24px;
  }

  .analytics-section-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    width: 42px;
    height: 42px;
    border-radius: 10px;
    background: #eff6ff;
    color: #2563eb;
    font-size: 19px;
    font-weight: 700;
  }

  .analytics-section-header h2 {
    margin: 0 0 5px;
    color: #0f172a;
    font-size: 20px;
    line-height: 1.3;
  }

  .analytics-section-header p {
    margin: 0;
    color: #64748b;
    font-size: 14px;
    line-height: 1.5;
  }

  .analytics-filter-grid {
    display: grid;
    grid-template-columns:
      repeat(3, minmax(0, 1fr));
    gap: 20px;
  }

  .analytics-field {
    display: flex;
    flex-direction: column;
    gap: 8px;
    min-width: 0;
  }

  .analytics-field label {
    color: #334155;
    font-size: 13px;
    font-weight: 700;
  }

  .analytics-field input,
  .analytics-field select {
    width: 100%;
    min-height: 46px;
    box-sizing: border-box;
    padding: 0 13px;
    border: 1px solid #cbd5e1;
    border-radius: 9px;
    background: #ffffff;
    color: #172033;
    font-family: inherit;
    font-size: 14px;
    outline: none;
  }

  .analytics-field input:focus,
  .analytics-field select:focus {
    border-color: #2563eb;
    box-shadow:
      0 0 0 3px
      rgba(37, 99, 235, 0.12);
  }

  .analytics-filter-actions {
    display: flex;
    justify-content: flex-end;
    margin-top: 20px;
  }

  .analytics-secondary-button {
    min-height: 42px;
    padding: 0 16px;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    background: #ffffff;
    color: #334155;
    font-family: inherit;
    font-size: 14px;
    font-weight: 700;
    cursor: pointer;
  }

  .analytics-secondary-button:hover {
    background: #f8fafc;
  }

  .analytics-section-title {
    margin: 30px 0 16px;
  }

  .analytics-section-title h2 {
    margin: 0 0 5px;
    color: #0f172a;
    font-size: 22px;
  }

  .analytics-section-title p {
    margin: 0;
    color: #64748b;
    font-size: 14px;
  }

  .analytics-stat-grid {
    display: grid;
    grid-template-columns:
      repeat(6, minmax(0, 1fr));
    gap: 14px;
    margin-bottom: 10px;
  }

  .analytics-four-columns {
    grid-template-columns:
      repeat(4, minmax(0, 1fr));
  }

  .analytics-stat-card {
    display: flex;
    align-items: center;
    gap: 13px;
    min-width: 0;
    min-height: 118px;
    padding: 18px;
    box-sizing: border-box;
    border: 1px solid #e2e8f0;
    border-radius: 13px;
    background: #ffffff;
    box-shadow:
      0 2px 8px rgba(15, 23, 42, 0.04);
  }

  .analytics-stat-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    width: 42px;
    height: 42px;
    border-radius: 11px;
    background: #eff6ff;
    color: #2563eb;
    font-size: 18px;
    font-weight: 800;
  }

  .analytics-stat-content {
    min-width: 0;
  }

  .analytics-stat-label {
    display: block;
    margin-bottom: 5px;
    color: #64748b;
    font-size: 12px;
    font-weight: 600;
    line-height: 1.4;
  }

  .analytics-stat-value {
    display: block;
    color: #0f172a;
    font-size: 25px;
    line-height: 1.2;
  }

  .analytics-stat-description {
    display: block;
    margin-top: 5px;
    color: #94a3b8;
    font-size: 11px;
    line-height: 1.4;
  }

  .analytics-status-card {
    min-width: 0;
    min-height: 118px;
    padding: 18px;
    box-sizing: border-box;
    border: 1px solid #e2e8f0;
    border-radius: 13px;
    background: #ffffff;
    box-shadow:
      0 2px 8px rgba(15, 23, 42, 0.04);
  }

  .analytics-status-top {
    margin-bottom: 13px;
  }

  .analytics-status-top span {
    color: #64748b;
    font-size: 12px;
    font-weight: 700;
  }

  .analytics-status-card strong {
    display: block;
    color: #0f172a;
    font-size: 27px;
    line-height: 1.2;
  }

  .analytics-status-card small {
    display: block;
    margin-top: 4px;
    color: #94a3b8;
    font-size: 11px;
  }

  .analytics-role-grid {
    display: grid;
    grid-template-columns:
      repeat(4, minmax(0, 1fr));
    gap: 14px;
  }

  .analytics-role-card {
    display: flex;
    align-items: center;
    gap: 13px;
    padding: 17px;
    border: 1px solid #e2e8f0;
    border-radius: 11px;
    background: #f8fafc;
  }

  .analytics-role-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    width: 40px;
    height: 40px;
    border-radius: 10px;
    background: #dbeafe;
    color: #1d4ed8;
    font-size: 16px;
    font-weight: 800;
  }

  .analytics-role-card span {
    display: block;
    color: #475569;
    font-size: 13px;
    font-weight: 700;
  }

  .analytics-role-card strong {
    display: block;
    margin-top: 3px;
    color: #0f172a;
    font-size: 22px;
  }

  .analytics-role-card small {
    display: block;
    margin-top: 2px;
    color: #94a3b8;
    font-size: 11px;
  }

  .analytics-table-wrapper {
    width: 100%;
    overflow-x: auto;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
  }

  .analytics-table {
    width: 100%;
    min-width: 700px;
    border-collapse: collapse;
    background: #ffffff;
  }

  .analytics-table th {
    padding: 14px 16px;
    border-bottom: 1px solid #e2e8f0;
    background: #f8fafc;
    color: #64748b;
    font-size: 12px;
    font-weight: 800;
    text-align: left;
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }

  .analytics-table td {
    padding: 15px 16px;
    border-bottom: 1px solid #f1f5f9;
    color: #475569;
    font-size: 14px;
    vertical-align: middle;
  }

  .analytics-table tbody tr:last-child td {
    border-bottom: none;
  }

  .analytics-table tbody tr:hover {
    background: #f8fafc;
  }

  .analytics-name-cell {
    color: #0f172a !important;
    font-weight: 700;
  }

  .analytics-number-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 34px;
    min-height: 27px;
    padding: 0 9px;
    box-sizing: border-box;
    border-radius: 7px;
    background: #eff6ff;
    color: #1d4ed8;
    font-size: 12px;
    font-weight: 800;
  }

  .analytics-id-badge {
    display: inline-flex;
    padding: 5px 8px;
    border-radius: 6px;
    background: #f1f5f9;
    color: #475569;
    font-size: 12px;
    font-weight: 700;
  }

  .analytics-empty {
    padding: 42px 20px;
    text-align: center;
    border: 1px dashed #cbd5e1;
    border-radius: 10px;
    background: #f8fafc;
  }

  .analytics-empty-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 46px;
    height: 46px;
    margin: 0 auto 12px;
    border-radius: 50%;
    background: #eff6ff;
    color: #2563eb;
    font-size: 20px;
    font-weight: 700;
  }

  .analytics-empty h3,
  .analytics-empty h2 {
    margin: 0 0 7px;
    color: #0f172a;
  }

  .analytics-empty p {
    max-width: 550px;
    margin: 0 auto;
    color: #64748b;
    line-height: 1.6;
  }

  .analytics-empty-card {
    padding: 60px 24px;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    background: #ffffff;
    text-align: center;
  }

  .analytics-empty-card .analytics-empty-icon {
    margin-bottom: 16px;
  }

  .analytics-empty-card h2 {
    margin: 0 0 8px;
    color: #0f172a;
  }

  .analytics-empty-card p {
    max-width: 500px;
    margin: 0 auto;
    color: #64748b;
    line-height: 1.6;
  }

  .analytics-error {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
    margin-bottom: 24px;
    padding: 16px 18px;
    border: 1px solid #fecaca;
    border-radius: 10px;
    background: #fef2f2;
  }

  .analytics-error strong {
    color: #991b1b;
    font-size: 14px;
  }

  .analytics-error p {
    margin: 4px 0 0;
    color: #b91c1c;
    font-size: 13px;
  }

  .analytics-error button {
    flex-shrink: 0;
    min-height: 38px;
    padding: 0 14px;
    border: 1px solid #fecaca;
    border-radius: 7px;
    background: #ffffff;
    color: #991b1b;
    font-family: inherit;
    font-weight: 700;
    cursor: pointer;
  }

  .analytics-loading {
    min-height: 400px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
  }

  .analytics-loading-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 52px;
    height: 52px;
    margin-bottom: 14px;
    border-radius: 50%;
    background: #eff6ff;
    color: #2563eb;
    font-size: 25px;
  }

  .analytics-loading h2 {
    margin: 0 0 7px;
    color: #0f172a;
  }

  .analytics-loading p {
    margin: 0;
    color: #64748b;
  }

  @media (max-width: 1200px) {
    .analytics-stat-grid {
      grid-template-columns:
        repeat(3, minmax(0, 1fr));
    }

    .analytics-four-columns {
      grid-template-columns:
        repeat(2, minmax(0, 1fr));
    }

    .analytics-role-grid {
      grid-template-columns:
        repeat(2, minmax(0, 1fr));
    }
  }

  @media (max-width: 800px) {
    .analytics-page {
      padding: 22px 16px;
    }

    .analytics-page-header {
      flex-direction: column;
      align-items: stretch;
    }

    .analytics-refresh-button {
      width: 100%;
    }

    .analytics-filter-grid {
      grid-template-columns: 1fr;
    }

    .analytics-stat-grid,
    .analytics-four-columns {
      grid-template-columns:
        repeat(2, minmax(0, 1fr));
    }
  }

  @media (max-width: 520px) {
    .analytics-page {
      padding: 18px 12px;
    }

    .analytics-page-header h1 {
      font-size: 26px;
    }

    .analytics-card {
      padding: 18px;
    }

    .analytics-stat-grid,
    .analytics-four-columns,
    .analytics-role-grid {
      grid-template-columns: 1fr;
    }

    .analytics-error {
      align-items: stretch;
      flex-direction: column;
    }

    .analytics-error button {
      width: 100%;
    }

    .analytics-filter-actions {
      justify-content: stretch;
    }

    .analytics-secondary-button {
      width: 100%;
    }
  }
`;
