import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  BookOpen,
  Search,
  RotateCcw,
  ArrowLeft,
  ArrowRight,
  CalendarDays,
  Tag,
  Database,
  ChevronLeft,
  ChevronRight,
  Loader2,
  AlertCircle,
  SlidersHorizontal,
} from "lucide-react";

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
      return "kr-status-approved";

    case "Rejected":
      return "kr-status-rejected";

    case "Under Review":
      return "kr-status-review";

    case "Archived":
      return "kr-status-archived";

    case "Draft":
    default:
      return "kr-status-draft";
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
      const data =
        await searchKnowledgeRepository({
          q: "",
          category: "",
          decision_status: "",
          tag: "",
          page: 1,
          page_size: PAGE_SIZE,
          sort_by: "created_at",
          order: "desc",
        });

      const results =
        getResponseResults(data);

      setDecisions(results);

      setTotal(
        getResponseTotal(
          data,
          results.length
        )
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
    const totalPages = Math.max(
      1,
      Math.ceil(total / PAGE_SIZE)
    );

    if (
      nextPage < 1 ||
      nextPage > totalPages
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
    <div className="kr-page">

      <style>{`
        .kr-page {
          max-width: 1200px;
          margin: 0 auto;
          padding: 4px 0 40px;
        }

        .kr-header {
          display: flex;
          align-items: flex-start;
          justify-content: space-between;
          gap: 20px;
          margin-bottom: 25px;
        }

        .kr-header-left {
          display: flex;
          align-items: flex-start;
          gap: 15px;
        }

        .kr-header-icon {
          width: 50px;
          height: 50px;
          min-width: 50px;
          border-radius: 14px;
          background: #eaf2ff;
          color: #2563eb;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .kr-back {
          display: inline-flex;
          align-items: center;
          gap: 7px;
          color: #64748b;
          text-decoration: none;
          font-size: 13px;
          font-weight: 650;
          margin-bottom: 8px;
        }

        .kr-back:hover {
          color: #2563eb;
        }

        .kr-eyebrow {
          color: #64748b;
          font-size: 11px;
          font-weight: 800;
          letter-spacing: .08em;
          text-transform: uppercase;
          margin-bottom: 5px;
        }

        .kr-header h1 {
          margin: 0;
          color: #0f172a;
          font-size: 29px;
          line-height: 1.2;
        }

        .kr-header p {
          margin: 7px 0 0;
          color: #64748b;
          font-size: 14px;
        }

        .kr-secondary {
          min-height: 42px;
          padding: 0 15px;
          border: 1px solid #cbd5e1;
          border-radius: 9px;
          background: #fff;
          color: #475569;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: 7px;
          font-family: inherit;
          font-size: 13px;
          font-weight: 750;
          text-decoration: none;
          cursor: pointer;
          transition: .15s ease;
        }

        .kr-secondary:hover:not(:disabled) {
          background: #f8fafc;
          border-color: #94a3b8;
        }

        .kr-secondary:disabled {
          opacity: .6;
          cursor: not-allowed;
        }

        .kr-card {
          background: #fff;
          border: 1px solid #e2e8f0;
          border-radius: 17px;
          box-shadow: 0 7px 25px rgba(15, 23, 42, .05);
          overflow: hidden;
          margin-bottom: 20px;
        }

        .kr-card-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 15px;
          padding: 20px 23px;
          background: #f8fafc;
          border-bottom: 1px solid #e2e8f0;
        }

        .kr-card-heading {
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .kr-card-icon {
          width: 36px;
          height: 36px;
          border-radius: 10px;
          background: #dbeafe;
          color: #2563eb;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .kr-card-header h2 {
          margin: 0;
          color: #0f172a;
          font-size: 17px;
        }

        .kr-card-header p {
          margin: 4px 0 0;
          color: #64748b;
          font-size: 12px;
        }

        .kr-results-count {
          padding: 6px 10px;
          border-radius: 20px;
          background: #e2e8f0;
          color: #475569;
          font-size: 11px;
          font-weight: 750;
          white-space: nowrap;
        }

        .kr-filter-body {
          padding: 22px;
        }

        .kr-filter-grid {
          display: grid;
          grid-template-columns: 2fr 1fr 1fr 1fr;
          gap: 16px;
        }

        .kr-filter-grid-secondary {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 16px;
          margin-top: 16px;
        }

        .kr-field {
          display: flex;
          flex-direction: column;
          gap: 7px;
        }

        .kr-field label {
          display: flex;
          align-items: center;
          gap: 6px;
          color: #334155;
          font-size: 12px;
          font-weight: 750;
        }

        .kr-field input,
        .kr-field select {
          width: 100%;
          box-sizing: border-box;
          min-height: 43px;
          border: 1px solid #cbd5e1;
          border-radius: 9px;
          padding: 0 12px;
          background: #fff;
          color: #0f172a;
          font-family: inherit;
          font-size: 13px;
          outline: none;
        }

        .kr-field input:focus,
        .kr-field select:focus {
          border-color: #2563eb;
          box-shadow: 0 0 0 3px rgba(37, 99, 235, .1);
        }

        .kr-field input::placeholder {
          color: #94a3b8;
        }

        .kr-filter-actions {
          display: flex;
          justify-content: flex-end;
          align-items: center;
          gap: 9px;
          margin-top: 18px;
          padding-top: 18px;
          border-top: 1px solid #e2e8f0;
        }

        .kr-primary {
          min-height: 42px;
          padding: 0 16px;
          border: 1px solid #2563eb;
          border-radius: 9px;
          background: #2563eb;
          color: #fff;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: 7px;
          font-family: inherit;
          font-size: 13px;
          font-weight: 750;
          cursor: pointer;
        }

        .kr-primary:hover:not(:disabled) {
          background: #1d4ed8;
          box-shadow: 0 4px 13px rgba(37, 99, 235, .18);
        }

        .kr-primary:disabled {
          opacity: .6;
          cursor: not-allowed;
        }

        .kr-error {
          display: flex;
          align-items: flex-start;
          gap: 11px;
          padding: 14px 16px;
          margin-bottom: 20px;
          border: 1px solid #fecaca;
          border-radius: 11px;
          background: #fef2f2;
          color: #991b1b;
        }

        .kr-error-content {
          flex: 1;
        }

        .kr-error strong {
          display: block;
          margin-bottom: 3px;
          font-size: 13px;
        }

        .kr-error p {
          margin: 0 0 10px;
          font-size: 12px;
          line-height: 1.5;
        }

        .kr-results-body {
          padding: 0;
        }

        .kr-loading {
          min-height: 300px;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          gap: 10px;
          color: #64748b;
          font-size: 13px;
        }

        .kr-spin {
          animation: krSpin 1s linear infinite;
        }

        @keyframes krSpin {
          from {
            transform: rotate(0deg);
          }

          to {
            transform: rotate(360deg);
          }
        }

        .kr-empty {
          min-height: 280px;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          text-align: center;
          padding: 25px;
        }

        .kr-empty-icon {
          width: 54px;
          height: 54px;
          border-radius: 14px;
          background: #f1f5f9;
          color: #64748b;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-bottom: 13px;
        }

        .kr-empty h3 {
          margin: 0 0 5px;
          color: #475569;
          font-size: 16px;
        }

        .kr-empty p {
          margin: 0;
          color: #94a3b8;
          font-size: 12px;
        }

        .kr-table-wrapper {
          overflow-x: auto;
        }

        .kr-table {
          width: 100%;
          border-collapse: collapse;
          min-width: 900px;
        }

        .kr-table th {
          padding: 13px 15px;
          background: #f8fafc;
          color: #64748b;
          font-size: 10px;
          font-weight: 800;
          text-transform: uppercase;
          letter-spacing: .05em;
          text-align: left;
          white-space: nowrap;
          border-bottom: 1px solid #e2e8f0;
        }

        .kr-table td {
          padding: 15px;
          color: #475569;
          font-size: 12px;
          vertical-align: middle;
          border-bottom: 1px solid #f1f5f9;
        }

        .kr-table tbody tr:hover {
          background: #f8fafc;
        }

        .kr-table tbody tr:last-child td {
          border-bottom: none;
        }

        .kr-decision-title {
          display: flex;
          flex-direction: column;
          gap: 4px;
          min-width: 190px;
        }

        .kr-decision-title strong {
          color: #0f172a;
          font-size: 13px;
          line-height: 1.4;
        }

        .kr-decision-id {
          color: #94a3b8;
          font-size: 10px;
        }

        .kr-status {
          display: inline-flex;
          align-items: center;
          padding: 5px 9px;
          border-radius: 20px;
          font-size: 10px;
          font-weight: 750;
          white-space: nowrap;
        }

        .kr-status-approved {
          background: #dcfce7;
          color: #166534;
        }

        .kr-status-rejected {
          background: #fee2e2;
          color: #991b1b;
        }

        .kr-status-review {
          background: #fef3c7;
          color: #92400e;
        }

        .kr-status-archived {
          background: #e2e8f0;
          color: #475569;
        }

        .kr-status-draft {
          background: #dbeafe;
          color: #1d4ed8;
        }

        .kr-tag-list {
          display: flex;
          flex-wrap: wrap;
          gap: 4px;
          max-width: 170px;
        }

        .kr-tag {
          display: inline-flex;
          align-items: center;
          gap: 4px;
          padding: 4px 7px;
          border-radius: 5px;
          background: #f1f5f9;
          color: #475569;
          font-size: 10px;
          font-weight: 650;
        }

        .kr-view {
          min-height: 34px;
          padding: 0 11px;
          border: 1px solid #cbd5e1;
          border-radius: 7px;
          background: #fff;
          color: #2563eb;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: 5px;
          font-size: 11px;
          font-weight: 750;
          text-decoration: none;
          white-space: nowrap;
        }

        .kr-view:hover {
          background: #eff6ff;
          border-color: #93c5fd;
        }

        .kr-pagination {
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 15px;
          padding: 17px 20px;
          border-top: 1px solid #e2e8f0;
          background: #f8fafc;
        }

        .kr-page-info {
          color: #64748b;
          font-size: 12px;
          font-weight: 650;
        }

        .kr-pagination-actions {
          display: flex;
          gap: 8px;
        }

        .kr-page-button {
          min-height: 35px;
          padding: 0 11px;
          border: 1px solid #cbd5e1;
          border-radius: 7px;
          background: #fff;
          color: #475569;
          display: inline-flex;
          align-items: center;
          gap: 5px;
          font-family: inherit;
          font-size: 11px;
          font-weight: 700;
          cursor: pointer;
        }

        .kr-page-button:hover:not(:disabled) {
          background: #f1f5f9;
        }

        .kr-page-button:disabled {
          opacity: .45;
          cursor: not-allowed;
        }

        @media (max-width: 900px) {
          .kr-filter-grid {
            grid-template-columns: 1fr 1fr;
          }

          .kr-filter-grid-secondary {
            grid-template-columns: 1fr 1fr;
          }
        }

        @media (max-width: 650px) {
          .kr-header {
            flex-direction: column;
          }

          .kr-header .kr-secondary {
            width: 100%;
          }

          .kr-filter-grid,
          .kr-filter-grid-secondary {
            grid-template-columns: 1fr;
          }

          .kr-filter-actions {
            flex-direction: column;
          }

          .kr-primary,
          .kr-secondary {
            width: 100%;
          }

          .kr-pagination {
            flex-direction: column;
            align-items: stretch;
          }

          .kr-pagination-actions {
            justify-content: space-between;
          }

          .kr-page-button {
            flex: 1;
            justify-content: center;
          }
        }
      `}</style>

      {/* HEADER */}
      <div className="kr-header">

        <div className="kr-header-left">

          <div className="kr-header-icon">
            <BookOpen size={24} />
          </div>

          <div>

            <Link
              to="/decisions"
              className="kr-back"
            >
              <ArrowLeft size={15} />
              Back to Decisions
            </Link>

            <div className="kr-eyebrow">
              Organizational Knowledge
            </div>

            <h1>Knowledge Repository</h1>

            <p>
              Search and explore previous
              organizational decisions.
            </p>

          </div>

        </div>

        <Link
          to="/decisions"
          className="kr-secondary"
        >
          <Database size={15} />
          View Decisions
        </Link>

      </div>

      {/* SEARCH / FILTERS */}
      <div className="kr-card">

        <div className="kr-card-header">

          <div className="kr-card-heading">

            <div className="kr-card-icon">
              <SlidersHorizontal size={18} />
            </div>

            <div>
              <h2>Search & Filter</h2>

              <p>
                Find decisions using keywords,
                categories, status, or tags.
              </p>
            </div>

          </div>

        </div>

        <div className="kr-filter-body">

          <form onSubmit={handleSearch}>

            <div className="kr-filter-grid">

              <div className="kr-field">
                <label htmlFor="repository-search">
                  <Search size={13} />
                  Search
                </label>

                <input
                  id="repository-search"
                  type="text"
                  value={searchInput}
                  onChange={(event) =>
                    setSearchInput(
                      event.target.value
                    )
                  }
                  placeholder="Search title, problem, or rationale..."
                />
              </div>

              <div className="kr-field">
                <label htmlFor="repository-category">
                  Category
                </label>

                <select
                  id="repository-category"
                  value={category}
                  onChange={(event) => {
                    setCategory(
                      event.target.value
                    );
                    setPage(1);
                  }}
                >
                  <option value="">
                    All Categories
                  </option>

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

              <div className="kr-field">
                <label htmlFor="repository-status">
                  Status
                </label>

                <select
                  id="repository-status"
                  value={status}
                  onChange={(event) => {
                    setStatus(
                      event.target.value
                    );
                    setPage(1);
                  }}
                >
                  <option value="">
                    All Statuses
                  </option>

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

              <div className="kr-field">
                <label htmlFor="repository-tag">
                  <Tag size={13} />
                  Tag
                </label>

                <input
                  id="repository-tag"
                  type="text"
                  value={tag}
                  onChange={(event) =>
                    setTag(
                      event.target.value
                    )
                  }
                  placeholder="e.g. PostgreSQL"
                />
              </div>

            </div>

            <div className="kr-filter-grid-secondary">

              <div className="kr-field">
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

              <div className="kr-field">
                <label htmlFor="repository-order">
                  Order
                </label>

                <select
                  id="repository-order"
                  value={order}
                  onChange={(event) => {
                    setOrder(
                      event.target.value
                    );
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

            </div>

            <div className="kr-filter-actions">

              <button
                type="button"
                className="kr-secondary"
                onClick={handleReset}
                disabled={loading}
              >
                <RotateCcw size={14} />
                Reset
              </button>

              <button
                type="submit"
                className="kr-primary"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader2
                      size={14}
                      className="kr-spin"
                    />
                    Searching...
                  </>
                ) : (
                  <>
                    <Search size={14} />
                    Search Decisions
                  </>
                )}
              </button>

            </div>

          </form>

        </div>
      </div>

      {/* ERROR */}
      {error && (
        <div className="kr-error">

          <AlertCircle size={19} />

          <div className="kr-error-content">

            <strong>
              Unable to load repository
            </strong>

            <p>{error}</p>

            <button
              type="button"
              className="kr-secondary"
              onClick={() =>
                loadRepository(page)
              }
            >
              Try Again
            </button>

          </div>

        </div>
      )}

      {/* RESULTS */}
      <div className="kr-card">

        <div className="kr-card-header">

          <div className="kr-card-heading">

            <div className="kr-card-icon">
              <Database size={18} />
            </div>

            <div>
              <h2>Decision Library</h2>

              {!loading && !error && (
                <p>
                  {total === 0
                    ? "No decisions found."
                    : `${total} decision${
                        total === 1
                          ? ""
                          : "s"
                      } found`}
                </p>
              )}
            </div>

          </div>

          {!loading && !error && total > 0 && (
            <span className="kr-results-count">
              {total} Results
            </span>
          )}

        </div>

        <div className="kr-results-body">

          {loading ? (
            <div className="kr-loading">
              <Loader2
                size={25}
                className="kr-spin"
              />

              <span>
                Loading Knowledge Repository...
              </span>
            </div>
          ) : error ? (
            <div className="kr-empty">

              <div className="kr-empty-icon">
                <AlertCircle size={23} />
              </div>

              <h3>
                Decision library unavailable
              </h3>

              <p>
                Try again using the button
                above.
              </p>

            </div>
          ) : decisions.length === 0 ? (
            <div className="kr-empty">

              <div className="kr-empty-icon">
                <BookOpen size={23} />
              </div>

              <h3>No decisions found</h3>

              <p>
                Try changing your search term
                or filters.
              </p>

            </div>
          ) : (
            <>
              <div className="kr-table-wrapper">

                <table className="kr-table">

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

                    {decisions.map(
                      (decision) => (
                        <tr key={decision.id}>

                          <td>
                            <div className="kr-decision-title">

                              <strong>
                                {decision.title ||
                                  "Untitled Decision"}
                              </strong>

                              <span className="kr-decision-id">
                                Decision #
                                {decision.id}
                              </span>

                            </div>
                          </td>

                          <td>
                            {decision.category ||
                              "—"}
                          </td>

                          <td>

                            <span
                              className={`kr-status ${getStatusClass(
                                decision.status
                              )}`}
                            >
                              {decision.status ||
                                "Unknown"}
                            </span>

                          </td>

                          <td>

                            {Array.isArray(
                              decision.tags
                            ) &&
                            decision.tags.length >
                              0 ? (
                              <div className="kr-tag-list">

                                {decision.tags.map(
                                  (
                                    item,
                                    index
                                  ) => (
                                    <span
                                      className="kr-tag"
                                      key={`${item}-${index}`}
                                    >
                                      <Tag
                                        size={10}
                                      />
                                      {item}
                                    </span>
                                  )
                                )}

                              </div>
                            ) : (
                              "—"
                            )}

                          </td>

                          <td>
                            <span
                              style={{
                                display:
                                  "inline-flex",
                                alignItems:
                                  "center",
                                gap: "5px",
                                whiteSpace:
                                  "nowrap",
                              }}
                            >
                              <CalendarDays
                                size={12}
                              />

                              {formatDate(
                                decision.created_at
                              )}
                            </span>
                          </td>

                          <td>
                            <span
                              style={{
                                display:
                                  "inline-flex",
                                alignItems:
                                  "center",
                                gap: "5px",
                                whiteSpace:
                                  "nowrap",
                              }}
                            >
                              <CalendarDays
                                size={12}
                              />

                              {formatDate(
                                decision.updated_at
                              )}
                            </span>
                          </td>

                          <td>

                            <Link
                              to={`/decisions/${decision.id}`}
                              className="kr-view"
                            >
                              View
                              <ArrowRight
                                size={12}
                              />
                            </Link>

                          </td>

                        </tr>
                      )
                    )}

                  </tbody>

                </table>

              </div>

              {/* PAGINATION */}
              <div className="kr-pagination">

                <div className="kr-page-info">
                  Showing page {page} of{" "}
                  {totalPages}
                </div>

                <div className="kr-pagination-actions">

                  <button
                    type="button"
                    className="kr-page-button"
                    disabled={
                      page <= 1 ||
                      loading
                    }
                    onClick={() =>
                      handlePageChange(
                        page - 1
                      )
                    }
                  >
                    <ChevronLeft size={14} />
                    Previous
                  </button>

                  <button
                    type="button"
                    className="kr-page-button"
                    disabled={
                      page >= totalPages ||
                      loading
                    }
                    onClick={() =>
                      handlePageChange(
                        page + 1
                      )
                    }
                  >
                    Next
                    <ChevronRight size={14} />
                  </button>

                </div>

              </div>
            </>
          )}

        </div>
      </div>

    </div>
  );
}

export default KnowledgeRepository;