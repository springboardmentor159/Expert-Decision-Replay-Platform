import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import {
  getAlternative,
  updateAlternative,
} from "../api/alternativeApi";

const RISK_LEVELS = [
  "Low",
  "Medium",
  "High",
  "Critical",
];

function EditAlternative() {
  const {
    alternativeId,
  } = useParams();

  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    name: "",
    description: "",
    pros: "",
    cons: "",
    estimated_cost: "",
    feasibility_score: "3",
    risk_level: "Medium",
  });

  const [decisionId, setDecisionId] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [saving, setSaving] =
    useState(false);

  const [errors, setErrors] =
    useState({});

  const [serverError, setServerError] =
    useState("");

  useEffect(() => {
    loadAlternative();
  }, [alternativeId]);

  async function loadAlternative() {
    try {
      setLoading(true);
      setServerError("");

      const data =
        await getAlternative(
          alternativeId
        );

      setDecisionId(data.decision_id);

      setFormData({
        name: data.name || "",
        description:
          data.description || "",
        pros: data.pros || "",
        cons: data.cons || "",
        estimated_cost:
          data.estimated_cost ?? "",
        feasibility_score:
          String(
            data.feasibility_score ?? 3
          ),
        risk_level:
          data.risk_level || "Medium",
      });
    } catch (err) {
      console.error(
        "Failed to load alternative:",
        err
      );

      if (err.response?.status === 401) {
        setServerError(
          "Your session has expired. Please log in again."
        );
      } else if (err.response?.status === 403) {
        setServerError(
          "You do not have permission to edit this alternative."
        );
      } else if (err.response?.status === 404) {
        setServerError(
          "Alternative not found."
        );
      } else {
        setServerError(
          "Unable to load the alternative."
        );
      }
    } finally {
      setLoading(false);
    }
  }

  function handleChange(event) {
    const {
      name,
      value,
    } = event.target;

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

    if (!formData.name.trim()) {
      newErrors.name =
        "Alternative name is required.";
    }

    if (!formData.description.trim()) {
      newErrors.description =
        "Description is required.";
    }

    if (!formData.pros.trim()) {
      newErrors.pros =
        "Pros are required.";
    }

    if (!formData.cons.trim()) {
      newErrors.cons =
        "Cons are required.";
    }

    if (
      formData.estimated_cost === "" ||
      Number.isNaN(
        Number(formData.estimated_cost)
      )
    ) {
      newErrors.estimated_cost =
        "Estimated cost must be a valid number.";
    } else if (
      Number(formData.estimated_cost) < 0
    ) {
      newErrors.estimated_cost =
        "Estimated cost cannot be negative.";
    }

    const feasibility =
      Number(
        formData.feasibility_score
      );

    if (
      !Number.isInteger(feasibility) ||
      feasibility < 1 ||
      feasibility > 5
    ) {
      newErrors.feasibility_score =
        "Feasibility score must be between 1 and 5.";
    }

    if (
      !RISK_LEVELS.includes(
        formData.risk_level
      )
    ) {
      newErrors.risk_level =
        "Please select a valid risk level.";
    }

    setErrors(newErrors);

    return (
      Object.keys(newErrors).length === 0
    );
  }

  async function handleSubmit(event) {
    event.preventDefault();

    setServerError("");

    if (!validateForm()) {
      return;
    }

    try {
      setSaving(true);

      const payload = {
        name: formData.name.trim(),
        description:
          formData.description.trim(),
        pros: formData.pros.trim(),
        cons: formData.cons.trim(),
        estimated_cost:
          Number(formData.estimated_cost),
        feasibility_score:
          Number(
            formData.feasibility_score
          ),
        risk_level:
          formData.risk_level,
      };

      await updateAlternative(
        alternativeId,
        payload
      );

      navigate(
        `/decisions/${decisionId}/alternatives`
      );
    } catch (err) {
      console.error(
        "Failed to update alternative:",
        err
      );

      if (err.response?.status === 401) {
        setServerError(
          "Your session has expired. Please log in again."
        );
      } else if (err.response?.status === 403) {
        setServerError(
          "You do not have permission to update this alternative."
        );
      } else if (err.response?.status === 404) {
        setServerError(
          "Alternative not found."
        );
      } else if (err.response?.status === 422) {
        const detail =
          err.response?.data?.detail;

        if (Array.isArray(detail)) {
          setServerError(
            detail
              .map((item) => item.msg)
              .join(" ")
          );
        } else {
          setServerError(
            detail ||
              "Please check the information entered."
          );
        }
      } else {
        setServerError(
          "Unable to update the alternative."
        );
      }
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="loading-state">
        Loading alternative...
      </div>
    );
  }

  if (serverError && !decisionId) {
    return (
      <div className="error-state">

        <h2>
          Unable to Load Alternative
        </h2>

        <p>
          {serverError}
        </p>

        <button
          type="button"
          className="primary-button"
          onClick={loadAlternative}
        >
          Try Again
        </button>

      </div>
    );
  }

  return (
    <div className="page-container">

      <div className="page-header">

        <div>

          <Link
            to={`/decisions/${decisionId}/alternatives`}
            className="back-link"
          >
            ← Back to Alternatives
          </Link>

          <h1>
            Edit Alternative
          </h1>

          <p>
            Alternative #{alternativeId}
          </p>

        </div>

      </div>


      {serverError && (
        <div className="error-state">

          <h3>
            Unable to Update Alternative
          </h3>

          <p>
            {serverError}
          </p>

        </div>
      )}


      <div className="card">

        <form onSubmit={handleSubmit}>

          {/* NAME */}

          <div className="form-group">

            <label htmlFor="name">
              Alternative Name *
            </label>

            <input
              id="name"
              name="name"
              type="text"
              value={formData.name}
              onChange={handleChange}
              disabled={saving}
            />

            {errors.name && (
              <div className="field-error">
                {errors.name}
              </div>
            )}

          </div>


          {/* DESCRIPTION */}

          <div className="form-group">

            <label htmlFor="description">
              Description *
            </label>

            <textarea
              id="description"
              name="description"
              rows="6"
              value={
                formData.description
              }
              onChange={handleChange}
              disabled={saving}
            />

            {errors.description && (
              <div className="field-error">
                {errors.description}
              </div>
            )}

          </div>


          {/* PROS */}

          <div className="form-group">

            <label htmlFor="pros">
              Pros *
            </label>

            <textarea
              id="pros"
              name="pros"
              rows="5"
              value={formData.pros}
              onChange={handleChange}
              disabled={saving}
            />

            {errors.pros && (
              <div className="field-error">
                {errors.pros}
              </div>
            )}

          </div>


          {/* CONS */}

          <div className="form-group">

            <label htmlFor="cons">
              Cons *
            </label>

            <textarea
              id="cons"
              name="cons"
              rows="5"
              value={formData.cons}
              onChange={handleChange}
              disabled={saving}
            />

            {errors.cons && (
              <div className="field-error">
                {errors.cons}
              </div>
            )}

          </div>


          {/* COST */}

          <div className="form-group">

            <label htmlFor="estimated_cost">
              Estimated Cost *
            </label>

            <input
              id="estimated_cost"
              name="estimated_cost"
              type="number"
              min="0"
              step="0.01"
              value={
                formData.estimated_cost
              }
              onChange={handleChange}
              disabled={saving}
            />

            {errors.estimated_cost && (
              <div className="field-error">
                {errors.estimated_cost}
              </div>
            )}

          </div>


          {/* FEASIBILITY */}

          <div className="form-group">

            <label htmlFor="feasibility_score">
              Feasibility Score *
            </label>

            <select
              id="feasibility_score"
              name="feasibility_score"
              value={
                formData.feasibility_score
              }
              onChange={handleChange}
              disabled={saving}
            >
              <option value="1">
                1 — Very Difficult
              </option>

              <option value="2">
                2 — Difficult
              </option>

              <option value="3">
                3 — Moderate
              </option>

              <option value="4">
                4 — Feasible
              </option>

              <option value="5">
                5 — Highly Feasible
              </option>
            </select>

            {errors.feasibility_score && (
              <div className="field-error">
                {errors.feasibility_score}
              </div>
            )}

          </div>


          {/* RISK */}

          <div className="form-group">

            <label htmlFor="risk_level">
              Risk Level *
            </label>

            <select
              id="risk_level"
              name="risk_level"
              value={
                formData.risk_level
              }
              onChange={handleChange}
              disabled={saving}
            >
              {RISK_LEVELS.map(
                (risk) => (
                  <option
                    key={risk}
                    value={risk}
                  >
                    {risk}
                  </option>
                )
              )}
            </select>

            {errors.risk_level && (
              <div className="field-error">
                {errors.risk_level}
              </div>
            )}

          </div>


          {/* ACTIONS */}

          <div className="form-actions">

            <Link
              to={`/decisions/${decisionId}/alternatives`}
              className="secondary-button"
            >
              Cancel
            </Link>

            <button
              type="submit"
              className="primary-button"
              disabled={saving}
            >
              {saving
                ? "Saving..."
                : "Save Changes"}
            </button>

          </div>

        </form>

      </div>

    </div>
  );
}

export default EditAlternative;