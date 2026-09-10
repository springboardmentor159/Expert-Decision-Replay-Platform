import { useCallback, useEffect, useState } from "react";
import {
  CheckCircle2,
  ChevronRight,
  Clock3,
  FileText,
  Filter,
  Plus,
  RefreshCw,
  Search,
  XCircle,
} from "lucide-react";
import { Link } from "react-router-dom";

import Alert from "../components/Alert";
import Button from "../components/Button";
import {
  getDecisions,
  type Decision,
  type DecisionFilters,
} from "../services/decisionService";

import "./DecisionListPage.css";

const STATUS_OPTIONS = [
  "Draft",
  "Pending Review",
  "Approved",
  "Rejected",
  "Archived",
];

function formatDate(value: string) {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "—";
  }

  return date.toLocaleDateString(undefined, {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function getStatusClass(status: string) {
  switch (status) {
    case "Approved":
      return "decision-status decision-status-approved";

    case "Rejected":
      return "decision-status decision-status-rejected";

    case "Pending Review":
      return "decision-status decision-status-review";

    case "Archived":
      return "decision-status decision-status-archived";

    default:
      return "decision-status decision-status-draft";
  }
}

function StatusIcon({ status }: { status: string }) {
  if (status === "Approved") {
    return <CheckCircle2 size={13} />;
  }

  if (status === "Rejected") {
    return <XCircle size={13} />;
  }

  if (status === "Pending Review") {
    return <Clock3 size={13} />;
  }

  return <FileText size={13} />;
}

export default function DecisionListPage() {
  const [decisions, setDecisions] = useState<Decision[]>([]);

  const [searchInput, setSearchInput] = useState("");
  const [statusInput, setStatusInput] = useState("");
  const [categoryInput, setCategoryInput] = useState("");

  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [category, setCategory] = useState("");

  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  const loadDecisions = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage("");

    try {
      const filters: DecisionFilters = {};

      if (status) {
        filters.status = status;
      }

      if (category.trim()) {
        filters.category = category.trim();
      }

      if (search.trim()) {
        filters.search = search.trim();
      }

      const data = await getDecisions(filters);

      setDecisions(data);
    } catch (error: unknown) {
      const statusCode = (
        error as {
          response?: {
            status?: number;
          };
        }
      )?.response?.status;

      if (statusCode === 401) {
        setErrorMessage(
          "Your session has expired. Please sign in again.",
        );
      } else if (statusCode === 403) {
        setErrorMessage(
          "You do not have permission to view these decisions.",
        );
      } else if (statusCode === 404) {
        setErrorMessage(
          "The decision service could not be found.",
        );
      } else if (statusCode === 422) {
        setErrorMessage(
          "Some filter values are invalid. Please check them and try again.",
        );
      } else if (statusCode && statusCode >= 500) {
        setErrorMessage(
          "The decision service is temporarily unavailable. Please try again.",
        );
      } else {
        setErrorMessage(
          "Unable to load decisions. Please try again.",
        );
      }
    } finally {
      setIsLoading(false);
    }
  }, [category, search, status]);

  useEffect(() => {
    void loadDecisions();
  }, [loadDecisions]);

  function handleApplyFilters() {
    setSearch(searchInput.trim());
    setStatus(statusInput);
    setCategory(categoryInput.trim());
  }

  function handleClearFilters() {
    setSearchInput("");
    setStatusInput("");
    setCategoryInput("");

    setSearch("");
    setStatus("");
    setCategory("");
  }

  function handleRetry() {
    void loadDecisions();
  }

  const hasActiveFilters =
    Boolean(search || status || category);

  const hasInputFilters =
    Boolean(
      searchInput.trim() ||
        statusInput ||
        categoryInput.trim(),
    );

  const draftCount = decisions.filter(
    (decision) => decision.status === "Draft",
  ).length;

  const reviewCount = decisions.filter(
    (decision) => decision.status === "Pending Review",
  ).length;

  const approvedCount = decisions.filter(
    (decision) => decision.status === "Approved",
  ).length;

  return (
    <div className="decisions-page">
      {/* =====================================================
          PAGE HEADER
         ===================================================== */}
      <header className="decisions-page-header">
        <div className="decisions-heading">
          <div className="decisions-breadcrumb">
            <span>Workspace</span>
            <ChevronRight size={13} />
            <strong>Decisions</strong>
          </div>

          <div className="decisions-title-row">
            <div>
              <p className="decisions-eyebrow">
                Decision management
              </p>

              <h1>Decisions</h1>

              <p className="decisions-description">
                Search, review, and manage organizational
                decisions throughout their lifecycle.
              </p>
            </div>
          </div>
        </div>

        <Link
          to="/decisions/new"
          className="decisions-create-button"
        >
          <Plus size={17} />
          <span>Create decision</span>
        </Link>
      </header>

      {/* =====================================================
          SUMMARY
         ===================================================== */}
      <section
        className="decisions-summary"
        aria-label="Decision summary"
      >
        <div className="decisions-summary-item">
          <span className="decisions-summary-icon decisions-summary-blue">
            <FileText size={16} />
          </span>

          <div>
            <strong>{decisions.length}</strong>
            <span>Visible decisions</span>
          </div>
        </div>

        <div className="decisions-summary-divider" />

        <div className="decisions-summary-item">
          <span className="decisions-summary-icon decisions-summary-amber">
            <Clock3 size={16} />
          </span>

          <div>
            <strong>{reviewCount}</strong>
            <span>Under review</span>
          </div>
        </div>

        <div className="decisions-summary-divider" />

        <div className="decisions-summary-item">
          <span className="decisions-summary-icon decisions-summary-green">
            <CheckCircle2 size={16} />
          </span>

          <div>
            <strong>{approvedCount}</strong>
            <span>Approved</span>
          </div>
        </div>

        <div className="decisions-summary-divider" />

        <div className="decisions-summary-item">
          <span className="decisions-summary-icon decisions-summary-purple">
            <Filter size={16} />
          </span>

          <div>
            <strong>
              {hasActiveFilters ? "Active" : "All"}
            </strong>
            <span>Filter view</span>
          </div>
        </div>
      </section>

      {/* =====================================================
          FILTER PANEL
         ===================================================== */}
      <section className="decisions-filter-panel">
        <div className="decisions-filter-header">
          <div>
            <div className="decisions-filter-title">
              <span className="decisions-filter-title-icon">
                <Filter size={15} />
              </span>

              <h2>Search & filters</h2>
            </div>

            <p>
              Refine the decision workspace using
              keywords, status, or category.
            </p>
          </div>

          {hasActiveFilters && (
            <span className="decisions-filter-active">
              Filters applied
            </span>
          )}
        </div>

        <form
          className="decisions-filter-form"
          onSubmit={(event) => {
            event.preventDefault();
            handleApplyFilters();
          }}
        >
          <div className="decisions-field decisions-field-search">
            <label htmlFor="decision-search">
              Search
            </label>

            <div className="decisions-input-wrapper">
              <Search
                className="decisions-input-icon"
                size={17}
                aria-hidden="true"
              />

              <input
                id="decision-search"
                name="search"
                type="search"
                value={searchInput}
                onChange={(event) =>
                  setSearchInput(event.target.value)
                }
                placeholder="Search title or problem statement..."
                autoComplete="off"
              />
            </div>
          </div>

          <div className="decisions-field">
            <label htmlFor="decision-status">
              Status
            </label>

            <select
              id="decision-status"
              name="status"
              value={statusInput}
              onChange={(event) =>
                setStatusInput(event.target.value)
              }
            >
              <option value="">All statuses</option>

              {STATUS_OPTIONS.map((option) => (
                <option
                  key={option}
                  value={option}
                >
                  {option}
                </option>
              ))}
            </select>
          </div>

          <div className="decisions-field">
            <label htmlFor="decision-category">
              Category
            </label>

            <input
              id="decision-category"
              name="category"
              type="text"
              value={categoryInput}
              onChange={(event) =>
                setCategoryInput(event.target.value)
              }
              placeholder="e.g. Technology"
              autoComplete="off"
            />
          </div>

          <div className="decisions-filter-actions">
            <Button
              type="submit"
              isLoading={isLoading}
            >
              <Search size={15} />
              Apply filters
            </Button>

            <Button
              type="button"
              variant="secondary"
              onClick={handleClearFilters}
              disabled={!hasInputFilters && !hasActiveFilters}
            >
              Clear
            </Button>
          </div>
        </form>
      </section>

      {/* =====================================================
          RESULTS
         ===================================================== */}
      <section className="decisions-results">
        <div className="decisions-results-header">
          <div>
            <p className="decisions-results-eyebrow">
              Decision records
            </p>

            <h2>All decisions</h2>

            <p>
              {isLoading
                ? "Loading decision records..."
                : decisions.length === 1
                  ? "1 decision found"
                  : `${decisions.length} decisions found`}
            </p>
          </div>

          <button
            type="button"
            className="decisions-refresh-button"
            onClick={handleRetry}
            disabled={isLoading}
            aria-label="Refresh decisions"
            title="Refresh decisions"
          >
            <RefreshCw
              size={15}
              className={
                isLoading
                  ? "decisions-refresh-spinning"
                  : ""
              }
            />
          </button>
        </div>

        {errorMessage && (
          <div className="decisions-results-message">
            <Alert variant="error">
              {errorMessage}
            </Alert>

            <button
              type="button"
              className="decisions-inline-retry"
              onClick={handleRetry}
            >
              Try again
            </button>
          </div>
        )}

        {isLoading ? (
          <div
            className="decisions-loading"
            role="status"
            aria-live="polite"
          >
            <div className="decisions-loading-row">
              <span />
              <span />
              <span />
              <span />
            </div>

            <div className="decisions-loading-row">
              <span />
              <span />
              <span />
              <span />
            </div>

            <div className="decisions-loading-row">
              <span />
              <span />
              <span />
              <span />
            </div>

            <p>Loading decisions...</p>
          </div>
        ) : !errorMessage &&
          decisions.length === 0 ? (
          <div className="decisions-empty">
            <div className="decisions-empty-icon">
              <FileText size={22} />
            </div>

            <h3>No decisions found</h3>

            <p>
              {hasActiveFilters
                ? "No decision records match your current filters. Try adjusting your search criteria."
                : "There are no decision records available yet."}
            </p>

            {hasActiveFilters ? (
              <button
                type="button"
                className="decisions-empty-action"
                onClick={handleClearFilters}
              >
                Clear filters
              </button>
            ) : (
              <Link
                to="/decisions/new"
                className="decisions-empty-action"
              >
                Create first decision
              </Link>
            )}
          </div>
        ) : (
          <div className="decisions-table-wrapper">
            <table className="decisions-table">
              <thead>
                <tr>
                  <th scope="col">Decision</th>
                  <th scope="col">Category</th>
                  <th scope="col">Status</th>
                  <th scope="col">Created</th>
                  <th
                    scope="col"
                    className="decisions-table-action-heading"
                  >
                    <span className="sr-only">
                      Actions
                    </span>
                  </th>
                </tr>
              </thead>

              <tbody>
                {decisions.map((decision) => (
                  <tr key={decision.id}>
                    <td className="decision-title-cell">
                      <Link
                        to={`/decisions/${decision.id}`}
                        className="decision-title-link"
                      >
                        <span className="decision-file-icon">
                          <FileText size={16} />
                        </span>

                        <span className="decision-title-content">
                          <strong>
                            {decision.title}
                          </strong>

                          <small>
                            Decision #{decision.id}
                          </small>
                        </span>
                      </Link>
                    </td>

                    <td>
                      <span className="decision-category">
                        {decision.category || "Uncategorized"}
                      </span>
                    </td>

                    <td>
                      <span
                        className={getStatusClass(
                          decision.status,
                        )}
                      >
                        <StatusIcon
                          status={decision.status}
                        />

                        <span>
                          {decision.status}
                        </span>
                      </span>
                    </td>

                    <td>
                      <span className="decision-date">
                        {formatDate(
                          decision.created_at,
                        )}
                      </span>
                    </td>

                    <td className="decision-action-cell">
                      <Link
                        to={`/decisions/${decision.id}`}
                        className="decision-open-link"
                        aria-label={`Open ${decision.title}`}
                      >
                        <ChevronRight size={17} />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* =====================================================
          FOOTER INSIGHT
         ===================================================== */}
      {!isLoading &&
        !errorMessage &&
        decisions.length > 0 && (
          <div className="decisions-footer">
            <span>
              Showing {decisions.length} decision
              {decisions.length === 1 ? "" : "s"}
            </span>

            <span className="decisions-footer-dot" />

            <span>
              {draftCount} draft
              {draftCount === 1 ? "" : "s"}
            </span>
          </div>
        )}
    </div>
  );
}