import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import {
  getDecision,
  updateDecision,
  deleteDecision,
} from "../api/decisionApi";

function EditDecision() {
  const { decisionId } = useParams();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    title: "",
    problem_statement: "",
    rationale: "",
    category: "",
    status: "Draft",
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [fieldErrors, setFieldErrors] = useState({});

  const [showDeleteConfirmation, setShowDeleteConfirmation] =
    useState(false);

  // =====================================================
  // LOAD DECISION
  // =====================================================

  useEffect(() => {
    loadDecision();
  }, [decisionId]);

  async function loadDecision() {
    try {
      setLoading(true);
      setError("");

      const data = await getDecision(decisionId);

      setFormData({
        title: data.title || "",
        problem_statement: data.problem_statement || "",
        rationale: data.rationale || "",
        category: data.category || "",
        status: data.status || "Draft",
      });
    } catch (err) {
      console.error("Failed to load decision:", err);

      if (err.response?.status === 401) {
        setError(
          "Your session has expired. Please log in again."
        );
      } else if (err.response?.status === 403) {
        setError(
          "You do not have permission to edit this decision."
        );
      } else if (err.response?.status === 404) {
        setError("Decision not found.");
      } else if (err.response?.status >= 500) {
        setError(
          "The server encountered an error. Please try again."
        );
      } else {
        setError(
          "Unable to load the decision. Please try again."
        );
      }
    } finally {
      setLoading(false);
    }
  }

  // =====================================================
  // HANDLE INPUT
  // =====================================================

  function handleChange(event) {
    const { name, value } = event.target;

    setFormData((current) => ({
      ...current,
      [name]: value,
    }));

    setFieldErrors((current) => ({
      ...current,
      [name]: "",
    }));

    setError("");
    setSuccess("");
  }

  // =====================================================
  // VALIDATE
  // =====================================================

  function validateForm() {
    const errors = {};

    if (!formData.title.trim()) {
      errors.title = "Decision title is required.";
    }

    if (!formData.problem_statement.trim()) {
      errors.problem_statement =
        "Problem statement is required.";
    }

    if (!formData.category.trim()) {
      errors.category =
        "Decision category is required.";
    }

    setFieldErrors(errors);

    return Object.keys(errors).length === 0;
  }

  // =====================================================
  // UPDATE DECISION
  // =====================================================

  async function handleSubmit(event) {
    event.preventDefault();

    setError("");
    setSuccess("");

    if (!validateForm()) {
      return;
    }

    try {
      setSaving(true);

      const payload = {
        title: formData.title.trim(),
        problem_statement:
          formData.problem_statement.trim(),
        rationale:
          formData.rationale.trim() || null,
        category: formData.category.trim(),
        status: formData.status,
      };

      await updateDecision(
        decisionId,
        payload
      );

      setSuccess(
        "Decision updated successfully."
      );

      // Give the user a moment to see the success message.
      setTimeout(() => {
        navigate(`/decisions/${decisionId}`);
      }, 700);
    } catch (err) {
      console.error(
        "Failed to update decision:",
        err
      );

      if (err.response?.status === 401) {
        setError(
          "Your session has expired. Please log in again."
        );
      } else if (err.response?.status === 403) {
        setError(
          "You do not have permission to update this decision."
        );
      } else if (err.response?.status === 404) {
        setError("Decision not found.");
      } else if (err.response?.status === 422) {
        const detail = err.response?.data?.detail;

        if (Array.isArray(detail)) {
          setError(
            detail
              .map((item) => item.msg)
              .join(" ")
          );
        } else {
          setError(
            detail ||
              "Please check the information you entered."
          );
        }
      } else if (err.response?.status === 400) {
        setError(
          err.response?.data?.detail ||
            "The decision could not be updated."
        );
      } else if (err.response?.status >= 500) {
        setError(
          "The server encountered an error. Please try again."
        );
      } else {
        setError(
          "Unable to update the decision. Please try again."
        );
      }
    } finally {
      setSaving(false);
    }
  }

  // =====================================================
  // DELETE DECISION
  // =====================================================

  async function handleDelete() {
    try {
      setDeleting(true);
      setError("");

      await deleteDecision(decisionId);

      navigate("/decisions");
    } catch (err) {
      console.error(
        "Failed to delete decision:",
        err
      );

      setDeleting(false);

      if (err.response?.status === 401) {
        setError(
          "Your session has expired. Please log in again."
        );
      } else if (err.response?.status === 403) {
        setError(
          "You do not have permission to delete this decision."
        );
      } else if (err.response?.status === 404) {
        setError("Decision not found.");
      } else if (err.response?.status >= 500) {
        setError(
          "The server encountered an error. Please try again."
        );
      } else {
        setError(
          err.response?.data?.detail ||
            "Unable to delete the decision."
        );
      }
    }
  }

  // =====================================================
  // LOADING
  // =====================================================

  if (loading) {
    return (
      <div className="loading-state">
        Loading decision...
      </div>
    );
  }

  // =====================================================
  // ERROR WITHOUT DATA
  // =====================================================

  if (error && !formData.title) {
    return (
      <div className="error-state">

        <h2>
          Unable to Load Decision
        </h2>

        <p>{error}</p>

        <div className="form-actions">

          <button
            type="button"
            className="primary-button"
            onClick={loadDecision}
          >
            Try Again
          </button>

          <Link
            to="/decisions"
            className="secondary-button"
          >
            ← Back to Decisions
          </Link>

        </div>

      </div>
    );
  }

  // =====================================================
  // PAGE
  // =====================================================

  return (
    <div className="page-container">

      {/* =================================================
          HEADER
      ================================================= */}

      <div className="page-header">

        <div>

          <Link
            to={`/decisions/${decisionId}`}
            className="back-link"
          >
            ← Back to Decision
          </Link>

          <h1>
            Edit Decision
          </h1>

          <p>
            Update the information for Decision #
            {decisionId}.
          </p>

        </div>

      </div>


      {/* =================================================
          SUCCESS MESSAGE
      ================================================= */}

      {success && (
        <div className="success-state">
          {success}
        </div>
      )}


      {/* =================================================
          SERVER ERROR
      ================================================= */}

      {error && (
        <div className="error-state form-error">

          <h3>
            Unable to Update Decision
          </h3>

          <p>{error}</p>

        </div>
      )}


      {/* =================================================
          EDIT FORM
      ================================================= */}

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
              value={formData.title}
              onChange={handleChange}
              disabled={saving || deleting}
              autoComplete="off"
            />

            {fieldErrors.title && (
              <div className="field-error">
                {fieldErrors.title}
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
              value={formData.category}
              onChange={handleChange}
              disabled={saving || deleting}
              autoComplete="off"
            />

            {fieldErrors.category && (
              <div className="field-error">
                {fieldErrors.category}
              </div>
            )}

          </div>


          {/* STATUS */}

          <div className="form-group">

            <label htmlFor="status">
              Status
            </label>

            <select
              id="status"
              name="status"
              value={formData.status}
              onChange={handleChange}
              disabled={saving || deleting}
            >
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

            <small>
              Status changes are recorded in the
              decision version and audit history.
            </small>

          </div>


          {/* PROBLEM STATEMENT */}

          <div className="form-group">

            <label htmlFor="problem_statement">
              Problem Statement *
            </label>

            <textarea
              id="problem_statement"
              name="problem_statement"
              rows="8"
              value={formData.problem_statement}
              onChange={handleChange}
              disabled={saving || deleting}
            />

            {fieldErrors.problem_statement && (
              <div className="field-error">
                {fieldErrors.problem_statement}
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
              rows="8"
              value={formData.rationale}
              onChange={handleChange}
              disabled={saving || deleting}
            />

          </div>


          {/* ACTIONS */}

          <div className="form-actions">

            <Link
              to={`/decisions/${decisionId}`}
              className="secondary-button"
            >
              Cancel
            </Link>

            <button
              type="submit"
              className="primary-button"
              disabled={saving || deleting}
            >
              {saving
                ? "Saving..."
                : "Save Changes"}
            </button>

          </div>

        </form>

      </div>


      {/* =================================================
          DELETE SECTION
      ================================================= */}

      <div className="card danger-card">

        <h2>
          Delete Decision
        </h2>

        <p>
          Deleting a decision permanently removes it
          from the decision database. This action
          cannot be undone.
        </p>

        {!showDeleteConfirmation ? (
          <button
            type="button"
            className="danger-button"
            onClick={() =>
              setShowDeleteConfirmation(true)
            }
            disabled={saving || deleting}
          >
            Delete Decision
          </button>
        ) : (
          <div className="delete-confirmation">

            <strong>
              Are you sure you want to delete
              Decision #{decisionId}?
            </strong>

            <p>
              This will permanently delete:
            </p>

            <ul>
              <li>
                The decision
              </li>

              <li>
                Its versions
              </li>

              <li>
                Related decision data
              </li>
            </ul>

            <div className="form-actions">

              <button
                type="button"
                className="secondary-button"
                onClick={() =>
                  setShowDeleteConfirmation(false)
                }
                disabled={deleting}
              >
                Cancel
              </button>

              <button
                type="button"
                className="danger-button"
                onClick={handleDelete}
                disabled={deleting}
              >
                {deleting
                  ? "Deleting..."
                  : "Yes, Delete Decision"}
              </button>

            </div>

          </div>
        )}

      </div>

    </div>
  );
}

export default EditDecision;