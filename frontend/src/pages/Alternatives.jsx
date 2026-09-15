import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../services/api";

function Alternatives() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [alternatives, setAlternatives] = useState([]);

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [pros, setPros] = useState("");
  const [cons, setCons] = useState("");
  const [estimatedCost, setEstimatedCost] = useState("");
  const [feasibilityScore, setFeasibilityScore] = useState("");
  const [riskLevel, setRiskLevel] = useState("");

  const [editingId, setEditingId] = useState(null);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const fetchAlternatives = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await api.get(`/decisions/${id}/alternatives`);
      setAlternatives(response.data);
    } catch (err) {
      console.error("Alternatives error:", err);
      setError("Unable to load alternatives.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlternatives();
  }, [id]);

  const clearForm = () => {
    setName("");
    setDescription("");
    setPros("");
    setCons("");
    setEstimatedCost("");
    setFeasibilityScore("");
    setRiskLevel("");
    setEditingId(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError("");
    setMessage("");

    if (!name.trim()) {
      setError("Alternative name is required.");
      return;
    }

    if (
      feasibilityScore !== "" &&
      (Number(feasibilityScore) < 1 ||
        Number(feasibilityScore) > 5)
    ) {
      setError("Feasibility score must be between 1 and 5.");
      return;
    }

    setSaving(true);

    const data = {
      name: name,
      description: description,
      pros: pros,
      cons: cons,
      estimated_cost:
        estimatedCost === "" ? null : Number(estimatedCost),
      feasibility_score:
        feasibilityScore === "" ? null : Number(feasibilityScore),
      risk_level: riskLevel,
    };

    try {
      if (editingId) {
        const response = await api.put(
          `/alternatives/${editingId}`,
          data
        );

        setAlternatives((current) =>
          current.map((alternative) =>
            alternative.id === editingId
              ? response.data
              : alternative
          )
        );

        setMessage("Alternative updated successfully.");
      } else {
        const response = await api.post(
          `/decisions/${id}/alternatives`,
          data
        );

        setAlternatives((current) => [
          ...current,
          response.data,
        ]);

        setMessage("Alternative added successfully.");
      }

      clearForm();
    } catch (err) {
      console.error("Alternative save error:", err);

      if (err.response?.data?.detail) {
        setError(
          typeof err.response.data.detail === "string"
            ? err.response.data.detail
            : "Unable to save alternative."
        );
      } else {
        setError("Unable to save alternative.");
      }
    } finally {
      setSaving(false);
    }
  };

  const handleEdit = (alternative) => {
    setEditingId(alternative.id);

    setName(alternative.name || "");
    setDescription(alternative.description || "");
    setPros(alternative.pros || "");
    setCons(alternative.cons || "");
    setEstimatedCost(alternative.estimated_cost ?? "");
    setFeasibilityScore(alternative.feasibility_score ?? "");
    setRiskLevel(alternative.risk_level || "");

    setMessage("");
    setError("");

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  return (
    <div className="alternatives-page">

      {/* Header */}
      <div className="alternatives-header">
        <div>
          <div className="page-breadcrumb">
            Decisions / Alternative Analysis
          </div>

          <h1>Alternative Analysis</h1>

          <p>
            Evaluate possible solutions and identify the best option
            for Decision #{id}.
          </p>
        </div>

        <div className="alternatives-header-actions">
          <button
            className="secondary-page-button"
            onClick={() => navigate(`/decisions/${id}`)}
          >
            ← Back to Decision
          </button>

          <button
            className="primary-submit-button"
            onClick={() =>
              navigate(`/decisions/${id}/alternatives/compare`)
            }
          >
            Compare Alternatives →
          </button>
        </div>
      </div>

      {/* Summary */}
      <div className="alternative-summary">
        <div className="alternative-summary-card">
          <div className="summary-icon">↔</div>
          <div>
            <span>Total Alternatives</span>
            <strong>{alternatives.length}</strong>
          </div>
        </div>

        <div className="alternative-summary-card">
          <div className="summary-icon">★</div>
          <div>
            <span>Decision</span>
            <strong>#{id}</strong>
          </div>
        </div>

        <div className="alternative-summary-card">
          <div className="summary-icon">✓</div>
          <div>
            <span>Analysis</span>
            <strong>
              {alternatives.length > 0 ? "In Progress" : "Not Started"}
            </strong>
          </div>
        </div>
      </div>

      {/* Main Layout */}
      <div className="alternatives-layout">

        {/* Form */}
        <div className="alternative-form-card">

          <div className="alternative-card-header">
            <div className="form-header-icon">
              {editingId ? "✎" : "+"}
            </div>

            <div>
              <h2>
                {editingId
                  ? "Edit Alternative"
                  : "Add Alternative"}
              </h2>

              <p>
                {editingId
                  ? "Update the selected alternative."
                  : "Add a possible solution to this decision."}
              </p>
            </div>
          </div>

          <form onSubmit={handleSubmit}>

            <div className="alternative-form-grid">

              <div className="alternative-field full-field">
                <label>
                  Alternative Name <span>*</span>
                </label>

                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Example: Implement cloud-based solution"
                />
              </div>

              <div className="alternative-field full-field">
                <label>Description</label>

                <textarea
                  rows="4"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Describe how this alternative would solve the problem..."
                />
              </div>

              <div className="alternative-field">
                <label>Pros</label>

                <textarea
                  rows="4"
                  value={pros}
                  onChange={(e) => setPros(e.target.value)}
                  placeholder="Advantages of this option"
                />
              </div>

              <div className="alternative-field">
                <label>Cons</label>

                <textarea
                  rows="4"
                  value={cons}
                  onChange={(e) => setCons(e.target.value)}
                  placeholder="Disadvantages or limitations"
                />
              </div>

              <div className="alternative-field">
                <label>Estimated Cost</label>

                <input
                  type="number"
                  min="0"
                  value={estimatedCost}
                  onChange={(e) =>
                    setEstimatedCost(e.target.value)
                  }
                  placeholder="Enter cost"
                />
              </div>

              <div className="alternative-field">
                <label>Feasibility Score</label>

                <select
                  value={feasibilityScore}
                  onChange={(e) =>
                    setFeasibilityScore(e.target.value)
                  }
                >
                  <option value="">Select score</option>
                  <option value="1">1 - Very Low</option>
                  <option value="2">2 - Low</option>
                  <option value="3">3 - Moderate</option>
                  <option value="4">4 - High</option>
                  <option value="5">5 - Very High</option>
                </select>
              </div>

              <div className="alternative-field">
                <label>Risk Level</label>

                <select
                  value={riskLevel}
                  onChange={(e) =>
                    setRiskLevel(e.target.value)
                  }
                >
                  <option value="">Select risk level</option>
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                  <option value="Critical">Critical</option>
                </select>
              </div>

            </div>

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

            <div className="alternative-form-actions">

              {editingId && (
                <button
                  type="button"
                  className="cancel-button"
                  onClick={clearForm}
                >
                  Cancel Edit
                </button>
              )}

              <button
                type="submit"
                className="primary-submit-button"
                disabled={saving}
              >
                {saving
                  ? "Saving..."
                  : editingId
                  ? "Update Alternative"
                  : "Add Alternative"}
              </button>

            </div>

          </form>
        </div>
      </div>

      {/* Existing Alternatives */}
      <div className="alternatives-list-card">

        <div className="alternatives-list-header">
          <div>
            <h2>Existing Alternatives</h2>
            <p>
              Review and manage the available options for this decision.
            </p>
          </div>

          <span className="alternative-count">
            {alternatives.length} option
            {alternatives.length !== 1 ? "s" : ""}
          </span>
        </div>

        {loading ? (
          <div className="page-loading">
            <div className="loading-spinner"></div>
            <p>Loading alternatives...</p>
          </div>
        ) : alternatives.length === 0 ? (
          <div className="alternatives-empty">
            <div className="empty-icon">↔</div>
            <h3>No Alternatives Yet</h3>
            <p>
              Add the first possible solution using the form above.
            </p>
          </div>
        ) : (
          <div className="alternative-cards">

            {alternatives.map((alternative) => (
              <div
                className="alternative-item-card"
                key={alternative.id}
              >

                <div className="alternative-item-top">

                  <div className="alternative-title-area">
                    <div className="alternative-number">
                      {alternative.id}
                    </div>

                    <div>
                      <h3>{alternative.name}</h3>

                      <span>
                        Alternative #{alternative.id}
                      </span>
                    </div>
                  </div>

                  <button
                    className="edit-alternative-button"
                    onClick={() => handleEdit(alternative)}
                  >
                    ✎ Edit
                  </button>

                </div>

                <p className="alternative-description">
                  {alternative.description || "No description provided."}
                </p>

                <div className="alternative-details-grid">

                  <div className="alternative-detail-box">
                    <span>Pros</span>
                    <p>{alternative.pros || "—"}</p>
                  </div>

                  <div className="alternative-detail-box">
                    <span>Cons</span>
                    <p>{alternative.cons || "—"}</p>
                  </div>

                  <div className="alternative-detail-box">
                    <span>Estimated Cost</span>
                    <strong>
                      {alternative.estimated_cost ?? "—"}
                    </strong>
                  </div>

                  <div className="alternative-detail-box">
                    <span>Feasibility</span>
                    <strong>
                      {alternative.feasibility_score
                        ? `${alternative.feasibility_score}/5`
                        : "—"}
                    </strong>
                  </div>

                  <div className="alternative-detail-box">
                    <span>Risk Level</span>

                    <strong
                      className={`risk-label ${
                        alternative.risk_level
                          ? alternative.risk_level.toLowerCase()
                          : ""
                      }`}
                    >
                      {alternative.risk_level || "—"}
                    </strong>
                  </div>

                </div>
              </div>
            ))}

          </div>
        )}

      </div>

      {/* Bottom Actions */}
      <div className="alternatives-bottom-actions">

        <button
          className="secondary-page-button"
          onClick={() => navigate(`/decisions/${id}`)}
        >
          ← Back to Decision
        </button>

        <button
          className="primary-submit-button"
          onClick={() =>
            navigate(`/decisions/${id}/alternatives/compare`)
          }
        >
          Compare Alternatives →
        </button>

      </div>

    </div>
  );
}

export default Alternatives;