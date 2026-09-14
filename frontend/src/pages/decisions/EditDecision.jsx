import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import axiosClient from "../../api/axiosClient";

import PageHeader from "../../components/PageHeader";
import Button from "../../components/Button";
import Card from "../../components/Card";
import Alert from "../../components/Alert";

const EditDecision = () => {
  const { decisionId } = useParams();
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

  // --------------------------------------------------
  // LOAD DECISION
  // --------------------------------------------------
  useEffect(() => {
    const loadDecision = async () => {
      try {
        setLoading(true);
        setError("");

        const response = await axiosClient.get(
          `/decisions/${decisionId}`
        );

        setFormData({
          title: response.data.title || "",
          problem_statement:
            response.data.problem_statement || "",
          category: response.data.category || "",
          rationale: response.data.rationale || "",
        });
      } catch (err) {
        console.error("Load decision error:", err);

        const statusCode = err.response?.status;

        if (statusCode === 401) {
          setError(
            "You are not authenticated. Please login again."
          );
        } else if (statusCode === 403) {
          setError(
            "You do not have permission to view this decision."
          );
        } else if (statusCode === 404) {
          setError("Decision not found.");
        } else {
          setError("Failed to load decision.");
        }
      } finally {
        setLoading(false);
      }
    };

    loadDecision();
  }, [decisionId]);

  // --------------------------------------------------
  // HANDLE INPUT CHANGE
  // --------------------------------------------------
  const handleChange = (event) => {
    const { name, value } = event.target;

    setFormData((previousData) => ({
      ...previousData,
      [name]: value,
    }));
  };

  // --------------------------------------------------
  // SAVE CHANGES
  // --------------------------------------------------
  const handleSubmit = async (event) => {
    event.preventDefault();

    // Validation
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
      setError("");

      // ----------------------------------------------
      // UPDATE DECISION INFORMATION
      // ----------------------------------------------
      await axiosClient.put(
        `/decisions/${decisionId}`,
        {
          title: formData.title,
          problem_statement: formData.problem_statement,
          category: formData.category,
        }
      );

      // ----------------------------------------------
      // UPDATE RATIONALE
      // ----------------------------------------------
      await axiosClient.put(
        `/decisions/${decisionId}/rationale`,
        {
          rationale: formData.rationale,
        }
      );

      // ----------------------------------------------
      // RETURN TO DETAILS
      // ----------------------------------------------
      navigate(`/decisions/${decisionId}`);
    } catch (err) {
      console.error("Update decision error:", err);

      const statusCode = err.response?.status;

      if (statusCode === 401) {
        setError(
          "You are not authenticated. Please login again."
        );
      } else if (statusCode === 403) {
        setError(
          "You do not have permission to edit this decision."
        );
      } else if (statusCode === 404) {
        setError("Decision not found.");
      } else if (statusCode === 422) {
        setError(
          "Please check the entered values."
        );
      } else if (statusCode >= 500) {
        setError(
          "Server error. Please try again later."
        );
      } else {
        setError("Failed to update decision.");
      }
    } finally {
      setSaving(false);
    }
  };

  // --------------------------------------------------
  // LOADING
  // --------------------------------------------------
  if (loading) {
    return (
      <div className="decision-edit-page">

        <PageHeader
          title="Edit Decision"
          subtitle="Update the decision details and rationale."
        />

        <div className="dashboard-loading">
          <div className="loading-spinner"></div>

          <p>Loading decision...</p>
        </div>

      </div>
    );
  }

  // --------------------------------------------------
  // PAGE
  // --------------------------------------------------
  return (
    <div className="decision-edit-page">

      {/* PAGE HEADER */}
      <PageHeader
        title="Edit Decision"
        subtitle="Update the decision details and rationale."
      />

      {/* ERROR */}
      {error && (
        <Alert
          message={error}
          type="error"
          onClose={() => setError("")}
        />
      )}

      {/* FORM CARD */}
      <Card
        title="Decision Information"
        className="decision-edit-card"
      >

        <form
          className="decision-edit-form"
          onSubmit={handleSubmit}
        >

          {/* TITLE */}
          <div className="decision-edit-field">

            <label htmlFor="edit-title">
              Title <span>*</span>
            </label>

            <input
              id="edit-title"
              type="text"
              name="title"
              value={formData.title}
              onChange={handleChange}
              placeholder="Enter decision title"
              disabled={saving}
            />

          </div>

          {/* PROBLEM STATEMENT */}
          <div className="decision-edit-field">

            <label htmlFor="edit-problem-statement">
              Problem Statement <span>*</span>
            </label>

            <textarea
              id="edit-problem-statement"
              name="problem_statement"
              value={formData.problem_statement}
              onChange={handleChange}
              rows="6"
              placeholder="Describe the problem that requires a decision..."
              disabled={saving}
            />

          </div>

          {/* CATEGORY */}
          <div className="decision-edit-field">

            <label htmlFor="edit-category">
              Category <span>*</span>
            </label>

            <input
              id="edit-category"
              type="text"
              name="category"
              value={formData.category}
              onChange={handleChange}
              placeholder="Enter decision category"
              disabled={saving}
            />

          </div>

          {/* RATIONALE */}
          <div className="decision-edit-field">

            <label htmlFor="edit-rationale">
              Rationale
            </label>

            <textarea
              id="edit-rationale"
              name="rationale"
              value={formData.rationale}
              onChange={handleChange}
              rows="7"
              placeholder="Explain the reason or justification behind this decision..."
              disabled={saving}
            />

            <p className="decision-edit-help">
              Provide the reasoning or justification supporting
              this decision.
            </p>

          </div>

          {/* ACTIONS */}
          <div className="decision-edit-actions">

            <Button
              type="submit"
              disabled={saving}
            >
              {saving
                ? "Saving Changes..."
                : "Save Changes"}
            </Button>

            <Button
              type="button"
              variant="secondary"
              onClick={() =>
                navigate(`/decisions/${decisionId}`)
              }
              disabled={saving}
            >
              Cancel
            </Button>

          </div>

        </form>

      </Card>

    </div>
  );
};

export default EditDecision;