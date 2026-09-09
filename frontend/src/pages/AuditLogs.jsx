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

  async function loadActivities(filters = appliedFilters, pageNumber = page) {
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
    loadActivities(appliedFilters, nextPage);
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
    loadActivities(appliedFilters, nextPage);
  }

  const totalPages = Math.max(
    1,
    Math.ceil(total / pageSize)
  );

  return (
    <div className="page-container">

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
            {loading ? "Refreshing..." : "Refresh"}
          </button>

        </div>

      </div>

      {/* FILTERS */}
      <div className="card">

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
          className="filter-form"
        >

          <div className="form-group">

            <label htmlFor="audit-user-id">
              User ID
            </label>

            <input
              id="audit-user-id"
              type="number"
              min="1"
              value={userId}
              onChange={(event) =>
                setUserId(event.target.value)
              }
              placeholder="e.g. 13"
            />

          </div>

          <div className="form-group">

            <label htmlFor="audit-action">
              Action
            </label>

            <input
              id="audit-action"
              type="text"
              value={action}
              onChange={(event) =>
                setAction(event.target.value)
              }
              placeholder="e.g. create"
            />

          </div>

          <div className="form-group">

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
              placeholder="e.g. decision"
            />

          </div>

          <div className="form-group">

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

          <div className="form-group">

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

          <div className="filter-actions">

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
              onClick={handleResetFilters}
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

          <h2>Unable to Load Audit Logs</h2>

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

          <div className="section-header">

            <div>
              <h2>Activity Records</h2>

              <p>
                {total} record
                {total !== 1 ? "s" : ""} found
              </p>
            </div>

          </div>

          {loading ? (
            <div className="loading-state">
              Loading audit logs...
            </div>
          ) : activities.length === 0 ? (
            <div className="empty-state">

              <h3>No Audit Records Found</h3>

              <p>
                There are no activity records
                matching the selected filters.
              </p>

            </div>
          ) : (
            <div className="table-container">

              <table className="data-table">

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

                        <td>
                          {activity.id ?? "—"}
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

                        <td>
                          {activity.entity_type ||
                            activity.entity ||
                            "—"}
                        </td>

                        <td>
                          {activity.entity_id ??
                            "—"}
                        </td>

                        <td>
                          {activity.user_id ??
                            "—"}
                        </td>

                        <td>
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
              <div className="pagination">

                <button
                  type="button"
                  className="secondary-button"
                  onClick={handlePreviousPage}
                  disabled={page <= 1}
                >
                  ← Previous
                </button>

                <span className="pagination-info">
                  Page {page} of{" "}
                  {totalPages}
                </span>

                <button
                  type="button"
                  className="secondary-button"
                  onClick={handleNextPage}
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
  );
}

export default AuditLogs;