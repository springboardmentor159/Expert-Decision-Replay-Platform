import {
  ArrowLeft,
  CheckCircle2,
  FileText,
  FolderKanban,
  Loader2,
  Save,
  Tag,
} from "lucide-react";
import { useEffect, useState, type FormEvent } from "react";
import { useNavigate, useParams } from "react-router-dom";

import Alert from "../components/Alert";
import Button from "../components/Button";
import Card from "../components/Card";
import Input from "../components/Input";
import {
  getDecision,
  updateDecision,
  type Decision,
} from "../services/decisionService";

import "./EditDecisionPage.css";

interface FormState {
  title: string;
  problem_statement: string;
  category: string;
  tags: string;
}

interface FormErrors {
  title?: string;
  problem_statement?: string;
  category?: string;
  tags?: string;
}

function getErrorMessage(error: unknown): string {
  const response = (
    error as {
      response?: {
        status?: number;
        data?: {
          detail?: string | Array<{ msg?: string }>;
        };
      };
    }
  ).response;

  const detail = response?.data?.detail;

  if (Array.isArray(detail)) {
    return detail
      .map((item) => item.msg)
      .filter(Boolean)
      .join(", ");
  }

  if (typeof detail === "string") {
    return detail;
  }

  switch (response?.status) {
    case 400:
      return "The submitted decision data is invalid.";
    case 401:
      return "Your session has expired. Please log in again.";
    case 403:
      return "You do not have permission to edit this decision.";
    case 404:
      return "The decision could not be found.";
    case 422:
      return "Please check the entered values.";
    case 500:
      return "The server encountered an error. Please try again.";
    default:
      return "Unable to save the decision. Please try again.";
  }
}

function validateForm(form: FormState): FormErrors {
  const errors: FormErrors = {};

  const title = form.title.trim();
  const problemStatement = form.problem_statement.trim();
  const category = form.category.trim();
  const tags = form.tags.trim();

  if (!title) {
    errors.title = "Decision title is required.";
  } else if (title.length < 3) {
    errors.title = "Title must contain at least 3 characters.";
  } else if (title.length > 120) {
    errors.title = "Title must not exceed 120 characters.";
  }

  if (!problemStatement) {
    errors.problem_statement = "Problem statement is required.";
  } else if (problemStatement.length < 10) {
    errors.problem_statement =
      "Problem statement must contain at least 10 characters.";
  } else if (problemStatement.length > 2000) {
    errors.problem_statement =
      "Problem statement must not exceed 2000 characters.";
  }

  if (!category) {
    errors.category = "Category is required.";
  } else if (category.length > 80) {
    errors.category = "Category must not exceed 80 characters.";
  }

  if (tags.length > 250) {
    errors.tags = "Tags must not exceed 250 characters.";
  }

  return errors;
}

