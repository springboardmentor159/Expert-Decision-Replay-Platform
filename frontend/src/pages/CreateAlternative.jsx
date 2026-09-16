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
      newErrors.name =
        "Alternative name is required.";
    }

    if (!formData.description.trim()) {
      newErrors.description =
        "Alternative description is required.";
    }

    if (!formData.pros.trim()) {
      newErrors.pros =
        "Please enter the advantages/pros.";
    }

    if (!formData.cons.trim()) {
      newErrors.cons =
        "Please enter the disadvantages/cons.";
    }

    if (
      formData.estimated_cost === "" ||
      Number.isNaN(
        Number(formData.estimated_cost)
      ) ||
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

    return (
      Object.keys(newErrors).length === 0
    );
  }

  async function handleSubmit(event) {
    event.preventDefault();

    setSubmitError("");

    if (!validate()) {
      return;
    }

    try {
      setSubmitting(true);

      const payload = {
        name: formData.name.trim(),
        description:
          formData.description.trim(),
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

      if (
        error.response?.status === 400
      ) {
        setSubmitError(
          error.response?.data?.detail ||
            "Invalid alternative data."
        );
      } else if (
        error.response?.status === 401
      ) {
        setSubmitError(
          "Your session has expired. Please log in again."
        );
      } else if (
        error.response?.status === 403
      ) {
        setSubmitError(
          "You do not have permission to add an alternative."
        );
      } else if (
        error.response?.status === 404
      ) {
        setSubmitError(
          "The decision could not be found."
        );
      } else if (
        error.response?.status === 422
      ) {
        const detail =
          error.response?.data?.detail;

        if (Array.isArray(detail)) {
          setSubmitError(
            detail
              .map(
                (item) =>
                  item.msg
              )
              .join(" ")
          );
        } else {
          setSubmitError(
            detail ||
              "Please check the entered values and try again."
          );
        }
      } else if (
        error.response?.status >= 500
      ) {
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
    <>
      <style>
        {createAlternativeStyles}
      </style>

      <div className="create-alternative-page">

        {/* HEADER */}

        <div className="create-alternative-header">

          <div>

            <Link
              to={`/decisions/${decisionId}/alternatives`}
              className="create-alternative-back"
            >
              ← Back to Alternatives
            </Link>

            <span className="create-alternative-eyebrow">
              DECISION ANALYSIS
            </span>

            <h1>
              Add Alternative
            </h1>

            <p>
              Add an alternative option for
              Decision #{decisionId}.
            </p>

          </div>

        </div>


        {/* ERROR */}

        {submitError && (
          <div className="create-alternative-error">

            <div className="create-alternative-error-icon">
              !
            </div>

            <div>
              <strong>
                Unable to save alternative
              </strong>

              <p>
                {submitError}
              </p>
            </div>

          </div>
        )}


        {/* FORM CARD */}

        <div className="create-alternative-card">

          <div className="create-alternative-card-header">

            <div className="create-alternative-section-icon">
              +
            </div>

            <div>
              <h2>
                Alternative Information
              </h2>

              <p>
                Provide the details used to
                evaluate this option.
              </p>
            </div>

          </div>


          <form
            onSubmit={handleSubmit}
          >

            {/* NAME */}

            <div className="create-alternative-form-group">

              <label htmlFor="name">
                Alternative Name
                <span>*</span>
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
                <p className="create-alternative-field-error">
                  {errors.name}
                </p>
              )}

            </div>


            {/* DESCRIPTION */}

            <div className="create-alternative-form-group">

              <label htmlFor="description">
                Description
                <span>*</span>
              </label>

              <textarea
                id="description"
                name="description"
                rows="5"
                value={formData.description}
                onChange={handleChange}
                placeholder="Describe this alternative and how it addresses the decision problem."
                disabled={submitting}
              />

              {errors.description && (
                <p className="create-alternative-field-error">
                  {errors.description}
                </p>
              )}

            </div>


            {/* PROS / CONS */}

            <div className="create-alternative-two-column">

              <div className="create-alternative-form-group">

                <label htmlFor="pros">
                  Advantages / Pros
                  <span>*</span>
                </label>

                <textarea
                  id="pros"
                  name="pros"
                  rows="6"
                  value={formData.pros}
                  onChange={handleChange}
                  placeholder="List the main advantages of this alternative."
                  disabled={submitting}
                />

                {errors.pros && (
                  <p className="create-alternative-field-error">
                    {errors.pros}
                  </p>
                )}

              </div>


              <div className="create-alternative-form-group">

                <label htmlFor="cons">
                  Disadvantages / Cons
                  <span>*</span>
                </label>

                <textarea
                  id="cons"
                  name="cons"
                  rows="6"
                  value={formData.cons}
                  onChange={handleChange}
                  placeholder="List the main disadvantages of this alternative."
                  disabled={submitting}
                />

                {errors.cons && (
                  <p className="create-alternative-field-error">
                    {errors.cons}
                  </p>
                )}

              </div>

            </div>


            {/* EVALUATION */}

            <div className="create-alternative-evaluation">

              <div className="create-alternative-evaluation-title">
                <h3>
                  Evaluation Criteria
                </h3>

                <p>
                  Enter the values used to
                  compare this alternative.
                </p>
              </div>


              <div className="create-alternative-three-column">

                {/* COST */}

                <div className="create-alternative-form-group">

                  <label htmlFor="estimated_cost">
                    Estimated Cost
                    <span>*</span>
                  </label>

                  <div className="create-alternative-input-prefix">

                    <span>
                      ₹
                    </span>

                    <input
                      id="estimated_cost"
                      name="estimated_cost"
                      type="number"
                      min="0"
                      step="0.01"
                      value={
                        formData.estimated_cost
                      }
                      onChange={
                        handleChange
                      }
                      placeholder="50000"
                      disabled={submitting}
                    />

                  </div>

                  {errors.estimated_cost && (
                    <p className="create-alternative-field-error">
                      {
                        errors.estimated_cost
                      }
                    </p>
                  )}

                </div>


                {/* FEASIBILITY */}

                <div className="create-alternative-form-group">

                  <label htmlFor="feasibility_score">
                    Feasibility Score
                    <span>*</span>
                  </label>

                  <select
                    id="feasibility_score"
                    name="feasibility_score"
                    value={
                      formData.feasibility_score
                    }
                    onChange={
                      handleChange
                    }
                    disabled={submitting}
                  >

                    <option value="">
                      Select score
                    </option>

                    <option value="1">
                      1 / 5 — Very Low
                    </option>

                    <option value="2">
                      2 / 5 — Low
                    </option>

                    <option value="3">
                      3 / 5 — Moderate
                    </option>

                    <option value="4">
                      4 / 5 — High
                    </option>

                    <option value="5">
                      5 / 5 — Very High
                    </option>

                  </select>

                  {errors.feasibility_score && (
                    <p className="create-alternative-field-error">
                      {
                        errors.feasibility_score
                      }
                    </p>
                  )}

                </div>


                {/* RISK */}

                <div className="create-alternative-form-group">

                  <label htmlFor="risk_level">
                    Risk Level
                    <span>*</span>
                  </label>

                  <select
                    id="risk_level"
                    name="risk_level"
                    value={
                      formData.risk_level
                    }
                    onChange={
                      handleChange
                    }
                    disabled={submitting}
                  >

                    <option value="Low">
                      Low
                    </option>

                    <option value="Medium">
                      Medium
                    </option>

                    <option value="High">
                      High
                    </option>

                    <option value="Critical">
                      Critical
                    </option>

                  </select>

                  {errors.risk_level && (
                    <p className="create-alternative-field-error">
                      {
                        errors.risk_level
                      }
                    </p>
                  )}

                </div>

              </div>

            </div>


            {/* ACTIONS */}

            <div className="create-alternative-actions">

              <Link
                to={`/decisions/${decisionId}/alternatives`}
                className="create-alternative-secondary-button"
              >
                Cancel
              </Link>

              <button
                type="submit"
                className="create-alternative-primary-button"
                disabled={submitting}
              >
                {submitting
                  ? "Saving Alternative..."
                  : "Save Alternative"}
              </button>

            </div>

          </form>

        </div>

      </div>
    </>
  );
}

