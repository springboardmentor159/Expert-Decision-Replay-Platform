import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

function CreateDecision() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    title: "",
    problem_statement: "",
    category: "",
    rationale: "",
  });

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (event) => {
    const { name, value } = event.target;

    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");
    setSuccess("");

    if (!formData.title.trim()) {
      setError("Decision title is required.");
      return;
    }

    if (!formData.problem_statement.trim()) {
      setError("Problem statement is required.");
      return;
    }

    if (!formData.category.trim()) {
      setError("Category is required.");
      return;
    }

    try {
      setLoading(true);

      await api.post("/decisions", formData);

      setSuccess("Decision created successfully!");

      setTimeout(() => {
        navigate("/decisions");
      }, 1000);
    } catch (error) {
      if (error.response?.status === 401) {
        setError("Your session has expired. Please login again.");
      } else if (error.response?.status === 403) {
        setError("You are not authorized to create a decision.");
      } else if (error.response?.status === 422) {
        setError("Please check the entered information.");
      } else {
        setError(
          error.response?.data?.detail ||
            "Unable to create decision. Please try again."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container create-decision-page">

      {/* Header */}
      <div className="create-decision-header">

        <div>
          <div className="page-eyebrow">
            DECISION MANAGEMENT
          </div>

          <h1>Create Decision</h1>

          <p>
            Document a business decision, explain the problem,
            and provide the reasoning behind it.
          </p>
        </div>

      </div>

      {/* Messages */}
      {error && (
        <div className="form-alert form-alert-error">
          <span className="alert-icon">!</span>

          <div>
            <strong>Unable to create decision</strong>
            <p>{error}</p>
          </div>
        </div>
      )}

      {success && (
        <div className="form-alert form-alert-success">
          <span className="alert-icon">✓</span>

          <div>
            <strong>Decision created successfully</strong>
            <p>Redirecting to your decisions...</p>
          </div>
        </div>
      )}

      {/* Form */}
      <form
        onSubmit={handleSubmit}
        className="professional-decision-form"
      >

        {/* Basic Information */}
        <div className="form-section">

          <div className="form-section-header">

            <div className="form-section-number">
              01
            </div>

            <div>
              <h2>Decision Information</h2>

              <p>
                Provide the basic information about the decision.
              </p>
            </div>

          </div>

          <div className="form-fields">

            <div className="form-group full-width">

              <label htmlFor="title">
                Decision Title
                <span className="required">*</span>
              </label>

              <input
                id="title"
                name="title"
                type="text"
                value={formData.title}
                onChange={handleChange}
                placeholder="e.g. Move application database to PostgreSQL"
                disabled={loading}
              />

              <small>
                Give your decision a clear and meaningful title.
              </small>

            </div>

            <div className="form-group">

              <label htmlFor="category">
                Category
                <span className="required">*</span>
              </label>

              <input
                id="category"
                name="category"
                type="text"
                value={formData.category}
                onChange={handleChange}
                placeholder="e.g. Technology"
                disabled={loading}
              />

              <small>
                Categorize the decision for easier searching.
              </small>

            </div>

          </div>

        </div>

        {/* Problem Statement */}
        <div className="form-section">

          <div className="form-section-header">

            <div className="form-section-number">
              02
            </div>

            <div>
              <h2>Problem Statement</h2>

              <p>
                Describe the situation or problem that requires
                a decision.
              </p>
            </div>

          </div>

          <div className="form-group full-width">

            <label htmlFor="problem_statement">
              Problem Statement
              <span className="required">*</span>
            </label>

            <textarea
              id="problem_statement"
              name="problem_statement"
              value={formData.problem_statement}
              onChange={handleChange}
              placeholder="Describe the problem, situation, or opportunity that led to this decision..."
              rows="6"
              disabled={loading}
            />

            <small>
              Include enough context so another person can
              understand the problem later.
            </small>

          </div>

        </div>

        {/* Rationale */}
        <div className="form-section">

          <div className="form-section-header">

            <div className="form-section-number">
              03
            </div>

            <div>
              <h2>Decision Rationale</h2>

              <p>
                Explain why this decision was made.
              </p>
            </div>

          </div>

          <div className="form-group full-width">

            <label htmlFor="rationale">
              Rationale
            </label>

            <textarea
              id="rationale"
              name="rationale"
              value={formData.rationale}
              onChange={handleChange}
              placeholder="Explain the reasoning, evidence, assumptions, or factors behind this decision..."
              rows="6"
              disabled={loading}
            />

            <small>
              A clear rationale helps reviewers understand the
              thinking behind the decision.
            </small>

          </div>

        </div>

        {/* Actions */}
        <div className="form-actions">

          <button
            type="button"
            className="professional-secondary-button"
            onClick={() => navigate("/decisions")}
            disabled={loading}
          >
            Cancel
          </button>

          <button
            type="submit"
            className="professional-primary-button"
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="button-spinner"></span>
                Creating...
              </>
            ) : (
              <>
                Create Decision
                <span>→</span>
              </>
            )}
          </button>

        </div>

      </form>

    </div>
  );
}

export default CreateDecision;