import { useEffect, useState } from "react";
import api from "../services/api";

function DecisionStatistics() {
  const [decisions, setDecisions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadStatistics = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await api.get("/decisions");

      const data = Array.isArray(response.data)
        ? response.data
        : response.data.data || [];

      setDecisions(data);
    } catch (err) {
      console.error("Decision statistics error:", err);

      setError(
        err.response?.data?.detail ||
          "Failed to load decision statistics."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStatistics();
  }, []);

  const total = decisions.length;

  const getStatusCount = (statuses) =>
    decisions.filter((decision) =>
      statuses.includes(
        decision.status?.toLowerCase()
      )
    ).length;

  const draft = getStatusCount(["draft"]);

  const underReview = getStatusCount([
    "under review",
    "under_review",
    "pending",
  ]);

  const approved = getStatusCount(["approved"]);

  const rejected = getStatusCount(["rejected"]);

  const percentage = (value) =>
    total ? ((value / total) * 100).toFixed(1) : "0.0";

  const statistics = [
    {
      title: "Total Decisions",
      value: total,
      description: "All decisions",
      icon: "▣",
    },
    {
      title: "Draft",
      value: draft,
      description: "In preparation",
      icon: "✎",
    },
    {
      title: "Under Review",
      value: underReview,
      description: "Awaiting review",
      icon: "◷",
    },
    {
      title: "Approved",
      value: approved,
      description: "Successfully approved",
      icon: "✓",
    },
    {
      title: "Rejected",
      value: rejected,
      description: "Not approved",
      icon: "×",
    },
  ];

  return (
    <div className="statistics-page">

      {/* Header */}
      <div className="statistics-header">
        <div>
          <span className="statistics-eyebrow">
            MANAGER ANALYTICS
          </span>

          <h1>Decision Statistics</h1>

          <p>
            Monitor decision activity, approval progress,
            and overall decision status.
          </p>
        </div>

        <button
          className="statistics-refresh"
          onClick={loadStatistics}
          disabled={loading}
        >
          ↻ {loading ? "Refreshing..." : "Refresh Data"}
        </button>
      </div>

      {error && (
        <div className="statistics-error">
          <strong>Unable to load statistics</strong>
          <span>{error}</span>
        </div>
      )}

      {loading ? (
        <div className="statistics-loading">
          <div className="statistics-spinner"></div>
          <p>Loading decision analytics...</p>
        </div>
      ) : (
        <>
          {/* Stat Cards */}
          <div className="statistics-cards">

            {statistics.map((item) => (
              <div
                className="statistics-card"
                key={item.title}
              >
                <div className="statistics-card-top">

                  <div className="statistics-icon">
                    {item.icon}
                  </div>

                  <span className="statistics-label">
                    {item.title}
                  </span>

                </div>

                <div className="statistics-value">
                  {item.value}
                </div>

                <div className="statistics-description">
                  {item.description}
                </div>
              </div>
            ))}

          </div>

          {/* Overview */}
          <div className="statistics-main-grid">

            <div className="statistics-panel">

              <div className="statistics-panel-header">
                <div>
                  <h2>Decision Overview</h2>
                  <p>
                    Current distribution of decisions by status
                  </p>
                </div>
              </div>

              <div className="statistics-bars">

                <div className="statistics-bar-row">
                  <div className="statistics-bar-info">
                    <span>Draft</span>
                    <strong>{draft}</strong>
                  </div>

                  <div className="statistics-bar-track">
                    <div
                      className="statistics-bar-fill draft-bar"
                      style={{
                        width: `${percentage(draft)}%`,
                      }}
                    ></div>
                  </div>

                  <span className="statistics-percent">
                    {percentage(draft)}%
                  </span>
                </div>

                <div className="statistics-bar-row">
                  <div className="statistics-bar-info">
                    <span>Under Review</span>
                    <strong>{underReview}</strong>
                  </div>

                  <div className="statistics-bar-track">
                    <div
                      className="statistics-bar-fill review-bar"
                      style={{
                        width: `${percentage(underReview)}%`,
                      }}
                    ></div>
                  </div>

                  <span className="statistics-percent">
                    {percentage(underReview)}%
                  </span>
                </div>

                <div className="statistics-bar-row">
                  <div className="statistics-bar-info">
                    <span>Approved</span>
                    <strong>{approved}</strong>
                  </div>

                  <div className="statistics-bar-track">
                    <div
                      className="statistics-bar-fill approved-bar"
                      style={{
                        width: `${percentage(approved)}%`,
                      }}
                    ></div>
                  </div>

                  <span className="statistics-percent">
                    {percentage(approved)}%
                  </span>
                </div>

                <div className="statistics-bar-row">
                  <div className="statistics-bar-info">
                    <span>Rejected</span>
                    <strong>{rejected}</strong>
                  </div>

                  <div className="statistics-bar-track">
                    <div
                      className="statistics-bar-fill rejected-bar"
                      style={{
                        width: `${percentage(rejected)}%`,
                      }}
                    ></div>
                  </div>

                  <span className="statistics-percent">
                    {percentage(rejected)}%
                  </span>
                </div>

              </div>
            </div>

            {/* Summary */}
            <div className="statistics-panel statistics-summary">

              <div className="statistics-panel-header">
                <div>
                  <h2>Summary</h2>
                  <p>Decision performance snapshot</p>
                </div>
              </div>

              <div className="summary-item">
                <div>
                  <span>Approval Rate</span>
                  <small>Approved decisions</small>
                </div>

                <strong>
                  {percentage(approved)}%
                </strong>
              </div>

              <div className="summary-item">
                <div>
                  <span>Review Queue</span>
                  <small>Decisions awaiting review</small>
                </div>

                <strong>
                  {underReview}
                </strong>
              </div>

              <div className="summary-item">
                <div>
                  <span>Draft Work</span>
                  <small>Decisions still being prepared</small>
                </div>

                <strong>
                  {draft}
                </strong>
              </div>

              <div className="summary-item">
                <div>
                  <span>Rejected</span>
                  <small>Decisions not approved</small>
                </div>

                <strong>
                  {rejected}
                </strong>
              </div>

            </div>

          </div>

          {/* Detailed Table */}
          <div className="statistics-panel statistics-table-panel">

            <div className="statistics-panel-header">
              <div>
                <h2>Status Breakdown</h2>
                <p>
                  Detailed distribution of all decisions
                </p>
              </div>
            </div>

            <div className="statistics-table-wrapper">

              <table className="statistics-table">

                <thead>
                  <tr>
                    <th>Status</th>
                    <th>Decisions</th>
                    <th>Percentage</th>
                  </tr>
                </thead>

                <tbody>

                  <tr>
                    <td>
                      <span className="status-dot draft-dot"></span>
                      Draft
                    </td>
                    <td>{draft}</td>
                    <td>{percentage(draft)}%</td>
                  </tr>

                  <tr>
                    <td>
                      <span className="status-dot review-dot"></span>
                      Under Review
                    </td>
                    <td>{underReview}</td>
                    <td>{percentage(underReview)}%</td>
                  </tr>

                  <tr>
                    <td>
                      <span className="status-dot approved-dot"></span>
                      Approved
                    </td>
                    <td>{approved}</td>
                    <td>{percentage(approved)}%</td>
                  </tr>

                  <tr>
                    <td>
                      <span className="status-dot rejected-dot"></span>
                      Rejected
                    </td>
                    <td>{rejected}</td>
                    <td>{percentage(rejected)}%</td>
                  </tr>

                </tbody>

              </table>

            </div>
          </div>
        </>
      )}

    </div>
  );
}

export default DecisionStatistics;