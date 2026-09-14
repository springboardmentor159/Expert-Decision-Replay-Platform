import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { createApproval } from "../../services/approvalService";
import { getDecisions } from "../../services/decisionService";
import { getUsers } from "../../services/authService";
import { useAuth } from "../../context/AuthContext";

const AssignApproval = () => {
  const navigate = useNavigate();
  const { role } = useAuth();

  const [decisions, setDecisions] = useState([]);
  const [reviewers, setReviewers] = useState([]);

  const [formData, setFormData] = useState({
    decision_id: "",
    assigned_to: "",
    approval_level: "1",
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] =
    useState("");

  // =========================================================
  // LOAD DECISIONS AND REVIEWERS
  // =========================================================

  useEffect(() => {
    if (
      role !== "Manager" &&
      role !== "Administrator"
    ) {
      setLoading(false);
      return;
    }

    loadFormData();
  }, [role]);

  const loadFormData = async () => {
    setLoading(true);
    setError("");

    try {
      const [decisionData, userData] =
        await Promise.all([
          getDecisions(),
          getUsers(),
        ]);

      setDecisions(
        Array.isArray(decisionData)
          ? decisionData
          : []
      );

      const userList = Array.isArray(userData)
        ? userData
        : [];

      const reviewerUsers = userList.filter(
        (user) => user.role === "Reviewer"
      );

      setReviewers(reviewerUsers);
    } catch (err) {
      console.error(
        "Failed to load approval form:",
        err
      );

      handleError(
        err,
        "Unable to load approval information."
      );
    } finally {
      setLoading(false);
    }
  };

  // =========================================================
  // FORM CHANGE
  // =========================================================

  const handleChange = (event) => {
    const { name, value } = event.target;

    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  // =========================================================
  // SUBMIT
  // =========================================================

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");
    setSuccessMessage("");

    if (!formData.decision_id) {
      setError("Please select a decision.");
      return;
    }

    if (!formData.assigned_to) {
      setError("Please select a reviewer.");
      return;
    }

    if (!formData.approval_level) {
      setError("Please enter an approval level.");
      return;
    }

    setSaving(true);

    try {
      const payload = {
        decision_id: Number(
          formData.decision_id
        ),
        assigned_to: Number(
          formData.assigned_to
        ),
        approval_level: Number(
          formData.approval_level
        ),
      };

      await createApproval(payload);

      setSuccessMessage(
        "Approval assigned successfully."
      );

      setFormData({
        decision_id: "",
        assigned_to: "",
        approval_level: "1",
      });

    } catch (err) {
      console.error(
        "Failed to create approval:",
        err
      );

      handleError(
        err,
        "Unable to assign approval."
      );
    } finally {
      setSaving(false);
    }
  };

  // =========================================================
  // ERROR HANDLING
  // =========================================================

  const handleError = (err, defaultMessage) => {
    const status = err?.response?.status;

    if (status === 400) {
      setError(
        err.response?.data?.detail ||
          "Invalid approval request."
      );
    } else if (status === 401) {
      setError(
        "Your session has expired. Please log in again."
      );
    } else if (status === 403) {
      setError(
        "You do not have permission to assign approvals."
      );
    } else if (status === 404) {
      setError(
        "The selected decision or reviewer was not found."
      );
    } else if (status === 422) {
      setError(
        "Please check all approval fields."
      );
    } else if (status >= 500) {
      setError(
        "A server error occurred. Please try again."
      );
    } else if (!err?.response) {
      setError(
        "Unable to connect to the backend server."
      );
    } else {
      setError(
        err.response?.data?.detail ||
          defaultMessage
      );
    }
  };

  // =========================================================
  // ROLE PROTECTION
  // =========================================================

  if (
    role !== "Manager" &&
    role !== "Administrator"
  ) {
    return (
      <div className="approval-page">

        <div className="page-header">
          <div>
            <h1>Assign Approval</h1>
            <p>
              Assign a decision approval request
            </p>
          </div>
        </div>

        <div className="approval-card">
          <div className="approval-empty">
            <strong>
              Access Restricted
            </strong>

            <p>
              Only Managers and Administrators can
              assign approval requests.
            </p>

            <button
              type="button"
              className="app-button secondary"
              onClick={() =>
                navigate("/approvals")
              }
            >
              Back to Approvals
            </button>
          </div>
        </div>

      </div>
    );
  }

  // =========================================================
  // LOADING
  // =========================================================

  if (loading) {
    return (
      <div className="approval-page">

        <div className="page-header">
          <div>
            <h1>Assign Approval</h1>
            <p>
              Assign a decision to a reviewer
            </p>
          </div>
        </div>

        <div className="approval-loading">
          Loading approval information...
        </div>

      </div>
    );
  }

  // =========================================================
  // UI
  // =========================================================

  return (
    <div className="approval-page">

      <div className="page-header">

        <div>
          <h1>Assign Approval</h1>

          <p>
            Assign a decision approval request to a
            reviewer
          </p>
        </div>

        <button
          type="button"
          className="app-button secondary"
          onClick={() =>
            navigate("/approvals")
          }
        >
          Back to Approvals
        </button>

      </div>

      {error && (
        <div className="alert alert-error">
          {error}
        </div>
      )}

      {successMessage && (
        <div className="alert alert-success">
          {successMessage}
        </div>
      )}

      <div className="approval-card assign-approval-card">

        <form
          className="approval-form"
          onSubmit={handleSubmit}
        >

          {/* DECISION */}

          <div className="form-group">
            <label htmlFor="decision_id">
              Decision
            </label>

            <select
              id="decision_id"
              name="decision_id"
              value={formData.decision_id}
              onChange={handleChange}
            >
              <option value="">
                Select a decision
              </option>

              {decisions.map((decision) => (
                <option
                  key={decision.id}
                  value={decision.id}
                >
                  #{decision.id} -{" "}
                  {decision.title}
                </option>
              ))}
            </select>
          </div>

          {/* REVIEWER */}

          <div className="form-group">
            <label htmlFor="assigned_to">
              Reviewer
            </label>

            <select
              id="assigned_to"
              name="assigned_to"
              value={formData.assigned_to}
              onChange={handleChange}
            >
              <option value="">
                Select a reviewer
              </option>

              {reviewers.map((reviewer) => (
                <option
                  key={reviewer.id}
                  value={reviewer.id}
                >
                  {reviewer.full_name} (
                  {reviewer.email})
                </option>
              ))}
            </select>

            {reviewers.length === 0 && (
              <p className="approval-help-text">
                No users with the Reviewer role
                were found.
              </p>
            )}
          </div>

          {/* APPROVAL LEVEL */}

          <div className="form-group">
            <label htmlFor="approval_level">
              Approval Level
            </label>

            <input
              id="approval_level"
              name="approval_level"
              type="number"
              min="1"
              value={formData.approval_level}
              onChange={handleChange}
            />

            <p className="approval-help-text">
              Enter the approval level required for
              this request.
            </p>
          </div>

          {/* ACTIONS */}

          <div className="approval-form-actions">

            <button
              type="button"
              className="app-button secondary"
              onClick={() =>
                navigate("/approvals")
              }
            >
              Cancel
            </button>

            <button
              type="submit"
              className="app-button primary"
              disabled={saving}
            >
              {saving
                ? "Assigning..."
                : "Assign Approval"}
            </button>

          </div>

        </form>

      </div>

    </div>
  );
};

export default AssignApproval;