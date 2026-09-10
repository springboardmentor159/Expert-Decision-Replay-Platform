import { useState, type FormEvent } from "react";
import {
  ArrowLeft,
  ArrowRight,
  CheckCircle2,
  FileText,
  FolderKanban,
  Lightbulb,
  Loader2,
  Tag,
} from "lucide-react";
import { Link, useNavigate } from "react-router-dom";

import Alert from "../components/Alert";
import { createDecision, type DecisionCreatePayload } from "../services/decisionService";
import "./CreateDecisionPage.css";

interface FormErrors {
  title?: string;
  problem_statement?: string;
  category?: string;
}

const MAX_TITLE_LENGTH = 120;
const MAX_PROBLEM_LENGTH = 2000;
const MAX_CATEGORY_LENGTH = 80;
const MAX_TAGS_LENGTH = 250;

export default function CreateDecisionPage() {
  const navigate = useNavigate();

  const [title, setTitle] = useState("");
  const [problemStatement, setProblemStatement] = useState("");
  const [category, setCategory] = useState("");
  const [tags, setTags] = useState("");

  const [errors, setErrors] = useState<FormErrors>({});
  const [errorMessage, setErrorMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  function validateForm(): FormErrors {
    const validationErrors: FormErrors = {};

    const trimmedTitle = title.trim();
    const trimmedProblem = problemStatement.trim();
    const trimmedCategory = category.trim();

    if (!trimmedTitle) {
      validationErrors.title = "Decision title is required.";
    } else if (trimmedTitle.length < 3) {
      validationErrors.title =
        "Decision title must contain at least 3 characters.";
    } else if (trimmedTitle.length > MAX_TITLE_LENGTH) {
      validationErrors.title = `Decision title must not exceed ${MAX_TITLE_LENGTH} characters.`;
    }

    if (!trimmedProblem) {
      validationErrors.problem_statement =
        "Problem statement is required.";
    } else if (trimmedProblem.length < 10) {
      validationErrors.problem_statement =
        "Problem statement must contain at least 10 characters.";
    } else if (trimmedProblem.length > MAX_PROBLEM_LENGTH) {
      validationErrors.problem_statement =
        `Problem statement must not exceed ${MAX_PROBLEM_LENGTH} characters.`;
    }

    if (!trimmedCategory) {
      validationErrors.category = "Category is required.";
    } else if (trimmedCategory.length > MAX_CATEGORY_LENGTH) {
      validationErrors.category =
        `Category must not exceed ${MAX_CATEGORY_LENGTH} characters.`;
    }

    if (tags.trim().length > MAX_TAGS_LENGTH) {
      setErrorMessage(
        `Tags must not exceed ${MAX_TAGS_LENGTH} characters.`,
      );
    }

    return validationErrors;
  }

  function clearFieldError(field: keyof FormErrors) {
    setErrors((current) => ({
      ...current,
      [field]: undefined,
    }));

    setErrorMessage("");
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setErrorMessage("");

    const validationErrors = validateForm();
    setErrors(validationErrors);

    if (
      Object.keys(validationErrors).length > 0 ||
      tags.trim().length > MAX_TAGS_LENGTH
    ) {
      return;
    }

    setIsSubmitting(true);

    const payload: DecisionCreatePayload = {
      title: title.trim(),
      problem_statement: problemStatement.trim(),
      category: category.trim(),
      tags: tags.trim() || null,
    };

    try {
      const decision = await createDecision(payload);

      navigate(`/decisions/${decision.id}`, {
        replace: true,
      });
    } catch (error: unknown) {
      const response = (
        error as {
          response?: {
            status?: number;
            data?: {
              detail?: string;
            };
          };
        }
      )?.response;

      if (response?.status === 401) {
        setErrorMessage(
          "Your session has expired. Please sign in again.",
        );
      } else if (response?.status === 403) {
        setErrorMessage(
          "You do not have permission to create a decision.",
        );
      } else if (response?.status === 422) {
        setErrorMessage(
          "Please check the entered information and try again.",
        );
      } else if (response?.status === 400) {
        setErrorMessage(
          response.data?.detail ||
            "The decision could not be created.",
        );
      } else if (
        response?.status &&
        response.status >= 500
      ) {
        setErrorMessage(
          "The server is temporarily unavailable. Please try again.",
        );
      } else {
        setErrorMessage(
          "Unable to create the decision right now. Please try again.",
        );
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="create-decision-page">
      <header className="create-decision-header">
        <div>
          <Link
            to="/decisions"
            className="create-decision-back"
          >
            <ArrowLeft size={16} aria-hidden="true" />
            <span>Back to Decisions</span>
          </Link>

          <div className="create-decision-heading">
            <span className="create-decision-kicker">
              DECISION MANAGEMENT
            </span>

            <h1>Create a new decision</h1>

            <p>
              Capture the problem, context, and classification
              behind an organizational decision.
            </p>
          </div>
        </div>

        <div className="create-decision-status">
          <span className="create-decision-status-dot" />
          Draft
        </div>
      </header>

      <div className="create-decision-layout">
        <main className="create-decision-main">
          <section className="create-decision-card">
            <div className="create-decision-card-header">
              <div className="create-decision-card-icon">
                <FileText
                  size={20}
                  strokeWidth={1.8}
                  aria-hidden="true"
                />
              </div>

              <div>
                <h2>Decision information</h2>
                <p>
                  Start with the essential information that
                  defines the decision.
                </p>
              </div>
            </div>

            {errorMessage && (
              <div className="create-decision-alert">
                <Alert variant="error">{errorMessage}</Alert>
              </div>
            )}

            <form
              className="create-decision-form"
              onSubmit={handleSubmit}
              noValidate
            >
              <div className="create-decision-field">
                <div className="create-decision-label-row">
                  <label htmlFor="decision-title">
                    Decision title
                  </label>

                  <span>
                    {title.length}/{MAX_TITLE_LENGTH}
                  </span>
                </div>

                <input
                  id="decision-title"
                  name="title"
                  type="text"
                  value={title}
                  onChange={(event) => {
                    setTitle(event.target.value);
                    clearFieldError("title");
                  }}
                  maxLength={MAX_TITLE_LENGTH}
                  placeholder="e.g. Migrate customer data to the new platform"
                  disabled={isSubmitting}
                  aria-invalid={Boolean(errors.title)}
                  aria-describedby={
                    errors.title
                      ? "decision-title-error"
                      : undefined
                  }
                  required
                />

                {errors.title && (
                  <span
                    id="decision-title-error"
                    className="create-decision-field-error"
                    role="alert"
                  >
                    {errors.title}
                  </span>
                )}

                {!errors.title && (
                  <span className="create-decision-helper">
                    Use a concise title that clearly identifies
                    the decision.
                  </span>
                )}
              </div>

              <div className="create-decision-field">
                <div className="create-decision-label-row">
                  <label htmlFor="problem-statement">
                    Problem statement
                  </label>

                  <span>
                    {problemStatement.length}/{MAX_PROBLEM_LENGTH}
                  </span>
                </div>

                <textarea
                  id="problem-statement"
                  name="problem_statement"
                  value={problemStatement}
                  onChange={(event) => {
                    setProblemStatement(event.target.value);
                    clearFieldError("problem_statement");
                  }}
                  maxLength={MAX_PROBLEM_LENGTH}
                  placeholder="Describe the problem, situation, or business context that requires a decision..."
                  rows={8}
                  disabled={isSubmitting}
                  aria-invalid={Boolean(
                    errors.problem_statement,
                  )}
                  aria-describedby={
                    errors.problem_statement
                      ? "problem-statement-error"
                      : "problem-statement-helper"
                  }
                  required
                />

                {errors.problem_statement && (
                  <span
                    id="problem-statement-error"
                    className="create-decision-field-error"
                    role="alert"
                  >
                    {errors.problem_statement}
                  </span>
                )}

                {!errors.problem_statement && (
                  <span
                    id="problem-statement-helper"
                    className="create-decision-helper"
                  >
                    Explain why the decision is needed and provide
                    enough context for future review and replay.
                  </span>
                )}
              </div>

              <div className="create-decision-divider" />

              <div className="create-decision-section-heading">
                <div className="create-decision-section-icon">
                  <FolderKanban
                    size={17}
                    strokeWidth={1.8}
                    aria-hidden="true"
                  />
                </div>

                <div>
                  <h3>Classification</h3>
                  <p>
                    Organize the decision so it can be found and
                    reviewed later.
                  </p>
                </div>
              </div>

              <div className="create-decision-two-column">
                <div className="create-decision-field">
                  <div className="create-decision-label-row">
                    <label htmlFor="decision-category">
                      Category
                    </label>

                    <span>
                      {category.length}/{MAX_CATEGORY_LENGTH}
                    </span>
                  </div>

                  <input
                    id="decision-category"
                    name="category"
                    type="text"
                    value={category}
                    onChange={(event) => {
                      setCategory(event.target.value);
                      clearFieldError("category");
                    }}
                    maxLength={MAX_CATEGORY_LENGTH}
                    placeholder="Technology, Finance, Operations..."
                    disabled={isSubmitting}
                    aria-invalid={Boolean(errors.category)}
                    aria-describedby={
                      errors.category
                        ? "decision-category-error"
                        : undefined
                    }
                    required
                  />

                  {errors.category && (
                    <span
                      id="decision-category-error"
                      className="create-decision-field-error"
                      role="alert"
                    >
                      {errors.category}
                    </span>
                  )}
                </div>

                <div className="create-decision-field">
                  <div className="create-decision-label-row">
                    <label htmlFor="decision-tags">
                      Tags
                    </label>

                    <span>
                      {tags.length}/{MAX_TAGS_LENGTH}
                    </span>
                  </div>

                  <div className="create-decision-input-with-icon">
                    <Tag
                      size={17}
                      strokeWidth={1.8}
                      aria-hidden="true"
                    />

                    <input
                      id="decision-tags"
                      name="tags"
                      type="text"
                      value={tags}
                      onChange={(event) => {
                        setTags(event.target.value);
                        setErrorMessage("");
                      }}
                      maxLength={MAX_TAGS_LENGTH}
                      placeholder="security, migration, architecture"
                      disabled={isSubmitting}
                    />
                  </div>

                  <span className="create-decision-helper">
                    Add relevant keywords separated by commas.
                  </span>
                </div>
              </div>

              <div className="create-decision-guidance">
                <div className="create-decision-guidance-icon">
                  <Lightbulb
                    size={17}
                    strokeWidth={1.8}
                    aria-hidden="true"
                  />
                </div>

                <div>
                  <strong>Good decision records are contextual.</strong>

                  <span>
                    Describe the situation clearly so the reasoning
                    behind this decision can be understood and
                    revisited later.
                  </span>
                </div>
              </div>

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
                  {isSubmitting ? (
                    <>
                      <Loader2
                        size={18}
                        className="create-decision-spinner"
                        aria-hidden="true"
                      />
                      <span>Creating...</span>
                    </>
                  ) : (
                    <>
                      <span>Create Decision</span>
                      <ArrowRight
                        size={18}
                        strokeWidth={2}
                        aria-hidden="true"
                      />
                    </>
                  )}
                </button>
              </div>
            </form>
          </section>
        </main>

        <aside className="create-decision-sidebar">
          <section className="create-decision-sidebar-card">
            <div className="create-decision-sidebar-header">
              <span className="create-decision-sidebar-kicker">
                DECISION LIFECYCLE
              </span>

              <h2>Build the record</h2>

              <p>
                This information becomes the foundation for the
                decision's review and history.
              </p>
            </div>

            <div className="create-decision-steps">
              <div className="create-decision-step active">
                <div className="create-decision-step-marker">
                  <CheckCircle2
                    size={15}
                    strokeWidth={2}
                    aria-hidden="true"
                  />
                </div>

                <div>
                  <strong>Decision context</strong>
                  <span>
                    Capture the problem and circumstances.
                  </span>
                </div>
              </div>

              <div className="create-decision-step-line" />

              <div className="create-decision-step">
                <div className="create-decision-step-marker">
                  02
                </div>

                <div>
                  <strong>Analysis</strong>
                  <span>
                    Evaluate alternatives and supporting reasoning.
                  </span>
                </div>
              </div>

              <div className="create-decision-step-line" />

              <div className="create-decision-step">
                <div className="create-decision-step-marker">
                  03
                </div>

                <div>
                  <strong>Review &amp; approval</strong>
                  <span>
                    Collaborate and record the outcome.
                  </span>
                </div>
              </div>

              <div className="create-decision-step-line" />

              <div className="create-decision-step">
                <div className="create-decision-step-marker">
                  04
                </div>

                <div>
                  <strong>Replay</strong>
                  <span>
                    Preserve the decision history and knowledge.
                  </span>
                </div>
              </div>
            </div>
          </section>

          <section className="create-decision-sidebar-note">
            <div className="create-decision-sidebar-note-icon">
              <Lightbulb
                size={17}
                strokeWidth={1.8}
                aria-hidden="true"
              />
            </div>

            <div>
              <strong>Start with the why.</strong>

              <span>
                A clear problem statement makes the decision
                easier to understand when it is revisited later.
              </span>
            </div>
          </section>
        </aside>
      </div>
    </div>
  );
}