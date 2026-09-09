import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import {
  searchKnowledgeRepository,
  getKnowledgeRepositoryErrorMessage,
} from "../api/knowledgeApi";

const CATEGORIES = [
  "Technology",
  "Finance",
  "Operations",
  "Human Resources",
  "Security",
  "Product",
  "Infrastructure",
  "Strategy",
];

const STATUSES = [
  "Draft",
  "Under Review",
  "Approved",
  "Rejected",
  "Archived",
];

const PAGE_SIZE = 10;

const formatDate = (value) => {
  if (!value) {
    return "—";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString();
};

const getStatusClass = (status) => {
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
};

const getResponseResults = (data) => {
  if (Array.isArray(data?.results)) {
    return data.results;
  }

  if (Array.isArray(data?.decisions)) {
    return data.decisions;
  }

  return [];
};

const getResponseTotal = (data, resultsLength) => {
  if (typeof data?.total === "number") {
    return data.total;
  }

  return resultsLength;
};

function KnowledgeRepository() {
  const [searchInput, setSearchInput] = useState("");
  const [category, setCategory] = useState("");
  const [status, setStatus] = useState("");
  const [tag, setTag] = useState("");

  const [sortBy, setSortBy] = useState("created_at");
  const [order, setOrder] = useState("desc");

  const [page, setPage] = useState(1);

  const [decisions, setDecisions] = useState([]);
  const [total, setTotal] = useState(0);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadRepository = useCallback(
    async (requestedPage = page) => {
      setLoading(true);
      setError("");

      try {
        const data = await searchKnowledgeRepository({
          q: searchInput,
          category,
          decision_status: status,
          tag,
          page: requestedPage,
          page_size: PAGE_SIZE,
          sort_by: sortBy,
          order,
        });

        const results = getResponseResults(data);
        const totalResults = getResponseTotal(
          data,
          results.length
        );

        setDecisions(results);
        setTotal(totalResults);
        setPage(requestedPage);
      } catch (requestError) {
        setDecisions([]);
        setTotal(0);
        setError(
          getKnowledgeRepositoryErrorMessage(
            requestError
          )
        );
      } finally {
        setLoading(false);
      }
    },
    [
      searchInput,
      category,
      status,
      tag,
      sortBy,
      order,
      page,
    ]
  );

  useEffect(() => {
    loadRepository(1);
  }, [category, status, sortBy, order]);

  const handleSearch = async (event) => {
    event.preventDefault();

    await loadRepository(1);
  };

  const handleReset = async () => {
    setSearchInput("");
    setCategory("");
    setStatus("");
    setTag("");
    setSortBy("created_at");
    setOrder("desc");

    setLoading(true);
    setError("");

    try {
      const data = await searchKnowledgeRepository({
        q: "",
        category: "",
        decision_status: "",
        tag: "",
        page: 1,
        page_size: PAGE_SIZE,
        sort_by: "created_at",
        order: "desc",
      });

      const results = getResponseResults(data);

      setDecisions(results);
      setTotal(
        getResponseTotal(data, results.length)
      );
      setPage(1);
    } catch (requestError) {
      setDecisions([]);
      setTotal(0);
      setError(
        getKnowledgeRepositoryErrorMessage(
          requestError
        )
      );
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = async (nextPage) => {
    if (
      nextPage < 1 ||
      nextPage > Math.ceil(total / PAGE_SIZE)
    ) {
      return;
    }

    await loadRepository(nextPage);
  };

  const handleSortChange = (event) => {
    const value = event.target.value;

    if (value === "title") {
      setSortBy("title");
    } else if (value === "updated_at") {
      setSortBy("updated_at");
    } else {
      setSortBy("created_at");
    }

    setPage(1);
  };

  const totalPages = Math.max(
    1,
    Math.ceil(total / PAGE_SIZE)
  );

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1>Knowledge Repository</h1>

          <p>
            Search and explore previous organizational
            decisions.
          </p>
        </div>

        <Link
          to="/decisions"
          className="secondary-button"
        >
          View Decisions
        </Link>
      </div>

      {/* SEARCH & FILTERS */}
      <div className="card">
        <div className="card-header">
          <div>
            <h2>Search Decisions</h2>

            <p>
              Find decisions using keywords, category,
              status, or tags.
            </p>
          </div>
        </div>

        <form
          onSubmit={handleSearch}
          className="repository-filter-form"
        >
          <div className="form-group repository-search-group">
            <label htmlFor="repository-search">
              Search
            </label>

            <input
              id="repository-search"
              type="text"
              value={searchInput}
              onChange={(event) =>
                setSearchInput(event.target.value)
              }
              placeholder="Search by title, problem, or rationale..."
            />
          </div>

          <div className="form-group">
            <label htmlFor="repository-category">
              Category
            </label>

            <select
              id="repository-category"
              value={category}
              onChange={(event) => {
                setCategory(event.target.value);
                setPage(1);
              }}
            >
              <option value="">All Categories</option>

              {CATEGORIES.map((item) => (
                <option
                  key={item}
                  value={item}
                >
                  {item}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="repository-status">
              Status
            </label>

            <select
              id="repository-status"
              value={status}
              onChange={(event) => {
                setStatus(event.target.value);
                setPage(1);
              }}
            >
              <option value="">All Statuses</option>

              {STATUSES.map((item) => (
                <option
                  key={item}
                  value={item}
                >
                  {item}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="repository-tag">
              Tag
            </label>

            <input
              id="repository-tag"
              type="text"
              value={tag}
              onChange={(event) =>
                setTag(event.target.value)
              }
              placeholder="e.g. PostgreSQL"
            />
          </div>

          <div className="form-group">
            <label htmlFor="repository-sort">
              Sort By
            </label>

            <select
              id="repository-sort"
              value={sortBy}
              onChange={handleSortChange}
            >
              <option value="created_at">
                Created Date
              </option>

              <option value="updated_at">
                Last Updated
              </option>

              <option value="title">
                Title
              </option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="repository-order">
              Order
            </label>

            <select
              id="repository-order"
              value={order}
              onChange={(event) => {
                setOrder(event.target.value);
                setPage(1);
              }}
            >
              <option value="desc">
                Descending
              </option>

              <option value="asc">
                Ascending
              </option>
            </select>
          </div>

          <div className="repository-filter-actions">
            <button
              type="submit"
              className="primary-button"
              disabled={loading}
            >
              {loading ? "Searching..." : "Search"}
            </button>

            <button
              type="button"
              className="secondary-button"
              onClick={handleReset}
              disabled={loading}
            >
              Reset
            </button>
          </div>
        </form>
      </div>

      {/* ERROR */}
      {error && (
        <div className="error-message">
          <strong>Unable to load repository.</strong>

          <p>{error}</p>

          <button
            type="button"
            className="secondary-button"
            onClick={() => loadRepository(page)}
          >
            Try Again
          </button>
        </div>
      )}

      {/* RESULTS */}
      <div className="card">
        <div className="card-header">
          <div>
            <h2>Decision Library</h2>

            {!loading && !error && (
              <p>
                {total === 0
                  ? "No decisions found."
                  : `${total} decision${
                      total === 1 ? "" : "s"
                    } found`}
              </p>
            )}
          </div>
        </div>

        {loading ? (
          <div className="loading-state">
            <p>Loading Knowledge Repository...</p>
          </div>
        ) : error ? (
          <div className="empty-state">
            <p>
              The decision library could not be
              displayed.
            </p>
          </div>
        ) : decisions.length === 0 ? (
          <div className="empty-state">
            <h3>No decisions found</h3>

            <p>
              Try changing your search term or filters.
            </p>
          </div>
        ) : (
          <>
            <div className="repository-table-wrapper">
              <table className="data-table">
                <thead>
                  <tr>
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
                        <div className="decision-title-cell">
                          <strong>
                            {decision.title ||
                              "Untitled Decision"}
                          </strong>

                          <span>
                            Decision #{decision.id}
                          </span>
                        </div>
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
                          {decision.status || "Unknown"}
                        </span>
                      </td>

                      <td>
                        {Array.isArray(
                          decision.tags
                        ) &&
                        decision.tags.length > 0 ? (
                          <div className="tag-list">
                            {decision.tags.map(
                              (item, index) => (
                                <span
                                  className="tag-badge"
                                  key={`${item}-${index}`}
                                >
                                  {item}
                                </span>
                              )
                            )}
                          </div>
                        ) : (
                          <span>—</span>
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

            {/* PAGINATION */}
            <div className="pagination-container">
              <button
                type="button"
                className="secondary-button"
                disabled={
                  page <= 1 || loading
                }
                onClick={() =>
                  handlePageChange(page - 1)
                }
              >
                Previous
              </button>

              <span className="pagination-info">
                Page {page} of {totalPages}
              </span>

              <button
                type="button"
                className="secondary-button"
                disabled={
                  page >= totalPages || loading
                }
                onClick={() =>
                  handlePageChange(page + 1)
                }
              >
                Next
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default KnowledgeRepository;