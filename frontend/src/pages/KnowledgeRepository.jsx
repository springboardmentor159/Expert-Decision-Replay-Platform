import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

function KnowledgeRepository() {
  const navigate = useNavigate();

  const [decisions, setDecisions] = useState([]);
  const [tags, setTags] = useState([]);
  const [tagName, setTagName] = useState("");

  const [searchText, setSearchText] = useState("");
  const [category, setCategory] = useState("");
  const [decisionStatus, setDecisionStatus] = useState("");

  const [loading, setLoading] = useState(false);
  const [tagsLoading, setTagsLoading] = useState(false);

  const [error, setError] = useState("");
  const [tagError, setTagError] = useState("");
  const [tagMessage, setTagMessage] = useState("");

  const categories = [
    "Technology",
    "Finance",
    "Operations",
    "Human Resources",
    "Security",
    "Product",
    "Infrastructure",
    "Strategy",
  ];

  const statuses = [
    "Draft",
    "Under Review",
    "Approved",
    "Rejected",
  ];

  const fetchDecisions = async () => {
    try {
      setLoading(true);
      setError("");

      let response;

      if (searchText.trim()) {
        response = await api.get("/decisions/search", {
          params: {
            q: searchText.trim(),
          },
        });
      } else {
        response = await api.get("/decisions/discover", {
          params: {
            ...(category && { category }),
            ...(decisionStatus && {
              status: decisionStatus,
            }),
          },
        });
      }

      setDecisions(response.data);
    } catch (err) {
      console.error("Knowledge Repository error:", err);

      if (err.response?.data?.detail) {
        setError(
          typeof err.response.data.detail === "string"
            ? err.response.data.detail
            : "Unable to load decisions."
        );
      } else {
        setError("Unable to load decisions.");
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchTags = async () => {
    try {
      setTagsLoading(true);
      setTagError("");

      const response = await api.get("/tags");

      setTags(response.data);
    } catch (err) {
      console.error("Tags error:", err);

      if (err.response?.data?.detail) {
        setTagError(
          typeof err.response.data.detail === "string"
            ? err.response.data.detail
            : "Unable to load tags."
        );
      } else {
        setTagError("Unable to load tags.");
      }
    } finally {
      setTagsLoading(false);
    }
  };

  useEffect(() => {
    fetchDecisions();
    fetchTags();
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchDecisions();
  };

  const handleAddTag = async (e) => {
    e.preventDefault();

    setTagError("");
    setTagMessage("");

    if (!tagName.trim()) {
      setTagError("Tag name is required.");
      return;
    }

    try {
      const response = await api.post("/tags", {
        name: tagName.trim(),
      });

      setTags((current) => [...current, response.data]);
      setTagName("");
      setTagMessage("Tag added successfully.");
    } catch (err) {
      console.error("Add tag error:", err);

      if (err.response?.data?.detail) {
        setTagError(
          typeof err.response.data.detail === "string"
            ? err.response.data.detail
            : "Unable to add tag."
        );
      } else {
        setTagError("Unable to add tag.");
      }
    }
  };

  const handleClear = () => {
    setSearchText("");
    setCategory("");
    setDecisionStatus("");

    setTimeout(() => {
      fetchDecisions();
    }, 0);
  };

  const getStatusClass = (status) => {
    switch (status) {
      case "Approved":
        return "repository-status approved";

      case "Rejected":
        return "repository-status rejected";

      case "Under Review":
        return "repository-status review";

      default:
        return "repository-status draft";
    }
  };

  return (
    <div className="repository-page">

      {/* Header */}
      <div className="repository-header">

        <div>
          <div className="page-breadcrumb">
            Workspace / Knowledge Repository
          </div>

          <h1>Knowledge Repository</h1>

          <p>
            Search, discover and explore organizational decisions.
          </p>
        </div>

        <button
          className="secondary-page-button"
          onClick={() => navigate("/dashboard")}
        >
          ← Dashboard
        </button>

      </div>

      {/* Summary Cards */}
      <div className="repository-summary">

        <div className="repository-summary-card">
          <div className="repository-summary-icon">
            ◈
          </div>

          <div>
            <span>Decisions Found</span>
            <strong>{decisions.length}</strong>
          </div>
        </div>

        <div className="repository-summary-card">
          <div className="repository-summary-icon">
            #
          </div>

          <div>
            <span>Available Tags</span>
            <strong>{tags.length}</strong>
          </div>
        </div>

        <div className="repository-summary-card">
          <div className="repository-summary-icon">
            ⌕
          </div>

          <div>
            <span>Search</span>
            <strong>Enabled</strong>
          </div>
        </div>

      </div>

      {/* Search & Filters */}
      <div className="repository-search-card">

        <div className="repository-section-heading">
          <div>
            <h2>Find a Decision</h2>
            <p>
              Search by title, problem statement or category.
            </p>
          </div>
        </div>

        <form
          className="repository-search-form"
          onSubmit={handleSearch}
        >

          <div className="repository-search-input">

            <span>⌕</span>

            <input
              type="text"
              value={searchText}
              onChange={(e) =>
                setSearchText(e.target.value)
              }
              placeholder="Search decisions..."
            />

          </div>

          <button
            type="submit"
            className="primary-submit-button"
          >
            Search
          </button>

        </form>

        <div className="repository-filters">

          <div className="repository-filter-group">

            <label>Category</label>

            <select
              value={category}
              onChange={(e) =>
                setCategory(e.target.value)
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

          <div className="repository-filter-group">

            <label>Status</label>

            <select
              value={decisionStatus}
              onChange={(e) =>
                setDecisionStatus(e.target.value)
              }
            >
              <option value="">
                All Statuses
              </option>

              {statuses.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>

          </div>

          <div className="repository-filter-actions">

            <button
              type="button"
              className="filter-apply-button"
              onClick={fetchDecisions}
            >
              Apply Filters
            </button>

            <button
              type="button"
              className="filter-clear-button"
              onClick={handleClear}
            >
              Clear
            </button>

          </div>

        </div>

      </div>

      {/* Tags */}
      <div className="repository-tags-card">

        <div className="repository-section-heading">

          <div>
            <h2>Knowledge Tags</h2>
            <p>
              Use tags to organize and classify decisions.
            </p>
          </div>

          <span className="repository-count">
            {tags.length} Tags
          </span>

        </div>

        <form
          className="tag-form"
          onSubmit={handleAddTag}
        >

          <input
            type="text"
            value={tagName}
            onChange={(e) =>
              setTagName(e.target.value)
            }
            placeholder="Enter a new tag name"
          />

          <button
            type="submit"
            className="primary-submit-button"
          >
            + Add Tag
          </button>

        </form>

        {tagMessage && (
          <div className="repository-success">
            ✓ {tagMessage}
          </div>
        )}

        {tagError && (
          <div className="repository-error">
            {tagError}
          </div>
        )}

        {!tagsLoading && tags.length > 0 && (
          <div className="tag-list">

            {tags.map((tag) => (
              <span
                className="tag-pill"
                key={tag.id}
              >
                #{tag.name}
              </span>
            ))}

          </div>
        )}

        {tagsLoading && (
          <div className="repository-small-loading">
            Loading tags...
          </div>
        )}

        {!tagsLoading && tags.length === 0 && (
          <div className="repository-small-empty">
            No tags found.
          </div>
        )}

      </div>

      {/* Decision Repository */}
      <div className="repository-results-card">

        <div className="repository-section-heading">

          <div>
            <h2>Decision Repository</h2>
            <p>
              Browse decisions available in the organizational knowledge base.
            </p>
          </div>

          <span className="repository-count">
            {decisions.length} Results
          </span>

        </div>

        {loading && (
          <div className="repository-loading">
            <div className="loading-spinner"></div>
            <p>Loading decisions...</p>
          </div>
        )}

        {!loading && error && (
          <div className="repository-error-box">

            <div className="repository-error-icon">
              !
            </div>

            <h3>Unable to Load Repository</h3>

            <p>{error}</p>

          </div>
        )}

        {!loading &&
          !error &&
          decisions.length === 0 && (
            <div className="repository-empty">

              <div className="repository-empty-icon">
                ◈
              </div>

              <h3>No Decisions Found</h3>

              <p>
                Try changing your search text or filters.
              </p>

            </div>
          )}

        {!loading &&
          !error &&
          decisions.length > 0 && (

            <div className="repository-table-wrapper">

              <table className="repository-table">

                <thead>
                  <tr>
                    <th>Decision</th>
                    <th>Category</th>
                    <th>Status</th>
                    <th>Created By</th>
                    <th>Last Updated</th>
                    <th>Action</th>
                  </tr>
                </thead>

                <tbody>

                  {decisions.map((decision) => (

                    <tr key={decision.id}>

                      <td>

                        <div className="repository-decision-cell">

                          <div className="repository-decision-icon">
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
                        <span className="repository-category">
                          {decision.category || "—"}
                        </span>
                      </td>

                      <td>

                        <span
                          className={getStatusClass(
                            decision.status
                          )}
                        >
                          {decision.status || "Draft"}
                        </span>

                      </td>

                      <td>
                        <span className="repository-user">
                          User #{decision.created_by || "—"}
                        </span>
                      </td>

                      <td>
                        <span className="repository-date">
                          {decision.updated_at
                            ? new Date(
                                decision.updated_at
                              ).toLocaleString()
                            : decision.created_at
                            ? new Date(
                                decision.created_at
                              ).toLocaleString()
                            : "—"}
                        </span>
                      </td>

                      <td>

                        <button
                          className="repository-view-button"
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

    </div>
  );
}

export default KnowledgeRepository;