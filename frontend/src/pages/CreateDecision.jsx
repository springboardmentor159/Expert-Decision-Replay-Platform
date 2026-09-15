import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

function CreateDecision() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    title: "",
    problem_statement: "",
    category: "",
  });

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setMessage("");
    setError("");
    setSaving(true);

    try {
      await api.post("/decisions", form);

      setMessage("Decision created successfully!");

      setTimeout(() => {
        navigate("/decisions");
      }, 1000);
    } catch (err) {
      console.error("Create decision error:", err);

      if (err.response?.status === 401) {
        setError("Please login again.");
      } else if (err.response?.status === 403) {
        setError("You don't have permission to create a decision.");
      } else {
        setError("Failed to create decision. Please try again.");
      }
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="create-decision-page">

      {/* Page Header */}
      <div className="create-page-header">
        <div>
          <div className="page-breadcrumb">
            Decisions / Create Decision
          </div>

          <h1>Create New Decision</h1>

          <p>
            Record a business decision and capture the problem that needs to
            be addressed.
          </p>
        </div>

        <button
          className="secondary-page-button"
          onClick={() => navigate("/decisions")}
        >
          ← Back to Decisions
        </button>
      </div>

      {/* Main Form Card */}
      <div className="create-decision-layout">

        <div className="create-form-card">

          <div className="form-card-header">
            <div className="form-header-icon">+</div>

            <div>
              <h2>Decision Information</h2>
              <p>
                Provide the basic information for this decision.
              </p>
            </div>
          </div>

          <form onSubmit={handleSubmit}>

            {/* Title */}
            <div className="form-field">
              <label htmlFor="title">
                Decision Title <span>*</span>
              </label>

              <input
                id="title"
                type="text"
                name="title"
                value={form.title}
                onChange={handleChange}
                placeholder="Enter a clear decision title"
                required
              />

              <small>
                Use a short and descriptive title.
              </small>
            </div>

            {/* Problem Statement */}
            <div className="form-field">
              <label htmlFor="problem_statement">
                Problem Statement <span>*</span>
              </label>

              <textarea
                id="problem_statement"
                name="problem_statement"
                value={form.problem_statement}
                onChange={handleChange}
                placeholder="Describe the problem or situation that requires a decision..."
                rows="7"
                required
              />

              <small>
                Clearly explain the problem, requirement, or situation.
              </small>
            </div>

            {/* Category */}
            <div className="form-field">
              <label htmlFor="category">
                Category <span>*</span>
              </label>

              <input
                id="category"
                type="text"
                name="category"
                value={form.category}
                onChange={handleChange}
                placeholder="Example: Technology, Finance, Operations"
                required
              />

              <small>
                Enter the category that best describes this decision.
              </small>
            </div>

            {/* Messages */}
            {message && (
              <div className="success-message">
                ✓ {message}
              </div>
            )}

            {error && (
              <div className="error-message">
                ⚠ {error}
              </div>
            )}

            {/* Actions */}
            <div className="form-actions">
              <button
                type="button"
                className="cancel-button"
                onClick={() => navigate("/decisions")}
              >
                Cancel
              </button>

              <button
                type="submit"
                className="primary-submit-button"
                disabled={saving}
              >
                {saving ? "Creating..." : "Create Decision →"}
              </button>
            </div>

          </form>
        </div>

        {/* Information Panel */}
        <div className="decision-info-card">

          <div className="info-icon">i</div>

          <h3>About Decision Replay</h3>

          <p>
            This platform helps capture important decisions so they can be
            reviewed, discussed, approved, and replayed later.
          </p>

          <div className="info-divider"></div>

          <h4>What happens next?</h4>

          <div className="process-step">
            <div className="step-number">1</div>
            <div>
              <strong>Create Decision</strong>
              <span>Record the problem and basic details.</span>
            </div>
          </div>

          <div className="process-step">
            <div className="step-number">2</div>
            <div>
              <strong>Add Alternatives</strong>
              <span>Compare possible solutions.</span>
            </div>
          </div>

          <div className="process-step">
            <div className="step-number">3</div>
            <div>
              <strong>Discuss & Review</strong>
              <span>Collaborate with other team members.</span>
            </div>
          </div>

          <div className="process-step">
            <div className="step-number">4</div>
            <div>
              <strong>Approval</strong>
              <span>Submit the decision through the approval workflow.</span>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}

export default CreateDecision;