const createAlternativeStyles = `
  .create-alternative-page {
    width: 100%;
    max-width: 1100px;
    margin: 0 auto;
    padding: 32px;
    box-sizing: border-box;
    background: #f8fafc;
  }

  .create-alternative-header {
    margin-bottom: 26px;
  }

  .create-alternative-back {
    display: inline-flex;
    margin-bottom: 16px;
    color: #2563eb;
    font-size: 13px;
    font-weight: 700;
    text-decoration: none;
  }

  .create-alternative-back:hover {
    text-decoration: underline;
  }

  .create-alternative-eyebrow {
    display: block;
    margin-bottom: 7px;
    color: #2563eb;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.14em;
  }

  .create-alternative-header h1 {
    margin: 0 0 7px;
    color: #0f172a;
    font-size: 32px;
    font-weight: 800;
    line-height: 1.2;
  }

  .create-alternative-header p {
    margin: 0;
    color: #64748b;
    font-size: 15px;
    line-height: 1.6;
  }

  .create-alternative-error {
    display: flex;
    align-items: flex-start;
    gap: 13px;
    margin-bottom: 22px;
    padding: 16px 18px;
    border: 1px solid #fecaca;
    border-radius: 10px;
    background: #fef2f2;
  }

  .create-alternative-error-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: #fee2e2;
    color: #b91c1c;
    font-weight: 800;
  }

  .create-alternative-error strong {
    display: block;
    margin-bottom: 3px;
    color: #991b1b;
    font-size: 14px;
  }

  .create-alternative-error p {
    margin: 0;
    color: #b91c1c;
    font-size: 13px;
    line-height: 1.5;
  }

  .create-alternative-card {
    padding: 28px;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    background: #ffffff;
    box-shadow:
      0 2px 10px
      rgba(15, 23, 42, 0.04);
  }

  .create-alternative-card-header {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    margin-bottom: 28px;
    padding-bottom: 22px;
    border-bottom: 1px solid #e2e8f0;
  }

  .create-alternative-section-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    width: 44px;
    height: 44px;
    border-radius: 10px;
    background: #eff6ff;
    color: #2563eb;
    font-size: 23px;
    font-weight: 500;
  }

  .create-alternative-card-header h2 {
    margin: 0 0 5px;
    color: #0f172a;
    font-size: 20px;
    font-weight: 800;
  }

  .create-alternative-card-header p {
    margin: 0;
    color: #64748b;
    font-size: 13px;
  }

  .create-alternative-form-group {
    margin-bottom: 22px;
  }

  .create-alternative-form-group label {
    display: block;
    margin-bottom: 8px;
    color: #334155;
    font-size: 13px;
    font-weight: 700;
  }

  .create-alternative-form-group label span {
    margin-left: 3px;
    color: #dc2626;
  }

  .create-alternative-form-group input,
  .create-alternative-form-group textarea,
  .create-alternative-form-group select {
    width: 100%;
    box-sizing: border-box;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    background: #ffffff;
    color: #0f172a;
    font-family: inherit;
    font-size: 13px;
    outline: none;
    transition:
      border-color 0.15s ease,
      box-shadow 0.15s ease;
  }

  .create-alternative-form-group input,
  .create-alternative-form-group select {
    min-height: 44px;
    padding: 0 13px;
  }

  .create-alternative-form-group textarea {
    min-height: 120px;
    padding: 12px 13px;
    resize: vertical;
    line-height: 1.55;
  }

  .create-alternative-form-group input::placeholder,
  .create-alternative-form-group textarea::placeholder {
    color: #94a3b8;
  }

  .create-alternative-form-group input:focus,
  .create-alternative-form-group textarea:focus,
  .create-alternative-form-group select:focus {
    border-color: #2563eb;
    box-shadow:
      0 0 0 3px
      rgba(37, 99, 235, 0.1);
  }

  .create-alternative-form-group input:disabled,
  .create-alternative-form-group textarea:disabled,
  .create-alternative-form-group select:disabled {
    background: #f8fafc;
    cursor: not-allowed;
  }

  .create-alternative-two-column {
    display: grid;
    grid-template-columns:
      repeat(2, minmax(0, 1fr));
    gap: 20px;
  }

  .create-alternative-evaluation {
    margin-top: 5px;
    margin-bottom: 10px;
    padding: 22px;
    border: 1px solid #e2e8f0;
    border-radius: 11px;
    background: #f8fafc;
  }

  .create-alternative-evaluation-title {
    margin-bottom: 20px;
  }

  .create-alternative-evaluation-title h3 {
    margin: 0 0 4px;
    color: #0f172a;
    font-size: 16px;
    font-weight: 800;
  }

  .create-alternative-evaluation-title p {
    margin: 0;
    color: #64748b;
    font-size: 12px;
  }

  .create-alternative-three-column {
    display: grid;
    grid-template-columns:
      repeat(3, minmax(0, 1fr));
    gap: 18px;
  }

  .create-alternative-input-prefix {
    display: flex;
    align-items: stretch;
  }

  .create-alternative-input-prefix span {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    border: 1px solid #cbd5e1;
    border-right: none;
    border-radius: 8px 0 0 8px;
    background: #f1f5f9;
    color: #475569;
    font-size: 13px;
    font-weight: 700;
  }

  .create-alternative-input-prefix input {
    border-radius: 0 8px 8px 0;
  }

  .create-alternative-field-error {
    margin: 6px 0 0;
    color: #dc2626;
    font-size: 11px;
    line-height: 1.4;
  }

  .create-alternative-actions {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    gap: 10px;
    margin-top: 26px;
    padding-top: 22px;
    border-top: 1px solid #e2e8f0;
  }

  .create-alternative-secondary-button,
  .create-alternative-primary-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-height: 42px;
    padding: 0 17px;
    border-radius: 8px;
    font-family: inherit;
    font-size: 13px;
    font-weight: 700;
    text-decoration: none;
    box-sizing: border-box;
    cursor: pointer;
  }

  .create-alternative-secondary-button {
    border: 1px solid #cbd5e1;
    background: #ffffff;
    color: #334155;
  }

  .create-alternative-secondary-button:hover {
    background: #f8fafc;
  }

  .create-alternative-primary-button {
    border: 1px solid #2563eb;
    background: #2563eb;
    color: #ffffff;
  }

  .create-alternative-primary-button:hover {
    background: #1d4ed8;
  }

  .create-alternative-primary-button:disabled,
  .create-alternative-secondary-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  @media (max-width: 850px) {
    .create-alternative-page {
      padding: 24px 18px;
    }

    .create-alternative-two-column,
    .create-alternative-three-column {
      grid-template-columns: 1fr;
      gap: 0;
    }

    .create-alternative-card {
      padding: 22px;
    }
  }

  @media (max-width: 520px) {
    .create-alternative-page {
      padding: 18px 12px;
    }

    .create-alternative-header h1 {
      font-size: 27px;
    }

    .create-alternative-card {
      padding: 18px;
    }

    .create-alternative-evaluation {
      padding: 16px;
    }

    .create-alternative-actions {
      flex-direction: column-reverse;
      align-items: stretch;
    }

    .create-alternative-secondary-button,
    .create-alternative-primary-button {
      width: 100%;
    }
  }
`;

export default CreateAlternative;