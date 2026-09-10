import {
  AlertTriangle,
  ArrowLeft,
  CheckCircle2,
  DollarSign,
  Edit3,
  Gauge,
  Loader2,
  Plus,
  ShieldAlert,
  XCircle,
} from "lucide-react";
import { useEffect, useState, type FormEvent } from "react";
import { useNavigate, useParams } from "react-router-dom";

import Alert from "../components/Alert";
import Button from "../components/Button";
import Card from "../components/Card";
import Input from "../components/Input";
import {
  compareAlternatives,
  createAlternative,
  getAlternatives,
  updateAlternative,
  type Alternative,
  type AlternativeComparison,
  type AlternativePayload,
  type RiskLevel,
} from "../services/alternativeService";

import "./AlternativesPage.css";

interface AlternativeForm {
  name: string;
  description: string;
  pros: string;
  cons: string;
  estimated_cost: string;
  feasibility_score: string;
  risk_level: RiskLevel;
}

interface FormErrors {
  name?: string;
  description?: string;
  pros?: string;
  cons?: string;
  estimated_cost?: string;
  feasibility_score?: string;
}

const initialForm: AlternativeForm = {
  name: "",
  description: "",
  pros: "",
  cons: "",
  estimated_cost: "",
  feasibility_score: "3",
  risk_level: "Medium",
};

const riskLevels: RiskLevel[] = [
  "Low",
  "Medium",
  "High",
  "Critical",
];

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
      return "The submitted alternative data is invalid.";
    case 401:
      return "Your session has expired. Please log in again.";
    case 403:
      return "You do not have permission to perform this action.";
    case 404:
      return "The decision or alternative could not be found.";
    case 422:
      return "Please check the entered values.";
    case 500:
      return "The server encountered an error. Please try again.";
    default:
      return "Something went wrong. Please try again.";
  }
}

function validateForm(form: AlternativeForm): FormErrors {
  const errors: FormErrors = {};

  const name = form.name.trim();
  const description = form.description.trim();
  const pros = form.pros.trim();
  const cons = form.cons.trim();
  const cost = Number(form.estimated_cost);
  const feasibility = Number(form.feasibility_score);

  if (!name) {
    errors.name = "Alternative name is required.";
  }

  if (!description) {
    errors.description = "Description is required.";
  }

  if (!pros) {
    errors.pros = "At least one advantage is required.";
  }

  if (!cons) {
    errors.cons = "At least one disadvantage is required.";
  }

  if (!form.estimated_cost.trim()) {
    errors.estimated_cost = "Estimated cost is required.";
  } else if (!Number.isInteger(cost) || cost < 0) {
    errors.estimated_cost =
      "Estimated cost must be a whole number of 0 or greater.";
  }

  if (
    !Number.isInteger(feasibility) ||
    feasibility < 1 ||
    feasibility > 5
  ) {
    errors.feasibility_score =
      "Feasibility score must be between 1 and 5.";
  }

  return errors;
}

function formatCost(value: number): string {
  return new Intl.NumberFormat("en-IN").format(value);
}

function getRiskClass(risk: RiskLevel): string {
  return `risk-${risk.toLowerCase()}`;
}

function getRiskIcon(risk: RiskLevel) {
  if (risk === "Low") {
    return <CheckCircle2 size={15} />;
  }

  if (risk === "Medium") {
    return <AlertTriangle size={15} />;
  }

  return <ShieldAlert size={15} />;
}

