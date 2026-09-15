import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../services/api";

function DecisionDetails() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [decision, setDecision] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchDecision = async () => {
      try {
        const response = await api.get(`/decisions/${id}`);
        setDecision(response.data);
      } catch (err) {
        console.error("Decision error:", err);
        setError("Unable to load decision.");
      } finally {
        setLoading(false);
      }
    };

    fetchDecision();
  }, [id]);

  if (loading) {
    return (
      <div className="decision-page-loading">
        <div className="loading-spinner"></div>
        <p>Loading decision...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="decision-error-card">
        <div className="error-large-icon">!</div>
        <h2>Unable to Load Decision</h2>
        <p>{error}</p>

        <button
          className="primary-submit-button"
          onClick={() => navigate("/decisions")}
        >
          ← Back to Decisions
        </button>
      </div>
    );
  }

  if (!decision) {
    return (
      <div className="decision-error-card">
        <h2>No Decision Found</h2>
        <button
          className="primary-submit-button"
          onClick={() => navigate("/decisions")}
        >
          Back to Decisions
        </button>
      </div>
    );
  }

  const status = decision.status || "Draft";

  return (
    <div className="decision-details-page">

      {/* Header */}
      <div className="decision-details-header">

        <div>
          <div className="page-breadcrumb">
            Decisions / Decision Details
          </div>

          <h1>{decision.title}</h1>

          <div className="decision-header-meta">
            <span className={`status-badge ${status.toLowerCase().replace(/\s+/g, "-")}`}>
              {status}
            </span>

            <span className="decision-id">
              Decision #{decision.id}
            </span>
          </div>
        </div>

        <div className="decision-header-actions">
          <button
            className="secondary-page-button"
            onClick={() => navigate("/decisions")}
          >
            ← Back
          </button>

          <button
            className="primary-submit-button"
            onClick={() => navigate(`/decisions/${id}/edit`)}
          >
            Edit Decision
          </button>
        </div>

      </div>

      {/* Main Content */}
      <div className="decision-details-grid">

        {/* Left Column */}
        <div className="decision-main-column">

          {/* Problem Statement */}
          <div className="details-card">

            <div className="details-card-title">
              <div className="details-icon">?</div>

              <div>
                <h2>Problem Statement</h2>
                <p>The business problem or situation requiring a decision</p>
              </div>
            </div>

            <div className="problem-content">
              {decision.problem_statement || "Not available"}
            </div>

          </div>

          {/* Decision Information */}
          <div className="details-card">

            <div className="details-card-title">
              <div className="details-icon">▣</div>

              <div>
                <h2>Decision Information</h2>
                <p>Basic information about this decision</p>
              </div>
            </div>

            <div className="decision-info-grid">

              <div className="info-item">
                <span>Decision ID</span>
                <strong>#{decision.id}</strong>
              </div>

              <div className="info-item">
                <span>Category</span>
                <strong>
                  {decision.category || "Not specified"}
                </strong>
              </div>

              <div className="info-item">
                <span>Status</span>
                <strong>{status}</strong>
              </div>

              <div className="info-item">
                <span>Created</span>
                <strong>
                  {decision.created_at
                    ? new Date(decision.created_at).toLocaleDateString()
                    : "Not available"}
                </strong>
              </div>

              <div className="info-item">
                <span>Last Updated</span>
                <strong>
                  {decision.updated_at
                    ? new Date(decision.updated_at).toLocaleDateString()
                    : "Not available"}
                </strong>
              </div>

            </div>

          </div>

          {/* Decision Modules */}
          <div className="details-card">

            <div className="details-card-title">
              <div className="details-icon">◇</div>

              <div>
                <h2>Decision Workspace</h2>
                <p>Continue working with this decision</p>
              </div>
            </div>

            <div className="decision-modules-grid">

              <button
                className="module-card"
                onClick={() =>
                  navigate(`/decisions/${id}/alternatives`)
                }
              >
                <div className="module-icon">↔</div>
                <div>
                  <strong>Alternatives</strong>
                  <span>Add and evaluate possible solutions</span>
                </div>
                <b>→</b>
              </button>

              <button
                className="module-card"
                onClick={() =>
                  navigate(`/decisions/${id}/alternatives/compare`)
                }
              >
                <div className="module-icon">⇄</div>
                <div>
                  <strong>Compare Alternatives</strong>
                  <span>Compare available options</span>
                </div>
                <b>→</b>
              </button>

              <button
                className="module-card"
                onClick={() =>
                  navigate(`/decisions/${id}/comments`)
                }
              >
                <div className="module-icon">☷</div>
                <div>
                  <strong>Discussions</strong>
                  <span>Collaborate through comments</span>
                </div>
                <b>→</b>
              </button>

              <button
                className="module-card"
                onClick={() =>
                  navigate(`/decisions/${id}/approvals`)
                }
              >
                <div className="module-icon">✓</div>
                <div>
                  <strong>Approval Workflow</strong>
                  <span>Review and approve the decision</span>
                </div>
                <b>→</b>
              </button>

              <button
                className="module-card"
                onClick={() =>
                  navigate(`/decisions/${id}/history`)
                }
              >
                <div className="module-icon">◷</div>
                <div>
                  <strong>Version History</strong>
                  <span>View previous decision versions</span>
                </div>
                <b>→</b>
              </button>

              <button
                className="module-card"
                onClick={() => navigate("/knowledge")}
              >
                <div className="module-icon">▤</div>
                <div>
                  <strong>Knowledge Repository</strong>
                  <span>Explore related knowledge</span>
                </div>
                <b>→</b>
              </button>

            </div>

          </div>

        </div>

        {/* Right Column */}
        <aside className="decision-side-column">

          {/* Status Card */}
          <div className="decision-status-card">

            <div className="side-card-heading">
              <span className="side-heading-icon">●</span>
              <h3>Decision Status</h3>
            </div>

            <div className="large-status">
              <span
                className={`status-dot ${status
                  .toLowerCase()
                  .replace(/\s+/g, "-")}`}
              ></span>

              {status}
            </div>

            <p>
              Current status of this decision in the decision lifecycle.
            </p>

          </div>

          {/* Quick Actions */}
          <div className="side-details-card">

            <div className="side-card-heading">
              <span className="side-heading-icon">⚡</span>
              <h3>Quick Actions</h3>
            </div>

            <button
              className="side-action-button"
              onClick={() =>
                navigate(`/decisions/${id}/comments`)
              }
            >
              <span>☷</span>
              Open Discussions
            </button>

            <button
              className="side-action-button"
              onClick={() =>
                navigate(`/decisions/${id}/approvals`)
              }
            >
              <span>✓</span>
              View Approvals
            </button>

            <button
              className="side-action-button"
              onClick={() =>
                navigate(`/decisions/${id}/history`)
              }
            >
              <span>◷</span>
              View History
            </button>

            <button
              className="side-action-button"
              onClick={() => navigate("/reports")}
            >
              <span>▥</span>
              View Reports
            </button>

          </div>

          {/* Administration */}
          <div className="side-details-card">

            <div className="side-card-heading">
              <span className="side-heading-icon">⚙</span>
              <h3>Administration</h3>
            </div>

            <button
              className="side-action-button"
              onClick={() => navigate("/audit-logs")}
            >
              <span>◉</span>
              Audit Logs
            </button>

            <button
              className="side-action-button"
              onClick={() => navigate("/knowledge")}
            >
              <span>▤</span>
              Knowledge Repository
            </button>

          </div>

        </aside>

      </div>
    </div>
  );
}

export default DecisionDetails;