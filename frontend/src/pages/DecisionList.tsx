import { useEffect, useState } from "react";
import {
  Search,
  Plus,
  FileText,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
  CalendarDays,
  User,
  Filter,
  ArrowUpRight,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

import api from "../services/api";

interface Decision {
  id: number;
  title: string;
  problem_statement: string;
  category: string;
  status: string;
  created_by: number;
  created_at: string;
  updated_at: string;
}

const statuses = [
  "All",
  "Draft",
  "Under Review",
  "Approved",
  "Rejected",
  "Archived",
];

function formatDate(dateString: string) {
  return new Date(dateString).toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function getStatusClass(status: string) {
  return status.toLowerCase().replace(/\s+/g, "-");
}

export default function DecisionList() {
  const navigate = useNavigate();

  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("All");
  const [category, setCategory] = useState("");

  const [page, setPage] = useState(1);
  const pageSize = 10;

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const loadDecisions = async () => {
    try {
      setIsLoading(true);
      setError("");

      const params: Record<string, string | number> = {
        page,
        page_size: pageSize,
        sort: "created_at",
        order: "desc",
      };

      if (search.trim()) {
        params.q = search.trim();
      }

      if (status !== "All") {
        params.status = status;
      }

      if (category.trim()) {
        params.category = category.trim();
      }

      const response = await api.get<Decision[]>("/decisions", {
        params,
      });

      setDecisions(response.data);
    } catch (err: unknown) {
      const responseStatus = axios.isAxiosError(err)
        ? err.response?.status
        : undefined;

      if (responseStatus === 401) {
        setError("Your session has expired. Please sign in again.");
      } else if (responseStatus === 403) {
        setError("You do not have permission to view decisions.");
      } else if (responseStatus === 404) {
        setError("Decision service was not found.");
      } else if (
        responseStatus !== undefined &&
        responseStatus >= 500
      ) {
        setError("Server error. Please try again later.");
      } else if (
        axios.isAxiosError(err) &&
        err.request
      ) {
        setError(
          "Unable to connect to the server. Make sure FastAPI is running.",
        );
      } else {
        setError("Unable to load decisions.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void loadDecisions();
    }, 0);

    return () => {
      window.clearTimeout(timer);
    };
  }, [page, status]);

  const handleSearch = () => {
    setPage(1);

    window.setTimeout(() => {
      void loadDecisions();
    }, 0);
  };

  const handleReset = () => {
    setSearch("");
    setStatus("All");
    setCategory("");
    setPage(1);
  };

  return (
    <main className="decision-page">
      {/* PAGE HEADER */}
      <header className="decision-page-header">
        <div className="decision-heading-area">
          <div className="decision-heading-icon">
            <FileText size={24} />
          </div>

          <div>
            <p className="decision-eyebrow">
              DECISION INTELLIGENCE
            </p>

            <h1>Decisions</h1>

            <p className="decision-subtitle">
              Review, search and manage organizational decisions
              throughout their complete lifecycle.
            </p>
          </div>
        </div>

        <button
          className="decision-create-button"
          onClick={() => navigate("/decisions/create")}
        >
          <Plus size={18} />
          Create Decision
          <ArrowUpRight size={16} />
        </button>
      </header>

      {/* FILTER PANEL */}
      <section className="decision-filter-panel">
        <div className="decision-filter-header">
          <div className="decision-filter-title">
            <Filter size={17} />

            <span>Search & Filter</span>
          </div>

          <button
            className="decision-reset-button"
            onClick={handleReset}
            title="Reset filters"
          >
            <RefreshCw size={15} />
            Reset
          </button>
        </div>

        <div className="decision-filter-grid">
          {/* SEARCH */}
          <div className="decision-search-field">
            <Search size={18} />

            <input
              type="text"
              value={search}
              onChange={(event) =>
                setSearch(event.target.value)
              }
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  handleSearch();
                }
              }}
              placeholder="Search by decision title..."
            />

            <button onClick={handleSearch}>
              Search
            </button>
          </div>

          {/* STATUS */}
          <div className="decision-input-field">
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
              {statuses.map((item) => (
                <option key={item} value={item}>
                  {item === "All"
                    ? "All Statuses"
                    : item}
                </option>
              ))}
            </select>
          </div>

          {/* CATEGORY */}
          <div className="decision-input-field">
            <label htmlFor="decision-category">
              Category
            </label>

            <input
              id="decision-category"
              type="text"
              value={category}
              onChange={(event) =>
                setCategory(event.target.value)
              }
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  handleSearch();
                }
              }}
              placeholder="e.g. Technology"
            />
          </div>
        </div>
      </section>

      {/* ERROR */}
      {error && (
        <section className="decision-error-card" role="alert">
          <div className="decision-error-icon">
            !
          </div>

          <div>
            <strong>Unable to load decisions</strong>
            <p>{error}</p>
          </div>

          <button onClick={loadDecisions}>
            Try Again
          </button>
        </section>
      )}

      {/* LOADING */}
      {isLoading ? (
        <section className="decision-state-card">
          <div className="loading-spinner" />

          <h3>Loading decisions</h3>

          <p>
            Retrieving the latest decision records...
          </p>
        </section>
      ) : !error && decisions.length === 0 ? (
        /* EMPTY STATE */
        <section className="decision-state-card decision-empty-state">
          <div className="decision-empty-icon">
            <FileText size={32} />
          </div>

          <h2>No decisions found</h2>

          <p>
            There are no decisions matching your current
            search and filter criteria.
          </p>

          <button
            className="decision-create-button"
            onClick={() => navigate("/decisions/create")}
          >
            <Plus size={18} />
            Create Your First Decision
          </button>
        </section>
      ) : (
        /* DECISION TABLE */
        <section className="decision-results-card">
          <div className="decision-results-header">
            <div>
              <p className="results-label">
                DECISION RECORDS
              </p>

              <h2>Organizational Decisions</h2>

              <p>
                Browse the latest decisions and open any
                record to replay its complete lifecycle.
              </p>
            </div>

            <div className="decision-result-count">
              <span>Page</span>
              <strong>{page}</strong>
            </div>
          </div>

          <div className="decision-table-wrapper">
            <table className="decision-table">
              <thead>
                <tr>
                  <th>Decision</th>
                  <th>Category</th>
                  <th>Created By</th>
                  <th>Status</th>
                  <th>Created</th>
                  <th>Updated</th>
                  <th></th>
                </tr>
              </thead>

              <tbody>
                {decisions.map((decision) => (
                  <tr key={decision.id}>
                    {/* DECISION */}
                    <td>
                      <div className="decision-title-cell">
                        <div className="decision-record-icon">
                          <FileText size={17} />
                        </div>

                        <div className="decision-title-content">
                          <strong>
                            {decision.title}
                          </strong>

                          <span>
                            Decision #{decision.id}
                          </span>
                        </div>
                      </div>
                    </td>

                    {/* CATEGORY */}
                    <td>
                      <span className="decision-category-badge">
                        {decision.category}
                      </span>
                    </td>

                    {/* CREATOR */}
                    <td>
                      <div className="decision-user-cell">
                        <div className="decision-user-icon">
                          <User size={14} />
                        </div>

                        <span>
                          User #{decision.created_by}
                        </span>
                      </div>
                    </td>

                    {/* STATUS */}
                    <td>
                      <span
                        className={`status-badge ${getStatusClass(
                          decision.status,
                        )}`}
                      >
                        <span className="status-dot" />
                        {decision.status}
                      </span>
                    </td>

                    {/* CREATED */}
                    <td>
                      <div className="decision-date-cell">
                        <CalendarDays size={14} />
                        {formatDate(
                          decision.created_at,
                        )}
                      </div>
                    </td>

                    {/* UPDATED */}
                    <td>
                      <div className="decision-date-cell">
                        <CalendarDays size={14} />
                        {formatDate(
                          decision.updated_at,
                        )}
                      </div>
                    </td>

                    {/* ACTION */}
                    <td>
                      <button
                        className="decision-view-button"
                        onClick={() =>
                          navigate(
                            `/decisions/${decision.id}`,
                          )
                        }
                      >
                        View
                        <ArrowUpRight size={15} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* PAGINATION */}
          <div className="decision-pagination">
            <div className="pagination-info">
              Showing{" "}
              <strong>{decisions.length}</strong>{" "}
              decision
              {decisions.length !== 1 ? "s" : ""}
            </div>

            <div className="pagination-controls">
              <button
                disabled={page === 1}
                onClick={() =>
                  setPage((current) =>
                    Math.max(1, current - 1),
                  )
                }
              >
                <ChevronLeft size={17} />
                Previous
              </button>

              <div className="pagination-page">
                Page <strong>{page}</strong>
              </div>

              <button
                disabled={decisions.length < pageSize}
                onClick={() =>
                  setPage((current) => current + 1)
                }
              >
                Next
                <ChevronRight size={17} />
              </button>
            </div>
          </div>
        </section>
      )}
    </main>
  );
}