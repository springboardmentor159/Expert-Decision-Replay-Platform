import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { createAlternative } from "../api/alternativeApi";

function CreateAlternative() {
  const { decisionId } = useParams();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    name: "",
    description: "",
    pros: "",
    cons: "",
    estimated_cost: "",
    feasibility_score: "",
    risk_level: "Low",
  });

  const [errors, setErrors] = useState({});
  const [submitError, setSubmitError] = useState("");
  const [submitting, setSubmitting] = useState(false);

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

    setSubmitError("");
  }

  function validate() {
    const newErrors = {};

    if (!formData.name.trim()) {
      newErrors.name = "Alternative name is required.";
    }

    if (!formData.description.trim()) {
      newErrors.description =
        "Alternative description is required.";
    }

    if (!formData.pros.trim()) {
      newErrors.pros = "Please enter the advantages/pros.";
    }

    if (!formData.cons.trim()) {
      newErrors.cons = "Please enter the disadvantages/cons.";
    }

    if (
      formData.estimated_cost === "" ||
      Number.isNaN(Number(formData.estimated_cost)) ||
      Number(formData.estimated_cost) < 0
    ) {
      newErrors.estimated_cost =
        "Enter a valid estimated cost.";
    }

    const feasibility = Number(
      formData.feasibility_score
    );

    if (
      formData.feasibility_score === "" ||
      !Number.isInteger(feasibility) ||
      feasibility < 1 ||
      feasibility > 5
    ) {
      newErrors.feasibility_score =
        "Feasibility score must be between 1 and 5.";
    }

    if (!formData.risk_level) {
      newErrors.risk_level =
        "Please select a risk level.";
    }

    setErrors(newErrors);

    return Object.keys(newErrors).length === 0;
  }

  async function handleSubmit(event) {
    event.preventDefault();

    if (!validate()) {
      return;
    }

    try {
      setSubmitting(true);
      setSubmitError("");

      const payload = {
        name: formData.name.trim(),
        description: formData.description.trim(),
        pros: formData.pros.trim(),
        cons: formData.cons.trim(),
        estimated_cost: Number(
          formData.estimated_cost
        ),
        feasibility_score: Number(
          formData.feasibility_score
        ),
        risk_level: formData.risk_level,
      };

      await createAlternative(
        Number(decisionId),
        payload
      );

      navigate(
        `/decisions/${decisionId}/alternatives`
      );
    } catch (error) {
      console.error(
        "Failed to create alternative:",
        error
      );

      if (error.response?.status === 400) {
        setSubmitError(
          error.response?.data?.detail ||
            "Invalid alternative data."
        );
      } else if (error.response?.status === 401) {
        setSubmitError(
          "Your session has expired. Please log in again."
        );
      } else if (error.response?.status === 403) {
        setSubmitError(
          "You do not have permission to add an alternative."
        );
      } else if (error.response?.status === 404) {
        setSubmitError(
          "The decision could not be found."
        );
      } else if (error.response?.status === 422) {
        setSubmitError(
          "Please check the entered values and try again."
        );
      } else if (error.response?.status >= 500) {
        setSubmitError(
          "The server encountered an error. Please try again."
        );
      } else {
        setSubmitError(
          "Unable to create the alternative. Please try again."
        );
      }
    } finally {
      setSubmitting(false);
    }
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

          <h1>Add Alternative</h1>

          <p>
            Add an alternative option for Decision #
            {decisionId}.
          </p>
        </div>
      </div>

      {submitError && (
        <div className="error-state">
          <p>{submitError}</p>
        </div>
      )}

      <div className="card">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="name">
              Alternative Name
            </label>

            <input
              id="name"
              name="name"
              type="text"
              value={formData.name}
              onChange={handleChange}
              placeholder="e.g. AWS CloudWatch"
              disabled={submitting}
            />

            {errors.name && (
              <p className="field-error">
                {errors.name}
              </p>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="description">
              Description
            </label>

            <textarea
              id="description"
              name="description"
              rows="4"
              value={formData.description}
              onChange={handleChange}
              placeholder="Describe this alternative."
              disabled={submitting}
            />

            {errors.description && (
              <p className="field-error">
                {errors.description}
              </p>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="pros">
              Pros
            </label>

            <textarea
              id="pros"
              name="pros"
              rows="4"
              value={formData.pros}
              onChange={handleChange}
              placeholder="Advantages of this alternative."
              disabled={submitting}
            />

            {errors.pros && (
              <p className="field-error">
                {errors.pros}
              </p>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="cons">
              Cons
            </label>

            <textarea
              id="cons"
              name="cons"
              rows="4"
              value={formData.cons}
              onChange={handleChange}
              placeholder="Disadvantages of this alternative."
              disabled={submitting}
            />

            {errors.cons && (
              <p className="field-error">
                {errors.cons}
              </p>
            )}
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="estimated_cost">
                Estimated Cost
              </label>

              <input
                id="estimated_cost"
                name="estimated_cost"
                type="number"
                min="0"
                step="0.01"
                value={formData.estimated_cost}
                onChange={handleChange}
                placeholder="50000"
                disabled={submitting}
              />

              {errors.estimated_cost && (
                <p className="field-error">
                  {errors.estimated_cost}
                </p>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="feasibility_score">
                Feasibility Score
              </label>

              <select
                id="feasibility_score"
                name="feasibility_score"
                value={formData.feasibility_score}
                onChange={handleChange}
                disabled={submitting}
              >
                <option value="">
                  Select score
                </option>
                <option value="1">1 / 5</option>
                <option value="2">2 / 5</option>
                <option value="3">3 / 5</option>
                <option value="4">4 / 5</option>
                <option value="5">5 / 5</option>
              </select>

              {errors.feasibility_score && (
                <p className="field-error">
                  {errors.feasibility_score}
                </p>
              )}
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="risk_level">
              Risk Level
            </label>

            <select
              id="risk_level"
              name="risk_level"
              value={formData.risk_level}
              onChange={handleChange}
              disabled={submitting}
            >
              <option value="Low">Low</option>
              <option value="Medium">Medium</option>
              <option value="High">High</option>
              <option value="Critical">
                Critical
              </option>
            </select>

            {errors.risk_level && (
              <p className="field-error">
                {errors.risk_level}
              </p>
            )}
          </div>

          <div className="page-footer-actions">
            <Link
              to={`/decisions/${decisionId}/alternatives`}
              className="secondary-button"
            >
              Cancel
            </Link>

            <button
              type="submit"
              className="primary-button"
              disabled={submitting}
            >
              {submitting
                ? "Saving..."
                : "Save Alternative"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CreateAlternative;