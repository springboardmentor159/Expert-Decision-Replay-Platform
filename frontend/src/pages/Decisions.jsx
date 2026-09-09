import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getDecisions } from "../api/decisionApi";

function formatDate(dateValue) {
  if (!dateValue) return "—";

  const date = new Date(dateValue);

  if (Number.isNaN(date.getTime())) {
    return "—";
  }

  return date.toLocaleString();
}

function getStatusClass(status) {
  switch (status) {
    case "Approved":
      return "status-approved";

    case "Rejected":
      return "status-rejected";

    case "Under Review":
      return "status-review";

    case "Archived":
      return "status-archived";

    case "Draft":
    default:
      return "status-draft";
  }
}

function Decisions() {
  const [decisions, setDecisions] = useState([]);

  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [status, setStatus] = useState("");
  const [tag, setTag] = useState("");

  const [sortBy, setSortBy] = useState("created_at");
  const [order, setOrder] = useState("desc");

  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);

  const [total, setTotal] = useState(0);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadDecisions() {
    try {
      setLoading(true);
      setError("");

      const data = await getDecisions({
        search,
        category,
        status,
        tag,
        page,
        pageSize,
        sortBy,
        order,
      });

      setDecisions(data.results || []);
      setTotal(data.total || 0);
    } catch (err) {
      console.error("Failed to load decisions:", err);

      if (err.response?.status === 401) {
        setError("Your session has expired. Please log in again.");
      } else if (err.response?.status === 403) {
        setError(
          "You do not have permission to view decisions."
        );
      } else if (err.response?.status === 404) {
        setError("Decision service was not found.");
      } else if (err.response?.status >= 500) {
        setError(
          "The server encountered an error. Please try again."
        );
      } else {
        setError(
          "Unable to load decisions. Please try again."
        );
      }
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDecisions();
  }, [page, sortBy, order]);

  function handleSearch(event) {
    event.preventDefault();

    setPage(1);
    loadDecisions();
  }

  function handleClearFilters() {
    setSearch("");
    setCategory("");
    setStatus("");
    setTag("");
    setSortBy("created_at");
    setOrder("desc");
    setPage(1);
  }

  const totalPages = Math.max(
    1,
    Math.ceil(total / pageSize)
  );

  return (
    <div className="page-container">

      {/* PAGE HEADER */}
      <div className="page-header">
        <div>
          <h1>Decisions</h1>
          <p>
            Search, review and manage organizational decisions.
          </p>
        </div>

        <Link
          to="/decisions/create"
          className="primary-button"
        >
          + Create Decision
        </Link>
      </div>

      {/* SEARCH AND FILTERS */}
      <div className="card decision-filters">

        <form onSubmit={handleSearch}>

          <div className="filter-grid">

            <div className="form-group">
              <label htmlFor="decision-search">
                Search
              </label>

              <input
                id="decision-search"
                type="text"
                placeholder="Search decisions..."
                value={search}
                onChange={(event) =>
                  setSearch(event.target.value)
                }
              />
            </div>

            <div className="form-group">
              <label htmlFor="decision-category">
                Category
              </label>

              <input
                id="decision-category"
                type="text"
                placeholder="e.g. Technology"
                value={category}
                onChange={(event) =>
                  setCategory(event.target.value)
                }
              />
            </div>

            <div className="form-group">
              <label htmlFor="decision-status">
                Status
              </label>

              <select
                id="decision-status"
                value={status}
                onChange={(event) => {
                  setStatus(event.target.value);
                  setPage(1);
                }}
              >
                <option value="">
                  All statuses
                </option>

                <option value="Draft">
                  Draft
                </option>

                <option value="Under Review">
                  Under Review
                </option>

                <option value="Approved">
                  Approved
                </option>

                <option value="Rejected">
                  Rejected
                </option>

                <option value="Archived">
                  Archived
                </option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="decision-tag">
                Tag
              </label>

              <input
                id="decision-tag"
                type="text"
                placeholder="Search by tag"
                value={tag}
                onChange={(event) =>
                  setTag(event.target.value)
                }
              />
            </div>

          </div>

          <div className="filter-actions">

            <button
              type="submit"
              className="primary-button"
            >
              Search
            </button>

            <button
              type="button"
              className="secondary-button"
              onClick={() => {
                handleClearFilters();
                setTimeout(loadDecisions, 0);
              }}
            >
              Clear
            </button>

          </div>

        </form>
      </div>

      {/* SORT */}
      <div className="decision-toolbar">

        <div>
          <strong>
            {total} decision{total !== 1 ? "s" : ""}
          </strong>
        </div>

        <div className="sort-controls">

          <label htmlFor="sort-by">
            Sort by
          </label>

          <select
            id="sort-by"
            value={sortBy}
            onChange={(event) => {
              setSortBy(event.target.value);
              setPage(1);
            }}
          >
            <option value="created_at">
              Created date
            </option>

            <option value="updated_at">
              Updated date
            </option>

            <option value="title">
              Title
            </option>
          </select>

          <button
            type="button"
            className="secondary-button"
            onClick={() => {
              setOrder(
                order === "desc"
                  ? "asc"
                  : "desc"
              );
              setPage(1);
            }}
          >
            {order === "desc"
              ? "Newest ↓"
              : "Oldest ↑"}
          </button>

        </div>

      </div>

      {/* ERROR */}
      {error && (
        <div className="error-state">

          <h2>Unable to Load Decisions</h2>

          <p>{error}</p>

          <button
            type="button"
            className="primary-button"
            onClick={loadDecisions}
          >
            Try Again
          </button>

        </div>
      )}

      {/* LOADING */}
      {loading && !error && (
        <div className="loading-state">
          Loading decisions...
        </div>
      )}

      {/* EMPTY */}
      {!loading &&
        !error &&
        decisions.length === 0 && (
          <div className="empty-state">

            <h2>No Decisions Found</h2>

            <p>
              There are no decisions matching your
              current search and filters.
            </p>

            <Link
              to="/decisions/create"
              className="primary-button"
            >
              Create Your First Decision
            </Link>

          </div>
        )}

      {/* DECISION TABLE */}
      {!loading &&
        !error &&
        decisions.length > 0 && (
          <div className="card decision-table-card">

            <div className="table-wrapper">

              <table className="decision-table">

                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Decision</th>
                    <th>Category</th>
                    <th>Status</th>
                    <th>Tags</th>
                    <th>Created</th>
                    <th>Updated</th>
                    <th>Action</th>
                  </tr>
                </thead>

                <tbody>

                  {decisions.map((decision) => (
                    <tr key={decision.id}>

                      <td>
                        #{decision.id}
                      </td>

                      <td>
                        <Link
                          to={`/decisions/${decision.id}`}
                          className="decision-title-link"
                        >
                          {decision.title}
                        </Link>
                      </td>

                      <td>
                        {decision.category || "—"}
                      </td>

                      <td>
                        <span
                          className={`status-badge ${getStatusClass(
                            decision.status
                          )}`}
                        >
                          {decision.status}
                        </span>
                      </td>

                      <td>

                        {decision.tags?.length > 0 ? (
                          <div className="tag-list">

                            {decision.tags.map(
                              (decisionTag) => (
                                <span
                                  key={decisionTag}
                                  className="tag-badge"
                                >
                                  {decisionTag}
                                </span>
                              )
                            )}

                          </div>
                        ) : (
                          "—"
                        )}

                      </td>

                      <td>
                        {formatDate(
                          decision.created_at
                        )}
                      </td>

                      <td>
                        {formatDate(
                          decision.updated_at
                        )}
                      </td>

                      <td>
                        <Link
                          to={`/decisions/${decision.id}`}
                          className="secondary-button small-button"
                        >
                          View
                        </Link>
                      </td>

                    </tr>
                  ))}

                </tbody>

              </table>

            </div>

          </div>
        )}

      {/* PAGINATION */}
      {!loading &&
        !error &&
        total > 0 && (
          <div className="pagination">

            <button
              type="button"
              className="secondary-button"
              disabled={page <= 1}
              onClick={() =>
                setPage((currentPage) =>
                  Math.max(1, currentPage - 1)
                )
              }
            >
              ← Previous
            </button>

            <span>
              Page {page} of {totalPages}
            </span>

            <button
              type="button"
              className="secondary-button"
              disabled={page >= totalPages}
              onClick={() =>
                setPage((currentPage) =>
                  Math.min(
                    totalPages,
                    currentPage + 1
                  )
                )
              }
            >
              Next →
            </button>

          </div>
        )}

    </div>
  );
}

export default Decisions;