import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../services/api";

function EditDecision() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    title: "",
    problem_statement: "",
    category: "",
    rationale: "",
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // Load existing decision
  useEffect(() => {
    const fetchDecision = async () => {
      try {
        setLoading(true);
        setError("");

        const response = await api.get(`/decisions/${id}`);

        const decision = response.data;

        setFormData({
          title: decision.title || "",
          problem_statement: decision.problem_statement || "",
          category: decision.category || "",
          rationale: decision.rationale || "",
        });
      } catch (error) {
        console.error("Failed to load decision:", error);

        if (error.response?.status === 404) {
          setError("Decision not found.");
        } else if (error.response?.status === 401) {
          setError("Your session has expired. Please login again.");
        } else if (error.response?.status === 403) {
          setError("You are not authorized to edit this decision.");
        } else {
          setError("Unable to load decision.");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchDecision();
  }, [id]);

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
      setError("Title is required.");
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
      setSaving(true);

      await api.put(`/decisions/${id}`, {
        title: formData.title.trim(),
        problem_statement: formData.problem_statement.trim(),
        category: formData.category.trim(),
        rationale: formData.rationale.trim(),
      });

      setSuccess("Decision updated successfully.");

      // Go back to decision details after successful update
      setTimeout(() => {
        navigate(`/decisions/${id}`);
      }, 800);
    } catch (error) {
      console.error("Failed to update decision:", error);

      if (error.response?.status === 400) {
        setError(
          error.response?.data?.detail ||
            "Invalid decision information."
        );
      } else if (error.response?.status === 401) {
        setError("Your session has expired. Please login again.");
      } else if (error.response?.status === 403) {
        setError("You are not authorized to edit this decision.");
      } else if (error.response?.status === 404) {
        setError("Decision not found.");
      } else if (error.response?.status === 422) {
        setError("Please check the entered information.");
      } else if (error.response?.status >= 500) {
        setError("Server error. Please try again later.");
      } else {
        setError("Unable to update decision.");
      }
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="page-container">
        <h1>Edit Decision</h1>
        <p>Loading decision...</p>
      </div>
    );
  }

  if (error && !formData.title) {
    return (
      <div className="page-container">
        <h1>Edit Decision</h1>

        <div className="error-message">
          {error}
        </div>

        <button onClick={() => navigate("/decisions")}>
          ← Back to My Decisions
        </button>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1>Edit Decision</h1>
          <p>Decision #{id}</p>
        </div>

        <button
          type="button"
          onClick={() => navigate(`/decisions/${id}`)}
        >
          ← Cancel
        </button>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {success && (
        <div className="success-message">
          {success}
        </div>
      )}

      <form onSubmit={handleSubmit} className="decision-form">
        <div className="form-group">
          <label htmlFor="title">
            Title *
          </label>

          <input
            id="title"
            name="title"
            type="text"
            value={formData.title}
            onChange={handleChange}
            placeholder="Enter decision title"
          />
        </div>

        <div className="form-group">
          <label htmlFor="category">
            Category *
          </label>

          <input
            id="category"
            name="category"
            type="text"
            value={formData.category}
            onChange={handleChange}
            placeholder="Enter category"
          />
        </div>

        <div className="form-group">
          <label htmlFor="problem_statement">
            Problem Statement *
          </label>

          <textarea
            id="problem_statement"
            name="problem_statement"
            value={formData.problem_statement}
            onChange={handleChange}
            placeholder="Describe the problem"
            rows="6"
          />
        </div>

        <div className="form-group">
          <label htmlFor="rationale">
            Rationale
          </label>

          <textarea
            id="rationale"
            name="rationale"
            value={formData.rationale}
            onChange={handleChange}
            placeholder="Enter the rationale"
            rows="6"
          />
        </div>

        <div className="form-actions">
          <button
            type="button"
            onClick={() => navigate(`/decisions/${id}`)}
            disabled={saving}
          >
            Cancel
          </button>

          <button
            type="submit"
            disabled={saving}
          >
            {saving ? "Saving..." : "Save Changes"}
          </button>
        </div>
      </form>
    </div>
  );
}

export default EditDecision;