import {
  useEffect,
  useState,
} from "react";

import {
  Link,
  useNavigate,
  useParams,
} from "react-router-dom";

import {
  AlertCircle,
  ArrowLeft,
  CheckCircle2,
  FileEdit,
  Loader2,
  Save,
  ShieldAlert,
  Trash2,
  X,
} from "lucide-react";

import {
  getDecision,
  updateDecision,
  deleteDecision,
} from "../api/decisionApi";


function EditDecision() {
  const {
    decisionId,
  } = useParams();

  const navigate =
    useNavigate();


  const [formData, setFormData] =
    useState({
      title: "",
      problem_statement: "",
      rationale: "",
      category: "",
      status: "Draft",
    });


  const [loading, setLoading] =
    useState(true);

  const [saving, setSaving] =
    useState(false);

  const [deleting, setDeleting] =
    useState(false);


  const [error, setError] =
    useState("");

  const [success, setSuccess] =
    useState("");


  const [fieldErrors, setFieldErrors] =
    useState({});


  const [
    showDeleteConfirmation,
    setShowDeleteConfirmation,
  ] = useState(false);


  useEffect(() => {
    loadDecision();
  }, [decisionId]);


  async function loadDecision() {
    try {
      setLoading(true);
      setError("");

      const data =
        await getDecision(
          decisionId
        );

      setFormData({
        title:
          data.title || "",

        problem_statement:
          data.problem_statement || "",

        rationale:
          data.rationale || "",

        category:
          data.category || "",

        status:
          data.status || "Draft",
      });

    } catch (err) {
      console.error(
        "Failed to load decision:",
        err
      );

      if (
        err.response?.status ===
        401
      ) {
        setError(
          "Your session has expired. Please log in again."
        );
      } else if (
        err.response?.status ===
        403
      ) {
        setError(
          "You do not have permission to edit this decision."
        );
      } else if (
        err.response?.status ===
        404
      ) {
        setError(
          "Decision not found."
        );
      } else if (
        err.response?.status >=
        500
      ) {
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


  function handleChange(event) {
    const {
      name,
      value,
    } = event.target;

    setFormData(
      (current) => ({
        ...current,
        [name]: value,
      })
    );

    setFieldErrors(
      (current) => ({
        ...current,
        [name]: "",
      })
    );

    setError("");
    setSuccess("");
  }


  function validateForm() {
    const errors = {};

    if (
      !formData.title.trim()
    ) {
      errors.title =
        "Decision title is required.";
    }

    if (
      !formData.problem_statement.trim()
    ) {
      errors.problem_statement =
        "Problem statement is required.";
    }

    if (
      !formData.category.trim()
    ) {
      errors.category =
        "Decision category is required.";
    }

    setFieldErrors(errors);

    return (
      Object.keys(errors)
        .length === 0
    );
  }


  async function handleSubmit(
    event
  ) {
    event.preventDefault();

    setError("");
    setSuccess("");

    if (!validateForm()) {
      return;
    }

    try {
      setSaving(true);

      const payload = {
        title:
          formData.title.trim(),

        problem_statement:
          formData.problem_statement.trim(),

        rationale:
          formData.rationale.trim() ||
          null,

        category:
          formData.category.trim(),

        status:
          formData.status,
      };

      await updateDecision(
        decisionId,
        payload
      );

      setSuccess(
        "Decision updated successfully."
      );

      setTimeout(() => {
        navigate(
          `/decisions/${decisionId}`
        );
      }, 700);

    } catch (err) {
      console.error(
        "Failed to update the decision:",
        err
      );

      if (
        err.response?.status ===
        401
      ) {
        setError(
          "Your session has expired. Please log in again."
        );
      } else if (
        err.response?.status ===
        403
      ) {
        setError(
          "You do not have permission to update this decision."
        );
      } else if (
        err.response?.status ===
        404
      ) {
        setError(
          "Decision not found."
        );
      } else if (
        err.response?.status ===
        422
      ) {
        const detail =
          err.response?.data?.detail;

        if (
          Array.isArray(detail)
        ) {
          setError(
            detail
              .map(
                (item) =>
                  item.msg
              )
              .join(" ")
          );
        } else {
          setError(
            detail ||
              "Please check the information you entered."
          );
        }

      } else if (
        err.response?.status ===
        400
      ) {
        setError(
          err.response?.data?.detail ||
            "The decision could not be updated."
        );

      } else if (
        err.response?.status >=
        500
      ) {
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


  async function handleDelete() {
    try {
      setDeleting(true);
      setError("");

      await deleteDecision(
        decisionId
      );

      navigate(
        "/decisions"
      );

    } catch (err) {
      console.error(
        "Failed to delete decision:",
        err
      );

      setDeleting(false);

      if (
        err.response?.status ===
        401
      ) {
        setError(
          "Your session has expired. Please log in again."
        );
      } else if (
        err.response?.status ===
        403
      ) {
        setError(
          "You do not have permission to delete this decision."
        );
      } else if (
        err.response?.status ===
        404
      ) {
        setError(
          "Decision not found."
        );
      } else if (
        err.response?.status >=
        500
      ) {
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


  if (loading) {
    return (
      <div className="ed-page">

        <style>{`
          .ed-page {
            max-width: 1100px;
            margin: 0 auto;
            padding: 30px 20px;
          }

          .ed-loading {
            min-height: 420px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 12px;
            color: #64748b;
            font-size: 13px;
          }

          .ed-spin {
            animation: edSpin 1s linear infinite;
          }

          @keyframes edSpin {
            from {
              transform: rotate(0deg);
            }

            to {
              transform: rotate(360deg);
            }
          }
        `}</style>

        <div className="ed-loading">

          <Loader2
            size={28}
            className="ed-spin"
          />

          <span>
            Loading decision...
          </span>

        </div>

      </div>
    );
  }


  if (
    error &&
    !formData.title
  ) {
    return (
      <div className="ed-page">

        <style>{`
          .ed-page {
            max-width: 1100px;
            margin: 0 auto;
            padding: 30px 20px;
          }

          .ed-load-error {
            max-width: 550px;
            margin: 80px auto;
            padding: 28px;
            border: 1px solid #fecaca;
            border-radius: 16px;
            background: #fff;
            text-align: center;
            box-shadow:
              0 10px 30px
              rgba(15,23,42,.06);
          }

          .ed-load-error-icon {
            width: 52px;
            height: 52px;
            margin: 0 auto 15px;
            border-radius: 14px;
            background: #fef2f2;
            color: #dc2626;
            display: flex;
            align-items: center;
            justify-content: center;
          }

          .ed-load-error h2 {
            margin: 0 0 7px;
            color: #0f172a;
            font-size: 19px;
          }

          .ed-load-error p {
            margin: 0 0 20px;
            color: #64748b;
            font-size: 13px;
            line-height: 1.5;
          }

          .ed-load-actions {
            display: flex;
            justify-content: center;
            gap: 9px;
            flex-wrap: wrap;
          }

          .ed-button {
            min-height: 40px;
            padding: 0 14px;
            border-radius: 8px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            text-decoration: none;
            font-family: inherit;
            font-size: 12px;
            font-weight: 750;
            cursor: pointer;
          }

          .ed-primary {
            border: 1px solid #2563eb;
            background: #2563eb;
            color: #fff;
          }

          .ed-secondary {
            border: 1px solid #cbd5e1;
            background: #fff;
            color: #475569;
          }
        `}</style>

        <div className="ed-load-error">

          <div className="ed-load-error-icon">
            <AlertCircle size={25} />
          </div>

          <h2>
            Unable to Load Decision
          </h2>

          <p>
            {error}
          </p>

          <div className="ed-load-actions">

            <button
              type="button"
              className="ed-button ed-primary"
              onClick={loadDecision}
            >
              Try Again
            </button>

            <Link
              to="/decisions"
              className="ed-button ed-secondary"
            >
              <ArrowLeft size={14} />
              Back to Decisions
            </Link>

          </div>

        </div>

      </div>
    );
  }


  return (
    <div className="ed-page">

      <style>{`
        .ed-page {
          max-width: 1100px;
          margin: 0 auto;
          padding: 4px 0 40px;
        }

        .ed-header {
          display: flex;
          align-items: flex-start;
          gap: 14px;
          margin-bottom: 22px;
        }

        .ed-header-icon {
          width: 49px;
          height: 49px;
          min-width: 49px;
          border-radius: 14px;
          background: #eaf2ff;
          color: #2563eb;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .ed-back {
          display: inline-flex;
          align-items: center;
          gap: 5px;
          margin-bottom: 6px;
          color: #64748b;
          text-decoration: none;
          font-size: 11px;
          font-weight: 700;
        }

        .ed-back:hover {
          color: #2563eb;
        }

        .ed-eyebrow {
          margin-bottom: 4px;
          color: #64748b;
          font-size: 10px;
          font-weight: 800;
          letter-spacing: .1em;
          text-transform: uppercase;
        }

        .ed-header h1 {
          margin: 0;
          color: #0f172a;
          font-size: 28px;
          line-height: 1.2;
        }

        .ed-header p {
          margin: 6px 0 0;
          color: #64748b;
          font-size: 13px;
        }

        .ed-card {
          overflow: hidden;
          margin-bottom: 20px;
          border: 1px solid #e2e8f0;
          border-radius: 17px;
          background: #fff;
          box-shadow:
            0 7px 25px
            rgba(15,23,42,.05);
        }

        .ed-card-header {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 19px 22px;
          border-bottom: 1px solid #e2e8f0;
          background: #f8fafc;
        }

        .ed-card-icon {
          width: 35px;
          height: 35px;
          border-radius: 9px;
          background: #dbeafe;
          color: #2563eb;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .ed-card-header h2 {
          margin: 0;
          color: #0f172a;
          font-size: 16px;
        }

        .ed-card-header p {
          margin: 4px 0 0;
          color: #64748b;
          font-size: 11px;
        }

        .ed-form {
          padding: 23px;
        }

        .ed-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 18px;
        }

        .ed-full {
          grid-column: 1 / -1;
        }

        .ed-field {
          display: flex;
          flex-direction: column;
          gap: 7px;
        }

        .ed-field label {
          color: #334155;
          font-size: 11px;
          font-weight: 750;
        }

        .ed-required {
          color: #dc2626;
          margin-left: 2px;
        }

        .ed-input,
        .ed-select,
        .ed-textarea {
          width: 100%;
          box-sizing: border-box;
          border: 1px solid #cbd5e1;
          border-radius: 9px;
          background: #fff;
          color: #0f172a;
          font-family: inherit;
          font-size: 13px;
          outline: none;
          transition: .15s ease;
        }

        .ed-input,
        .ed-select {
          min-height: 44px;
          padding: 0 12px;
        }

        .ed-textarea {
          min-height: 150px;
          padding: 12px;
          resize: vertical;
          line-height: 1.6;
        }

        .ed-input:focus,
        .ed-select:focus,
        .ed-textarea:focus {
          border-color: #2563eb;
          box-shadow:
            0 0 0 3px
            rgba(37,99,235,.10);
        }

        .ed-input:disabled,
        .ed-select:disabled,
        .ed-textarea:disabled {
          background: #f8fafc;
          opacity: .7;
          cursor: not-allowed;
        }

        .ed-input::placeholder,
        .ed-textarea::placeholder {
          color: #94a3b8;
        }

        .ed-field-error {
          display: flex;
          align-items: center;
          gap: 5px;
          color: #dc2626;
          font-size: 10px;
          font-weight: 650;
        }

        .ed-status-note {
          display: flex;
          align-items: flex-start;
          gap: 7px;
          padding: 10px 11px;
          border-radius: 8px;
          background: #f8fafc;
          color: #64748b;
          font-size: 10px;
          line-height: 1.5;
        }

        .ed-actions {
          display: flex;
          justify-content: flex-end;
          gap: 9px;
          margin-top: 22px;
          padding-top: 18px;
          border-top: 1px solid #e2e8f0;
        }

        .ed-button {
          min-height: 41px;
          padding: 0 14px;
          border-radius: 8px;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: 6px;
          font-family: inherit;
          font-size: 11px;
          font-weight: 750;
          text-decoration: none;
          cursor: pointer;
        }

        .ed-button:disabled {
          opacity: .55;
          cursor: not-allowed;
        }

        .ed-button-primary {
          border: 1px solid #2563eb;
          background: #2563eb;
          color: #fff;
        }

        .ed-button-primary:hover:not(:disabled) {
          background: #1d4ed8;
        }

        .ed-button-secondary {
          border: 1px solid #cbd5e1;
          background: #fff;
          color: #475569;
        }

        .ed-button-secondary:hover:not(:disabled) {
          background: #f8fafc;
        }

        .ed-success {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 20px;
          padding: 13px 15px;
          border: 1px solid #bbf7d0;
          border-radius: 10px;
          background: #f0fdf4;
          color: #166534;
          font-size: 12px;
          font-weight: 650;
        }

        .ed-error {
          display: flex;
          align-items: flex-start;
          gap: 9px;
          margin-bottom: 20px;
          padding: 13px 15px;
          border: 1px solid #fecaca;
          border-radius: 10px;
          background: #fef2f2;
          color: #991b1b;
        }

        .ed-error strong {
          display: block;
          margin-bottom: 3px;
          font-size: 12px;
        }

        .ed-error p {
          margin: 0;
          font-size: 11px;
          line-height: 1.5;
        }

        .ed-delete-card {
          border-color: #fecaca;
        }

        .ed-delete-header {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 18px 22px;
          border-bottom: 1px solid #fecaca;
          background: #fffafa;
        }

        .ed-delete-icon {
          width: 35px;
          height: 35px;
          border-radius: 9px;
          background: #fee2e2;
          color: #dc2626;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .ed-delete-header h2 {
          margin: 0;
          color: #991b1b;
          font-size: 16px;
        }

        .ed-delete-body {
          padding: 20px 22px;
        }

        .ed-delete-body > p {
          margin: 0 0 17px;
          color: #64748b;
          font-size: 12px;
          line-height: 1.6;
        }

        .ed-danger {
          min-height: 40px;
          padding: 0 13px;
          border: 1px solid #dc2626;
          border-radius: 8px;
          background: #dc2626;
          color: #fff;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: 6px;
          font-family: inherit;
          font-size: 11px;
          font-weight: 750;
          cursor: pointer;
        }

        .ed-danger:hover:not(:disabled) {
          background: #b91c1c;
        }

        .ed-danger:disabled {
          opacity: .55;
          cursor: not-allowed;
        }

        .ed-confirmation {
          padding: 16px;
          border: 1px solid #fecaca;
          border-radius: 10px;
          background: #fef2f2;
        }

        .ed-confirmation-title {
          display: flex;
          align-items: flex-start;
          gap: 8px;
          color: #991b1b;
          font-size: 12px;
          font-weight: 800;
        }

        .ed-confirmation p {
          margin: 9px 0;
          color: #475569;
          font-size: 11px;
          line-height: 1.5;
        }

        .ed-confirmation ul {
          margin: 7px 0 17px 20px;
          padding: 0;
          color: #475569;
          font-size: 11px;
        }

        .ed-confirmation li {
          margin-bottom: 4px;
        }

        .ed-delete-actions {
          display: flex;
          gap: 8px;
        }

        .ed-footer {
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 10px;
          margin-top: 4px;
        }

        .ed-spin {
          animation: edSpin 1s linear infinite;
        }

        @keyframes edSpin {
          from {
            transform: rotate(0deg);
          }

          to {
            transform: rotate(360deg);
          }
        }

        @media (max-width: 700px) {
          .ed-page {
            padding-bottom: 30px;
          }

          .ed-grid {
            grid-template-columns: 1fr;
          }

          .ed-full {
            grid-column: auto;
          }

          .ed-actions {
            flex-direction: column-reverse;
          }

          .ed-actions .ed-button {
            width: 100%;
          }

          .ed-footer {
            flex-direction: column;
            align-items: stretch;
          }

          .ed-footer .ed-button {
            width: 100%;
          }
        }

        @media (max-width: 480px) {
          .ed-header h1 {
            font-size: 24px;
          }

          .ed-form {
            padding: 18px;
          }

          .ed-delete-body {
            padding: 18px;
          }

          .ed-delete-actions {
            flex-direction: column;
          }

          .ed-delete-actions button {
            width: 100%;
          }
        }
      `}</style>


      {/* HEADER */}
      <div className="ed-header">

        <div className="ed-header-icon">
          <FileEdit size={23} />
        </div>

        <div>

          <Link
            to={`/decisions/${decisionId}`}
            className="ed-back"
          >
            <ArrowLeft size={13} />
            Back to Decision
          </Link>

          <div className="ed-eyebrow">
            Decision Management
          </div>

          <h1>
            Edit Decision
          </h1>

          <p>
            Update the information for
            Decision #{decisionId}.
          </p>

        </div>

      </div>


      {/* SUCCESS */}
      {success && (
        <div className="ed-success">

          <CheckCircle2 size={17} />

          {success}

        </div>
      )}


      {/* ERROR */}
      {error && (
        <div className="ed-error">

          <AlertCircle size={17} />

          <div>

            <strong>
              Unable to Update Decision
            </strong>

            <p>
              {error}
            </p>

          </div>

        </div>
      )}


      {/* EDIT FORM */}
      <div className="ed-card">

        <div className="ed-card-header">

          <div className="ed-card-icon">
            <FileEdit size={17} />
          </div>

          <div>

            <h2>
              Decision Information
            </h2>

            <p>
              Update the main details
              of this decision.
            </p>

          </div>

        </div>


        <form
          onSubmit={handleSubmit}
          className="ed-form"
        >

          <div className="ed-grid">

            {/* TITLE */}
            <div className="ed-field ed-full">

              <label htmlFor="title">
                Decision Title
                <span className="ed-required">
                  *
                </span>
              </label>

              <input
                id="title"
                name="title"
                type="text"
                className="ed-input"
                value={formData.title}
                onChange={handleChange}
                disabled={
                  saving ||
                  deleting
                }
                autoComplete="off"
                placeholder="Enter decision title"
              />

              {fieldErrors.title && (
                <div className="ed-field-error">
                  <AlertCircle size={12} />
                  {fieldErrors.title}
                </div>
              )}

            </div>


            {/* CATEGORY */}
            <div className="ed-field">

              <label htmlFor="category">
                Category
                <span className="ed-required">
                  *
                </span>
              </label>

              <input
                id="category"
                name="category"
                type="text"
                className="ed-input"
                value={formData.category}
                onChange={handleChange}
                disabled={
                  saving ||
                  deleting
                }
                autoComplete="off"
                placeholder="e.g. Technology"
              />

              {fieldErrors.category && (
                <div className="ed-field-error">
                  <AlertCircle size={12} />
                  {fieldErrors.category}
                </div>
              )}

            </div>


            {/* STATUS */}
            <div className="ed-field">

              <label htmlFor="status">
                Status
              </label>

              <select
                id="status"
                name="status"
                className="ed-select"
                value={formData.status}
                onChange={handleChange}
                disabled={
                  saving ||
                  deleting
                }
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

              <div className="ed-status-note">
                <ShieldAlert size={13} />

                Status changes are recorded
                in the decision version and
                audit history.
              </div>

            </div>


            {/* PROBLEM */}
            <div className="ed-field ed-full">

              <label htmlFor="problem_statement">
                Problem Statement
                <span className="ed-required">
                  *
                </span>
              </label>

              <textarea
                id="problem_statement"
                name="problem_statement"
                className="ed-textarea"
                rows="7"
                value={
                  formData.problem_statement
                }
                onChange={handleChange}
                disabled={
                  saving ||
                  deleting
                }
                placeholder="Describe the problem that this decision addresses..."
              />

              {fieldErrors.problem_statement && (
                <div className="ed-field-error">
                  <AlertCircle size={12} />
                  {
                    fieldErrors.problem_statement
                  }
                </div>
              )}

            </div>


            {/* RATIONALE */}
            <div className="ed-field ed-full">

              <label htmlFor="rationale">
                Rationale
              </label>

              <textarea
                id="rationale"
                name="rationale"
                className="ed-textarea"
                rows="7"
                value={
                  formData.rationale
                }
                onChange={handleChange}
                disabled={
                  saving ||
                  deleting
                }
                placeholder="Explain the reasoning behind this decision..."
              />

            </div>

          </div>


          {/* ACTIONS */}
          <div className="ed-actions">

            <Link
              to={`/decisions/${decisionId}`}
              className="ed-button ed-button-secondary"
            >
              <X size={14} />
              Cancel
            </Link>

            <button
              type="submit"
              className="ed-button ed-button-primary"
              disabled={
                saving ||
                deleting
              }
            >

              {saving ? (
                <>
                  <Loader2
                    size={14}
                    className="ed-spin"
                  />

                  Saving...
                </>
              ) : (
                <>
                  <Save size={14} />

                  Save Changes
                </>
              )}

            </button>

          </div>

        </form>

      </div>


      {/* DELETE */}
      <div className="ed-card ed-delete-card">

        <div className="ed-delete-header">

          <div className="ed-delete-icon">
            <Trash2 size={17} />
          </div>

          <div>

            <h2>
              Delete Decision
            </h2>

          </div>

        </div>


        <div className="ed-delete-body">

          <p>
            Deleting this decision permanently
            removes it from the decision database.
            This action cannot be undone.
          </p>


          {!showDeleteConfirmation ? (
            <button
              type="button"
              className="ed-danger"
              onClick={() =>
                setShowDeleteConfirmation(
                  true
                )
              }
              disabled={
                saving ||
                deleting
              }
            >
              <Trash2 size={14} />
              Delete Decision
            </button>
          ) : (
            <div className="ed-confirmation">

              <div className="ed-confirmation-title">

                <ShieldAlert size={17} />

                Are you sure you want to
                delete Decision #{decisionId}?

              </div>

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


              <div className="ed-delete-actions">

                <button
                  type="button"
                  className="ed-button ed-button-secondary"
                  onClick={() =>
                    setShowDeleteConfirmation(
                      false
                    )
                  }
                  disabled={
                    deleting
                  }
                >
                  Cancel
                </button>

                <button
                  type="button"
                  className="ed-danger"
                  onClick={handleDelete}
                  disabled={
                    deleting
                  }
                >

                  {deleting ? (
                    <>
                      <Loader2
                        size={14}
                        className="ed-spin"
                      />

                      Deleting...
                    </>
                  ) : (
                    <>
                      <Trash2 size={14} />

                      Yes, Delete Decision
                    </>
                  )}

                </button>

              </div>

            </div>
          )}

        </div>

      </div>


      {/* FOOTER */}
      <div className="ed-footer">

        <Link
          to="/decisions"
          className="ed-button ed-button-secondary"
        >
          <ArrowLeft size={14} />
          Back to Decisions
        </Link>

      </div>

    </div>
  );
}


export default EditDecision;