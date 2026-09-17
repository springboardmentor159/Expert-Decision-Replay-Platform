import {
  useEffect,
  useState,
  type ChangeEvent,
  type FormEvent,
} from "react";
import {
  AlertCircle,
  ArrowLeft,
  CheckCircle2,
  FileText,
  Save,
} from "lucide-react";
import { useNavigate, useParams } from "react-router-dom";
import { isAxiosError } from "axios";

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

  const [decision, setDecision] =
    useState<Decision | null>(null);

  const [isLoading, setIsLoading] =
    useState(true);

  const [isSaving, setIsSaving] =
    useState(false);

  const [error, setError] =
    useState("");

  const [success, setSuccess] =
    useState("");

  const loadDecision = async () => {
    if (!id) {
      setError("Invalid decision ID.");
      setIsLoading(false);
      return;
    }

    try {
      setIsLoading(true);
      setError("");

      const response =
        await api.get<Decision>(
          `/decisions/${id}`,
        );

      setDecision(response.data);

      setForm({
        title: response.data.title,
        problem_statement:
          response.data.problem_statement,
        category:
          response.data.category,
      });
    } catch (err: unknown) {
      const status = isAxiosError(err)
        ? err.response?.status
        : undefined;

      if (status === 401) {
        setError(
          "Your session has expired. Please sign in again.",
        );
      } else if (status === 403) {
        setError(
          "You do not have permission to edit this decision.",
        );
      } else if (status === 404) {
        setError(
          "Decision not found.",
        );
      } else if (
        status !== undefined &&
        status >= 500
      ) {
        setError(
          "Server error. Please try again later.",
        );
      } else if (
        isAxiosError(err) &&
        err.request
      ) {
        setError(
          "Unable to connect to the server. Make sure FastAPI is running.",
        );
      } else {
        setError(
          "Unable to load the decision.",
        );
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const timer =
      window.setTimeout(() => {
        if (!id) {
          setError(
            "Invalid decision ID.",
          );
          setIsLoading(false);
          return;
        }

        void loadDecision();
      }, 0);

    return () => {
      window.clearTimeout(timer);
    };
  }, [id]);

  const handleChange = (
    event: ChangeEvent<
      HTMLInputElement |
        HTMLTextAreaElement
    >,
  ) => {
    const {
      name,
      value,
    } = event.target;

    setForm((current) => ({
      ...current,
      [name]: value,
    }));

    if (error) {
      setError("");
    }

    if (success) {
      setSuccess("");
    }
  };

  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();

    setError("");
    setSuccess("");

    if (!form.title.trim()) {
      setError(
        "Please enter a decision title.",
      );
      return;
    }

    if (
      !form.problem_statement.trim()
    ) {
      setError(
        "Please enter the problem statement.",
      );
      return;
    }

    if (!form.category.trim()) {
      setError(
        "Please enter a category.",
      );
      return;
    }

    try {
      setIsSaving(true);

      await api.put(
        `/decisions/${id}`,
        {
          title:
            form.title.trim(),
          problem_statement:
            form.problem_statement.trim(),
          category:
            form.category.trim(),
        },
      );

      setSuccess(
        "Decision updated successfully.",
      );

      setTimeout(() => {
        navigate(
          `/decisions/${id}`,
        );
      }, 800);
    } catch (err: unknown) {
      const status = isAxiosError(err)
        ? err.response?.status
        : undefined;

      if (status === 400) {
        setError(
          isAxiosError(err) &&
            err.response?.data?.detail
            ? err.response.data.detail
            : "Invalid decision information.",
        );
      } else if (status === 401) {
        setError(
          "Your session has expired. Please sign in again.",
        );
      } else if (status === 403) {
        setError(
          isAxiosError(err) &&
            err.response?.data?.detail
            ? err.response.data.detail
            : "You do not have permission to edit this decision.",
        );
      } else if (status === 404) {
        setError(
          "Decision not found.",
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
        isAxiosError(err) &&
        err.request
      ) {
        setError(
          "Unable to connect to the server. Make sure FastAPI is running.",
        );
      } else {
        setError(
          "Unable to update the decision.",
        );
      }
    } finally {
      setIsSaving(false);
    }
  };

  const backToDecision = () => {
    navigate(`/decisions/${id}`);
  };

  if (isLoading) {
    return (
      <main className="edit-decision-loading-page">
        <div className="edit-decision-loading-card">
          <div className="loading-spinner" />

          <p>
            Loading decision...
          </p>
        </div>
      </main>
    );
  }

  if (error && !decision) {
    return (
      <main className="edit-decision-page">
        <section
          className="edit-decision-error-card"
          role="alert"
        >
          <div className="edit-decision-error-icon">
            <AlertCircle size={24} />
          </div>

          <div className="edit-decision-error-content">
            <p className="edit-decision-eyebrow">
              Decision Editor
            </p>

            <h1>
              Unable to load decision
            </h1>

            <p>{error}</p>

            <button
              type="button"
              className="edit-decision-secondary-button"
              onClick={
                backToDecision
              }
            >
              <ArrowLeft size={18} />

              Back to Decision
            </button>
          </div>
        </section>
      </main>
    );
  }

  if (!decision) {
    return null;
  }

  return (
    <main className="edit-decision-page">
      <div className="edit-decision-container">

        {/* HEADER */}

        <header className="edit-decision-header">
          <div className="edit-decision-heading">

            <div className="edit-decision-title-icon">
              <FileText size={23} />
            </div>

            <div>
              <p className="edit-decision-eyebrow">
                Expert Decision Replay Platform
              </p>

              <h1>
                Edit Decision
              </h1>

              <p className="edit-decision-reference">
                Update Decision #
                {decision.id}
              </p>
            </div>

          </div>

          <button
            type="button"
            className="edit-decision-secondary-button"
            onClick={
              backToDecision
            }
            disabled={isSaving}
          >
            <ArrowLeft size={18} />

            Back to Decision
          </button>
        </header>

        {/* FORM CARD */}

        <section className="edit-decision-card">

          <div className="edit-decision-card-header">

            <div className="edit-decision-card-icon">
              <Save size={21} />
            </div>

            <div>
              <h2>
                Edit Decision Information
              </h2>

              <p>
                Update the decision details
                and save your changes.
              </p>
            </div>

          </div>

          <form
            onSubmit={
              handleSubmit
            }
            className="edit-decision-form"
          >

            {/* TITLE */}

            <div className="edit-decision-field">

              <div className="edit-decision-field-heading">

                <label htmlFor="title">
                  Decision Title
                  <span>*</span>
                </label>

                <span>
                  Clear and recognizable
                  name
                </span>

              </div>

              <input
                id="title"
                name="title"
                type="text"
                value={
                  form.title
                }
                onChange={
                  handleChange
                }
                placeholder="Enter decision title"
                disabled={
                  isSaving
                }
              />

            </div>

            {/* CATEGORY */}

            <div className="edit-decision-field">

              <div className="edit-decision-field-heading">

                <label htmlFor="category">
                  Category
                  <span>*</span>
                </label>

                <span>
                  Area or domain of
                  the decision
                </span>

              </div>

              <input
                id="category"
                name="category"
                type="text"
                value={
                  form.category
                }
                onChange={
                  handleChange
                }
                placeholder="Enter category"
                disabled={
                  isSaving
                }
              />

            </div>

            {/* PROBLEM STATEMENT */}

            <div className="edit-decision-field">

              <div className="edit-decision-field-heading">

                <label htmlFor="problem_statement">
                  Problem Statement
                  <span>*</span>
                </label>

                <span>
                  Explain the situation
                  or challenge
                </span>

              </div>

              <textarea
                id="problem_statement"
                name="problem_statement"
                value={
                  form.problem_statement
                }
                onChange={
                  handleChange
                }
                placeholder="Describe the problem"
                rows={7}
                disabled={
                  isSaving
                }
              />

              <div className="edit-decision-textarea-footer">

                <span>
                  Provide enough context
                  for the decision to
                  be understood clearly.
                </span>

                <strong>
                  {
                    form
                      .problem_statement
                      .length
                  }{" "}
                  characters
                </strong>

              </div>

            </div>

            {/* ERROR */}

            {error && (
              <div
                className="edit-decision-alert error"
                role="alert"
              >
                <AlertCircle
                  size={18}
                />

                <div>
                  <strong>
                    Unable to save
                    changes
                  </strong>

                  <p>
                    {error}
                  </p>
                </div>
              </div>
            )}

            {/* SUCCESS */}

            {success && (
              <div
                className="edit-decision-alert success"
                role="status"
              >
                <CheckCircle2
                  size={18}
                />

                <div>
                  <strong>
                    Changes saved
                  </strong>

                  <p>
                    {success}
                  </p>
                </div>
              </div>
            )}

            {/* ACTIONS */}

            <div className="edit-decision-actions">

              <button
                type="button"
                className="edit-decision-cancel"
                onClick={
                  backToDecision
                }
                disabled={
                  isSaving
                }
              >
                Cancel
              </button>

              <button
                type="submit"
                className="edit-decision-submit"
                disabled={
                  isSaving
                }
              >
                <Save size={18} />

                {isSaving
                  ? "Saving Changes..."
                  : "Save Changes"}
              </button>

            </div>

          </form>
        </section>
      </div>
    </main>
  );
}