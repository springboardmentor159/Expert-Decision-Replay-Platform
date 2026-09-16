import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import {
  getAuditActivities,
  getAuditErrorMessage,
} from "../api/auditApi";

function formatDate(dateValue) {
  if (!dateValue) {
    return "—";
  }

  const date = new Date(dateValue);

  if (Number.isNaN(date.getTime())) {
    return "—";
  }

  return date.toLocaleString();
}

function getActionClass(action) {
  if (!action) {
    return "";
  }

  const normalized = action.toLowerCase();

  if (
    normalized.includes("delete") ||
    normalized.includes("reject")
  ) {
    return "status-rejected";
  }

  if (
    normalized.includes("approve") ||
    normalized.includes("create") ||
    normalized.includes("login")
  ) {
    return "status-approved";
  }

  if (
    normalized.includes("update") ||
    normalized.includes("edit")
  ) {
    return "status-review";
  }

  return "status-draft";
}

function AuditLogs() {
  const [activities, setActivities] = useState([]);
  const [total, setTotal] = useState(0);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [userId, setUserId] = useState("");
  const [action, setAction] = useState("");
  const [entityType, setEntityType] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  const [appliedFilters, setAppliedFilters] = useState({
    user_id: "",
    action: "",
    entity_type: "",
    start_date: "",
    end_date: "",
  });

  const [page, setPage] = useState(1);
  const pageSize = 20;

  async function loadActivities(
    filters = appliedFilters,
    pageNumber = page
  ) {
    try {
      setLoading(true);
      setError("");

      const data = await getAuditActivities({
        ...filters,
        page: pageNumber,
        page_size: pageSize,
      });

      const records =
        Array.isArray(data?.activities)
          ? data.activities
          : Array.isArray(data?.results)
          ? data.results
          : Array.isArray(data)
          ? data
          : [];

      setActivities(records);

      setTotal(
        Number(data?.total ?? records.length)
      );
    } catch (err) {
      console.error(
        "Failed to load audit activities:",
        err
      );

      setError(
        getAuditErrorMessage(err)
      );

      setActivities([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadActivities();
  }, []);

  function handleApplyFilters(event) {
    event.preventDefault();

    if (
      startDate &&
      endDate &&
      startDate > endDate
    ) {
      setError(
        "Start date cannot be after end date."
      );
      return;
    }

    const filters = {
      user_id: userId.trim(),
      action: action.trim(),
      entity_type: entityType.trim(),
      start_date: startDate,
      end_date: endDate,
    };

    setAppliedFilters(filters);
    setPage(1);

    loadActivities(filters, 1);
  }

  function handleResetFilters() {
    const emptyFilters = {
      user_id: "",
      action: "",
      entity_type: "",
      start_date: "",
      end_date: "",
    };

    setUserId("");
    setAction("");
    setEntityType("");
    setStartDate("");
    setEndDate("");

    setAppliedFilters(emptyFilters);
    setPage(1);

    loadActivities(emptyFilters, 1);
  }

  function handlePreviousPage() {
    if (page <= 1) {
      return;
    }

    const nextPage = page - 1;

    setPage(nextPage);
    loadActivities(
      appliedFilters,
      nextPage
    );
  }

  function handleNextPage() {
    const totalPages = Math.ceil(
      total / pageSize
    );

    if (page >= totalPages) {
      return;
    }

    const nextPage = page + 1;

    setPage(nextPage);
    loadActivities(
      appliedFilters,
      nextPage
    );
  }

  const totalPages = Math.max(
    1,
    Math.ceil(total / pageSize)
  );

  return (
    <>
      <style>
        {`
          .audit-page {
            width: 100%;
          }

          .audit-filter-card {
            margin-top: 24px;
          }

          .audit-filter-form {
            display: grid;
            grid-template-columns:
              repeat(3, minmax(0, 1fr));
            gap: 20px;
            margin-top: 24px;
            width: 100%;
          }

          .audit-filter-field {
            display: flex;
            flex-direction: column;
            gap: 8px;
            min-width: 0;
          }

          .audit-filter-field label {
            display: block;
            font-size: 14px;
            font-weight: 600;
            color: #172554;
            line-height: 1.4;
          }

          .audit-filter-field input {
            width: 100%;
            min-width: 0;
            height: 44px;
            padding: 0 13px;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            background: #ffffff;
            color: #172033;
            font-size: 14px;
            box-sizing: border-box;
            outline: none;
            transition:
              border-color 0.2s ease,
              box-shadow 0.2s ease;
          }

          .audit-filter-field input::placeholder {
            color: #94a3b8;
          }

          .audit-filter-field input:focus {
            border-color: #2563eb;
            box-shadow:
              0 0 0 3px
              rgba(37, 99, 235, 0.12);
          }

          .audit-filter-actions {
            grid-column: 1 / -1;
            display: flex;
            align-items: center;
            gap: 12px;
            padding-top: 4px;
          }

          .audit-filter-actions button {
            min-width: 130px;
            height: 44px;
          }

          .audit-results-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
          }

          .audit-results-count {
            margin: 4px 0 0;
            color: #64748b;
            font-size: 14px;
          }

          .audit-table-wrapper {
            width: 100%;
            overflow-x: auto;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
          }

          .audit-table {
            width: 100%;
            min-width: 950px;
            border-collapse: collapse;
          }

          .audit-table th {
            white-space: nowrap;
            background: #f8fafc;
            color: #334155;
            font-size: 13px;
            font-weight: 700;
            text-align: left;
            padding: 14px 16px;
            border-bottom: 1px solid #e2e8f0;
          }

          .audit-table td {
            padding: 14px 16px;
            border-bottom: 1px solid #eef2f7;
            color: #334155;
            font-size: 14px;
            vertical-align: top;
          }

          .audit-table tbody tr:last-child td {
            border-bottom: none;
          }

          .audit-table tbody tr:hover {
            background: #f8fafc;
          }

          .audit-description {
            min-width: 220px;
            max-width: 360px;
            line-height: 1.5;
          }

          .audit-entity {
            font-weight: 600;
            color: #1e293b;
          }

          .audit-id {
            color: #64748b;
            font-weight: 600;
          }

          .audit-pagination {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 18px;
            margin-top: 24px;
            padding-top: 20px;
            border-top: 1px solid #e2e8f0;
          }

          .audit-pagination button {
            min-width: 120px;
          }

          .audit-pagination-info {
            min-width: 110px;
            text-align: center;
            color: #475569;
            font-size: 14px;
            font-weight: 600;
          }

          @media (max-width: 900px) {
            .audit-filter-form {
              grid-template-columns:
                repeat(2, minmax(0, 1fr));
            }
          }

          @media (max-width: 600px) {
            .audit-filter-form {
              grid-template-columns: 1fr;
              gap: 16px;
            }

            .audit-filter-actions {
              grid-column: auto;
              flex-direction: column;
              align-items: stretch;
            }

            .audit-filter-actions button {
              width: 100%;
            }

            .audit-results-header {
              align-items: flex-start;
              flex-direction: column;
            }

            .audit-pagination {
              flex-wrap: wrap;
            }

            .audit-pagination button {
              min-width: 110px;
            }
          }
        `}
      </style>

      <div className="page-container audit-page">

        {/* HEADER */}
        <div className="page-header">

          <div>
            <Link
              to="/dashboard"
              className="back-link"
            >
              ← Back to Dashboard
            </Link>

            <h1>Audit Logs</h1>

            <p>
              Review recorded user activity and
              system actions across the platform.
            </p>
          </div>

          <div className="page-header-actions">

            <button
              type="button"
              className="secondary-button"
              onClick={() =>
                loadActivities(
                  appliedFilters,
                  page
                )
              }
              disabled={loading}
            >
              {loading
                ? "Refreshing..."
                : "Refresh"}
            </button>

          </div>

        </div>

        {/* FILTER CARD */}
        <div className="card audit-filter-card">

          <div className="section-header">
            <div>
              <h2>Filter Activity</h2>

              <p>
                Narrow the audit records using
                one or more filters.
              </p>
            </div>
          </div>

          <form
            onSubmit={handleApplyFilters}
            className="audit-filter-form"
          >

            {/* USER ID */}
            <div className="audit-filter-field">

              <label htmlFor="audit-user-id">
                User ID
              </label>

              <input
                id="audit-user-id"
                type="number"
                min="1"
                value={userId}
                onChange={(event) =>
                  setUserId(
                    event.target.value
                  )
                }
                placeholder="e.g. 13"
              />

            </div>

            {/* ACTION */}
            <div className="audit-filter-field">

              <label htmlFor="audit-action">
                Action
              </label>

              <input
                id="audit-action"
                type="text"
                value={action}
                onChange={(event) =>
                  setAction(
                    event.target.value
                  )
                }
                placeholder="e.g. create"
              />

            </div>

            {/* ENTITY TYPE */}
            <div className="audit-filter-field">

              <label htmlFor="audit-entity-type">
                Entity Type
              </label>

              <input
                id="audit-entity-type"
                type="text"
                value={entityType}
                onChange={(event) =>
                  setEntityType(
                    event.target.value
                  )
                }
                placeholder="e.g. Decision"
              />

            </div>

            {/* START DATE */}
            <div className="audit-filter-field">

              <label htmlFor="audit-start-date">
                Start Date
              </label>

              <input
                id="audit-start-date"
                type="date"
                value={startDate}
                onChange={(event) =>
                  setStartDate(
                    event.target.value
                  )
                }
              />

            </div>

            {/* END DATE */}
            <div className="audit-filter-field">

              <label htmlFor="audit-end-date">
                End Date
              </label>

              <input
                id="audit-end-date"
                type="date"
                value={endDate}
                onChange={(event) =>
                  setEndDate(
                    event.target.value
                  )
                }
              />

            </div>

            {/* BUTTONS */}
            <div className="audit-filter-actions">

              <button
                type="submit"
                className="primary-button"
                disabled={loading}
              >
                Apply Filters
              </button>

              <button
                type="button"
                className="secondary-button"
                onClick={
                  handleResetFilters
                }
                disabled={loading}
              >
                Reset
              </button>

            </div>

          </form>

        </div>

        {/* ERROR */}
        {error && (
          <div className="error-state">

            <h2>
              Unable to Load Audit Logs
            </h2>

            <p>{error}</p>

            <button
              type="button"
              className="primary-button"
              onClick={() =>
                loadActivities(
                  appliedFilters,
                  page
                )
              }
            >
              Try Again
            </button>

          </div>
        )}

        {/* RESULTS */}
        {!error && (
          <div className="card">

            <div className="audit-results-header">

              <div>
                <h2>Activity Records</h2>

                <p className="audit-results-count">
                  {total} record
                  {total !== 1
                    ? "s"
                    : ""}{" "}
                  found
                </p>
              </div>

            </div>

            {loading ? (
              <div className="loading-state">
                Loading audit logs...
              </div>
            ) : activities.length === 0 ? (
              <div className="empty-state">

                <h3>
                  No Audit Records Found
                </h3>

                <p>
                  There are no activity
                  records matching the
                  selected filters.
                </p>

              </div>
            ) : (
              <div className="audit-table-wrapper">

                <table className="audit-table">

                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Action</th>
                      <th>Entity</th>
                      <th>Entity ID</th>
                      <th>User</th>
                      <th>Description</th>
                      <th>Date & Time</th>
                    </tr>
                  </thead>

                  <tbody>

                    {activities.map(
                      (activity, index) => (
                        <tr
                          key={
                            activity.id ??
                            `activity-${index}`
                          }
                        >

                          <td className="audit-id">
                            {activity.id ??
                              "—"}
                          </td>

                          <td>
                            <span
                              className={`status-badge ${getActionClass(
                                activity.action
                              )}`}
                            >
                              {activity.action ||
                                "—"}
                            </span>
                          </td>

                          <td className="audit-entity">
                            {activity.entity_type ||
                              activity.entity ||
                              "—"}
                          </td>

                          <td className="audit-id">
                            {activity.entity_id ??
                              "—"}
                          </td>

                          <td className="audit-id">
                            {activity.user_id ??
                              "—"}
                          </td>

                          <td className="audit-description">
                            {activity.description ||
                              activity.details ||
                              "—"}
                          </td>

                          <td>
                            {formatDate(
                              activity.created_at ||
                                activity.timestamp ||
                                activity.occurred_at
                            )}
                          </td>

                        </tr>
                      )
                    )}

                  </tbody>

                </table>

              </div>
            )}

            {/* PAGINATION */}
            {!loading &&
              activities.length > 0 && (
                <div className="audit-pagination">

                  <button
                    type="button"
                    className="secondary-button"
                    onClick={
                      handlePreviousPage
                    }
                    disabled={page <= 1}
                  >
                    ← Previous
                  </button>

                  <span className="audit-pagination-info">
                    Page {page} of{" "}
                    {totalPages}
                  </span>

                  <button
                    type="button"
                    className="secondary-button"
                    onClick={
                      handleNextPage
                    }
                    disabled={
                      page >= totalPages
                    }
                  >
                    Next →
                  </button>

                </div>
              )}

          </div>
        )}

        {/* FOOTER */}
        <div className="page-footer-actions">

          <Link
            to="/dashboard"
            className="secondary-button"
          >
            ← Back to Dashboard
          </Link>

        </div>

      </div>
    </>
  );
}

export default AuditLogs;