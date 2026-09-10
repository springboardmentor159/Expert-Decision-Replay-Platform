import { useCallback, useEffect, useMemo, useState } from "react";
import {
  ArrowLeft,
  ArrowUpDown,
  BookOpen,
  ChevronLeft,
  ChevronRight,
  Clock3,
  FileText,
  RefreshCw,
  Search,
  SlidersHorizontal,
  Tag,
} from "lucide-react";
import { useNavigate } from "react-router-dom";

import Alert from "../components/Alert";
import Button from "../components/Button";
import StatusBadge from "../components/StatusBadge";
import {
  searchRepository,
  type RepositoryDecision,
} from "../services/repositoryService";
import "./RepositoryPage.css";

const PAGE_SIZE = 10;

const STATUSES = [
  "All statuses",
  "Draft",
  "Under Review",
  "Approved",
  "Rejected",
  "Archived",
];

const SORT_OPTIONS = [
  {
    value: "created_at",
    label: "Newest first",
    order: "desc" as const,
  },
  {
    value: "created_at",
    label: "Oldest first",
    order: "asc" as const,
  },
  {
    value: "updated_at",
    label: "Recently updated",
    order: "desc" as const,
  },
  {
    value: "title",
    label: "Title A–Z",
    order: "asc" as const,
  },
];

function getStatusVariant(
  status: string,
): "success" | "danger" | "warning" | "neutral" {
  const normalized = status.toLowerCase();

  if (normalized === "approved") {
    return "success";
  }

  if (normalized === "rejected") {
    return "danger";
  }

  if (
    normalized === "draft" ||
    normalized === "pending" ||
    normalized === "under review"
  ) {
    return "warning";
  }

  return "neutral";
}

function formatDate(value: string): string {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "—";
  }

  return date.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function getErrorMessage(
  error: unknown,
  action: string,
): string {
  const status = (
    error as {
      response?: {
        status?: number;
      };
    }
  )?.response?.status;

  if (status === 401) {
    return "Your session has expired. Please sign in again.";
  }

  if (status === 403) {
    return "You do not have permission to access the knowledge repository.";
  }

  if (status === 404) {
    return "The requested repository resource was not found.";
  }

  if (status === 422) {
    return "One or more search or filter values are invalid.";
  }

  if (status && status >= 500) {
    return "The server is temporarily unavailable. Please try again.";
  }

  return `Unable to ${action}. Please try again.`;
}

