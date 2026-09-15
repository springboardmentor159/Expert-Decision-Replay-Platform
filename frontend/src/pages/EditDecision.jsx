import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../services/api";

function EditDecision() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [title, setTitle] = useState("");
  const [problemStatement, setProblemStatement] = useState("");
  const [category, setCategory] = useState("");

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    const fetchDecision = async () => {
      try {
        setLoading(true);
        setError("");

        const response = await api.get(`/decisions/${id}`);

        setTitle(response.data.title || "");
        setProblemStatement(response.data.problem_statement || "");
        setCategory(response.data.category || "");
      } catch (err) {
        console.error("Load decision error:", err);
        setError("Unable to load decision. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    fetchDecision();
  }, [id]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError("");
    setMessage("");

    if (!title.trim()) {
      setError("Decision title is required.");
      return;
    }

    if (!problemStatement.trim()) {
      setError("Problem statement is required.");
      return;
    }

    if (!category) {
      setError("Please select a category.");
      return;
    }

    try {
      setSaving(true);

      await api.put(`/decisions/${id}`, {
        title: title.trim(),
        problem_statement: problemStatement.trim(),
        category: category,
      });

      setMessage("Decision updated successfully.");

      setTimeout(() => {
        navigate(`/decisions/${id}`);
      }, 1000);
    } catch (err) {
      console.error("Update decision error:", err);

      if (err.response?.data?.detail) {
        setError(
          typeof err.response.data.detail === "string"
            ? err.response.data.detail
            : "Unable to update decision."
        );
      } else {
        setError("Unable to update decision. Please try again.");
      }
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="page-container">
        <div className="loading-state-card">
          <div className="loading-spinner"></div>
          <p>Loading decision details...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container edit-decision-page">
      {/* Breadcrumb */}
      <div className="page-breadcrumb">
        <button
          type="button"
          onClick={() => navigate("/decisions")}
          className="breadcrumb-link"
        >
          Decisions
        </button>

        <span>/</span>

        <button
          type="button"
          onClick={() => navigate(`/decisions/${id}`)}
          className="breadcrumb-link"
        >
          Decision #{id}
        </button>

        <span>/</span>

        <span className="breadcrumb-current">Edit</span>
      </div>

      {/* Page Header */}
      <div className="edit-decision-header">
        <div>
          <span className="section-eyebrow">DECISION MANAGEMENT</span>

          <h1>Edit Decision</h1>

          <p>
            Update the decision information and keep the decision record
            accurate and up to date.
          </p>
        </div>

        <div className="decision-id-badge">
          <span>DECISION ID</span>
          <strong>#{id}</strong>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="edit-alert edit-alert-error">
          <div className="edit-alert-icon">!</div>
          <div>
            <strong>Unable to complete request</strong>
            <p>{error}</p>
          </div>
        </div>
      )}

      {/* Success */}
      {message && (
        <div className="edit-alert edit-alert-success">
          <div className="edit-alert-icon">✓</div>
          <div>
            <strong>Update successful</strong>
            <p>{message}</p>
          </div>
        </div>
      )}

      <div className="edit-decision-layout">
        {/* Main Form */}
        <div className="edit-decision-card">
          <div className="edit-card-header">
            <div>
              <h2>Decision Information</h2>
              <p>Modify the details of this decision.</p>
            </div>

            <div className="edit-card-icon">✎</div>
          </div>

          <form onSubmit={handleSubmit} className="edit-decision-form">
            {/* Title */}
            <div className="edit-form-field">
              <label htmlFor="decision-title">
                Decision Title <span>*</span>
              </label>

              <input
                id="decision-title"
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Enter decision title"
                disabled={saving}
              />

              <small>
                Use a clear and descriptive title for the decision.
              </small>
            </div>

            {/* Problem Statement */}
            <div className="edit-form-field">
              <label htmlFor="problem-statement">
                Problem Statement <span>*</span>
              </label>

              <textarea
                id="problem-statement"
                rows="7"
                value={problemStatement}
                onChange={(e) => setProblemStatement(e.target.value)}
                placeholder="Describe the problem or situation requiring a decision..."
                disabled={saving}
              />

              <small>
                Clearly describe the business problem or situation.
              </small>
            </div>

            {/* Category */}
            <div className="edit-form-field">
              <label htmlFor="decision-category">
                Category <span>*</span>
              </label>

              <select
                id="decision-category"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                disabled={saving}
              >
                <option value="">Select Category</option>
                <option value="Technology">Technology</option>
                <option value="Finance">Finance</option>
                <option value="Operations">Operations</option>
                <option value="Human Resources">
                  Human Resources
                </option>
                <option value="Security">Security</option>
                <option value="Product">Product</option>
                <option value="Infrastructure">
                  Infrastructure
                </option>
                <option value="Strategy">Strategy</option>
              </select>

              <small>
                Select the category that best represents this decision.
              </small>
            </div>

            {/* Actions */}
            <div className="edit-form-actions">
              <button
                type="button"
                className="edit-cancel-button"
                onClick={() => navigate(`/decisions/${id}`)}
                disabled={saving}
              >
                Cancel
              </button>

              <button
                type="submit"
                className="edit-save-button"
                disabled={saving}
              >
                {saving ? (
                  <>
                    <span className="edit-button-spinner"></span>
                    Saving Changes...
                  </>
                ) : (
                  <>
                    <span>✓</span>
                    Save Changes
                  </>
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Side Information */}
        <aside className="edit-decision-sidebar">
          <div className="edit-info-card">
            <div className="edit-info-card-icon">i</div>

            <h3>Editing a Decision</h3>

            <p>
              Update the information carefully. Changes will be saved to the
              decision record.
            </p>

            <div className="edit-info-list">
              <div>
                <span>01</span>
                <p>Review the current information.</p>
              </div>

              <div>
                <span>02</span>
                <p>Make the required changes.</p>
              </div>

              <div>
                <span>03</span>
                <p>Save the updated decision.</p>
              </div>
            </div>
          </div>

          <div className="edit-history-card">
            <span className="section-eyebrow">RECORD</span>

            <h3>Decision History</h3>

            <p>
              Updates to decisions can be reviewed through the decision
              history and audit records.
            </p>

            <button
              type="button"
              onClick={() => navigate(`/decisions/${id}/history`)}
              className="edit-history-button"
            >
              View History →
            </button>
          </div>
        </aside>
      </div>
    </div>
  );
}

export default EditDecision;