import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import {
  Search,
  SlidersHorizontal,
  Plus,
  FileText,
  CalendarDays,
  ArrowUpDown,
  ChevronLeft,
  ChevronRight,
  Eye,
  X,
  RefreshCw,
} from "lucide-react";

import { getDecisions } from "../api/decisionApi";

function formatDate(dateValue) {
  if (!dateValue) return "—";

  const date = new Date(dateValue);

  if (Number.isNaN(date.getTime())) {
    return "—";
  }

  return date.toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
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

  const [sortBy, setSortBy] =
    useState("created_at");

  const [order, setOrder] =
    useState("desc");

  const [page, setPage] =
    useState(1);

  const [pageSize] =
    useState(10);

  const [total, setTotal] =
    useState(0);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

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

      setDecisions(
        data.results || []
      );

      setTotal(
        data.total || 0
      );
    } catch (err) {
      console.error(
        "Failed to load decisions:",
        err
      );

      if (
        err.response?.status === 401
      ) {
        setError(
          "Your session has expired. Please log in again."
        );
      } else if (
        err.response?.status === 403
      ) {
        setError(
          "You do not have permission to view decisions."
        );
      } else if (
        err.response?.status === 404
      ) {
        setError(
          "Decision service was not found."
        );
      } else if (
        err.response?.status === 422
      ) {
        setError(
          "The search request contains invalid information."
        );
      } else if (
        err.response?.status >= 500
      ) {
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
  }, [
    page,
    sortBy,
    order,
  ]);

  function handleSearch(event) {
    event.preventDefault();

    setPage(1);

    setTimeout(() => {
      loadDecisions();
    }, 0);
  }

  function handleClearFilters() {
    setSearch("");
    setCategory("");
    setStatus("");
    setTag("");
    setSortBy("created_at");
    setOrder("desc");
    setPage(1);

    setTimeout(() => {
      loadDecisions();
    }, 0);
  }

  const totalPages = Math.max(
    1,
    Math.ceil(total / pageSize)
  );

  return (
    <div className="page-container decisions-page">

      {/* ==================================================
          PAGE HEADER
      =================================================== */}

      <div className="decisions-header">

        <div className="decisions-title-area">

          <div className="decisions-page-icon">
            <FileText
              size={21}
              strokeWidth={2}
            />
          </div>

          <div>
            <div className="page-eyebrow">
              DECISION MANAGEMENT
            </div>

            <h1>
              Decisions
            </h1>

            <p>
              Search, review and manage
              organizational decisions.
            </p>
          </div>

        </div>

        <Link
          to="/decisions/create"
          className="primary-button create-decision-button"
        >
          <Plus
            size={16}
            strokeWidth={2.5}
          />

          Create Decision
        </Link>

      </div>


      {/* ==================================================
          SEARCH / FILTER CARD
      =================================================== */}

      <div className="card decision-filter-card">

        <div className="decision-filter-heading">

          <div className="filter-heading-title">

            <SlidersHorizontal
              size={17}
              strokeWidth={2}
            />

            <span>
              Search & Filters
            </span>

          </div>

          {(search ||
            category ||
            status ||
            tag) && (
            <button
              type="button"
              className="clear-filter-link"
              onClick={handleClearFilters}
            >
              <X size={13} />
              Clear filters
            </button>
          )}

        </div>


        <form
          onSubmit={handleSearch}
          className="decision-filter-form"
        >

          {/* Search */}

          <div className="decision-search-field">

            <label htmlFor="decision-search">
              Search decisions
            </label>

            <div className="input-with-icon">

              <Search
                size={16}
                strokeWidth={2}
              />

              <input
                id="decision-search"
                type="text"
                placeholder="Search by title or keyword..."
                value={search}
                onChange={(event) =>
                  setSearch(
                    event.target.value
                  )
                }
              />

            </div>

          </div>


          {/* Category */}

          <div className="decision-filter-field">

            <label htmlFor="decision-category">
              Category
            </label>

            <input
              id="decision-category"
              type="text"
              placeholder="Technology"
              value={category}
              onChange={(event) =>
                setCategory(
                  event.target.value
                )
              }
            />

          </div>


          {/* Status */}

          <div className="decision-filter-field">

            <label htmlFor="decision-status">
              Status
            </label>

            <select
              id="decision-status"
              value={status}
              onChange={(event) => {
                setStatus(
                  event.target.value
                );
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


          {/* Tag */}

          <div className="decision-filter-field">

            <label htmlFor="decision-tag">
              Tag
            </label>

            <input
              id="decision-tag"
              type="text"
              placeholder="Search by tag"
              value={tag}
              onChange={(event) =>
                setTag(
                  event.target.value
                )
              }
            />

          </div>


          {/* Search Button */}

          <button
            type="submit"
            className="primary-button decision-search-button"
          >
            <Search
              size={15}
              strokeWidth={2.5}
            />

            Search
          </button>

        </form>

      </div>


      {/* ==================================================
          TOOLBAR
      =================================================== */}

      <div className="decision-toolbar-new">

        <div className="decision-count">

          <div className="decision-count-icon">
            <FileText
              size={15}
            />
          </div>

          <div>
            <strong>
              {total}
            </strong>

            <span>
              {total === 1
                ? "decision"
                : "decisions"}
            </span>
          </div>

        </div>


        <div className="decision-sort-area">

          <div className="sort-label">
            <ArrowUpDown
              size={14}
            />

            Sort by
          </div>

          <select
            value={sortBy}
            onChange={(event) => {
              setSortBy(
                event.target.value
              );
              setPage(1);
            }}
            className="sort-select"
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
            className="sort-order-button"
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
              ? "Newest first"
              : "Oldest first"}

            <ArrowUpDown
              size={13}
            />
          </button>

          <button
            type="button"
            className="refresh-button"
            onClick={loadDecisions}
            title="Refresh decisions"
          >
            <RefreshCw
              size={15}
            />
          </button>

        </div>

      </div>


      {/* ==================================================
          ERROR
      =================================================== */}

      {error && (
        <div className="decision-state-card decision-error-card">

          <div className="decision-state-icon error-icon">
            !
          </div>

          <div>

            <h2>
              Unable to Load Decisions
            </h2>

            <p>
              {error}
            </p>

            <button
              type="button"
              className="primary-button"
              onClick={loadDecisions}
            >
              Try Again
            </button>

          </div>

        </div>
      )}


      {/* ==================================================
          LOADING
      =================================================== */}

      {loading && !error && (
        <div className="decision-state-card">

          <div className="decision-loading-spinner">
            <RefreshCw
              size={20}
            />
          </div>

          <h2>
            Loading decisions
          </h2>

          <p>
            Retrieving decision records...
          </p>

        </div>
      )}


      {/* ==================================================
          EMPTY
      =================================================== */}

      {!loading &&
        !error &&
        decisions.length === 0 && (
          <div className="decision-state-card">

            <div className="decision-state-icon">
              <FileText
                size={22}
              />
            </div>

            <h2>
              No Decisions Found
            </h2>

            <p>
              There are no decisions matching
              your current search and filters.
            </p>

            <Link
              to="/decisions/create"
              className="primary-button"
            >
              <Plus size={15} />
              Create Decision
            </Link>

          </div>
        )}


      {/* ==================================================
          DECISION TABLE
      =================================================== */}

      {!loading &&
        !error &&
        decisions.length > 0 && (
          <div className="card decision-table-card">

            <div className="decision-table-header">

              <div>
                <h2>
                  Decision Records
                </h2>

                <p>
                  Organizational decisions
                  tracked in the platform.
                </p>
              </div>

              <div className="table-record-count">
                Showing{" "}
                {Math.min(
                  (page - 1) * pageSize + 1,
                  total
                )}
                –
                {Math.min(
                  page * pageSize,
                  total
                )}{" "}
                of {total}
              </div>

            </div>


            <div className="decision-table-scroll">

              <table className="decision-table-new">

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

                  {decisions.map(
                    (decision) => (
                      <tr
                        key={decision.id}
                      >

                        {/* ID */}

                        <td>
                          <span className="decision-id">
                            #{decision.id}
                          </span>
                        </td>


                        {/* TITLE */}

                        <td>

                          <Link
                            to={`/decisions/${decision.id}`}
                            className="decision-title-new"
                          >
                            {decision.title}
                          </Link>

                          <span className="decision-subtitle">
                            Decision record
                          </span>

                        </td>


                        {/* CATEGORY */}

                        <td>

                          <span className="category-badge">
                            {decision.category ||
                              "Uncategorized"}
                          </span>

                        </td>


                        {/* STATUS */}

                        <td>

                          <span
                            className={`status-badge ${getStatusClass(
                              decision.status
                            )}`}
                          >
                            <span className="status-dot-small" />

                            {decision.status}
                          </span>

                        </td>


                        {/* TAGS */}

                        <td>

                          {decision.tags?.length >
                          0 ? (
                            <div className="decision-tag-list">

                              {decision.tags
                                .slice(0, 2)
                                .map(
                                  (
                                    decisionTag
                                  ) => (
                                    <span
                                      key={
                                        decisionTag
                                      }
                                      className="decision-tag"
                                    >
                                      {decisionTag}
                                    </span>
                                  )
                                )}

                              {decision.tags
                                .length > 2 && (
                                <span className="decision-tag-more">
                                  +
                                  {decision.tags
                                    .length -
                                    2}
                                </span>
                              )}

                            </div>
                          ) : (
                            <span className="muted-value">
                              No tags
                            </span>
                          )}

                        </td>


                        {/* CREATED */}

                        <td>

                          <div className="date-cell">

                            <CalendarDays
                              size={14}
                            />

                            <span>
                              {formatDate(
                                decision.created_at
                              )}
                            </span>

                          </div>

                        </td>


                        {/* UPDATED */}

                        <td>

                          <div className="date-cell">

                            <CalendarDays
                              size={14}
                            />

                            <span>
                              {formatDate(
                                decision.updated_at
                              )}
                            </span>

                          </div>

                        </td>


                        {/* ACTION */}

                        <td>

                          <Link
                            to={`/decisions/${decision.id}`}
                            className="view-decision-button"
                          >
                            <Eye
                              size={14}
                            />

                            View
                          </Link>

                        </td>

                      </tr>
                    )
                  )}

                </tbody>

              </table>

            </div>

          </div>
        )}


      {/* ==================================================
          PAGINATION
      =================================================== */}

      {!loading &&
        !error &&
        total > 0 && (
          <div className="decision-pagination">

            <button
              type="button"
              className="pagination-button"
              disabled={page <= 1}
              onClick={() =>
                setPage(
                  (currentPage) =>
                    Math.max(
                      1,
                      currentPage - 1
                    )
                )
              }
            >
              <ChevronLeft
                size={15}
              />

              Previous
            </button>


            <div className="pagination-info">

              <span>
                Page
              </span>

              <strong>
                {page}
              </strong>

              <span>
                of {totalPages}
              </span>

            </div>


            <button
              type="button"
              className="pagination-button"
              disabled={
                page >= totalPages
              }
              onClick={() =>
                setPage(
                  (currentPage) =>
                    Math.min(
                      totalPages,
                      currentPage + 1
                    )
                )
              }
            >
              Next

              <ChevronRight
                size={15}
              />

            </button>

          </div>
        )}

    </div>
  );
}

export default Decisions;