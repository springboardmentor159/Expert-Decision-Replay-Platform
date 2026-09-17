import {
  useEffect,
  useState,
  type ChangeEvent,
  type FormEvent,
} from "react";

import {
  ArrowLeft,
  Edit3,
  Plus,
  RefreshCw,
  Save,
  Trash2,
  Scale,
  X,
  FileText,
  Gauge,
  ShieldAlert,
  CheckCircle2,
  MessageSquare,
  ClipboardCheck,
  History,
} from "lucide-react";

import {
  useNavigate,
  useParams,
} from "react-router-dom";

import axios from "axios";
import api from "../services/api";

interface Alternative {
  id: number;
  decision_id: number;
  name: string;
  description: string;
  pros: string;
  cons: string;
  estimated_cost: number;
  feasibility_score: number;
  risk_level: string;
  created_at: string;
  updated_at: string;
}

const riskLevels = [
  "Low",
  "Medium",
  "High",
];

const emptyForm = {
  name: "",
  description: "",
  pros: "",
  cons: "",
  estimated_cost: "",
  feasibility_score: "3",
  risk_level: "Medium",
};

function getApiErrorStatus(
  error: unknown,
): number | undefined {
  if (axios.isAxiosError(error)) {
    return error.response?.status;
  }

  return undefined;
}

function isAxiosRequestError(
  error: unknown,
): boolean {
  return (
    axios.isAxiosError(error) &&
    !!error.request
  );
}

function getRiskRank(
  risk: string,
): number {
  const value = risk.toLowerCase();

  if (value === "low") {
    return 1;
  }

  if (value === "medium") {
    return 2;
  }

  if (value === "high") {
    return 3;
  }

  return 99;
}

function formatCost(
  cost: number,
): string {
  return `₹${cost.toLocaleString("en-IN", {
    maximumFractionDigits: 2,
  })}`;
}

function getRiskClass(
  risk: string,
): string {
  return risk.toLowerCase();
}

function getFeasibilityLabel(
  score: number,
): string {
  if (score <= 1) {
    return "Very Low";
  }

  if (score === 2) {
    return "Low";
  }

  if (score === 3) {
    return "Medium";
  }

  if (score === 4) {
    return "High";
  }

  return "Very High";
}

