import {
  useCallback,
  useEffect,
  useState,
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
  return `₹${cost.toLocaleString(
    "en-IN",
    {
      maximumFractionDigits: 2,
    },
  )}`;
}

export default function Alternatives() {
  const { id } =
    useParams<{ id: string }>();

  const navigate = useNavigate();

  const [
    alternatives,
    setAlternatives,
  ] = useState<Alternative[]>([]);

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

  const [
    showComparison,
    setShowComparison,
  ] = useState(false);

  const [
    editingAlternativeId,
    setEditingAlternativeId,
  ] = useState<number | null>(null);

  const loadAlternatives =
    useCallback(async () => {
      if (!id) {
        setError(
          "Invalid decision ID.",
        );

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

        setAlternatives(
          response.data,
        );
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
    }, [id]);

  useEffect(() => {
    if (!id) {
      return;
    }

    const timer =
      window.setTimeout(() => {
        loadAlternatives();
      }, 0);

    return () => {
      window.clearTimeout(timer);
    };
  }, [id, loadAlternatives]);

  const handleChange = (
    event: React.ChangeEvent<
      HTMLInputElement |
        HTMLTextAreaElement |
        HTMLSelectElement
    >,
  ) => {
    const {
      name,
      value,
    } = event.target;

    setForm(
      (current) => ({
        ...current,
        [name]: value,
      }),
    );
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
    setEditingAlternativeId(
      null,
    );

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
      Number(
        form.estimated_cost,
      );

    if (
      form.estimated_cost.trim() ===
        "" ||
      Number.isNaN(
        estimatedCost,
      ) ||
      estimatedCost < 0
    ) {
      setFormError(
        "Please enter a valid estimated cost.",
      );
      return;
    }

    const feasibilityScore =
      Number(
        form.feasibility_score,
      );

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
        editingAlternativeId !==
        null
      ) {
        await api.put(
          `/alternatives/${editingAlternativeId}`,
          payload,
        );

        setForm(emptyForm);

        setEditingAlternativeId(
          null,
        );

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
          editingAlternativeId !==
            null
            ? "You do not have permission to update this alternative."
            : "You do not have permission to add an alternative.",
        );
      } else if (status === 404) {
        setFormError(
          editingAlternativeId !==
            null
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
          editingAlternativeId !==
            null
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

      setAlternatives(
        (current) =>
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
        setEditingAlternativeId(
          null,
        );

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

  const submitButtonStyle: React.CSSProperties =
    {
      display: "inline-flex",
      alignItems: "center",
      justifyContent: "center",
      gap: "8px",
      padding: "10px 18px",
      border: "none",
      borderRadius: "8px",
      backgroundColor: "#2563eb",
      color: "#ffffff",
      fontWeight: 600,
      fontSize: "14px",
      cursor: isSubmitting
        ? "not-allowed"
        : "pointer",
      opacity: isSubmitting
        ? 0.7
        : 1,
      minWidth: "170px",
      minHeight: "42px",
      boxShadow:
        "0 2px 6px rgba(0, 0, 0, 0.15)",
    };

  const cancelButtonStyle: React.CSSProperties =
    {
      display: "inline-flex",
      alignItems: "center",
      justifyContent: "center",
      gap: "8px",
      padding: "10px 18px",
      border: "1px solid #cbd5e1",
      borderRadius: "8px",
      backgroundColor: "#ffffff",
      color: "#334155",
      fontWeight: 600,
      fontSize: "14px",
      cursor: isSubmitting
        ? "not-allowed"
        : "pointer",
      opacity: isSubmitting
        ? 0.7
        : 1,
      minWidth: "140px",
      minHeight: "42px",
    };

  const editButtonStyle: React.CSSProperties =
    {
      display: "inline-flex",
      alignItems: "center",
      justifyContent: "center",
      gap: "6px",
      padding: "8px 12px",
      border: "1px solid #cbd5e1",
      borderRadius: "7px",
      backgroundColor: "#ffffff",
      color: "#1e40af",
      fontWeight: 600,
      fontSize: "13px",
      cursor: isSubmitting
        ? "not-allowed"
        : "pointer",
    };

  /*
   * Explicit styling for the comparison button.
   * This overrides the existing primary-button CSS
   * that was making the text appear white on white.
   */
  const compareButtonStyle: React.CSSProperties =
    {
      display: "inline-flex",
      alignItems: "center",
      justifyContent: "center",
      gap: "8px",
      padding: "10px 18px",
      border: "none",
      borderRadius: "8px",
      backgroundColor: "#2563eb",
      color: "#ffffff",
      fontWeight: 600,
      fontSize: "14px",
      cursor: "pointer",
      minWidth: "190px",
      minHeight: "42px",
      boxShadow:
        "0 2px 6px rgba(0, 0, 0, 0.15)",
    };

  return (
    <main className="alternatives-page">

      <header className="page-header">

        <div>

          <p className="page-eyebrow">
            Expert Decision Replay Platform
          </p>

          <h1>
            Alternative Analysis
          </h1>

          <p>
            Compare possible solutions
            for Decision #{id}.
          </p>

        </div>

        <button
          className="secondary-button"
          onClick={() =>
            navigate(
              `/decisions/${id}`,
            )
          }
        >
          <ArrowLeft size={18} />

          Back to Decision
        </button>

      </header>

      {error && (
        <section
          className="decision-error"
          role="alert"
        >

          <strong>
            Error
          </strong>

          <p>{error}</p>

          <button
            onClick={
              loadAlternatives
            }
          >

            <RefreshCw size={17} />

            Try Again

          </button>

        </section>
      )}

      <section className="alternative-form-card">

        <div className="details-card-header">

          <div className="details-icon">
            {editingAlternativeId !==
            null ? (
              <Edit3 size={22} />
            ) : (
              <Plus size={22} />
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
                ? "Update the selected alternative."
                : "Add a possible solution for this decision."}
            </p>

          </div>

        </div>

        <form
          onSubmit={handleSubmit}
          className="alternative-form"
        >

          <div className="form-group">

            <label htmlFor="name">
              Alternative Name
            </label>

            <input
              id="name"
              name="name"
              type="text"
              value={form.name}
              onChange={
                handleChange
              }
              placeholder="e.g. Cloud-Based Solution"
              disabled={
                isSubmitting
              }
            />

          </div>

          <div className="form-group">

            <label htmlFor="description">
              Description
            </label>

            <textarea
              id="description"
              name="description"
              value={
                form.description
              }
              onChange={
                handleChange
              }
              placeholder="Describe this alternative..."
              rows={4}
              disabled={
                isSubmitting
              }
            />

          </div>

          <div className="form-row">

            <div className="form-group">

              <label htmlFor="pros">
                Pros
              </label>

              <textarea
                id="pros"
                name="pros"
                value={form.pros}
                onChange={
                  handleChange
                }
                placeholder="Advantages..."
                rows={4}
                disabled={
                  isSubmitting
                }
              />

            </div>

            <div className="form-group">

              <label htmlFor="cons">
                Cons
              </label>

              <textarea
                id="cons"
                name="cons"
                value={form.cons}
                onChange={
                  handleChange
                }
                placeholder="Disadvantages..."
                rows={4}
                disabled={
                  isSubmitting
                }
              />

            </div>

          </div>

          <div className="form-row">

            <div className="form-group">

              <label htmlFor="estimated_cost">
                Estimated Cost
              </label>

              <input
                id="estimated_cost"
                name="estimated_cost"
                type="number"
                min="0"
                step="0.01"
                value={
                  form.estimated_cost
                }
                onChange={
                  handleChange
                }
                placeholder="e.g. 50000"
                disabled={
                  isSubmitting
                }
              />

            </div>

            <div className="form-group">

              <label htmlFor="feasibility_score">
                Feasibility Score
              </label>

              <select
                id="feasibility_score"
                name="feasibility_score"
                value={
                  form.feasibility_score
                }
                onChange={
                  handleChange
                }
                disabled={
                  isSubmitting
                }
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

            <div className="form-group">

              <label htmlFor="risk_level">
                Risk Level
              </label>

              <select
                id="risk_level"
                name="risk_level"
                value={
                  form.risk_level
                }
                onChange={
                  handleChange
                }
                disabled={
                  isSubmitting
                }
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

          {formError && (
            <div
              className="auth-error"
              role="alert"
            >
              {formError}
            </div>
          )}

          <div
            className="form-actions"
            style={{
              display: "flex",
              alignItems: "center",
              gap: "12px",
              marginTop: "8px",
              flexWrap: "wrap",
            }}
          >

            <button
              type="submit"
              disabled={isSubmitting}
              style={submitButtonStyle}
            >

              <Save size={18} />

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
                disabled={
                  isSubmitting
                }
                style={
                  cancelButtonStyle
                }
              >

                <X size={18} />

                Cancel Edit

              </button>
            )}

          </div>

        </form>

      </section>

      <section className="alternative-list-section">

        <div className="page-section-header">

          <div>

            <h2>
              Existing Alternatives
            </h2>

            <p>
              {alternatives.length}{" "}
              alternative
              {alternatives.length ===
              1
                ? ""
                : "s"}{" "}
              added to this decision.
            </p>

          </div>

          {alternatives.length >=
            2 && (

            <button
              className="primary-button"
              onClick={() =>
                setShowComparison(
                  (current) =>
                    !current,
                )
              }
              style={
                compareButtonStyle
              }
            >

              {showComparison ? (
                <>
                  <X size={18} />

                  Close Comparison
                </>
              ) : (
                <>
                  <Scale
                    size={18}
                  />

                  Compare Alternatives
                </>
              )}

            </button>

          )}

        </div>

        {showComparison &&
          alternatives.length >=
            2 && (

          <section className="alternative-comparison-card">

            <div className="details-card-header">

              <div className="details-icon">
                <Scale
                  size={22}
                />
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

            <div className="comparison-table-wrapper">

              <table className="comparison-table">

                <thead>

                  <tr>

                    <th>
                      Criteria
                    </th>

                    {alternatives.map(
                      (
                        alternative,
                      ) => (
                        <th
                          key={
                            alternative.id
                          }
                        >
                          {
                            alternative.name
                          }
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
                      (
                        alternative,
                      ) => (
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
                      (
                        alternative,
                      ) => (
                        <td
                          key={
                            alternative.id
                          }
                        >

                          <strong>
                            {formatCost(
                              alternative.estimated_cost,
                            )}
                          </strong>

                        </td>
                      ),
                    )}

                  </tr>

                  <tr>

                    <th>
                      Feasibility
                    </th>

                    {alternatives.map(
                      (
                        alternative,
                      ) => (
                        <td
                          key={
                            alternative.id
                          }
                        >

                          <strong>
                            {
                              alternative.feasibility_score
                            }
                            /5
                          </strong>

                        </td>
                      ),
                    )}

                  </tr>

                  <tr>

                    <th>
                      Risk
                    </th>

                    {alternatives.map(
                      (
                        alternative,
                      ) => (
                        <td
                          key={
                            alternative.id
                          }
                        >

                          <strong>
                            {
                              alternative.risk_level
                            }
                          </strong>

                        </td>
                      ),
                    )}

                  </tr>

                  <tr>

                    <th>
                      Pros
                    </th>

                    {alternatives.map(
                      (
                        alternative,
                      ) => (
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
                      (
                        alternative,
                      ) => (
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

              <h3>
                Comparison Summary
              </h3>

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

          <section className="decision-loading">

            <div className="loading-spinner" />

            <p>
              Loading alternatives...
            </p>

          </section>

        ) : alternatives.length ===
          0 ? (

          <section className="decision-empty">

            <Plus size={42} />

            <h2>
              No alternatives yet
            </h2>

            <p>
              Add possible solutions
              using the form above.
            </p>

          </section>

        ) : (

          <div className="alternative-grid">

            {alternatives.map(
              (alternative) => (

                <article
                  key={
                    alternative.id
                  }
                  className="alternative-card"
                >

                  <div className="alternative-card-header">

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

                    <div
                      style={{
                        display: "flex",
                        gap: "8px",
                        alignItems:
                          "center",
                      }}
                    >

                      <button
                        onClick={() =>
                          handleEdit(
                            alternative,
                          )
                        }
                        title="Edit alternative"
                        disabled={
                          isSubmitting
                        }
                        style={
                          editButtonStyle
                        }
                      >

                        <Edit3
                          size={17}
                        />

                        Edit

                      </button>

                      <button
                        className="danger-button"
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
                          size={17}
                        />

                      </button>

                    </div>

                  </div>

                  <div className="alternative-description">
                    {
                      alternative.description
                    }
                  </div>

                  <div className="alternative-comparison">

                    <div>

                      <strong>
                        Pros
                      </strong>

                      <p>
                        {
                          alternative.pros
                        }
                      </p>

                    </div>

                    <div>

                      <strong>
                        Cons
                      </strong>

                      <p>
                        {
                          alternative.cons
                        }
                      </p>

                    </div>

                  </div>

                  <div className="alternative-metrics">

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

                    <div>

                      <span>
                        Risk
                      </span>

                      <strong>
                        {
                          alternative.risk_level
                        }
                      </strong>

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