export default function EditDecisionPage() {
  const navigate = useNavigate();
  const { decisionId } = useParams<{ decisionId: string }>();

  const [decision, setDecision] = useState<Decision | null>(null);

  const [form, setForm] = useState<FormState>({
    title: "",
    problem_statement: "",
    category: "",
    tags: "",
  });

  const [errors, setErrors] = useState<FormErrors>({});
  const [pageError, setPageError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (!decisionId) {
      setPageError("Invalid decision ID.");
      setIsLoading(false);
      return;
    }

    const id = Number(decisionId);

    if (!Number.isInteger(id) || id <= 0) {
      setPageError("Invalid decision ID.");
      setIsLoading(false);
      return;
    }

    let isMounted = true;

    async function loadDecision() {
      try {
        setIsLoading(true);
        setPageError("");

        const data = await getDecision(id);

        if (!isMounted) {
          return;
        }

        setDecision(data);

        setForm({
          title: data.title,
          problem_statement: data.problem_statement,
          category: data.category,
          tags: data.tags ?? "",
        });
      } catch (error) {
        if (!isMounted) {
          return;
        }

        setPageError(getErrorMessage(error));
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    void loadDecision();

    return () => {
      isMounted = false;
    };
  }, [decisionId]);

  function updateField(field: keyof FormState, value: string) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));

    setErrors((current) => ({
      ...current,
      [field]: undefined,
    }));

    setPageError("");
    setSuccessMessage("");
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const validationErrors = validateForm(form);

    setErrors(validationErrors);
    setPageError("");
    setSuccessMessage("");

    if (Object.keys(validationErrors).length > 0) {
      return;
    }

    if (!decision) {
      setPageError("Decision data is unavailable.");
      return;
    }

    try {
      setIsSaving(true);

      const updatedDecision = await updateDecision(decision.id, {
        title: form.title.trim(),
        problem_statement: form.problem_statement.trim(),
        category: form.category.trim(),
        tags: form.tags.trim() || null,
      });

      setDecision(updatedDecision);
      setSuccessMessage("Decision updated successfully.");

      setTimeout(() => {
        navigate(`/decisions/${updatedDecision.id}`);
      }, 700);
    } catch (error) {
      setPageError(getErrorMessage(error));
    } finally {
      setIsSaving(false);
    }
  }

  function handleCancel() {
    if (decision) {
      navigate(`/decisions/${decision.id}`);
      return;
    }

    navigate("/decisions");
  }

  if (isLoading) {
    return (
      <section className="edit-decision-page">
        <div
          className="edit-decision-loading"
          role="status"
          aria-live="polite"
        >
          <Loader2 size={24} className="edit-decision-spinner" />
          <span>Loading decision...</span>
        </div>
      </section>
    );
  }

  if (pageError && !decision) {
    return (
      <section className="edit-decision-page">
        <div className="edit-decision-header">
          <button
            type="button"
            className="edit-decision-back"
            onClick={() => navigate("/decisions")}
          >
            <ArrowLeft size={18} />
            Back to Decisions
          </button>

          <div>
            <p className="edit-decision-eyebrow">Decision Management</p>
            <h1>Edit Decision</h1>
            <p className="edit-decision-subtitle">
              Update the decision information.
            </p>
          </div>
        </div>

        <Alert variant="error">{pageError}</Alert>
      </section>
    );
  }

  return (
    <section className="edit-decision-page">
      <div className="edit-decision-header">
        <button
          type="button"
          className="edit-decision-back"
          onClick={handleCancel}
        >
          <ArrowLeft size={18} />
          Back to Decision
        </button>

        <div className="edit-decision-heading-row">
          <div>
            <p className="edit-decision-eyebrow">Decision Management</p>
            <h1>Edit Decision</h1>
            <p className="edit-decision-subtitle">
              Refine the decision details while preserving its history.
            </p>
          </div>

          {decision && (
            <div className="edit-decision-version">
              <span>Decision</span>
              <strong>#{decision.id}</strong>
            </div>
          )}
        </div>
      </div>

      <div className="edit-decision-content">
        <Card>
          <div className="edit-decision-card-header">
            <div className="edit-decision-card-icon">
              <FileText size={20} />
            </div>

            <div>
              <h2>Decision Information</h2>
              <p>
                Update the core information associated with this decision.
              </p>
            </div>
          </div>

          {pageError && (
            <div className="edit-decision-alert">
              <Alert variant="error">{pageError}</Alert>
            </div>
          )}

          {successMessage && (
            <div className="edit-decision-alert">
              <Alert variant="success">{successMessage}</Alert>
            </div>
          )}

          <form
            className="edit-decision-form"
            onSubmit={handleSubmit}
            noValidate
          >
            <div className="edit-decision-field">
              <Input
                label="Decision Title"
                value={form.title}
                onChange={(event) =>
                  updateField("title", event.target.value)
                }
                placeholder="Enter the decision title"
                disabled={isSaving}
                error={errors.title}
                required
              />

              <span className="edit-decision-counter">
                {form.title.length}/120
              </span>
            </div>

            <div className="edit-decision-field">
              <label htmlFor="problem_statement">
                Problem Statement <span>*</span>
              </label>

              <textarea
                id="problem_statement"
                value={form.problem_statement}
                onChange={(event) =>
                  updateField("problem_statement", event.target.value)
                }
                placeholder="Describe the problem or situation that led to this decision..."
                disabled={isSaving}
                maxLength={2000}
                rows={7}
                aria-invalid={Boolean(errors.problem_statement)}
              />

              {errors.problem_statement && (
                <p className="edit-decision-field-error">
                  {errors.problem_statement}
                </p>
              )}

              <span className="edit-decision-counter">
                {form.problem_statement.length}/2000
              </span>
            </div>

            <div className="edit-decision-grid">
              <div className="edit-decision-field">
                <label htmlFor="category">
                  <FolderKanban size={16} />
                  Category <span>*</span>
                </label>

                <input
                  id="category"
                  type="text"
                  value={form.category}
                  onChange={(event) =>
                    updateField("category", event.target.value)
                  }
                  placeholder="e.g. Technology, Operations"
                  disabled={isSaving}
                  maxLength={80}
                  aria-invalid={Boolean(errors.category)}
                />

                {errors.category && (
                  <p className="edit-decision-field-error">
                    {errors.category}
                  </p>
                )}
              </div>

              <div className="edit-decision-field">
                <label htmlFor="tags">
                  <Tag size={16} />
                  Tags
                </label>

                <input
                  id="tags"
                  type="text"
                  value={form.tags}
                  onChange={(event) =>
                    updateField("tags", event.target.value)
                  }
                  placeholder="e.g. AI, Security, Process"
                  disabled={isSaving}
                  maxLength={250}
                  aria-invalid={Boolean(errors.tags)}
                />

                {errors.tags && (
                  <p className="edit-decision-field-error">
                    {errors.tags}
                  </p>
                )}

                <small>Separate multiple tags with commas.</small>
              </div>
            </div>

            <div className="edit-decision-info">
              <CheckCircle2 size={18} />

              <div>
                <strong>Version history is preserved</strong>

                <p>
                  Saving changes creates a new decision version through the
                  existing backend workflow.
                </p>
              </div>
            </div>

            <div className="edit-decision-actions">
              <Button
                type="button"
                variant="secondary"
                onClick={handleCancel}
                disabled={isSaving}
              >
                Cancel
              </Button>

              <Button type="submit" disabled={isSaving}>
                {isSaving ? (
                  <>
                    <Loader2
                      size={17}
                      className="edit-decision-spinner"
                    />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save size={17} />
                    Save Changes
                  </>
                )}
              </Button>
            </div>
          </form>
        </Card>
      </div>
    </section>
  );
}