export default function Alternatives() {
  const { id } = useParams<{
    id: string;
  }>();

  const navigate = useNavigate();

  const [alternatives, setAlternatives] =
    useState<Alternative[]>([]);

  const [form, setForm] =
    useState(emptyForm);

  const [isLoading, setIsLoading] =
    useState(true);

  const [isSubmitting, setIsSubmitting] =
    useState(false);

  const [error, setError] =
    useState("");

  const [formError, setFormError] =
    useState("");

  const [showComparison, setShowComparison] =
    useState(false);

  const [
    editingAlternativeId,
    setEditingAlternativeId,
  ] = useState<number | null>(null);

  const loadAlternatives =
    async () => {
      if (!id) {
        setError("Invalid decision ID.");
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        setError("");

        const response =
          await api.get<Alternative[]>(
            `/decisions/${id}/alternatives`,
          );

        setAlternatives(response.data);
      } catch (err: unknown) {
        const status =
          getApiErrorStatus(err);

        if (status === 401) {
          setError(
            "Your session has expired. Please login again.",
          );
        } else if (status === 403) {
          setError(
            "You do not have permission to view alternatives.",
          );
        } else if (status === 404) {
          setError("Decision not found.");
        } else if (
          status !== undefined &&
          status >= 500
        ) {
          setError(
            "Server error. Please try again later.",
          );
        } else if (
          isAxiosRequestError(err)
        ) {
          setError(
            "Unable to connect to the server. Make sure FastAPI is running.",
          );
        } else {
          setError(
            "Unable to load alternatives.",
          );
        }
      } finally {
        setIsLoading(false);
      }
    };

  useEffect(() => {
    let isMounted = true;

    const loadInitialAlternatives =
      async () => {
        if (!id) {
          if (isMounted) {
            setError("Invalid decision ID.");
            setIsLoading(false);
          }

          return;
        }

        try {
          if (isMounted) {
            setIsLoading(true);
            setError("");
          }

          const response =
            await api.get<Alternative[]>(
              `/decisions/${id}/alternatives`,
            );

          if (isMounted) {
            setAlternatives(response.data);
          }
        } catch (err: unknown) {
          if (!isMounted) {
            return;
          }

          const status =
            getApiErrorStatus(err);

          if (status === 401) {
            setError(
              "Your session has expired. Please login again.",
            );
          } else if (status === 403) {
            setError(
              "You do not have permission to view alternatives.",
            );
          } else if (status === 404) {
            setError("Decision not found.");
          } else if (
            status !== undefined &&
            status >= 500
          ) {
            setError(
              "Server error. Please try again later.",
            );
          } else if (
            isAxiosRequestError(err)
          ) {
            setError(
              "Unable to connect to the server. Make sure FastAPI is running.",
            );
          } else {
            setError(
              "Unable to load alternatives.",
            );
          }
        } finally {
          if (isMounted) {
            setIsLoading(false);
          }
        }
      };

    void loadInitialAlternatives();

    return () => {
      isMounted = false;
    };
  }, [id]);

  const handleChange = (
    event: ChangeEvent<
      HTMLInputElement |
        HTMLTextAreaElement |
        HTMLSelectElement
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
  };

  const handleEdit = (
    alternative: Alternative,
  ) => {
    setEditingAlternativeId(
      alternative.id,
    );

    setForm({
      name: alternative.name,
      description:
        alternative.description,
      pros: alternative.pros,
      cons: alternative.cons,
      estimated_cost:
        String(
          alternative.estimated_cost,
        ),
      feasibility_score:
        String(
          alternative.feasibility_score,
        ),
      risk_level:
        alternative.risk_level,
    });

    setFormError("");
    setError("");
    setShowComparison(false);

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  const handleCancelEdit = () => {
    setEditingAlternativeId(null);
    setForm(emptyForm);
    setFormError("");
    setError("");
  };

  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();

    setFormError("");

    const name =
      form.name.trim();

    const description =
      form.description.trim();

    const pros =
      form.pros.trim();

    const cons =
      form.cons.trim();

    if (!name) {
      setFormError(
        "Please enter an alternative name.",
      );
      return;
    }

    if (!description) {
      setFormError(
        "Please enter a description.",
      );
      return;
    }

    if (!pros) {
      setFormError(
        "Please enter the advantages.",
      );
      return;
    }

    if (!cons) {
      setFormError(
        "Please enter the disadvantages.",
      );
      return;
    }

    const estimatedCost =
      Number(form.estimated_cost);

    if (
      form.estimated_cost.trim() === "" ||
      Number.isNaN(estimatedCost) ||
      estimatedCost < 0
    ) {
      setFormError(
        "Please enter a valid estimated cost.",
      );
      return;
    }

    const feasibilityScore =
      Number(form.feasibility_score);

    if (
      !Number.isInteger(
        feasibilityScore,
      ) ||
      feasibilityScore < 1 ||
      feasibilityScore > 5
    ) {
      setFormError(
        "Feasibility score must be between 1 and 5.",
      );
      return;
    }

    if (!id) {
      setFormError(
        "Invalid decision ID.",
      );
      return;
    }

    const payload = {
      name,
      description,
      pros,
      cons,
      estimated_cost:
        estimatedCost,
      feasibility_score:
        feasibilityScore,
      risk_level:
        form.risk_level,
    };

    try {
      setIsSubmitting(true);

      if (
        editingAlternativeId !== null
      ) {
        await api.put(
          `/alternatives/${editingAlternativeId}`,
          payload,
        );

        setForm(emptyForm);
        setEditingAlternativeId(null);

        await loadAlternatives();
      } else {
        await api.post(
          `/decisions/${id}/alternatives`,
          payload,
        );

        setForm(emptyForm);

        await loadAlternatives();
      }
    } catch (err: unknown) {
      const status =
        getApiErrorStatus(err);

      if (status === 401) {
        setFormError(
          "Your session has expired. Please login again.",
        );
      } else if (status === 403) {
        setFormError(
          editingAlternativeId !== null
            ? "You do not have permission to update this alternative."
            : "You do not have permission to add an alternative.",
        );
      } else if (status === 404) {
        setFormError(
          editingAlternativeId !== null
            ? "Alternative not found."
            : "Decision not found.",
        );
      } else if (status === 422) {
        setFormError(
          "Please check the entered details.",
        );
      } else if (
        status !== undefined &&
        status >= 500
      ) {
        setFormError(
          "Server error. Please try again later.",
        );
      } else if (
        isAxiosRequestError(err)
      ) {
        setFormError(
          "Unable to connect to the server.",
        );
      } else {
        setFormError(
          editingAlternativeId !== null
            ? "Unable to update alternative."
            : "Unable to create alternative.",
        );
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (
    alternativeId: number,
  ) => {
    const confirmed =
      window.confirm(
        "Are you sure you want to delete this alternative?",
      );

    if (!confirmed) {
      return;
    }

    try {
      setError("");

      await api.delete(
        `/alternatives/${alternativeId}`,
      );

      setAlternatives((current) =>
        current.filter(
          (alternative) =>
            alternative.id !==
            alternativeId,
        ),
      );

      if (
        editingAlternativeId ===
        alternativeId
      ) {
        setEditingAlternativeId(null);
        setForm(emptyForm);
        setFormError("");
      }

      setShowComparison(false);
    } catch (err: unknown) {
      const status =
        getApiErrorStatus(err);

      if (status === 401) {
        setError(
          "Your session has expired. Please login again.",
        );
      } else if (status === 403) {
        setError(
          "You do not have permission to delete this alternative.",
        );
      } else if (status === 404) {
        setError(
          "Alternative not found.",
        );
      } else if (
        status !== undefined &&
        status >= 500
      ) {
        setError(
          "Server error. Please try again later.",
        );
      } else if (
        isAxiosRequestError(err)
      ) {
        setError(
          "Unable to connect to the server.",
        );
      } else {
        setError(
          "Unable to delete the alternative.",
        );
      }
    }
  };

  const decisionTabs = [
    {
      label: "Overview",
      icon: FileText,
      path: `/decisions/${id}`,
    },
    {
      label: "Alternatives",
      icon: Scale,
      path: `/decisions/${id}/alternatives`,
    },
    {
      label: "Discussion",
      icon: MessageSquare,
      path: `/decisions/${id}/discussion`,
    },
    {
      label: "Approval",
      icon: ClipboardCheck,
      path: `/decisions/${id}/approval`,
    },
    {
      label: "History",
      icon: History,
      path: `/decisions/${id}/history`,
    },
  ];

  return (
    <main className="alternatives-page">
      <header className="alternatives-header">
        <div className="alternatives-heading">
          <div className="alternatives-heading-icon">
            <Scale size={24} />
          </div>

          <div>
            <p className="alternatives-eyebrow">
              Expert Decision Replay Platform
            </p>

            <h1>
              Alternative Analysis
            </h1>

            <p className="alternatives-subtitle">
              Compare possible solutions
              for Decision #{id}.
            </p>
          </div>
        </div>

        <button
          type="button"
          className="alternatives-back-button"
          onClick={() =>
            navigate(`/decisions/${id}`)
          }
        >
          <ArrowLeft size={18} />
          Back to Decision
        </button>
      </header>

      <nav
        className="decision-context-nav alternatives-context-nav"
        aria-label="Decision navigation"
      >
        {decisionTabs.map((tab) => {
          const Icon = tab.icon;

          const isActive =
            tab.label === "Alternatives";

          return (
            <button
              key={tab.label}
              type="button"
              className={`decision-context-tab ${
                isActive ? "active" : ""
              }`}
              onClick={() =>
                navigate(tab.path)
              }
            >
              <Icon size={17} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </nav>

      {error && (
        <section
          className="alternatives-error"
          role="alert"
        >
          <div className="alternatives-error-icon">
            <ShieldAlert size={20} />
          </div>

          <div>
            <strong>
              Unable to complete request
            </strong>

            <p>{error}</p>
          </div>

          <button
            type="button"
            onClick={() => {
              void loadAlternatives();
            }}
          >
            <RefreshCw size={16} />
            Try Again
          </button>
        </section>
      )}

      <section className="alternatives-form-card">
        <div className="alternatives-card-header">
          <div className="alternatives-card-header-left">
            <div className="alternatives-section-icon">
              {editingAlternativeId !==
              null ? (
                <Edit3 size={21} />
              ) : (
                <Plus size={21} />
              )}
            </div>

            <div>
              <h2>
                {editingAlternativeId !==
                null
                  ? "Edit Alternative"
                  : "Add Alternative"}
              </h2>

              <p>
                {editingAlternativeId !==
                null
                  ? "Update the details of this solution."
                  : "Add a possible solution for this decision."}
              </p>
            </div>
          </div>

          {editingAlternativeId !==
            null && (
            <span className="editing-indicator">
              Editing #{editingAlternativeId}
            </span>
          )}
        </div>

        <form
          onSubmit={handleSubmit}
          className="alternatives-form"
        >
          <div className="alternative-field full-width">
            <label htmlFor="name">
              Alternative Name
              <span>*</span>
            </label>

            <div className="alternative-input-wrapper">
              <FileText size={17} />

              <input
                id="name"
                name="name"
                type="text"
                value={form.name}
                onChange={handleChange}
                placeholder="e.g. Cloud-Based Solution"
                disabled={isSubmitting}
              />
            </div>
          </div>

          <div className="alternative-field full-width">
            <label htmlFor="description">
              Description
              <span>*</span>
            </label>

            <textarea
              id="description"
              name="description"
              value={form.description}
              onChange={handleChange}
              placeholder="Describe this alternative..."
              rows={4}
              disabled={isSubmitting}
            />

            <small>
              Explain how this solution
              would address the decision.
            </small>
          </div>

          <div className="alternatives-pros-cons">
            <div className="alternative-field">
              <label htmlFor="pros">
                Pros
                <span>*</span>
              </label>

              <textarea
                id="pros"
                name="pros"
                value={form.pros}
                onChange={handleChange}
                placeholder="Advantages..."
                rows={4}
                disabled={isSubmitting}
              />
            </div>

            <div className="alternative-field">
              <label htmlFor="cons">
                Cons
                <span>*</span>
              </label>

              <textarea
                id="cons"
                name="cons"
                value={form.cons}
                onChange={handleChange}
                placeholder="Disadvantages..."
                rows={4}
                disabled={isSubmitting}
              />
            </div>
          </div>

          <div className="alternatives-metric-fields">
            <div className="alternative-field">
              <label htmlFor="estimated_cost">
                Estimated Cost
                <span>*</span>
              </label>

              <div className="alternative-input-wrapper">
                <span className="currency-symbol">
                  ₹
                </span>

                <input
                  id="estimated_cost"
                  name="estimated_cost"
                  type="number"
                  min="0"
                  step="0.01"
                  value={form.estimated_cost}
                  onChange={handleChange}
                  placeholder="e.g. 50000"
                  disabled={isSubmitting}
                />
              </div>
            </div>

            <div className="alternative-field">
              <label htmlFor="feasibility_score">
                Feasibility Score
                <span>*</span>
              </label>

              <div className="alternative-select-wrapper">
                <Gauge size={17} />

                <select
                  id="feasibility_score"
                  name="feasibility_score"
                  value={
                    form.feasibility_score
                  }
                  onChange={handleChange}
                  disabled={isSubmitting}
                >
                  <option value="1">
                    1 - Very Low
                  </option>

                  <option value="2">
                    2 - Low
                  </option>

                  <option value="3">
                    3 - Medium
                  </option>

                  <option value="4">
                    4 - High
                  </option>

                  <option value="5">
                    5 - Very High
                  </option>
                </select>
              </div>
            </div>

            <div className="alternative-field">
              <label htmlFor="risk_level">
                Risk Level
                <span>*</span>
              </label>

              <div className="alternative-select-wrapper">
                <ShieldAlert size={17} />

                <select
                  id="risk_level"
                  name="risk_level"
                  value={form.risk_level}
                  onChange={handleChange}
                  disabled={isSubmitting}
                >
                  {riskLevels.map(
                    (risk) => (
                      <option
                        key={risk}
                        value={risk}
                      >
                        {risk}
                      </option>
                    ),
                  )}
                </select>
              </div>
            </div>
          </div>

          {formError && (
            <div
              className="alternatives-form-error"
              role="alert"
            >
              <ShieldAlert size={17} />
              {formError}
            </div>
          )}

          <div className="alternatives-form-actions">
            <button
              type="submit"
              disabled={isSubmitting}
              className="alternatives-submit-button"
            >
              {isSubmitting ? (
                <RefreshCw
                  size={18}
                  className="alternatives-spin"
                />
              ) : (
                <Save size={18} />
              )}

              {isSubmitting
                ? editingAlternativeId !==
                  null
                  ? "Updating..."
                  : "Saving..."
                : editingAlternativeId !==
                    null
                  ? "Update Alternative"
                  : "Add Alternative"}
            </button>

            {editingAlternativeId !==
              null && (
              <button
                type="button"
                onClick={
                  handleCancelEdit
                }
                disabled={isSubmitting}
                className="alternatives-cancel-button"
              >
                <X size={18} />
                Cancel Edit
              </button>
            )}
          </div>
        </form>
      </section>

      <section className="alternatives-list-section">
        <div className="alternatives-list-header">
          <div>
            <p className="alternatives-section-eyebrow">
              Decision Options
            </p>

            <h2>
              Existing Alternatives
            </h2>

            <p>
              {alternatives.length}{" "}
              alternative
              {alternatives.length === 1
                ? ""
                : "s"}{" "}
              added to this decision.
            </p>
          </div>

          {alternatives.length >= 2 && (
            <button
              type="button"
              className="alternatives-compare-button"
              onClick={() =>
                setShowComparison(
                  (current) =>
                    !current,
                )
              }
            >
              {showComparison ? (
                <>
                  <X size={18} />
                  Close Comparison
                </>
              ) : (
                <>
                  <Scale size={18} />
                  Compare Alternatives
                </>
              )}
            </button>
          )}
        </div>

        {showComparison &&
          alternatives.length >= 2 && (
            <section className="alternatives-comparison-card">
              <div className="comparison-header">
                <div className="comparison-title-area">
                  <div className="comparison-icon">
                    <Scale size={21} />
                  </div>

                  <div>
                    <h2>
                      Alternative Comparison
                    </h2>

                    <p>
                      Compare all available
                      alternatives side by
                      side.
                    </p>
                  </div>
                </div>

                <span className="comparison-count">
                  {alternatives.length} options
                </span>
              </div>

              <div className="comparison-table-container">
                <table className="comparison-table">
                  <thead>
                    <tr>
                      <th>
                        Criteria
                      </th>

                      {alternatives.map(
                        (alternative) => (
                          <th
                            key={
                              alternative.id
                            }
                          >
                            <div className="comparison-alternative-name">
                              {
                                alternative.name
                              }
                            </div>

                            <span>
                              Alternative #
                              {
                                alternative.id
                              }
                            </span>
                          </th>
                        ),
                      )}
                    </tr>
                  </thead>

                  <tbody>
                    <tr>
                      <th>
                        Description
                      </th>

                      {alternatives.map(
                        (alternative) => (
                          <td
                            key={
                              alternative.id
                            }
                          >
                            {
                              alternative.description
                            }
                          </td>
                        ),
                      )}
                    </tr>

                    <tr>
                      <th>
                        Estimated Cost
                      </th>

                      {alternatives.map(
                        (alternative) => (
                          <td
                            key={
                              alternative.id
                            }
                          >
                            <div className="comparison-metric-value">
                              <span className="currency-symbol">
                                ₹
                              </span>

                              {formatCost(
                                alternative.estimated_cost,
                              )}
                            </div>
                          </td>
                        ),
                      )}
                    </tr>

                    <tr>
                      <th>
                        Feasibility
                      </th>

                      {alternatives.map(
                        (alternative) => (
                          <td
                            key={
                              alternative.id
                            }
                          >
                            <div className="comparison-feasibility">
                              <strong>
                                {
                                  alternative.feasibility_score
                                }
                                /5
                              </strong>

                              <span>
                                {getFeasibilityLabel(
                                  alternative.feasibility_score,
                                )}
                              </span>
                            </div>
                          </td>
                        ),
                      )}
                    </tr>

                    <tr>
                      <th>
                        Risk
                      </th>

                      {alternatives.map(
                        (alternative) => (
                          <td
                            key={
                              alternative.id
                            }
                          >
                            <span
                              className={`comparison-risk ${getRiskClass(
                                alternative.risk_level,
                              )}`}
                            >
                              <span />
                              {
                                alternative.risk_level
                              }
                            </span>
                          </td>
                        ),
                      )}
                    </tr>

                    <tr>
                      <th>
                        Pros
                      </th>

                      {alternatives.map(
                        (alternative) => (
                          <td
                            key={
                              alternative.id
                            }
                          >
                            {
                              alternative.pros
                            }
                          </td>
                        ),
                      )}
                    </tr>

                    <tr>
                      <th>
                        Cons
                      </th>

                      {alternatives.map(
                        (alternative) => (
                          <td
                            key={
                              alternative.id
                            }
                          >
                            {
                              alternative.cons
                            }
                          </td>
                        ),
                      )}
                    </tr>
                  </tbody>
                </table>
              </div>

              <div className="comparison-summary">
                <div className="comparison-summary-heading">
                  <CheckCircle2
                    size={19}
                  />

                  <h3>
                    Comparison Summary
                  </h3>
                </div>

                <div className="comparison-summary-grid">
                  <div>
                    <span>
                      Lowest Cost
                    </span>

                    <strong>
                      {
                        alternatives.reduce(
                          (
                            lowest,
                            current,
                          ) =>
                            current.estimated_cost <
                            lowest.estimated_cost
                              ? current
                              : lowest,
                          alternatives[0],
                        ).name
                      }
                    </strong>
                  </div>

                  <div>
                    <span>
                      Highest Feasibility
                    </span>

                    <strong>
                      {
                        alternatives.reduce(
                          (
                            highest,
                            current,
                          ) =>
                            current.feasibility_score >
                            highest.feasibility_score
                              ? current
                              : highest,
                          alternatives[0],
                        ).name
                      }
                    </strong>
                  </div>

                  <div>
                    <span>
                      Lowest Risk
                    </span>

                    <strong>
                      {
                        alternatives.reduce(
                          (
                            lowest,
                            current,
                          ) =>
                            getRiskRank(
                              current.risk_level,
                            ) <
                            getRiskRank(
                              lowest.risk_level,
                            )
                              ? current
                              : lowest,
                          alternatives[0],
                        ).name
                      }
                    </strong>
                  </div>
                </div>
              </div>
            </section>
          )}

        {isLoading ? (
          <section className="alternatives-state-card">
            <div className="alternatives-loading-spinner" />

            <h3>
              Loading alternatives
            </h3>

            <p>
              Retrieving available
              decision options...
            </p>
          </section>
        ) : alternatives.length === 0 ? (
          <section className="alternatives-empty-state">
            <div className="alternatives-empty-icon">
              <Scale size={28} />
            </div>

            <h2>
              No alternatives yet
            </h2>

            <p>
              Add possible solutions
              using the form above.
            </p>
          </section>
        ) : (
          <div className="alternatives-grid">
            {alternatives.map(
              (alternative) => (
                <article
                  key={
                    alternative.id
                  }
                  className="alternatives-item-card"
                >
                  <div className="alternatives-item-top">
                    <div className="alternative-item-title-area">
                      <div className="alternative-item-icon">
                        <Scale size={19} />
                      </div>

                      <div>
                        <h3>
                          {
                            alternative.name
                          }
                        </h3>

                        <span>
                          Alternative #
                          {
                            alternative.id
                          }
                        </span>
                      </div>
                    </div>

                    <div className="alternative-item-actions">
                      <button
                        type="button"
                        className="alternative-edit-button"
                        onClick={() =>
                          handleEdit(
                            alternative,
                          )
                        }
                        title="Edit alternative"
                        disabled={
                          isSubmitting
                        }
                      >
                        <Edit3
                          size={16}
                        />
                        Edit
                      </button>

                      <button
                        type="button"
                        className="alternative-delete-button"
                        onClick={() =>
                          handleDelete(
                            alternative.id,
                          )
                        }
                        title="Delete alternative"
                        disabled={
                          isSubmitting
                        }
                      >
                        <Trash2
                          size={16}
                        />
                      </button>
                    </div>
                  </div>

                  <div className="alternative-item-description">
                    <p>
                      {
                        alternative.description
                      }
                    </p>
                  </div>

                  <div className="alternative-pros-cons">
                    <div className="alternative-pro-box">
                      <span className="alternative-detail-label">
                        Pros
                      </span>

                      <p>
                        {
                          alternative.pros
                        }
                      </p>
                    </div>

                    <div className="alternative-con-box">
                      <span className="alternative-detail-label">
                        Cons
                      </span>

                      <p>
                        {
                          alternative.cons
                        }
                      </p>
                    </div>
                  </div>

                  <div className="alternative-metrics">
                    <div className="alternative-metric">
                      <div className="alternative-metric-icon">
                        <span className="currency-symbol">
                          ₹
                        </span>
                      </div>

                      <div>
                        <span>
                          Estimated Cost
                        </span>

                        <strong>
                          {formatCost(
                            alternative.estimated_cost,
                          )}
                        </strong>
                      </div>
                    </div>

                    <div className="alternative-metric">
                      <div className="alternative-metric-icon">
                        <Gauge size={16} />
                      </div>

                      <div>
                        <span>
                          Feasibility
                        </span>

                        <strong>
                          {
                            alternative.feasibility_score
                          }
                          /5
                        </strong>
                      </div>
                    </div>

                    <div className="alternative-metric">
                      <div className="alternative-metric-icon">
                        <ShieldAlert
                          size={16}
                        />
                      </div>

                      <div>
                        <span>
                          Risk
                        </span>

                        <strong
                          className={`risk-text ${getRiskClass(
                            alternative.risk_level,
                          )}`}
                        >
                          {
                            alternative.risk_level
                          }
                        </strong>
                      </div>
                    </div>
                  </div>
                </article>
              ),
            )}
          </div>
        )}
      </section>
    </main>
  );
}