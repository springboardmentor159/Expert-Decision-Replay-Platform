import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  FilePlus2,
  Lightbulb,
  FolderKanban,
  FileText,
  MessageSquareText,
  Loader2,
  Save,
  X,
} from "lucide-react";

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

      navigate(`/decisions/${createdDecision.id}`);
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
    <div className="create-decision-page">

      <style>{`
        .create-decision-page {
          max-width: 1100px;
          margin: 0 auto;
          padding: 8px 0 40px;
        }

        .create-decision-header {
          display: flex;
          align-items: flex-start;
          justify-content: space-between;
          gap: 24px;
          margin-bottom: 28px;
        }

        .create-decision-header-left {
          display: flex;
          gap: 16px;
          align-items: flex-start;
        }

        .create-decision-icon {
          width: 52px;
          height: 52px;
          min-width: 52px;
          border-radius: 14px;
          background: #eaf2ff;
          color: #2563eb;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .create-decision-eyebrow {
          margin: 0 0 6px;
          font-size: 12px;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 0.08em;
          color: #64748b;
        }

        .create-decision-header h1 {
          margin: 0;
          color: #0f172a;
          font-size: 30px;
          line-height: 1.2;
        }

        .create-decision-header p {
          margin: 8px 0 0;
          color: #64748b;
          font-size: 15px;
        }

        .create-decision-back {
          display: inline-flex;
          align-items: center;
          gap: 7px;
          color: #475569;
          text-decoration: none;
          font-size: 14px;
          font-weight: 600;
          margin-bottom: 12px;
        }

        .create-decision-back:hover {
          color: #2563eb;
        }

        .create-decision-card {
          background: #ffffff;
          border: 1px solid #e2e8f0;
          border-radius: 18px;
          box-shadow: 0 8px 30px rgba(15, 23, 42, 0.06);
          overflow: hidden;
        }

        .create-decision-card-header {
          padding: 22px 28px;
          border-bottom: 1px solid #e2e8f0;
          background: #f8fafc;
        }

        .create-decision-card-header h2 {
          margin: 0;
          display: flex;
          align-items: center;
          gap: 9px;
          font-size: 18px;
          color: #0f172a;
        }

        .create-decision-card-header p {
          margin: 6px 0 0 29px;
          color: #64748b;
          font-size: 13px;
        }

        .create-decision-form {
          padding: 28px;
        }

        .create-decision-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 22px;
        }

        .create-decision-full {
          grid-column: 1 / -1;
        }

        .create-decision-field {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .create-decision-field label {
          display: flex;
          align-items: center;
          gap: 7px;
          font-size: 14px;
          font-weight: 700;
          color: #334155;
        }

        .required-mark {
          color: #dc2626;
        }

        .optional-label {
          color: #94a3b8;
          font-size: 12px;
          font-weight: 500;
        }

        .create-decision-field input,
        .create-decision-field textarea {
          width: 100%;
          box-sizing: border-box;
          border: 1px solid #cbd5e1;
          border-radius: 10px;
          padding: 12px 14px;
          font-family: inherit;
          font-size: 14px;
          color: #0f172a;
          background: #ffffff;
          outline: none;
          transition:
            border-color 0.2s ease,
            box-shadow 0.2s ease;
        }

        .create-decision-field input {
          min-height: 46px;
        }

        .create-decision-field textarea {
          min-height: 145px;
          resize: vertical;
          line-height: 1.6;
        }

        .create-decision-field input::placeholder,
        .create-decision-field textarea::placeholder {
          color: #94a3b8;
        }

        .create-decision-field input:focus,
        .create-decision-field textarea:focus {
          border-color: #2563eb;
          box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        }

        .create-decision-field input:disabled,
        .create-decision-field textarea:disabled {
          background: #f8fafc;
          cursor: not-allowed;
        }

        .create-decision-field.has-error input,
        .create-decision-field.has-error textarea {
          border-color: #ef4444;
        }

        .create-decision-field.has-error input:focus,
        .create-decision-field.has-error textarea:focus {
          box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
        }

        .create-decision-error {
          color: #dc2626;
          font-size: 12px;
          font-weight: 600;
        }

        .create-decision-helper {
          color: #94a3b8;
          font-size: 12px;
          line-height: 1.5;
        }

        .create-decision-server-error {
          display: flex;
          align-items: flex-start;
          gap: 12px;
          margin-top: 24px;
          padding: 15px 16px;
          border: 1px solid #fecaca;
          border-radius: 12px;
          background: #fef2f2;
          color: #991b1b;
        }

        .create-decision-server-error strong {
          display: block;
          margin-bottom: 3px;
          font-size: 14px;
        }

        .create-decision-server-error p {
          margin: 0;
          font-size: 13px;
          line-height: 1.5;
        }

        .create-decision-actions {
          display: flex;
          align-items: center;
          justify-content: flex-end;
          gap: 12px;
          margin-top: 30px;
          padding-top: 22px;
          border-top: 1px solid #e2e8f0;
        }

        .create-decision-cancel,
        .create-decision-submit {
          min-height: 44px;
          padding: 0 18px;
          border-radius: 9px;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          font-family: inherit;
          font-size: 14px;
          font-weight: 700;
          text-decoration: none;
          cursor: pointer;
          transition:
            transform 0.15s ease,
            box-shadow 0.15s ease,
            background 0.15s ease;
        }

        .create-decision-cancel {
          border: 1px solid #cbd5e1;
          background: #ffffff;
          color: #475569;
        }

        .create-decision-cancel:hover {
          background: #f8fafc;
        }

        .create-decision-submit {
          border: none;
          background: #2563eb;
          color: #ffffff;
        }

        .create-decision-submit:hover:not(:disabled) {
          background: #1d4ed8;
          box-shadow: 0 5px 15px rgba(37, 99, 235, 0.2);
          transform: translateY(-1px);
        }

        .create-decision-submit:disabled {
          opacity: 0.65;
          cursor: not-allowed;
        }

        .create-decision-info {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 14px;
          margin-bottom: 24px;
        }

        .create-decision-info-item {
          padding: 14px;
          border-radius: 12px;
          background: #f8fafc;
          border: 1px solid #e2e8f0;
        }

        .create-decision-info-item div:first-child {
          color: #475569;
          font-size: 12px;
          font-weight: 700;
          margin-bottom: 5px;
        }

        .create-decision-info-item div:last-child {
          color: #64748b;
          font-size: 12px;
          line-height: 1.4;
        }

        @media (max-width: 800px) {
          .create-decision-grid {
            grid-template-columns: 1fr;
          }

          .create-decision-full {
            grid-column: auto;
          }

          .create-decision-info {
            grid-template-columns: 1fr;
          }
        }

        @media (max-width: 600px) {
          .create-decision-page {
            padding: 0 0 24px;
          }

          .create-decision-header {
            flex-direction: column;
            margin-bottom: 20px;
          }

          .create-decision-header h1 {
            font-size: 25px;
          }

          .create-decision-card {
            border-radius: 14px;
          }

          .create-decision-form {
            padding: 20px;
          }

          .create-decision-card-header {
            padding: 18px 20px;
          }

          .create-decision-actions {
            flex-direction: column-reverse;
          }

          .create-decision-cancel,
          .create-decision-submit {
            width: 100%;
          }
        }
      `}</style>

      {/* HEADER */}
      <div className="create-decision-header">
        <div className="create-decision-header-left">
          <div className="create-decision-icon">
            <FilePlus2 size={25} />
          </div>

          <div>
            <Link
              to="/decisions"
              className="create-decision-back"
            >
              <ArrowLeft size={16} />
              Back to Decisions
            </Link>

            <div className="create-decision-eyebrow">
              Decision Management
            </div>

            <h1>Create Decision</h1>

            <p>
              Record a new organizational decision
              with its context and reasoning.
            </p>
          </div>
        </div>
      </div>

      {/* INFORMATION STRIP */}
      <div className="create-decision-info">
        <div className="create-decision-info-item">
          <div>Structured Decision</div>
          <div>
            Capture the key information needed
            to understand the decision.
          </div>
        </div>

        <div className="create-decision-info-item">
          <div>Traceable Record</div>
          <div>
            The platform will maintain history
            and activity for the decision.
          </div>
        </div>

        <div className="create-decision-info-item">
          <div>Next Steps</div>
          <div>
            Add alternatives, discussions and
            approvals after creation.
          </div>
        </div>
      </div>

      {/* FORM CARD */}
      <div className="create-decision-card">

        <div className="create-decision-card-header">
          <h2>
            <Lightbulb size={19} />
            Decision Information
          </h2>

          <p>
            Provide the basic details for this
            decision.
          </p>
        </div>

        <form
          className="create-decision-form"
          onSubmit={handleSubmit}
        >

          <div className="create-decision-grid">

            {/* TITLE */}
            <div
              className={`create-decision-field ${
                errors.title ? "has-error" : ""
              }`}
            >
              <label htmlFor="title">
                <FileText size={15} />
                Decision Title
                <span className="required-mark">
                  *
                </span>
              </label>

              <input
                id="title"
                name="title"
                type="text"
                placeholder="e.g. Select Cloud Monitoring Platform"
                value={formData.title}
                onChange={handleChange}
                disabled={loading}
                autoComplete="off"
              />

              {errors.title && (
                <div className="create-decision-error">
                  {errors.title}
                </div>
              )}
            </div>

            {/* CATEGORY */}
            <div
              className={`create-decision-field ${
                errors.category ? "has-error" : ""
              }`}
            >
              <label htmlFor="category">
                <FolderKanban size={15} />
                Category
                <span className="required-mark">
                  *
                </span>
              </label>

              <input
                id="category"
                name="category"
                type="text"
                placeholder="e.g. Technology, Finance, Infrastructure"
                value={formData.category}
                onChange={handleChange}
                disabled={loading}
                autoComplete="off"
              />

              {errors.category && (
                <div className="create-decision-error">
                  {errors.category}
                </div>
              )}
            </div>

            {/* PROBLEM */}
            <div
              className={`create-decision-field create-decision-full ${
                errors.problem_statement
                  ? "has-error"
                  : ""
              }`}
            >
              <label htmlFor="problem_statement">
                <MessageSquareText size={15} />
                Problem Statement
                <span className="required-mark">
                  *
                </span>
              </label>

              <textarea
                id="problem_statement"
                name="problem_statement"
                rows="7"
                placeholder="Describe the problem, business need, or situation that requires a decision..."
                value={formData.problem_statement}
                onChange={handleChange}
                disabled={loading}
              />

              <div className="create-decision-helper">
                Clearly explain what problem needs
                to be solved and why a decision is
                required.
              </div>

              {errors.problem_statement && (
                <div className="create-decision-error">
                  {errors.problem_statement}
                </div>
              )}
            </div>

            {/* RATIONALE */}
            <div className="create-decision-field create-decision-full">
              <label htmlFor="rationale">
                <Lightbulb size={15} />
                Rationale
                <span className="optional-label">
                  Optional
                </span>
              </label>

              <textarea
                id="rationale"
                name="rationale"
                rows="7"
                placeholder="Explain the reasoning, background, or factors that support this decision..."
                value={formData.rationale}
                onChange={handleChange}
                disabled={loading}
              />

              <div className="create-decision-helper">
                You can add supporting reasoning now
                or provide more details later.
              </div>
            </div>

          </div>

          {/* SERVER ERROR */}
          {serverError && (
            <div className="create-decision-server-error">
              <X size={20} />

              <div>
                <strong>
                  Unable to Create Decision
                </strong>

                <p>
                  {serverError}
                </p>
              </div>
            </div>
          )}

          {/* ACTIONS */}
          <div className="create-decision-actions">

            <Link
              to="/decisions"
              className="create-decision-cancel"
            >
              <X size={16} />
              Cancel
            </Link>

            <button
              type="submit"
              className="create-decision-submit"
              disabled={loading}
            >
              {loading ? (
                <>
                  <Loader2
                    size={17}
                    className="spin"
                  />
                  Creating...
                </>
              ) : (
                <>
                  <Save size={17} />
                  Create Decision
                </>
              )}
            </button>

          </div>

        </form>
      </div>
    </div>
  );
}

export default CreateDecision;