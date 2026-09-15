import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

function Decisions() {
  const [decisions, setDecisions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");

  const navigate = useNavigate();

  useEffect(() => {
    fetchDecisions();
  }, []);

  const fetchDecisions = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await api.get("/decisions");
      setDecisions(response.data);
    } catch (err) {
      if (err.response?.status === 401) {
        setError("Your session has expired. Please login again.");
      } else if (err.response?.status === 403) {
        setError("You don't have permission to view decisions.");
      } else {
        setError("Unable to load decisions.");
      }
    } finally {
      setLoading(false);
    }
  };

  const filteredDecisions = useMemo(() => {
    return decisions.filter((decision) => {
      const text = `${decision.title || ""} ${
        decision.category || ""
      }`.toLowerCase();

      const matchesSearch = text.includes(search.toLowerCase());

      const matchesStatus =
        statusFilter === "All" ||
        String(decision.status || "").toLowerCase() ===
          statusFilter.toLowerCase();

      return matchesSearch && matchesStatus;
    });
  }, [decisions, search, statusFilter]);

  const getStatusClass = (status) => {
    return String(status || "Unknown")
      .toLowerCase()
      .replace(/\s+/g, "-");
  };

  if (loading) {
    return (
      <div className="page-loading">
        <div className="loading-spinner"></div>
        <p>Loading decisions...</p>
      </div>
    );
  }

  return (
    <div className="decisions-page">

      {/* HEADER */}

      <div className="decisions-page-header">

        <div>
          <p className="page-label">DECISION MANAGEMENT</p>

          <h1>Decisions</h1>

          <p>
            Create, manage and review organizational decisions.
          </p>
        </div>

        <button
          className="primary-button"
          onClick={() => navigate("/decisions/create")}
        >
          <span>+</span>
          Create Decision
        </button>

      </div>


      {/* ERROR */}

      {error && (
        <div className="error-card">
          {error}
        </div>
      )}


      {/* TOOLBAR */}

      <div className="decisions-toolbar">

        <div className="decision-search">

          <span>⌕</span>

          <input
            type="text"
            placeholder="Search by title or category..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />

        </div>


        <div className="filter-group">

          <label>Status</label>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="All">All Statuses</option>
            <option value="Draft">Draft</option>
            <option value="Under Review">Under Review</option>
            <option value="Approved">Approved</option>
            <option value="Rejected">Rejected</option>
          </select>

        </div>

      </div>


      {/* SUMMARY */}

      <div className="decision-summary">

        <div>
          <strong>{decisions.length}</strong>
          <span>Total Decisions</span>
        </div>

        <div>
          <strong>{filteredDecisions.length}</strong>
          <span>Showing</span>
        </div>

      </div>


      {/* DECISION TABLE */}

      <div className="dashboard-card decisions-list-card">

        <div className="card-header">

          <div>
            <h2>All Decisions</h2>
            <p>
              {filteredDecisions.length} decision
              {filteredDecisions.length !== 1 ? "s" : ""} found
            </p>
          </div>

        </div>


        {filteredDecisions.length === 0 ? (

          <div className="empty-state">

            <div className="empty-icon">
              ▣
            </div>

            <h3>No decisions found</h3>

            <p>
              Try changing your search or create a new decision.
            </p>

            <button
              className="secondary-button"
              onClick={() => navigate("/decisions/create")}
            >
              Create Decision
            </button>

          </div>

        ) : (

          <div className="decision-table-wrapper">

            <table className="modern-table decisions-table">

              <thead>
                <tr>
                  <th>Decision</th>
                  <th>Category</th>
                  <th>Status</th>
                  <th>ID</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>

                {filteredDecisions.map((decision) => (

                  <tr key={decision.id}>

                    <td>

                      <div className="decision-name">

                        <div className="decision-avatar">
                          {decision.title
                            ? decision.title.charAt(0).toUpperCase()
                            : "D"}
                        </div>

                        <div>

                          <strong>
                            {decision.title || "Untitled Decision"}
                          </strong>

                          <span>
                            Decision #{decision.id}
                          </span>

                        </div>

                      </div>

                    </td>

                    <td>
                      {decision.category || "-"}
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
                      #{decision.id}
                    </td>

                    <td>

                      <button
                        className="view-button"
                        onClick={() =>
                          navigate(`/decisions/${decision.id}`)
                        }
                      >
                        View →
                      </button>

                    </td>

                  </tr>

                ))}

              </tbody>

            </table>

          </div>

        )}

      </div>

    </div>
  );
}

export default Decisions;