export default function AlternativesPage() {
  const navigate = useNavigate();
  const { decisionId } = useParams<{ decisionId: string }>();

  const [alternatives, setAlternatives] = useState<Alternative[]>(
    [],
  );

  const [comparison, setComparison] =
    useState<AlternativeComparison | null>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [isComparing, setIsComparing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const [pageError, setPageError] = useState("");
  const [formError, setFormError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const [showForm, setShowForm] = useState(false);

  const [editingAlternative, setEditingAlternative] =
    useState<Alternative | null>(null);

  const [form, setForm] =
    useState<AlternativeForm>(initialForm);

  const [errors, setErrors] = useState<FormErrors>({});

  const parsedDecisionId = Number(decisionId);

  async function loadAlternatives() {
    if (
      !decisionId ||
      !Number.isInteger(parsedDecisionId) ||
      parsedDecisionId <= 0
    ) {
      setPageError("Invalid decision ID.");
      setIsLoading(false);
      return;
    }

    try {
      setIsLoading(true);
      setPageError("");

      const data = await getAlternatives(parsedDecisionId);

      setAlternatives(data);
    } catch (error) {
      setPageError(getErrorMessage(error));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadAlternatives();
  }, [decisionId]);

  function updateField(
    field: keyof AlternativeForm,
    value: string,
  ) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));

    setErrors((current) => ({
      ...current,
      [field]: undefined,
    }));

    setFormError("");
    setSuccessMessage("");
  }

  function openCreateForm() {
    setEditingAlternative(null);
    setForm(initialForm);
    setErrors({});
    setFormError("");
    setSuccessMessage("");
    setShowForm(true);
  }

  function openEditForm(alternative: Alternative) {
    setEditingAlternative(alternative);

    setForm({
      name: alternative.name,
      description: alternative.description,
      pros: alternative.pros,
      cons: alternative.cons,
      estimated_cost: String(alternative.estimated_cost),
      feasibility_score: String(
        alternative.feasibility_score,
      ),
      risk_level: alternative.risk_level,
    });

    setErrors({});
    setFormError("");
    setSuccessMessage("");
    setShowForm(true);
  }

  function closeForm() {
    if (isSaving) {
      return;
    }

    setShowForm(false);
    setEditingAlternative(null);
    setForm(initialForm);
    setErrors({});
    setFormError("");
  }

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    const validationErrors = validateForm(form);

    setErrors(validationErrors);
    setFormError("");
    setSuccessMessage("");

    if (Object.keys(validationErrors).length > 0) {
      return;
    }

    if (
      !Number.isInteger(parsedDecisionId) ||
      parsedDecisionId <= 0
    ) {
      setFormError("Invalid decision ID.");
      return;
    }

    const payload: AlternativePayload = {
      name: form.name.trim(),
      description: form.description.trim(),
      pros: form.pros.trim(),
      cons: form.cons.trim(),
      estimated_cost: Number(form.estimated_cost),
      feasibility_score: Number(form.feasibility_score),
      risk_level: form.risk_level,
    };

    try {
      setIsSaving(true);

      if (editingAlternative) {
        await updateAlternative(
          editingAlternative.id,
          payload,
        );

        setSuccessMessage(
          "Alternative updated successfully.",
        );
      } else {
        await createAlternative(
          parsedDecisionId,
          payload,
        );

        setSuccessMessage(
          "Alternative created successfully.",
        );
      }

      await loadAlternatives();

      setTimeout(() => {
        closeForm();
      }, 500);
    } catch (error) {
      setFormError(getErrorMessage(error));
    } finally {
      setIsSaving(false);
    }
  }

  async function handleCompare() {
    if (
      !Number.isInteger(parsedDecisionId) ||
      parsedDecisionId <= 0
    ) {
      setPageError("Invalid decision ID.");
      return;
    }

    try {
      setIsComparing(true);
      setPageError("");

      const data =
        await compareAlternatives(parsedDecisionId);

      setComparison(data);
    } catch (error) {
      setPageError(getErrorMessage(error));
    } finally {
      setIsComparing(false);
    }
  }

  if (isLoading) {
    return (
      <section className="alternatives-page">
        <div
          className="alternatives-loading"
          role="status"
          aria-live="polite"
        >
          <Loader2
            size={24}
            className="alternatives-spinner"
          />
          <span>Loading alternatives...</span>
        </div>
      </section>
    );
  }

  return (
    <section className="alternatives-page">
      <div className="alternatives-header">
        <button
          type="button"
          className="alternatives-back"
          onClick={() =>
            navigate(
              `/decisions/${parsedDecisionId}`,
            )
          }
        >
          <ArrowLeft size={18} />
          Back to Decision
        </button>

        <div className="alternatives-heading-row">
          <div>
            <p className="alternatives-eyebrow">
              Decision Analysis
            </p>

            <h1>Alternatives & Comparison</h1>

            <p className="alternatives-subtitle">
              Evaluate available approaches using cost,
              feasibility, and risk.
            </p>
          </div>

          <Button onClick={openCreateForm}>
            <Plus size={17} />
            Add Alternative
          </Button>
        </div>
      </div>

      {pageError && (
        <div className="alternatives-alert">
          <Alert variant="error">
            {pageError}
          </Alert>
        </div>
      )}

      {successMessage && (
        <div className="alternatives-alert">
          <Alert variant="success">
            {successMessage}
          </Alert>
        </div>
      )}

      <div className="alternatives-summary">
        <Card>
          <div className="alternatives-summary-card">
            <div className="alternatives-summary-icon">
              <Gauge size={20} />
            </div>

            <div>
              <span>Total Alternatives</span>
              <strong>{alternatives.length}</strong>
            </div>
          </div>
        </Card>

        <Card>
          <div className="alternatives-summary-card">
            <div className="alternatives-summary-icon">
              <DollarSign size={20} />
            </div>

            <div>
              <span>Lowest Cost</span>

              <strong>
                {alternatives.length > 0
                  ? `₹${formatCost(
                      Math.min(
                        ...alternatives.map(
                          (item) =>
                            item.estimated_cost,
                        ),
                      ),
                    )}`
                  : "—"}
              </strong>
            </div>
          </div>
        </Card>

        <Card>
          <div className="alternatives-summary-card">
            <div className="alternatives-summary-icon">
              <CheckCircle2 size={20} />
            </div>

            <div>
              <span>Highest Feasibility</span>

              <strong>
                {alternatives.length > 0
                  ? `${Math.max(
                      ...alternatives.map(
                        (item) =>
                          item.feasibility_score,
                      ),
                    )}/5`
                  : "—"}
              </strong>
            </div>
          </div>
        </Card>
      </div>

      <Card>
        <div className="alternatives-section-header">
          <div>
            <h2>Available Alternatives</h2>

            <p>
              Compare and refine the approaches
              associated with this decision.
            </p>
          </div>

          {alternatives.length >= 2 && (
            <Button
              variant="secondary"
              onClick={handleCompare}
              disabled={isComparing}
            >
              {isComparing ? (
                <>
                  <Loader2
                    size={16}
                    className="alternatives-spinner"
                  />
                  Comparing...
                </>
              ) : (
                <>
                  <Gauge size={16} />
                  Compare Alternatives
                </>
              )}
            </Button>
          )}
        </div>

        {alternatives.length === 0 ? (
          <div className="alternatives-empty">
            <div className="alternatives-empty-icon">
              <Gauge size={24} />
            </div>

            <h3>No alternatives yet</h3>

            <p>
              Add different approaches to evaluate
              this decision from multiple perspectives.
            </p>

            <Button onClick={openCreateForm}>
              <Plus size={17} />
              Add First Alternative
            </Button>
          </div>
        ) : (
          <div className="alternatives-grid">
            {alternatives.map((alternative) => (
              <article
                className="alternative-card"
                key={alternative.id}
              >
                <div className="alternative-card-top">
                  <div>
                    <span className="alternative-number">
                      Alternative #{alternative.id}
                    </span>

                    <h3>{alternative.name}</h3>
                  </div>

                  <button
                    type="button"
                    className="alternative-edit"
                    onClick={() =>
                      openEditForm(alternative)
                    }
                    aria-label={`Edit ${alternative.name}`}
                  >
                    <Edit3 size={16} />
                  </button>
                </div>

                <p className="alternative-description">
                  {alternative.description}
                </p>

                <div className="alternative-pros-cons">
                  <div className="alternative-pro">
                    <CheckCircle2 size={16} />

                    <div>
                      <span>Pros</span>
                      <p>{alternative.pros}</p>
                    </div>
                  </div>

                  <div className="alternative-cons">
                    <XCircle size={16} />

                    <div>
                      <span>Cons</span>
                      <p>{alternative.cons}</p>
                    </div>
                  </div>
                </div>

                <div className="alternative-metrics">
                  <div>
                    <span>Estimated Cost</span>

                    <strong>
                      ₹
                      {formatCost(
                        alternative.estimated_cost,
                      )}
                    </strong>
                  </div>

                  <div>
                    <span>Feasibility</span>

                    <strong>
                      {alternative.feasibility_score}/5
                    </strong>
                  </div>

                  <div>
                    <span>Risk</span>

                    <strong
                      className={`alternative-risk ${getRiskClass(
                        alternative.risk_level,
                      )}`}
                    >
                      {getRiskIcon(
                        alternative.risk_level,
                      )}
                      {alternative.risk_level}
                    </strong>
                  </div>
                </div>
              </article>
            ))}
          </div>
        )}
      </Card>

      {comparison && (
        <Card>
          <div className="comparison-section">
            <div className="alternatives-section-header">
              <div>
                <h2>Comparison</h2>

                <p>
                  Side-by-side comparison returned by
                  the decision analysis service.
                </p>
              </div>
            </div>

            {comparison.alternatives.length === 0 ? (
              <div className="comparison-empty">
                No alternatives are available for
                comparison.
              </div>
            ) : (
              <div className="comparison-table-wrapper">
                <table className="comparison-table">
                  <thead>
                    <tr>
                      <th>Alternative</th>
                      <th>Estimated Cost</th>
                      <th>Feasibility</th>
                      <th>Risk Level</th>
                    </tr>
                  </thead>

                  <tbody>
                    {comparison.alternatives.map(
                      (alternative) => (
                        <tr key={alternative.name}>
                          <td>
                            <strong>
                              {alternative.name}
                            </strong>
                          </td>

                          <td>
                            ₹
                            {formatCost(
                              alternative.estimated_cost,
                            )}
                          </td>

                          <td>
                            <div className="feasibility-cell">
                              <span>
                                {
                                  alternative.feasibility_score
                                }
                                /5
                              </span>

                              <div className="feasibility-bar">
                                <div
                                  className="feasibility-fill"
                                  style={{
                                    width: `${
                                      alternative.feasibility_score *
                                      20
                                    }%`,
                                  }}
                                />
                              </div>
                            </div>
                          </td>

                          <td>
                            <span
                              className={`comparison-risk ${getRiskClass(
                                alternative.risk_level,
                              )}`}
                            >
                              {getRiskIcon(
                                alternative.risk_level,
                              )}
                              {alternative.risk_level}
                            </span>
                          </td>
                        </tr>
                      ),
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </Card>
      )}

      {showForm && (
        <div
          className="alternative-modal-backdrop"
          role="presentation"
          onMouseDown={(event) => {
            if (
              event.target === event.currentTarget
            ) {
              closeForm();
            }
          }}
        >
          <div
            className="alternative-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="alternative-form-title"
          >
            <div className="alternative-modal-header">
              <div>
                <p className="alternatives-eyebrow">
                  Decision Analysis
                </p>

                <h2 id="alternative-form-title">
                  {editingAlternative
                    ? "Edit Alternative"
                    : "Add Alternative"}
                </h2>
              </div>

              <button
                type="button"
                className="alternative-modal-close"
                onClick={closeForm}
                disabled={isSaving}
                aria-label="Close"
              >
                ×
              </button>
            </div>

            {formError && (
              <div className="alternative-modal-alert">
                <Alert variant="error">
                  {formError}
                </Alert>
              </div>
            )}

            <form
              className="alternative-form"
              onSubmit={handleSubmit}
              noValidate
            >
              <Input
                label="Alternative Name"
                value={form.name}
                onChange={(event) =>
                  updateField(
                    "name",
                    event.target.value,
                  )
                }
                placeholder="Enter alternative name"
                disabled={isSaving}
                error={errors.name}
                required
              />

              <div className="alternative-form-field">
                <label htmlFor="alternative-description">
                  Description <span>*</span>
                </label>

                <textarea
                  id="alternative-description"
                  value={form.description}
                  onChange={(event) =>
                    updateField(
                      "description",
                      event.target.value,
                    )
                  }
                  placeholder="Describe this approach..."
                  rows={4}
                  disabled={isSaving}
                  aria-invalid={Boolean(
                    errors.description,
                  )}
                />

                {errors.description && (
                  <p className="alternative-field-error">
                    {errors.description}
                  </p>
                )}
              </div>

              <div className="alternative-form-grid">
                <div className="alternative-form-field">
                  <label htmlFor="alternative-pros">
                    Pros <span>*</span>
                  </label>

                  <textarea
                    id="alternative-pros"
                    value={form.pros}
                    onChange={(event) =>
                      updateField(
                        "pros",
                        event.target.value,
                      )
                    }
                    placeholder="Key advantages..."
                    rows={4}
                    disabled={isSaving}
                    aria-invalid={Boolean(
                      errors.pros,
                    )}
                  />

                  {errors.pros && (
                    <p className="alternative-field-error">
                      {errors.pros}
                    </p>
                  )}
                </div>

                <div className="alternative-form-field">
                  <label htmlFor="alternative-cons">
                    Cons <span>*</span>
                  </label>

                  <textarea
                    id="alternative-cons"
                    value={form.cons}
                    onChange={(event) =>
                      updateField(
                        "cons",
                        event.target.value,
                      )
                    }
                    placeholder="Key disadvantages..."
                    rows={4}
                    disabled={isSaving}
                    aria-invalid={Boolean(
                      errors.cons,
                    )}
                  />

                  {errors.cons && (
                    <p className="alternative-field-error">
                      {errors.cons}
                    </p>
                  )}
                </div>
              </div>

              <div className="alternative-form-grid">
                <div className="alternative-form-field">
                  <label htmlFor="estimated-cost">
                    Estimated Cost <span>*</span>
                  </label>

                  <div className="alternative-input-prefix">
                    <span>₹</span>

                    <input
                      id="estimated-cost"
                      type="number"
                      min="0"
                      step="1"
                      value={form.estimated_cost}
                      onChange={(event) =>
                        updateField(
                          "estimated_cost",
                          event.target.value,
                        )
                      }
                      placeholder="0"
                      disabled={isSaving}
                      aria-invalid={Boolean(
                        errors.estimated_cost,
                      )}
                    />
                  </div>

                  {errors.estimated_cost && (
                    <p className="alternative-field-error">
                      {errors.estimated_cost}
                    </p>
                  )}
                </div>

                <div className="alternative-form-field">
                  <label htmlFor="feasibility-score">
                    Feasibility Score <span>*</span>
                  </label>

                  <select
                    id="feasibility-score"
                    value={form.feasibility_score}
                    onChange={(event) =>
                      updateField(
                        "feasibility_score",
                        event.target.value,
                      )
                    }
                    disabled={isSaving}
                  >
                    {[1, 2, 3, 4, 5].map(
                      (score) => (
                        <option
                          key={score}
                          value={score}
                        >
                          {score} / 5
                        </option>
                      ),
                    )}
                  </select>

                  {errors.feasibility_score && (
                    <p className="alternative-field-error">
                      {errors.feasibility_score}
                    </p>
                  )}
                </div>
              </div>

              <div className="alternative-form-field">
                <label htmlFor="risk-level">
                  Risk Level <span>*</span>
                </label>

                <select
                  id="risk-level"
                  value={form.risk_level}
                  onChange={(event) =>
                    updateField(
                      "risk_level",
                      event.target.value,
                    )
                  }
                  disabled={isSaving}
                >
                  {riskLevels.map((risk) => (
                    <option key={risk} value={risk}>
                      {risk}
                    </option>
                  ))}
                </select>
              </div>

              <div className="alternative-modal-actions">
                <Button
                  type="button"
                  variant="secondary"
                  onClick={closeForm}
                  disabled={isSaving}
                >
                  Cancel
                </Button>

                <Button
                  type="submit"
                  disabled={isSaving}
                >
                  {isSaving ? (
                    <>
                      <Loader2
                        size={16}
                        className="alternatives-spinner"
                      />
                      Saving...
                    </>
                  ) : (
                    <>
                      <CheckCircle2 size={16} />
                      {editingAlternative
                        ? "Save Changes"
                        : "Create Alternative"}
                    </>
                  )}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </section>
  );
}