import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

function TeamDecisions() {
  const navigate = useNavigate();

  const [decisions, setDecisions] = useState([]);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [category, setCategory] = useState("");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadDecisions = async () => {
    try {
      setLoading(true);
      setError("");

      const params = {
        page: 1,
        page_size: 100,
        sort: "created_at",
        order: "desc",
      };

      if (search.trim()) {
        params.q = search.trim();
      }

      if (status) {
        params.status = status;
      }

      if (category.trim()) {
        params.category = category.trim();
      }

      const response = await api.get("/decisions", { params });

      const data = Array.isArray(response.data)
        ? response.data
        : response.data.data || [];

      setDecisions(data);
    } catch (err) {
      console.error("Team decisions error:", err);

      setError(
        err.response?.data?.detail ||
          "Unable to load team decisions. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDecisions();
  }, [status]);

  const handleSearch = (e) => {
    e.preventDefault();
    loadDecisions();
  };

  const clearFilters = () => {
    setSearch("");
    setStatus("");
    setCategory("");

    setTimeout(() => {
      loadDecisions();
    }, 0);
  };

  const draftCount = decisions.filter(
    (decision) => decision.status === "Draft"
  ).length;

  const reviewCount = decisions.filter(
    (decision) => decision.status === "Under Review"
  ).length;

  const approvedCount = decisions.filter(
    (decision) => decision.status === "Approved"
  ).length;

  const rejectedCount = decisions.filter(
    (decision) => decision.status === "Rejected"
  ).length;

  if (loading) {
    return (
      <div className="page-container team-decisions-page">
        <div className="page-header">
          <div>
            <h1>Team Decisions</h1>
            <p>
              Review and monitor organizational decisions.
            </p>
          </div>
        </div>

        <div className="empty-state">
          <h3>Loading team decisions...</h3>
          <p>Please wait while the decision registry is loading.</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-container team-decisions-page">
        <div className="page-header">
          <div>
            <h1>Team Decisions</h1>
            <p>
              Review and monitor organizational decisions.
            </p>
          </div>
        </div>

        <div className="error-message">
          {error}
        </div>

        <button
          className="primary-button"
          onClick={loadDecisions}
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="page-container team-decisions-page">

      {/* ================= HEADER ================= */}

      <div className="page-header">
        <div>
          <h1>Team Decisions</h1>
          <p>
            Monitor organizational decisions, track their status,
            and review decision activity.
          </p>
        </div>
      </div>

      {/* ================= STATISTICS ================= */}

      <div className="dashboard-cards team-stats">

        <div className="dashboard-card team-stat-card">
          <div className="dashboard-card-label">
            Total Decisions
          </div>

          <div className="dashboard-card-value">
            {decisions.length}
          </div>

          <div className="dashboard-card-info">
            Organizational decisions
          </div>
        </div>

        <div className="dashboard-card team-stat-card">
          <div className="dashboard-card-label">
            Draft
          </div>

          <div className="dashboard-card-value">
            {draftCount}
          </div>

          <div className="dashboard-card-info">
            Decisions in draft
          </div>
        </div>

        <div className="dashboard-card team-stat-card">
          <div className="dashboard-card-label">
            Under Review
          </div>

          <div className="dashboard-card-value">
            {reviewCount}
          </div>

          <div className="dashboard-card-info">
            Awaiting review
          </div>
        </div>

        <div className="dashboard-card team-stat-card">
          <div className="dashboard-card-label">
            Approved
          </div>

          <div className="dashboard-card-value">
            {approvedCount}
          </div>

          <div className="dashboard-card-info">
            Approved decisions
          </div>
        </div>

        <div className="dashboard-card team-stat-card">
          <div className="dashboard-card-label">
            Rejected
          </div>

          <div className="dashboard-card-value">
            {rejectedCount}
          </div>

          <div className="dashboard-card-info">
            Rejected decisions
          </div>
        </div>

      </div>

      {/* ================= FILTERS ================= */}

      <div className="dashboard-section">

        <div className="section-heading">
          <div>
            <h2>Search & Filters</h2>
            <span>
              Find decisions quickly using the available filters.
            </span>
          </div>
        </div>

        <form
          onSubmit={handleSearch}
          className="filters-row"
        >

          <input
            type="text"
            placeholder="Search decisions..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="form-input"
          />

          <select
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            className="form-input"
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

          <input
            type="text"
            placeholder="Category"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="form-input"
          />

          <button
            type="submit"
            className="primary-button"
          >
            Search
          </button>

          <button
            type="button"
            className="secondary-button"
            onClick={clearFilters}
          >
            Clear
          </button>

        </form>

      </div>

      {/* ================= DECISION REGISTRY ================= */}

      <div className="dashboard-section">

        <div className="section-heading">
          <div>
            <h2>Decision Registry</h2>

            <span>
              {decisions.length}{" "}
              {decisions.length === 1
                ? "decision"
                : "decisions"}{" "}
              found
            </span>
          </div>
        </div>

        {decisions.length === 0 ? (

          <div className="empty-state">

            <h3>
              No decisions found
            </h3>

            <p>
              No decisions match the selected search or filters.
            </p>

          </div>

        ) : (

          <div className="dashboard-table-container team-table-container">

            <table className="dashboard-table">

              <thead>
                <tr>
                  <th>ID</th>
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
                      <strong>
                        #{decision.id}
                      </strong>
                    </td>

                    <td>
                      <strong>
                        {decision.title}
                      </strong>
                    </td>

                    <td>
                      {decision.category || "N/A"}
                    </td>

                    <td>
                      User #{decision.created_by}
                    </td>

                    <td>
                      <span className="status-badge">
                        {decision.status}
                      </span>
                    </td>

                    <td>
                      {decision.created_at
                        ? new Date(
                            decision.created_at
                          ).toLocaleDateString()
                        : "N/A"}
                    </td>

                    <td>
                      {decision.updated_at
                        ? new Date(
                            decision.updated_at
                          ).toLocaleDateString()
                        : "N/A"}
                    </td>

                    <td>
                      <button
                        className="secondary-button team-view-btn"
                        onClick={() =>
                          navigate(
                            `/decisions/${decision.id}`
                          )
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

        )}

      </div>

    </div>
  );
}

export default TeamDecisions;