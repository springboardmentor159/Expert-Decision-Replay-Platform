import { useEffect, useState } from "react";
import {
  Search,
  Plus,
  FileText,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { useNavigate } from "react-router-dom";

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
    } catch (err: any) {
      const responseStatus = err?.response?.status;

      if (responseStatus === 401) {
        setError("Your session has expired. Please sign in again.");
      } else if (responseStatus === 403) {
        setError("You do not have permission to view decisions.");
      } else if (responseStatus === 404) {
        setError("Decision service was not found.");
      } else if (responseStatus >= 500) {
        setError("Server error. Please try again later.");
      } else if (err?.request) {
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
    loadDecisions();
  }, [page, status]);

  const handleSearch = () => {
    setPage(1);
    loadDecisions();
  };

  const handleReset = () => {
    setSearch("");
    setStatus("All");
    setCategory("");
    setPage(1);
  };

  return (
    <main className="decision-page">
      <header className="page-header">
        <div>
          <p className="page-eyebrow">
            Expert Decision Replay Platform
          </p>

          <h1>Decisions</h1>

          <p>
            View, search and manage organizational decisions.
          </p>
        </div>

        <button
          className="primary-button"
          onClick={() => navigate("/decisions/create")}
        >
          <Plus size={18} />
          Create Decision
        </button>
      </header>

      <section className="decision-toolbar">
        <div className="search-box">
          <Search size={18} />

          <input
            type="text"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                handleSearch();
              }
            }}
            placeholder="Search decisions..."
          />

          <button onClick={handleSearch}>
            Search
          </button>
        </div>

        <select
          value={status}
          onChange={(event) => {
            setStatus(event.target.value);
            setPage(1);
          }}
        >
          {statuses.map((item) => (
            <option key={item} value={item}>
              {item === "All" ? "All Statuses" : item}
            </option>
          ))}
        </select>

        <input
          type="text"
          value={category}
          onChange={(event) => setCategory(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter") {
              handleSearch();
            }
          }}
          placeholder="Category"
        />

        <button
          className="secondary-button"
          onClick={handleReset}
          title="Reset filters"
        >
          <RefreshCw size={17} />
          Reset
        </button>
      </section>

      {error && (
        <section className="decision-error" role="alert">
          <strong>Unable to load decisions</strong>
          <p>{error}</p>

          <button onClick={loadDecisions}>
            Try Again
          </button>
        </section>
      )}

      {isLoading ? (
        <section className="decision-loading">
          <div className="loading-spinner" />
          <p>Loading decisions...</p>
        </section>
      ) : !error && decisions.length === 0 ? (
        <section className="decision-empty">
          <FileText size={42} />

          <h2>No decisions found</h2>

          <p>
            There are no decisions matching your current filters.
          </p>

          <button
            className="primary-button"
            onClick={() => navigate("/decisions/create")}
          >
            <Plus size={18} />
            Create Your First Decision
          </button>
        </section>
      ) : (
        <section className="decision-table-section">
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
                  <th>Action</th>
                </tr>
              </thead>

              <tbody>
                {decisions.map((decision) => (
                  <tr key={decision.id}>
                    <td>
                      <div className="decision-title-cell">
                        <div className="decision-icon">
                          <FileText size={17} />
                        </div>

                        <div>
                          <strong>{decision.title}</strong>

                          <span>
                            Decision #{decision.id}
                          </span>
                        </div>
                      </div>
                    </td>

                    <td>{decision.category}</td>

                    <td>
                      User #{decision.created_by}
                    </td>

                    <td>
                      <span
                        className={`status-badge ${getStatusClass(
                          decision.status,
                        )}`}
                      >
                        {decision.status}
                      </span>
                    </td>

                    <td>
                      {formatDate(decision.created_at)}
                    </td>

                    <td>
                      {formatDate(decision.updated_at)}
                    </td>

                    <td>
                      <button
                        className="view-button"
                        onClick={() =>
                          navigate(`/decisions/${decision.id}`)
                        }
                      >
                        View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="pagination">
            <button
              disabled={page === 1}
              onClick={() =>
                setPage((current) => Math.max(1, current - 1))
              }
            >
              <ChevronLeft size={17} />
              Previous
            </button>

            <span>Page {page}</span>

            <button
              disabled={decisions.length < pageSize}
              onClick={() => setPage((current) => current + 1)}
            >
              Next
              <ChevronRight size={17} />
            </button>
          </div>
        </section>
      )}
    </main>
  );
}