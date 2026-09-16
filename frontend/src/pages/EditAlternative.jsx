import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import {
  ArrowLeft,
  Pencil,
  FileText,
  ThumbsUp,
  ThumbsDown,
  IndianRupee,
  Gauge,
  ShieldAlert,
  Save,
  X,
  Loader2,
  AlertCircle,
  Target,
} from "lucide-react";

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
  const { alternativeId } = useParams();
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

  const [decisionId, setDecisionId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState({});
  const [serverError, setServerError] = useState("");

  useEffect(() => {
    loadAlternative();
  }, [alternativeId]);

  async function loadAlternative() {
    try {
      setLoading(true);
      setServerError("");

      const data = await getAlternative(alternativeId);

      setDecisionId(data.decision_id);

      setFormData({
        name: data.name || "",
        description: data.description || "",
        pros: data.pros || "",
        cons: data.cons || "",
        estimated_cost: data.estimated_cost ?? "",
        feasibility_score: String(
          data.feasibility_score ?? 3
        ),
        risk_level: data.risk_level || "Medium",
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
        setServerError("Alternative not found.");
      } else if (err.response?.status >= 500) {
        setServerError(
          "The server encountered an error. Please try again."
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

    if (!formData.name.trim()) {
      newErrors.name =
        "Alternative name is required.";
    }

    if (!formData.description.trim()) {
      newErrors.description =
        "Description is required.";
    }

    if (!formData.pros.trim()) {
      newErrors.pros = "Pros are required.";
    }

    if (!formData.cons.trim()) {
      newErrors.cons = "Cons are required.";
    }

    if (
      formData.estimated_cost === "" ||
      Number.isNaN(Number(formData.estimated_cost))
    ) {
      newErrors.estimated_cost =
        "Estimated cost must be a valid number.";
    } else if (
      Number(formData.estimated_cost) < 0
    ) {
      newErrors.estimated_cost =
        "Estimated cost cannot be negative.";
    }

    const feasibility = Number(
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

    if (!RISK_LEVELS.includes(formData.risk_level)) {
      newErrors.risk_level =
        "Please select a valid risk level.";
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
      setSaving(true);

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
        setServerError("Alternative not found.");
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
      } else if (err.response?.status >= 500) {
        setServerError(
          "The server encountered an error. Please try again."
        );
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
      <div className="ea-loading">
        <Loader2
          size={24}
          className="ea-spin"
        />
        <span>Loading alternative...</span>
      </div>
    );
  }

  if (serverError && !decisionId) {
    return (
      <div className="ea-error-page">
        <AlertCircle size={30} />

        <h2>Unable to Load Alternative</h2>

        <p>{serverError}</p>

        <button
          type="button"
          className="ea-primary"
          onClick={loadAlternative}
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="ea-page">

      <style>{`
        .ea-page {
          max-width: 1080px;
          margin: 0 auto;
          padding: 4px 0 40px;
        }

        .ea-loading {
          min-height: 400px;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 10px;
          color: #64748b;
          font-size: 14px;
        }

        .ea-spin {
          animation: eaSpin 1s linear infinite;
        }

        @keyframes eaSpin {
          from {
            transform: rotate(0deg);
          }

          to {
            transform: rotate(360deg);
          }
        }

        .ea-error-page {
          min-height: 400px;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          text-align: center;
          color: #64748b;
        }

        .ea-error-page h2 {
          margin: 12px 0 6px;
          color: #334155;
        }

        .ea-error-page p {
          margin: 0 0 18px;
        }

        .ea-header {
          display: flex;
          align-items: flex-start;
          gap: 15px;
          margin-bottom: 25px;
        }

        .ea-header-icon {
          width: 50px;
          height: 50px;
          min-width: 50px;
          border-radius: 14px;
          background: #eaf2ff;
          color: #2563eb;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .ea-back {
          display: inline-flex;
          align-items: center;
          gap: 7px;
          color: #64748b;
          text-decoration: none;
          font-size: 13px;
          font-weight: 650;
          margin-bottom: 8px;
        }

        .ea-back:hover {
          color: #2563eb;
        }

        .ea-eyebrow {
          color: #64748b;
          text-transform: uppercase;
          letter-spacing: .08em;
          font-size: 11px;
          font-weight: 800;
          margin-bottom: 5px;
        }

        .ea-header h1 {
          margin: 0;
          color: #0f172a;
          font-size: 29px;
          line-height: 1.2;
        }

        .ea-header p {
          margin: 7px 0 0;
          color: #64748b;
          font-size: 14px;
        }

        .ea-id {
          color: #2563eb;
          font-weight: 700;
        }

        .ea-card {
          background: #fff;
          border: 1px solid #e2e8f0;
          border-radius: 17px;
          box-shadow: 0 8px 28px rgba(15, 23, 42, .05);
          overflow: hidden;
        }

        .ea-card-header {
          padding: 20px 24px;
          background: #f8fafc;
          border-bottom: 1px solid #e2e8f0;
        }

        .ea-card-header h2 {
          margin: 0;
          display: flex;
          align-items: center;
          gap: 9px;
          color: #0f172a;
          font-size: 17px;
        }

        .ea-card-header p {
          margin: 5px 0 0 27px;
          color: #64748b;
          font-size: 12px;
        }

        .ea-form {
          padding: 25px;
        }

        .ea-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 20px;
        }

        .ea-full {
          grid-column: 1 / -1;
        }

        .ea-field {
          display: flex;
          flex-direction: column;
          gap: 7px;
        }

        .ea-field label {
          display: flex;
          align-items: center;
          gap: 6px;
          color: #334155;
          font-size: 13px;
          font-weight: 750;
        }

        .ea-required {
          color: #dc2626;
        }

        .ea-field input,
        .ea-field textarea,
        .ea-field select {
          width: 100%;
          box-sizing: border-box;
          border: 1px solid #cbd5e1;
          border-radius: 10px;
          background: #fff;
          color: #0f172a;
          padding: 11px 13px;
          font-family: inherit;
          font-size: 13px;
          outline: none;
          transition:
            border-color .2s,
            box-shadow .2s;
        }

        .ea-field input {
          min-height: 44px;
        }

        .ea-field textarea {
          min-height: 125px;
          resize: vertical;
          line-height: 1.6;
        }

        .ea-field input:focus,
        .ea-field textarea:focus,
        .ea-field select:focus {
          border-color: #2563eb;
          box-shadow: 0 0 0 3px rgba(37, 99, 235, .1);
        }

        .ea-field input::placeholder,
        .ea-field textarea::placeholder {
          color: #94a3b8;
        }

        .ea-field.has-error input,
        .ea-field.has-error textarea,
        .ea-field.has-error select {
          border-color: #ef4444;
        }

        .ea-field-error {
          color: #dc2626;
          font-size: 11px;
          font-weight: 650;
        }

        .ea-section-title {
          grid-column: 1 / -1;
          display: flex;
          align-items: center;
          gap: 9px;
          margin-top: 5px;
          padding-bottom: 10px;
          border-bottom: 1px solid #e2e8f0;
          color: #334155;
          font-size: 13px;
          font-weight: 800;
          text-transform: uppercase;
          letter-spacing: .05em;
        }

        .ea-server-error {
          display: flex;
          align-items: flex-start;
          gap: 10px;
          margin-top: 22px;
          padding: 14px 15px;
          border: 1px solid #fecaca;
          border-radius: 11px;
          background: #fef2f2;
          color: #991b1b;
        }

        .ea-server-error strong {
          display: block;
          margin-bottom: 3px;
          font-size: 13px;
        }

        .ea-server-error p {
          margin: 0;
          font-size: 12px;
          line-height: 1.5;
        }

        .ea-actions {
          display: flex;
          justify-content: flex-end;
          gap: 10px;
          margin-top: 28px;
          padding-top: 21px;
          border-top: 1px solid #e2e8f0;
        }

        .ea-primary,
        .ea-secondary {
          min-height: 42px;
          padding: 0 16px;
          border-radius: 9px;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: 7px;
          font-family: inherit;
          font-size: 13px;
          font-weight: 750;
          text-decoration: none;
          cursor: pointer;
          transition: .15s ease;
        }

        .ea-primary {
          border: 1px solid #2563eb;
          background: #2563eb;
          color: #fff;
        }

        .ea-primary:hover:not(:disabled) {
          background: #1d4ed8;
          box-shadow: 0 4px 13px rgba(37, 99, 235, .2);
        }

        .ea-secondary {
          border: 1px solid #cbd5e1;
          background: #fff;
          color: #475569;
        }

        .ea-secondary:hover {
          background: #f8fafc;
        }

        .ea-primary:disabled {
          opacity: .6;
          cursor: not-allowed;
        }

        .ea-tip {
          grid-column: 1 / -1;
          display: flex;
          align-items: flex-start;
          gap: 10px;
          padding: 13px 14px;
          border-radius: 10px;
          background: #f8fafc;
          border: 1px solid #e2e8f0;
          color: #64748b;
          font-size: 12px;
          line-height: 1.5;
        }

        @media (max-width: 720px) {
          .ea-grid {
            grid-template-columns: 1fr;
          }

          .ea-full,
          .ea-section-title,
          .ea-tip {
            grid-column: auto;
          }
        }

        @media (max-width: 520px) {
          .ea-header h1 {
            font-size: 24px;
          }

          .ea-form {
            padding: 18px;
          }

          .ea-card-header {
            padding: 18px;
          }

          .ea-actions {
            flex-direction: column-reverse;
          }

          .ea-primary,
          .ea-secondary {
            width: 100%;
          }
        }
      `}</style>

      {/* HEADER */}
      <div className="ea-header">

        <div className="ea-header-icon">
          <Pencil size={24} />
        </div>

        <div>
          <Link
            to={`/decisions/${decisionId}/alternatives`}
            className="ea-back"
          >
            <ArrowLeft size={15} />
            Back to Alternatives
          </Link>

          <div className="ea-eyebrow">
            Alternative Analysis
          </div>

          <h1>Edit Alternative</h1>

          <p>
            Update the details and evaluation
            criteria for{" "}
            <span className="ea-id">
              Alternative #{alternativeId}
            </span>
          </p>
        </div>

      </div>

      {/* SERVER ERROR */}
      {serverError && (
        <div className="ea-server-error">
          <AlertCircle size={19} />

          <div>
            <strong>
              Unable to Update Alternative
            </strong>

            <p>{serverError}</p>
          </div>
        </div>
      )}

      {/* FORM */}
      <div className="ea-card">

        <div className="ea-card-header">
          <h2>
            <Target size={18} />
            Alternative Information
          </h2>

          <p>
            Update the option's description,
            advantages, disadvantages and evaluation.
          </p>
        </div>

        <form
          className="ea-form"
          onSubmit={handleSubmit}
        >

          <div className="ea-grid">

            {/* NAME */}
            <div
              className={`ea-field ${
                errors.name ? "has-error" : ""
              }`}
            >
              <label htmlFor="name">
                <FileText size={14} />
                Alternative Name
                <span className="ea-required">
                  *
                </span>
              </label>

              <input
                id="name"
                name="name"
                type="text"
                placeholder="e.g. AWS CloudWatch"
                value={formData.name}
                onChange={handleChange}
                disabled={saving}
              />

              {errors.name && (
                <div className="ea-field-error">
                  {errors.name}
                </div>
              )}
            </div>

            {/* COST */}
            <div
              className={`ea-field ${
                errors.estimated_cost
                  ? "has-error"
                  : ""
              }`}
            >
              <label htmlFor="estimated_cost">
                <IndianRupee size={14} />
                Estimated Cost
                <span className="ea-required">
                  *
                </span>
              </label>

              <input
                id="estimated_cost"
                name="estimated_cost"
                type="number"
                min="0"
                step="0.01"
                placeholder="e.g. 50000"
                value={
                  formData.estimated_cost
                }
                onChange={handleChange}
                disabled={saving}
              />

              {errors.estimated_cost && (
                <div className="ea-field-error">
                  {errors.estimated_cost}
                </div>
              )}
            </div>

            {/* DESCRIPTION */}
            <div
              className={`ea-field ea-full ${
                errors.description
                  ? "has-error"
                  : ""
              }`}
            >
              <label htmlFor="description">
                <FileText size={14} />
                Description
                <span className="ea-required">
                  *
                </span>
              </label>

              <textarea
                id="description"
                name="description"
                rows="5"
                placeholder="Describe this alternative and how it addresses the decision problem..."
                value={
                  formData.description
                }
                onChange={handleChange}
                disabled={saving}
              />

              {errors.description && (
                <div className="ea-field-error">
                  {errors.description}
                </div>
              )}
            </div>

            {/* PROS */}
            <div
              className={`ea-field ${
                errors.pros
                  ? "has-error"
                  : ""
              }`}
            >
              <label htmlFor="pros">
                <ThumbsUp size={14} />
                Pros
                <span className="ea-required">
                  *
                </span>
              </label>

              <textarea
                id="pros"
                name="pros"
                rows="6"
                placeholder="List the main advantages of this option..."
                value={formData.pros}
                onChange={handleChange}
                disabled={saving}
              />

              {errors.pros && (
                <div className="ea-field-error">
                  {errors.pros}
                </div>
              )}
            </div>

            {/* CONS */}
            <div
              className={`ea-field ${
                errors.cons
                  ? "has-error"
                  : ""
              }`}
            >
              <label htmlFor="cons">
                <ThumbsDown size={14} />
                Cons
                <span className="ea-required">
                  *
                </span>
              </label>

              <textarea
                id="cons"
                name="cons"
                rows="6"
                placeholder="List the main disadvantages or limitations..."
                value={formData.cons}
                onChange={handleChange}
                disabled={saving}
              />

              {errors.cons && (
                <div className="ea-field-error">
                  {errors.cons}
                </div>
              )}
            </div>

            {/* EVALUATION */}
            <div className="ea-section-title">
              <Gauge size={15} />
              Evaluation
            </div>

            {/* FEASIBILITY */}
            <div
              className={`ea-field ${
                errors.feasibility_score
                  ? "has-error"
                  : ""
              }`}
            >
              <label htmlFor="feasibility_score">
                <Gauge size={14} />
                Feasibility Score
                <span className="ea-required">
                  *
                </span>
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
                <div className="ea-field-error">
                  {errors.feasibility_score}
                </div>
              )}
            </div>

            {/* RISK */}
            <div
              className={`ea-field ${
                errors.risk_level
                  ? "has-error"
                  : ""
              }`}
            >
              <label htmlFor="risk_level">
                <ShieldAlert size={14} />
                Risk Level
                <span className="ea-required">
                  *
                </span>
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
                {RISK_LEVELS.map((risk) => (
                  <option
                    key={risk}
                    value={risk}
                  >
                    {risk}
                  </option>
                ))}
              </select>

              {errors.risk_level && (
                <div className="ea-field-error">
                  {errors.risk_level}
                </div>
              )}
            </div>

            {/* TIP */}
            <div className="ea-tip">
              <Target size={17} />

              <span>
                Evaluation scores help compare
                alternatives later. Feasibility is
                rated from 1–5, while risk represents
                the assessed level of risk.
              </span>
            </div>

          </div>

          {/* ACTIONS */}
          <div className="ea-actions">

            <Link
              to={`/decisions/${decisionId}/alternatives`}
              className="ea-secondary"
            >
              <X size={15} />
              Cancel
            </Link>

            <button
              type="submit"
              className="ea-primary"
              disabled={saving}
            >
              {saving ? (
                <>
                  <Loader2
                    size={15}
                    className="ea-spin"
                  />
                  Saving...
                </>
              ) : (
                <>
                  <Save size={15} />
                  Save Changes
                </>
              )}
            </button>

          </div>

        </form>
      </div>
    </div>
  );
}

export default EditAlternative;