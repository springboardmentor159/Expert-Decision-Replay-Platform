import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

function KnowledgeRepository() {
  const navigate = useNavigate();

  const [decisions, setDecisions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [status, setStatus] = useState("");
  const [tag, setTag] = useState("");

  const [categories, setCategories] = useState([]);
  const [tags, setTags] = useState([]);

  const fetchDecisions = async () => {
    try {
      setLoading(true);
      setError("");

      const params = {};

      if (search.trim()) {
        params.q = search.trim();
      }

      if (category) {
        params.category = category;
      }

      if (status) {
        params.status = status;
      }

      if (tag) {
        params.tag = tag;
      }

      const response = await api.get("/decisions", {
        params,
      });

      const data = Array.isArray(response.data)
        ? response.data
        : response.data.data || [];

      setDecisions(data);

      const uniqueCategories = [
        ...new Set(
          data
            .map((decision) => decision.category)
            .filter(Boolean)
        ),
      ];

      setCategories(uniqueCategories);

      const uniqueTags = [
        ...new Set(
          data
            .flatMap((decision) => decision.tags || [])
            .filter(Boolean)
        ),
      ];

      setTags(uniqueTags);
    } catch (error) {
      console.error(
        "Failed to load knowledge repository:",
        error
      );

      setError(
        error.response?.data?.detail ||
          "Unable to load knowledge repository."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDecisions();
  }, []);

  const handleSearch = (event) => {
    event.preventDefault();
    fetchDecisions();
  };

  const handleClearFilters = () => {
    setSearch("");
    setCategory("");
    setStatus("");
    setTag("");

    setTimeout(() => {
      fetchDecisions();
    }, 0);
  };

  const getStatusClass = (statusValue) => {
    switch (statusValue) {
      case "Draft":
        return "knowledge-status knowledge-status-draft";

      case "Under Review":
        return "knowledge-status knowledge-status-review";

      case "Approved":
        return "knowledge-status knowledge-status-approved";

      case "Rejected":
        return "knowledge-status knowledge-status-rejected";

      case "Archived":
        return "knowledge-status knowledge-status-archived";

      default:
        return "knowledge-status";
    }
  };

  return (
    <div className="page-container knowledge-page">

      {/* Header */}
      <div className="knowledge-header">

        <div>
          <div className="page-eyebrow">
            ORGANIZATIONAL KNOWLEDGE
          </div>

          <h1>Knowledge Repository</h1>

          <p>
            Search, explore, and revisit organizational
            decisions and their history.
          </p>
        </div>

        <div className="knowledge-header-count">
          <strong>{decisions.length}</strong>
          <span>Decisions</span>
        </div>

      </div>

      {/* Search Panel */}
      <div className="knowledge-search-card">

        <div className="knowledge-search-heading">

          <div className="knowledge-search-icon">
            ⌕
          </div>

          <div>
            <h2>Find a Decision</h2>

            <p>
              Search by title, problem, rationale, category,
              status, or tag.
            </p>
          </div>

        </div>

        <form onSubmit={handleSearch}>

          <div className="knowledge-search-row">

            <div className="knowledge-search-input">

              <span>⌕</span>

              <input
                type="text"
                placeholder="Search decisions..."
                value={search}
                onChange={(event) =>
                  setSearch(event.target.value)
                }
              />

            </div>

            <button
              type="submit"
              className="knowledge-search-button"
            >
              Search
            </button>

          </div>

          <div className="knowledge-filters">

            <div className="knowledge-filter">

              <label>Category</label>

              <select
                value={category}
                onChange={(event) =>
                  setCategory(event.target.value)
                }
              >
                <option value="">
                  All Categories
                </option>

                {categories.map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </select>

            </div>

            <div className="knowledge-filter">

              <label>Status</label>

              <select
                value={status}
                onChange={(event) =>
                  setStatus(event.target.value)
                }
              >
                <option value="">
                  All Statuses
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

            <div className="knowledge-filter">

              <label>Tag</label>

              <select
                value={tag}
                onChange={(event) =>
                  setTag(event.target.value)
                }
              >
                <option value="">
                  All Tags
                </option>

                {tags.map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </select>

            </div>

            <button
              type="button"
              className="knowledge-clear-button"
              onClick={handleClearFilters}
            >
              Clear Filters
            </button>

          </div>

        </form>

      </div>

      {/* Error */}
      {error && (
        <div className="form-alert form-alert-error">
          <span className="alert-icon">!</span>

          <div>
            <strong>Unable to load repository</strong>
            <p>{error}</p>
          </div>
        </div>
      )}

      {/* Decision Archive */}
      <div className="knowledge-section">

        <div className="knowledge-section-header">

          <div>
            <div className="knowledge-section-label">
              ARCHIVE
            </div>

            <h2>Decision Archive</h2>

            <p>
              Browse previously recorded organizational
              decisions.
            </p>
          </div>

          <div className="knowledge-result-count">
            {decisions.length} result
            {decisions.length !== 1 ? "s" : ""}
          </div>

        </div>

        {loading ? (
          <div className="knowledge-empty-state">
            <div className="knowledge-loader"></div>
            <h3>Loading decisions...</h3>
            <p>Please wait while the repository is loaded.</p>
          </div>
        ) : decisions.length === 0 ? (
          <div className="knowledge-empty-state">

            <div className="knowledge-empty-icon">
              ◫
            </div>

            <h3>No decisions found</h3>

            <p>
              Try changing your search or filters to find
              other decisions.
            </p>

            <button
              type="button"
              className="knowledge-clear-button"
              onClick={handleClearFilters}
            >
              Clear Filters
            </button>

          </div>
        ) : (
          <div className="knowledge-table-wrapper">

            <table className="knowledge-table">

              <thead>
                <tr>
                  <th>Decision</th>
                  <th>Category</th>
                  <th>Status</th>
                  <th>Created By</th>
                  <th>Created</th>
                  <th></th>
                </tr>
              </thead>

              <tbody>

                {decisions.map((decision) => (

                  <tr key={decision.id}>

                    <td>

                      <div className="knowledge-decision-cell">

                        <div className="knowledge-decision-icon">
                          D
                        </div>

                        <div>
                          <strong>
                            {decision.title}
                          </strong>

                          <span>
                            Decision #{decision.id}
                          </span>
                        </div>

                      </div>

                    </td>

                    <td>
                      <span className="knowledge-category">
                        {decision.category || "Uncategorized"}
                      </span>
                    </td>

                    <td>
                      <span
                        className={getStatusClass(
                          decision.status
                        )}
                      >
                        {decision.status || "Unknown"}
                      </span>
                    </td>

                    <td>
                      {decision.created_by || "N/A"}
                    </td>

                    <td>
                      {decision.created_at
                        ? new Date(
                            decision.created_at
                          ).toLocaleDateString()
                        : "N/A"}
                    </td>

                    <td>

                      <button
                        type="button"
                        className="knowledge-view-button"
                        onClick={() =>
                          navigate(
                            `/decisions/${decision.id}`
                          )
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

      {/* Timeline */}
      {decisions.length > 0 && (
        <div className="knowledge-section">

          <div className="knowledge-section-header">

            <div>
              <div className="knowledge-section-label">
                HISTORY
              </div>

              <h2>Decision Timeline</h2>

              <p>
                A chronological view of recorded decisions.
              </p>
            </div>

          </div>

          <div className="knowledge-timeline">

            {decisions.map((decision, index) => (

              <div
                key={decision.id}
                className="knowledge-timeline-item"
              >

                <div className="knowledge-timeline-line">

                  <div className="knowledge-timeline-dot">
                    {index + 1}
                  </div>

                </div>

                <div className="knowledge-timeline-content">

                  <div className="knowledge-timeline-top">

                    <div>
                      <h3>
                        {decision.title}
                      </h3>

                      <div className="knowledge-timeline-meta">

                        <span>
                          {decision.category ||
                            "Uncategorized"}
                        </span>

                        <span>•</span>

                        <span>
                          {decision.created_at
                            ? new Date(
                                decision.created_at
                              ).toLocaleString()
                            : "Date unavailable"}
                        </span>

                      </div>
                    </div>

                    <span
                      className={getStatusClass(
                        decision.status
                      )}
                    >
                      {decision.status || "Unknown"}
                    </span>

                  </div>

                  <button
                    type="button"
                    className="knowledge-timeline-button"
                    onClick={() =>
                      navigate(
                        `/decisions/${decision.id}`
                      )
                    }
                  >
                    View Decision
                    <span>→</span>
                  </button>

                </div>

              </div>

            ))}

          </div>

        </div>
      )}

    </div>
  );
}

export default KnowledgeRepository;