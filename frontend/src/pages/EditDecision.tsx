import { useEffect, useState, type FormEvent } from "react";
import { ArrowLeft, Save } from "lucide-react";
import { useNavigate, useParams } from "react-router-dom";

import api from "../services/api";

interface Decision {
  id: number;
  title: string;
  problem_statement: string;
  category: string;
  status: string;
  created_by: number;
  created_at: string;
  updated_at: string;
}

export default function EditDecision() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    title: "",
    problem_statement: "",
    category: "",
  });

  const [decision, setDecision] = useState<Decision | null>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const loadDecision = async () => {
    try {
      setIsLoading(true);
      setError("");

      const response = await api.get<Decision>(
        `/decisions/${id}`,
      );

      setDecision(response.data);

      setForm({
        title: response.data.title,
        problem_statement: response.data.problem_statement,
        category: response.data.category,
      });
    } catch (err: any) {
      const status = err?.response?.status;

      if (status === 401) {
        setError(
          "Your session has expired. Please sign in again.",
        );
      } else if (status === 403) {
        setError(
          "You do not have permission to edit this decision.",
        );
      } else if (status === 404) {
        setError("Decision not found.");
      } else if (status >= 500) {
        setError(
          "Server error. Please try again later.",
        );
      } else if (err?.request) {
        setError(
          "Unable to connect to the server. Make sure FastAPI is running.",
        );
      } else {
        setError("Unable to load the decision.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (id) {
      loadDecision();
    }
  }, [id]);

  const handleChange = (
    event: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
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
    setSuccess("");

    if (!form.title.trim()) {
      setError("Please enter a decision title.");
      return;
    }

    if (!form.problem_statement.trim()) {
      setError("Please enter the problem statement.");
      return;
    }

    if (!form.category.trim()) {
      setError("Please enter a category.");
      return;
    }

    try {
      setIsSaving(true);

      await api.put(`/decisions/${id}`, {
        title: form.title.trim(),
        problem_statement: form.problem_statement.trim(),
        category: form.category.trim(),
      });

      setSuccess("Decision updated successfully.");

      setTimeout(() => {
        navigate(`/decisions/${id}`);
      }, 800);
    } catch (err: any) {
      const status = err?.response?.status;

      if (status === 400) {
        setError(
          err?.response?.data?.detail ||
            "Invalid decision information.",
        );
      } else if (status === 401) {
        setError(
          "Your session has expired. Please sign in again.",
        );
      } else if (status === 403) {
        setError(
          err?.response?.data?.detail ||
            "You do not have permission to edit this decision.",
        );
      } else if (status === 404) {
        setError("Decision not found.");
      } else if (status === 422) {
        setError(
          "Please check the entered information.",
        );
      } else if (status >= 500) {
        setError(
          "Server error. Please try again later.",
        );
      } else if (err?.request) {
        setError(
          "Unable to connect to the server. Make sure FastAPI is running.",
        );
      } else {
        setError("Unable to update the decision.");
      }
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <main className="decision-loading">
        <div className="loading-spinner" />
        <p>Loading decision...</p>
      </main>
    );
  }

  if (error && !decision) {
    return (
      <main className="decision-page">
        <section className="decision-error" role="alert">
          <h2>Unable to load decision</h2>

          <p>{error}</p>

          <button
            className="secondary-button"
            onClick={() => navigate(`/decisions/${id}`)}
          >
            <ArrowLeft size={18} />
            Back to Decision
          </button>
        </section>
      </main>
    );
  }

  return (
    <main className="decision-details-page">
      <header className="page-header">
        <div>
          <p className="page-eyebrow">
            Expert Decision Replay Platform
          </p>

          <h1>Edit Decision</h1>

          <p>
            Update Decision #{id}
          </p>
        </div>

        <button
          className="secondary-button"
          onClick={() => navigate(`/decisions/${id}`)}
          disabled={isSaving}
        >
          <ArrowLeft size={18} />
          Back to Decision
        </button>
      </header>

      <section className="decision-details-card">
        <div className="details-card-header">
          <div className="details-icon">
            <Save size={24} />
          </div>

          <div>
            <h2>Edit Decision Information</h2>

            <p>
              Update the decision details and save your
              changes.
            </p>
          </div>
        </div>

        <form
          onSubmit={handleSubmit}
          className="auth-form"
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
              placeholder="Enter decision title"
              disabled={isSaving}
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
              placeholder="Describe the problem"
              rows={6}
              disabled={isSaving}
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
              placeholder="Enter category"
              disabled={isSaving}
            />
          </div>

          {error && (
            <div className="auth-error" role="alert">
              {error}
            </div>
          )}

          {success && (
            <div className="auth-success" role="status">
              {success}
            </div>
          )}

          <div className="form-actions">
            <button
              type="button"
              className="secondary-button"
              onClick={() =>
                navigate(`/decisions/${id}`)
              }
              disabled={isSaving}
            >
              Cancel
            </button>

            <button
              type="submit"
              className="primary-button"
              disabled={isSaving}
            >
              <Save size={18} />

              {isSaving
                ? "Saving Changes..."
                : "Save Changes"}
            </button>
          </div>
        </form>
      </section>
    </main>
  );
}