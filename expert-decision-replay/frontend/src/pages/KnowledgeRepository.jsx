import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import knowledgeService from "../services/knowledgeService";
import "./KnowledgeRepository.css";

const KnowledgeRepository = () => {
  const navigate = useNavigate();

  const [decisions, setDecisions] = useState([]);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [status, setStatus] = useState("");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Load decisions
  const loadKnowledgeRepository = async (
    searchValue = "",
    categoryValue = "",
    statusValue = ""
  ) => {
    try {
      setLoading(true);
      setError("");

      const response = await knowledgeService.searchKnowledge({
        search: searchValue,
        category: categoryValue,
        status: statusValue,
      });

      console.log("Knowledge Repository Response:", response);

      let data = [];

      if (Array.isArray(response)) {
        data = response;
      } else if (Array.isArray(response?.data)) {
        data = response.data;
      } else if (Array.isArray(response?.decisions)) {
        data = response.decisions;
      } else if (Array.isArray(response?.data?.decisions)) {
        data = response.data.decisions;
      }

      setDecisions(data);
    } catch (err) {
      console.error("Knowledge Repository Error:", err);

      const detail =
        err.response?.data?.detail ||
        err.message ||
        "Unable to load knowledge repository.";

      setError(detail);
      setDecisions([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadKnowledgeRepository();
  }, []);

  // Search
  const handleSearch = (event) => {
    event.preventDefault();

    loadKnowledgeRepository(
      search.trim(),
      category.trim(),
      status
    );
  };

  // Clear filters
  const clearFilters = () => {
    setSearch("");
    setCategory("");
    setStatus("");

    loadKnowledgeRepository("", "", "");
  };

  // Status style
  const getStatusClass = (value) => {
    switch (value?.toLowerCase()) {
      case "approved":
        return "status-approved";

      case "rejected":
        return "status-rejected";

      case "pending":
        return "status-pending";

      case "draft":
        return "status-draft";

      default:
        return "status-default";
    }
  };

  // Open decision details
  const handleViewDetails = (decisionId) => {
    if (!decisionId) {
      return;
    }

    navigate(`/decisions/${decisionId}`);
  };

  return (
    <div className="knowledge-page">

      {/* HEADER */}

      <div className="knowledge-header">
        <div>
          <div className="knowledge-breadcrumb">
            Workspace / Knowledge Repository
          </div>

          <h1>Knowledge Repository</h1>

          <p>
            Search and explore previously recorded decisions.
          </p>
        </div>
      </div>

      {/* SEARCH CARD */}

      <div className="knowledge-filter-card">

        <div className="filter-card-title">
          <div>
            <h2>Search Decisions</h2>

            <p>
              Use the filters below to find previously recorded
              decisions.
            </p>
          </div>
        </div>

        <form onSubmit={handleSearch}>

          <div className="filter-grid">

            {/* SEARCH */}

            <div className="filter-field">
              <label htmlFor="search">
                Search
              </label>

              <input
                id="search"
                type="text"
                value={search}
                onChange={(event) =>
                  setSearch(event.target.value)
                }
                placeholder="Search decisions..."
              />
            </div>

            {/* CATEGORY */}

            <div className="filter-field">
              <label htmlFor="category">
                Category
              </label>

              <input
                id="category"
                type="text"
                value={category}
                onChange={(event) =>
                  setCategory(event.target.value)
                }
                placeholder="Enter category..."
              />
            </div>

            {/* STATUS */}

            <div className="filter-field">
              <label htmlFor="status">
                Status
              </label>

              <select
                id="status"
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

                <option value="Pending">
                  Pending
                </option>

                <option value="Approved">
                  Approved
                </option>

                <option value="Rejected">
                  Rejected
                </option>
              </select>
            </div>

          </div>

          {/* BUTTONS */}

          <div className="filter-actions">

            <button
              type="submit"
              className="search-btn"
            >
              Search
            </button>

            <button
              type="button"
              className="clear-btn"
              onClick={clearFilters}
            >
              Clear
            </button>

          </div>

        </form>
      </div>

      {/* ERROR */}

      {error && (
        <div className="knowledge-error">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* LOADING */}

      {loading && (
        <div className="knowledge-message">
          <div className="loading-spinner"></div>

          <h3>Loading Knowledge Repository</h3>

          <p>
            Please wait while we load the decision records.
          </p>
        </div>
      )}

      {/* EMPTY */}

      {!loading &&
        !error &&
        decisions.length === 0 && (
          <div className="knowledge-message">
            <div className="empty-icon">📂</div>

            <h3>No decisions found</h3>

            <p>
              No matching decision records are available.
            </p>
          </div>
        )}

      {/* RESULTS */}

      {!loading &&
        !error &&
        decisions.length > 0 && (
          <div className="knowledge-results">

            {/* RESULTS HEADER */}

            <div className="results-header">

              <div>
                <h2>Decision Records</h2>

                <p>
                  {decisions.length} decision
                  {decisions.length !== 1 ? "s" : ""} found
                </p>
              </div>

            </div>

            {/* CARDS */}

            <div className="knowledge-grid">

              {decisions.map((decision) => (

                <div
                  className="knowledge-card"
                  key={decision.id}
                >

                  {/* CARD TOP */}

                  <div className="knowledge-card-header">

                    <div className="decision-heading">

                      <span className="decision-number">
                        Decision #{decision.id}
                      </span>

                      <h3>
                        {decision.title ||
                          `Decision #${decision.id}`}
                      </h3>

                    </div>

                    <span
                      className={`status-badge ${getStatusClass(
                        decision.status
                      )}`}
                    >
                      {decision.status || "Unknown"}
                    </span>

                  </div>

                  {/* DESCRIPTION */}

                  <div className="knowledge-description">

                    <p>
                      {decision.description ||
                        decision.rationale ||
                        "No description available."}
                    </p>

                  </div>

                  {/* DETAILS */}

                  <div className="knowledge-details">

                    <div className="detail-item">
                      <span>Category</span>

                      <strong>
                        {decision.category || "Not specified"}
                      </strong>
                    </div>

                    <div className="detail-item">
                      <span>Created By</span>

                      <strong>
                        {decision.created_by ||
                          decision.user_id ||
                          "-"}
                      </strong>
                    </div>

                    <div className="detail-item">
                      <span>Created At</span>

                      <strong>
                        {decision.created_at
                          ? new Date(
                              decision.created_at
                            ).toLocaleDateString()
                          : "-"}
                      </strong>
                    </div>

                  </div>

                  {/* FOOTER */}

                  <div className="knowledge-card-footer">

                    <span className="decision-id">
                      ID: {decision.id}
                    </span>

                    <button
                      type="button"
                      onClick={() =>
                        handleViewDetails(decision.id)
                      }
                    >
                      View Details
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
};

export default KnowledgeRepository;