export default function RepositoryPage() {
  const navigate = useNavigate();

  const [decisions, setDecisions] = useState<
    RepositoryDecision[]
  >([]);

  const [searchInput, setSearchInput] = useState("");
  const [searchQuery, setSearchQuery] = useState("");

  const [category, setCategory] = useState("");
  const [status, setStatus] = useState("");
  const [tag, setTag] = useState("");

  const [sortIndex, setSortIndex] = useState(0);
  const [page, setPage] = useState(1);

  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  const selectedSort = SORT_OPTIONS[sortIndex];

  const totalPages = Math.max(
    1,
    Math.ceil(total / PAGE_SIZE),
  );

  const loadRepository = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage("");

    try {
      const response = await searchRepository({
        q: searchQuery || undefined,
        category: category || undefined,
        status: status || undefined,
        tag: tag || undefined,
        page,
        page_size: PAGE_SIZE,
        sort: selectedSort.value as
          | "created_at"
          | "updated_at"
          | "title",
        order: selectedSort.order,
      });

      setDecisions(response.items);
      setTotal(response.total);
    } catch (error: unknown) {
      setDecisions([]);
      setTotal(0);
      setErrorMessage(
        getErrorMessage(error, "load the knowledge repository"),
      );
    } finally {
      setIsLoading(false);
    }
  }, [
    searchQuery,
    category,
    status,
    tag,
    page,
    selectedSort.value,
    selectedSort.order,
  ]);

  useEffect(() => {
    void loadRepository();
  }, [loadRepository]);

  const categories = useMemo(() => {
    const values = decisions
      .map((decision) => decision.category)
      .filter(Boolean);

    return Array.from(new Set(values)).sort();
  }, [decisions]);

  function handleSearchSubmit(
    event: React.FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setPage(1);
    setSearchQuery(searchInput.trim());
  }

  function handleCategoryChange(
    value: string,
  ) {
    setCategory(value);
    setPage(1);
  }

  function handleStatusChange(
    value: string,
  ) {
    setStatus(value === "All statuses" ? "" : value);
    setPage(1);
  }

  function handleTagSearch(
    event: React.ChangeEvent<HTMLInputElement>,
  ) {
    setTag(event.target.value);
    setPage(1);
  }

  function clearFilters() {
    setSearchInput("");
    setSearchQuery("");
    setCategory("");
    setStatus("");
    setTag("");
    setSortIndex(0);
    setPage(1);
  }

  function handleSortChange(
    event: React.ChangeEvent<HTMLSelectElement>,
  ) {
    setSortIndex(Number(event.target.value));
    setPage(1);
  }

  const firstResult =
    total === 0 ? 0 : (page - 1) * PAGE_SIZE + 1;

  const lastResult = Math.min(
    page * PAGE_SIZE,
    total,
  );

  return (
    <div className="repository-page">
      <header className="repository-header">
        <div>
          <button
            type="button"
            className="repository-back-button"
            onClick={() => navigate("/dashboard")}
          >
            <ArrowLeft size={15} aria-hidden="true" />
            Back to Dashboard
          </button>

          <div className="repository-kicker">
            ORGANIZATIONAL KNOWLEDGE
          </div>

          <div className="repository-title-row">
            <div className="repository-title-icon">
              <BookOpen
                size={23}
                aria-hidden="true"
              />
            </div>

            <div>
              <h1>Knowledge Repository</h1>
              <p>
                Discover previous decisions using keywords,
                categories, status, and tags.
              </p>
            </div>
          </div>
        </div>

        <div className="repository-count-chip">
          {total} {total === 1 ? "decision" : "decisions"}
        </div>
      </header>

      {errorMessage && (
        <div className="repository-alert">
          <Alert variant="error">
            {errorMessage}
          </Alert>
        </div>
      )}

      <section className="repository-search-card">
        <div className="repository-search-heading">
          <div className="repository-search-heading-icon">
            <Search size={17} aria-hidden="true" />
          </div>

          <div>
            <h2>Search decisions</h2>
            <p>
              Search titles, problem statements, categories,
              and tags.
            </p>
          </div>
        </div>

        <form
          className="repository-search-form"
          onSubmit={handleSearchSubmit}
        >
          <div className="repository-search-input">
            <Search size={17} aria-hidden="true" />

            <input
              type="search"
              value={searchInput}
              onChange={(event) =>
                setSearchInput(event.target.value)
              }
              placeholder="Search organizational decisions..."
              aria-label="Search decisions"
            />
          </div>

          <Button type="submit">
            <Search size={16} aria-hidden="true" />
            Search
          </Button>
        </form>

        <div className="repository-filter-divider" />

        <div className="repository-filter-heading">
          <SlidersHorizontal
            size={15}
            aria-hidden="true"
          />
          <span>Refine results</span>
        </div>

        <div className="repository-filters">
          <label>
            <span>Category</span>

            <select
              value={category}
              onChange={(event) =>
                handleCategoryChange(event.target.value)
              }
            >
              <option value="">All categories</option>

              {categories.map((item) => (
                <option value={item} key={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>

          <label>
            <span>Status</span>

            <select
              value={status || "All statuses"}
              onChange={(event) =>
                handleStatusChange(event.target.value)
              }
            >
              {STATUSES.map((item) => (
                <option value={item} key={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>

          <label>
            <span>Tag</span>

            <div className="repository-tag-input">
              <Tag size={15} aria-hidden="true" />

              <input
                type="text"
                value={tag}
                onChange={handleTagSearch}
                placeholder="e.g. PostgreSQL"
                aria-label="Filter by tag"
              />
            </div>
          </label>

          <label>
            <span>Sort by</span>

            <select
              value={sortIndex}
              onChange={handleSortChange}
            >
              {SORT_OPTIONS.map((option, index) => (
                <option value={index} key={`${option.value}-${option.order}`}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>

          <button
            type="button"
            className="repository-clear-button"
            onClick={clearFilters}
          >
            Clear filters
          </button>
        </div>
      </section>

      <section className="repository-results-card">
        <div className="repository-results-header">
          <div>
            <h2>Decision records</h2>

            <p>
              {total === 0
                ? "No matching decisions"
                : `Showing ${firstResult}–${lastResult} of ${total}`}
            </p>
          </div>

          <button
            type="button"
            className="repository-refresh-button"
            onClick={() => void loadRepository()}
            disabled={isLoading}
            aria-label="Refresh repository"
          >
            <RefreshCw
              size={15}
              className={
                isLoading
                  ? "repository-refresh-spinning"
                  : undefined
              }
              aria-hidden="true"
            />
            Refresh
          </button>
        </div>

        {isLoading ? (
          <div
            className="repository-loading"
            role="status"
            aria-live="polite"
          >
            <div className="repository-spinner" />
            <span>
              Searching organizational knowledge...
            </span>
          </div>
        ) : decisions.length === 0 ? (
          <div className="repository-empty">
            <div className="repository-empty-icon">
              <BookOpen size={24} aria-hidden="true" />
            </div>

            <h3>No decisions found</h3>

            <p>
              Try changing your search term or removing one
              or more filters.
            </p>

            <Button
              variant="secondary"
              onClick={clearFilters}
            >
              Clear filters
            </Button>
          </div>
        ) : (
          <div className="repository-results">
            {decisions.map((decision) => (
              <article
                className="repository-result"
                key={decision.id}
                onClick={() =>
                  navigate(`/decisions/${decision.id}`)
                }
                onKeyDown={(event) => {
                  if (
                    event.key === "Enter" ||
                    event.key === " "
                  ) {
                    event.preventDefault();
                    navigate(
                      `/decisions/${decision.id}`,
                    );
                  }
                }}
                role="button"
                tabIndex={0}
              >
                <div className="repository-result-icon">
                  <FileText
                    size={19}
                    aria-hidden="true"
                  />
                </div>

                <div className="repository-result-content">
                  <div className="repository-result-top">
                    <div>
                      <div className="repository-result-id">
                        DECISION #{decision.id}
                      </div>

                      <h3>{decision.title}</h3>
                    </div>

                    <StatusBadge
                      variant={getStatusVariant(
                        decision.status,
                      )}
                    >
                      {decision.status}
                    </StatusBadge>
                  </div>

                  <div className="repository-result-meta">
                    <span>
                      <BookOpen
                        size={13}
                        aria-hidden="true"
                      />
                      {decision.category || "Uncategorized"}
                    </span>

                    <span>
                      <Clock3
                        size={13}
                        aria-hidden="true"
                      />
                      Created {formatDate(decision.created_at)}
                    </span>
                  </div>

                  {decision.tags && (
                    <div className="repository-result-tags">
                      {decision.tags
                        .split(",")
                        .map((item) => item.trim())
                        .filter(Boolean)
                        .map((item) => (
                          <span
                            className="repository-tag"
                            key={item}
                          >
                            <Tag
                              size={11}
                              aria-hidden="true"
                            />
                            {item}
                          </span>
                        ))}
                    </div>
                  )}
                </div>

                <div className="repository-result-arrow">
                  <ChevronRight
                    size={18}
                    aria-hidden="true"
                  />
                </div>
              </article>
            ))}
          </div>
        )}

        {!isLoading && total > 0 && (
          <div className="repository-pagination">
            <span>
              Page {page} of {totalPages}
            </span>

            <div className="repository-pagination-actions">
              <button
                type="button"
                onClick={() =>
                  setPage((current) =>
                    Math.max(1, current - 1),
                  )
                }
                disabled={page <= 1}
                aria-label="Previous page"
              >
                <ChevronLeft
                  size={16}
                  aria-hidden="true"
                />
                Previous
              </button>

              <button
                type="button"
                onClick={() =>
                  setPage((current) =>
                    Math.min(
                      totalPages,
                      current + 1,
                    ),
                  )
                }
                disabled={page >= totalPages}
                aria-label="Next page"
              >
                Next
                <ChevronRight
                  size={16}
                  aria-hidden="true"
                />
              </button>
            </div>
          </div>
        )}
      </section>

      <div className="repository-footer-note">
        <ArrowUpDown size={14} aria-hidden="true" />
        <span>
          Search and filtering are performed by the backend
          repository API.
        </span>
      </div>
    </div>
  );
}