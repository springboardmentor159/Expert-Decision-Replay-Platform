import { useCallback, useEffect, useState } from "react";
import {
  ArrowLeft,
  ArrowRight,
  Check,
  Clock3,
  GitCompareArrows,
  History,
  Loader2,
  X,
} from "lucide-react";
import { Link, useParams } from "react-router-dom";

import Alert from "../components/Alert";
import {
  compareDecisionVersions,
  getDecisionHistory,
  type DecisionVersion,
  type DecisionVersionComparison,
} from "../services/decisionService";
import "./DecisionHistoryPage.css";

export default function DecisionHistoryPage() {
  const { decisionId } = useParams<{ decisionId: string }>();

  const [versions, setVersions] = useState<DecisionVersion[]>([]);
  const [comparison, setComparison] =
    useState<DecisionVersionComparison | null>(null);

  const [selectedVersionA, setSelectedVersionA] =
    useState<number | null>(null);
  const [selectedVersionB, setSelectedVersionB] =
    useState<number | null>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [isComparing, setIsComparing] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [comparisonError, setComparisonError] = useState("");

  const numericDecisionId = Number(decisionId);

  const loadHistory = useCallback(async () => {
    if (
      !decisionId ||
      !Number.isInteger(numericDecisionId) ||
      numericDecisionId <= 0
    ) {
      setErrorMessage("Invalid decision identifier.");
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setErrorMessage("");

    try {
      const data = await getDecisionHistory(numericDecisionId);

      setVersions(data);

      if (data.length >= 2) {
        const latest = data[data.length - 1];
        const previous = data[data.length - 2];

        setSelectedVersionA(previous.version_number);
        setSelectedVersionB(latest.version_number);
      } else if (data.length === 1) {
        setSelectedVersionA(data[0].version_number);
        setSelectedVersionB(null);
      }
    } catch (error: unknown) {
      const status = (
        error as {
          response?: {
            status?: number;
          };
        }
      )?.response?.status;

      if (status === 401) {
        setErrorMessage(
          "Your session has expired. Please sign in again.",
        );
      } else if (status === 403) {
        setErrorMessage(
          "You do not have permission to view this history.",
        );
      } else if (status === 404) {
        setErrorMessage(
          "The requested decision was not found.",
        );
      } else if (status && status >= 500) {
        setErrorMessage(
          "The server is temporarily unavailable. Please try again.",
        );
      } else {
        setErrorMessage(
          "Unable to load the decision history. Please try again.",
        );
      }
    } finally {
      setIsLoading(false);
    }
  }, [decisionId, numericDecisionId]);

  useEffect(() => {
    void loadHistory();
  }, [loadHistory]);

  async function handleCompare() {
    if (
      !Number.isInteger(numericDecisionId) ||
      numericDecisionId <= 0 ||
      selectedVersionA === null ||
      selectedVersionB === null
    ) {
      return;
    }

    if (selectedVersionA === selectedVersionB) {
      setComparisonError(
        "Select two different versions to compare.",
      );
      setComparison(null);
      return;
    }

    setIsComparing(true);
    setComparisonError("");
    setComparison(null);

    try {
      const result = await compareDecisionVersions(
        numericDecisionId,
        selectedVersionA,
        selectedVersionB,
      );

      setComparison(result);
    } catch (error: unknown) {
      const status = (
        error as {
          response?: {
            status?: number;
          };
        }
      )?.response?.status;

      if (status === 401) {
        setComparisonError(
          "Your session has expired. Please sign in again.",
        );
      } else if (status === 403) {
        setComparisonError(
          "You do not have permission to compare these versions.",
        );
      } else if (status === 404) {
        setComparisonError(
          "One or both selected versions could not be found.",
        );
      } else if (status === 422) {
        setComparisonError(
          "Please select valid versions to compare.",
        );
      } else if (status && status >= 500) {
        setComparisonError(
          "The server is temporarily unavailable. Please try again.",
        );
      } else {
        setComparisonError(
          "Unable to compare the selected versions.",
        );
      }
    } finally {
      setIsComparing(false);
    }
  }

  function formatDate(value: string) {
    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
      return "—";
    }

    return date.toLocaleString(undefined, {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
    });
  }

  function formatFieldName(field: string) {
    return field
      .replace(/_/g, " ")
      .replace(/\b\w/g, (character) =>
        character.toUpperCase(),
      );
  }

  if (isLoading) {
    return (
      <div className="decision-history-page">
        <div
          className="decision-history-loading"
          role="status"
          aria-live="polite"
        >
          <Loader2
            size={19}
            className="decision-history-spinner"
            aria-hidden="true"
          />
          Loading version history...
        </div>
      </div>
    );
  }

  if (errorMessage) {
    return (
      <div className="decision-history-page">
        <div className="decision-history-error">
          <Alert variant="error">{errorMessage}</Alert>

          <Link
            to={
              decisionId
                ? `/decisions/${decisionId}`
                : "/decisions"
            }
            className="decision-history-back-button"
          >
            <ArrowLeft size={15} aria-hidden="true" />
            Back to Decision
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="decision-history-page">
      <header className="decision-history-header">
        <div>
          <Link
            to={
              decisionId
                ? `/decisions/${decisionId}`
                : "/decisions"
            }
            className="decision-history-back"
          >
            <ArrowLeft size={15} aria-hidden="true" />
            Back to Decision
          </Link>

          <span className="decision-history-kicker">
            DECISION MANAGEMENT
          </span>

          <h1>Version history</h1>

          <p>
            Review how this decision has changed over time and
            compare recorded versions.
          </p>
        </div>

        <div className="decision-history-count">
          <History size={15} aria-hidden="true" />
          <span>
            {versions.length}{" "}
            {versions.length === 1 ? "version" : "versions"}
          </span>
        </div>
      </header>

      <div className="decision-history-layout">
        <main className="decision-history-main">
          <section className="decision-history-card">
            <div className="decision-history-card-header">
              <div className="decision-history-card-icon">
                <History
                  size={19}
                  strokeWidth={1.8}
                  aria-hidden="true"
                />
              </div>

              <div>
                <h2>Decision timeline</h2>
                <p>
                  Every recorded version of this decision.
                </p>
              </div>
            </div>

            {versions.length === 0 ? (
              <div className="decision-history-empty">
                <History
                  size={25}
                  strokeWidth={1.6}
                  aria-hidden="true"
                />
                <strong>No version history available</strong>
                <span>
                  There are no recorded versions for this
                  decision yet.
                </span>
              </div>
            ) : (
              <div className="decision-history-timeline">
                {versions.map((version, index) => (
                  <div
                    className="decision-history-item"
                    key={version.id}
                  >
                    <div className="decision-history-marker-column">
                      <div className="decision-history-marker">
                        {version.version_number}
                      </div>

                      {index < versions.length - 1 && (
                        <div className="decision-history-line" />
                      )}
                    </div>

                    <div className="decision-history-version">
                      <div className="decision-history-version-top">
                        <div>
                          <span className="decision-history-version-label">
                            Version {version.version_number}
                          </span>

                          {index === versions.length - 1 && (
                            <span className="decision-history-latest">
                              Latest
                            </span>
                          )}
                        </div>

                        <span className="decision-history-date">
                          <Clock3
                            size={13}
                            aria-hidden="true"
                          />
                          {formatDate(version.created_at)}
                        </span>
                      </div>

                      <h3>{version.title}</h3>

                      <p className="decision-history-summary">
                        {version.change_summary ||
                          "No change summary recorded."}
                      </p>

                      <div className="decision-history-version-meta">
                        <span>
                          Status:{" "}
                          <strong>{version.status}</strong>
                        </span>

                        <span>
                          Category:{" "}
                          <strong>{version.category}</strong>
                        </span>

                        <span>
                          Changed by:{" "}
                          <strong>
                            User #{version.changed_by}
                          </strong>
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        </main>

        <aside className="decision-history-sidebar">
          <section className="decision-history-side-card">
            <div className="decision-history-side-heading">
              <GitCompareArrows
                size={17}
                aria-hidden="true"
              />

              <div>
                <span>VERSION COMPARISON</span>
                <h2>Compare changes</h2>
              </div>
            </div>

            {versions.length < 2 ? (
              <div className="decision-history-compare-empty">
                <span>
                  At least two versions are required to compare
                  changes.
                </span>
              </div>
            ) : (
              <>
                <div className="decision-history-select-field">
                  <label htmlFor="version-a">
                    Earlier version
                  </label>

                  <select
                    id="version-a"
                    value={selectedVersionA ?? ""}
                    onChange={(event) => {
                      setSelectedVersionA(
                        Number(event.target.value),
                      );
                      setComparison(null);
                      setComparisonError("");
                    }}
                  >
                    <option value="" disabled>
                      Select version
                    </option>

                    {versions.map((version) => (
                      <option
                        key={version.version_number}
                        value={version.version_number}
                      >
                        Version {version.version_number}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="decision-history-compare-arrow">
                  <ArrowRight
                    size={15}
                    aria-hidden="true"
                  />
                </div>

                <div className="decision-history-select-field">
                  <label htmlFor="version-b">
                    Later version
                  </label>

                  <select
                    id="version-b"
                    value={selectedVersionB ?? ""}
                    onChange={(event) => {
                      setSelectedVersionB(
                        Number(event.target.value),
                      );
                      setComparison(null);
                      setComparisonError("");
                    }}
                  >
                    <option value="" disabled>
                      Select version
                    </option>

                    {versions.map((version) => (
                      <option
                        key={version.version_number}
                        value={version.version_number}
                      >
                        Version {version.version_number}
                      </option>
                    ))}
                  </select>
                </div>

                {comparisonError && (
                  <div className="decision-history-compare-error">
                    <Alert variant="error">
                      {comparisonError}
                    </Alert>
                  </div>
                )}

                <button
                  type="button"
                  className="decision-history-compare-button"
                  onClick={() => void handleCompare()}
                  disabled={
                    isComparing ||
                    selectedVersionA === null ||
                    selectedVersionB === null
                  }
                >
                  {isComparing ? (
                    <>
                      <Loader2
                        size={16}
                        className="decision-history-spinner"
                        aria-hidden="true"
                      />
                      Comparing...
                    </>
                  ) : (
                    <>
                      <GitCompareArrows
                        size={16}
                        aria-hidden="true"
                      />
                      Compare versions
                    </>
                  )}
                </button>
              </>
            )}
          </section>

          {comparison && (
            <section className="decision-history-side-card">
              <div className="decision-history-side-heading">
                <div>
                  <span>COMPARISON RESULT</span>
                  <h2>
                    v{comparison.version_a} → v
                    {comparison.version_b}
                  </h2>
                </div>
              </div>

              {Object.keys(comparison.differences).length === 0 ? (
                <div className="decision-history-no-differences">
                  <Check size={17} aria-hidden="true" />

                  <span>
                    No differences were found between the selected
                    versions.
                  </span>
                </div>
              ) : (
                <div className="decision-history-differences">
                  {Object.entries(comparison.differences).map(
                    ([field, difference]) => (
                      <div
                        className="decision-history-difference"
                        key={field}
                      >
                        <span className="decision-history-difference-field">
                          {formatFieldName(field)}
                        </span>

                        <div className="decision-history-change old">
                          <X
                            size={13}
                            aria-hidden="true"
                          />
                          <span>
                            {difference.version_a || "Empty"}
                          </span>
                        </div>

                        <div className="decision-history-change new">
                          <Check
                            size={13}
                            aria-hidden="true"
                          />
                          <span>
                            {difference.version_b || "Empty"}
                          </span>
                        </div>
                      </div>
                    ),
                  )}
                </div>
              )}
            </section>
          )}
        </aside>
      </div>
    </div>
  );
}