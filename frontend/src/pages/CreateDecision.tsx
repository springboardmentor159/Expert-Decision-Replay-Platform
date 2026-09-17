import { useState, type FormEvent } from "react";
import {
  ArrowLeft,
  FileText,
  Save,
} from "lucide-react";
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
    event: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement
    >,
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
    const problemStatement =
      form.problem_statement.trim();
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

  return (
    <main className="create-decision-page">
      <div className="create-decision-container">

        {/* TOP BAR */}
        <div className="create-decision-topbar">
          <button
            type="button"
            className="create-decision-back"
            onClick={() => navigate("/decisions")}
            disabled={isSubmitting}
          >
            <ArrowLeft size={17} />
            <span>Back to Decisions</span>
          </button>

          <div className="create-decision-brand">
            Expert Decision Replay Platform
          </div>
        </div>

        {/* PAGE HEADER */}
        <header className="create-decision-header">

          <div className="create-decision-header-icon">
            <FileText size={22} />
          </div>

          <div>
            <p className="create-decision-eyebrow">
              NEW DECISION
            </p>

            <h1>Create Decision</h1>

            <p className="create-decision-subtitle">
              Start a new decision record that can be
              evaluated, reviewed, approved, and replayed
              throughout its lifecycle.
            </p>
          </div>

        </header>

        {/* CENTERED FORM */}
        <section className="create-decision-card">

          {/* CARD HEADER */}
          <div className="create-decision-card-header">

            <div className="create-decision-card-icon">
              <FileText size={20} />
            </div>

            <div>
              <p className="create-decision-card-label">
                DECISION RECORD
              </p>

              <h2>Decision Information</h2>

              <p>
                Define the core information that will begin
                this decision&apos;s replay history.
              </p>
            </div>

          </div>

          <div className="create-decision-divider" />

          {/* FORM */}
          <form
            className="create-decision-form"
            onSubmit={handleSubmit}
          >

            {/* TITLE */}
            <div className="create-field">

              <label htmlFor="title">
                Decision Title
                <span>*</span>
              </label>

              <p className="create-field-help">
                Give the decision a clear and recognizable
                name.
              </p>

              <input
                id="title"
                name="title"
                type="text"
                value={form.title}
                onChange={handleChange}
                placeholder="Enter a clear decision title"
                disabled={isSubmitting}
                maxLength={255}
              />

            </div>

            {/* CATEGORY */}
            <div className="create-field">

              <label htmlFor="category">
                Category
                <span>*</span>
              </label>

              <p className="create-field-help">
                Identify the area or domain this decision
                belongs to.
              </p>

              <input
                id="category"
                name="category"
                type="text"
                value={form.category}
                onChange={handleChange}
                placeholder="e.g. Technology, Cloud, AI Testing"
                disabled={isSubmitting}
                maxLength={255}
              />

            </div>

            {/* PROBLEM STATEMENT */}
            <div className="create-field">

              <label htmlFor="problem_statement">
                Problem Statement
                <span>*</span>
              </label>

              <p className="create-field-help">
                Explain the situation, challenge, or problem
                requiring a decision.
              </p>

              <textarea
                id="problem_statement"
                name="problem_statement"
                value={form.problem_statement}
                onChange={handleChange}
                placeholder="Describe the problem or situation that requires a decision..."
                rows={8}
                disabled={isSubmitting}
              />

              <div className="create-textarea-footer">
                <span>
                  Provide enough context for reviewers to
                  understand the decision.
                </span>

                <span>
                  {form.problem_statement.length} characters
                </span>
              </div>

            </div>

            {/* ERROR */}
            {error && (
              <div
                className="create-decision-error"
                role="alert"
              >
                <div className="create-error-icon">
                  !
                </div>

                <div>
                  <strong>
                    Unable to create decision
                  </strong>

                  <p>{error}</p>
                </div>
              </div>
            )}

            {/* ACTION BAR */}
            <div className="create-decision-actions">

              <button
                type="button"
                className="create-decision-cancel"
                onClick={() => navigate("/decisions")}
                disabled={isSubmitting}
              >
                Cancel
              </button>

              <button
                type="submit"
                className="create-decision-submit"
                disabled={isSubmitting}
              >
                <Save size={17} />

                {isSubmitting
                  ? "Creating..."
                  : "Create Decision"}
              </button>

            </div>

          </form>
        </section>

      </div>
    </main>
  );
}