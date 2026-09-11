import { useState, type FormEvent } from "react";
import { ArrowLeft, FileText, Save } from "lucide-react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

import api from "../services/api";

export default function CreateDecision() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    title: "",
    problem_statement: "",
    category: "",
  });

  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (
    event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  ) => {
    const { name, value } = event.target;

    setForm((current) => ({
      ...current,
      [name]: value,
    }));
  };

  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();

    setError("");

    const title = form.title.trim();
    const problemStatement = form.problem_statement.trim();
    const category = form.category.trim();

    if (!title) {
      setError("Please enter a decision title.");
      return;
    }

    if (!problemStatement) {
      setError("Please enter the problem statement.");
      return;
    }

    if (!category) {
      setError("Please enter a category.");
      return;
    }

    try {
      setIsSubmitting(true);

      const response = await api.post("/decisions", {
        title,
        problem_statement: problemStatement,
        category,
      });

      const decisionId = response.data.id;

      navigate(`/decisions/${decisionId}`);
    } catch (err: unknown) {
      const status = axios.isAxiosError(err)
        ? err.response?.status
        : undefined;

      if (status === 401) {
        setError(
          "Your session has expired. Please sign in again.",
        );
      } else if (status === 403) {
        setError(
          "You do not have permission to create a decision.",
        );
      } else if (status === 422) {
        setError(
          "Please check the entered information.",
        );
      } else if (
        status !== undefined &&
        status >= 500
      ) {
        setError(
          "Server error. Please try again later.",
        );
      } else if (
        axios.isAxiosError(err) &&
        err.request
      ) {
        setError(
          "Unable to connect to the server. Make sure FastAPI is running.",
        );
      } else {
        setError("Unable to create the decision.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const createButtonStyle: React.CSSProperties = {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "8px",
    padding: "10px 20px",
    minWidth: "165px",
    minHeight: "42px",
    border: "none",
    borderRadius: "8px",
    backgroundColor: "#2563eb",
    color: "#ffffff",
    fontWeight: 600,
    fontSize: "14px",
    cursor: isSubmitting ? "not-allowed" : "pointer",
    boxShadow: "0 2px 6px rgba(0, 0, 0, 0.15)",
    opacity: isSubmitting ? 0.7 : 1,
  };

  return (
    <main className="decision-form-page">
      <header className="page-header">
        <div>
          <p className="page-eyebrow">
            Expert Decision Replay Platform
          </p>

          <h1>Create Decision</h1>

          <p>
            Create a new decision for evaluation and review.
          </p>
        </div>

        <button
          className="secondary-button"
          onClick={() => navigate("/decisions")}
          disabled={isSubmitting}
        >
          <ArrowLeft size={18} />
          Back to Decisions
        </button>
      </header>

      <section className="decision-form-card">
        <div className="form-card-header">
          <div className="form-card-icon">
            <FileText size={22} />
          </div>

          <div>
            <h2>Decision Information</h2>

            <p>
              Enter the basic information for your decision.
            </p>
          </div>
        </div>

        <form
          onSubmit={handleSubmit}
          className="decision-form"
        >
          <div className="form-group">
            <label htmlFor="title">
              Decision Title
            </label>

            <input
              id="title"
              name="title"
              type="text"
              value={form.title}
              onChange={handleChange}
              placeholder="e.g. Select Cloud Provider"
              disabled={isSubmitting}
              maxLength={255}
            />
          </div>

          <div className="form-group">
            <label htmlFor="category">
              Category
            </label>

            <input
              id="category"
              name="category"
              type="text"
              value={form.category}
              onChange={handleChange}
              placeholder="e.g. Technology"
              disabled={isSubmitting}
              maxLength={255}
            />
          </div>

          <div className="form-group">
            <label htmlFor="problem_statement">
              Problem Statement
            </label>

            <textarea
              id="problem_statement"
              name="problem_statement"
              value={form.problem_statement}
              onChange={handleChange}
              placeholder="Describe the problem or situation that requires a decision..."
              rows={7}
              disabled={isSubmitting}
            />
          </div>

          {error && (
            <div
              className="auth-error"
              role="alert"
            >
              {error}
            </div>
          )}

          <div className="form-actions">
            <button
              type="button"
              className="secondary-button"
              onClick={() => navigate("/decisions")}
              disabled={isSubmitting}
            >
              Cancel
            </button>

            <button
              type="submit"
              className="primary-button"
              style={createButtonStyle}
              disabled={isSubmitting}
            >
              <Save size={18} />

              {isSubmitting
                ? "Creating..."
                : "Create Decision"}
            </button>
          </div>
        </form>
      </section>
    </main>
  );
}