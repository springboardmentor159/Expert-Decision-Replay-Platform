import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { createDecision } from "../api/decisionApi";

function CreateDecision() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    title: "",
    problem_statement: "",
    rationale: "",
    category: "",
  });

  const [errors, setErrors] = useState({});
  const [serverError, setServerError] = useState("");
  const [loading, setLoading] = useState(false);

  function handleChange(event) {
    const { name, value } = event.target;

    setFormData((current) => ({
      ...current,
      [name]: value,
    }));

    setErrors((current) => ({
      ...current,
      [name]: "",
    }));

    setServerError("");
  }

  function validateForm() {
    const newErrors = {};

    if (!formData.title.trim()) {
      newErrors.title = "Decision title is required.";
    } else if (formData.title.trim().length < 1) {
      newErrors.title =
        "Decision title must contain at least 1 character.";
    }

    if (!formData.problem_statement.trim()) {
      newErrors.problem_statement =
        "Problem statement is required.";
    }

    if (!formData.category.trim()) {
      newErrors.category =
        "Decision category is required.";
    }

    setErrors(newErrors);

    return Object.keys(newErrors).length === 0;
  }

  async function handleSubmit(event) {
    event.preventDefault();

    setServerError("");

    if (!validateForm()) {
      return;
    }

    try {
      setLoading(true);

      const payload = {
        title: formData.title.trim(),
        problem_statement:
          formData.problem_statement.trim(),
        rationale: formData.rationale.trim() || null,
        category: formData.category.trim(),
      };

      const response = await createDecision(payload);

      const createdDecision = response?.decision;

      if (!createdDecision?.id) {
        throw new Error(
          "The server did not return the created decision."
        );
      }

      navigate(
        `/decisions/${createdDecision.id}`
      );
    } catch (err) {
      console.error(
        "Failed to create decision:",
        err
      );

      if (err.response?.status === 401) {
        setServerError(
          "Your session has expired. Please log in again."
        );
      } else if (err.response?.status === 403) {
        setServerError(
          "You do not have permission to create a decision."
        );
      } else if (err.response?.status === 422) {
        const detail = err.response?.data?.detail;

        if (Array.isArray(detail)) {
          setServerError(
            detail
              .map((item) => item.msg)
              .join(" ")
          );
        } else {
          setServerError(
            detail ||
              "Please check the information you entered."
          );
        }
      } else if (err.response?.status === 400) {
        setServerError(
          err.response?.data?.detail ||
            "The decision could not be created."
        );
      } else if (err.response?.status >= 500) {
        setServerError(
          "The server encountered an error. Please try again."
        );
      } else {
        setServerError(
          "Unable to create the decision. Please try again."
        );
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page-container">

      {/* =====================================================
          PAGE HEADER
      ===================================================== */}

      <div className="page-header">

        <div>
          <Link
            to="/decisions"
            className="back-link"
          >
            ← Back to Decisions
          </Link>

          <h1>Create Decision</h1>

          <p>
            Record a new organizational decision.
          </p>
        </div>

      </div>


      {/* =====================================================
          FORM
      ===================================================== */}

      <div className="card">

        <form onSubmit={handleSubmit}>

          {/* TITLE */}

          <div className="form-group">

            <label htmlFor="title">
              Decision Title *
            </label>

            <input
              id="title"
              name="title"
              type="text"
              placeholder="Enter the decision title"
              value={formData.title}
              onChange={handleChange}
              disabled={loading}
              autoComplete="off"
            />

            {errors.title && (
              <div className="field-error">
                {errors.title}
              </div>
            )}

          </div>


          {/* CATEGORY */}

          <div className="form-group">

            <label htmlFor="category">
              Category *
            </label>

            <input
              id="category"
              name="category"
              type="text"
              placeholder="e.g. Technology, Infrastructure, Finance"
              value={formData.category}
              onChange={handleChange}
              disabled={loading}
              autoComplete="off"
            />

            {errors.category && (
              <div className="field-error">
                {errors.category}
              </div>
            )}

          </div>


          {/* PROBLEM STATEMENT */}

          <div className="form-group">

            <label htmlFor="problem_statement">
              Problem Statement *
            </label>

            <textarea
              id="problem_statement"
              name="problem_statement"
              rows="7"
              placeholder="Describe the problem or situation that requires a decision..."
              value={formData.problem_statement}
              onChange={handleChange}
              disabled={loading}
            />

            {errors.problem_statement && (
              <div className="field-error">
                {errors.problem_statement}
              </div>
            )}

          </div>


          {/* RATIONALE */}

          <div className="form-group">

            <label htmlFor="rationale">
              Rationale
            </label>

            <textarea
              id="rationale"
              name="rationale"
              rows="7"
              placeholder="Explain the reasoning behind the decision. This field is optional."
              value={formData.rationale}
              onChange={handleChange}
              disabled={loading}
            />

          </div>


          {/* SERVER ERROR */}

          {serverError && (
            <div className="error-state form-error">

              <h3>
                Unable to Create Decision
              </h3>

              <p>
                {serverError}
              </p>

            </div>
          )}


          {/* FORM ACTIONS */}

          <div className="form-actions">

            <Link
              to="/decisions"
              className="secondary-button"
            >
              Cancel
            </Link>

            <button
              type="submit"
              className="primary-button"
              disabled={loading}
            >
              {loading
                ? "Creating..."
                : "Create Decision"}
            </button>

          </div>

        </form>

      </div>

    </div>
  );
}

export default CreateDecision;