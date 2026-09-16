import React, {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  ArrowLeft,
  ArrowRight,
  CalendarDays,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Clock3,
  Edit3,
  FileClock,
  FileText,
  History,
  Layers3,
  MessageSquare,
  Pencil,
  Scale,
  ShieldAlert,
  Tag,
  User,
  XCircle,
} from "lucide-react";

import {
  Link,
  useNavigate,
  useParams,
} from "react-router-dom";

import {
  getDecision,
  getDecisionTags,
  getDecisionVersions,
  getDecisionHistory,
  getDecisionTimeline,
  compareAlternatives,
} from "../api/decisionApi";


// =========================================================
// HELPERS
// =========================================================

function formatDate(value) {
  if (!value) return "—";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return String(value);
  }

  return date.toLocaleString();
}


function getStatusClass(status) {
  const normalized = String(status || "")
    .toLowerCase()
    .replace(/\s+/g, "-");

  if (normalized.includes("approved")) {
    return "status-approved";
  }

  if (normalized.includes("rejected")) {
    return "status-rejected";
  }

  if (normalized.includes("review")) {
    return "status-review";
  }

  if (normalized.includes("draft")) {
    return "status-draft";
  }

  if (normalized.includes("archived")) {
    return "status-archived";
  }

  return "status-default";
}


function getStatusIcon(status) {
  const normalized = String(status || "")
    .toLowerCase();

  if (normalized.includes("approved")) {
    return <CheckCircle2 size={15} />;
  }

  if (normalized.includes("rejected")) {
    return <XCircle size={15} />;
  }

  if (normalized.includes("review")) {
    return <Clock3 size={15} />;
  }

  return <FileText size={15} />;
}


function getArray(data, possibleKeys = []) {
  if (Array.isArray(data)) {
    return data;
  }

  if (!data || typeof data !== "object") {
    return [];
  }

  for (const key of possibleKeys) {
    if (Array.isArray(data[key])) {
      return data[key];
    }
  }

  return [];
}


// =========================================================
// COMPONENT
// =========================================================

export default function DecisionDetails() {
  const { decisionId } = useParams();
  const navigate = useNavigate();

  const [decision, setDecision] =
    useState(null);

  const [versions, setVersions] =
    useState([]);

  const [history, setHistory] =
    useState([]);

  const [timeline, setTimeline] =
    useState([]);

  const [alternatives, setAlternatives] =
    useState([]);

  const [tags, setTags] =
    useState([]);


  const [loading, setLoading] =
    useState(true);

  const [versionsLoading, setVersionsLoading] =
    useState(true);

  const [historyLoading, setHistoryLoading] =
    useState(true);

  const [timelineLoading, setTimelineLoading] =
    useState(true);

  const [alternativesLoading, setAlternativesLoading] =
    useState(true);

  const [tagsLoading, setTagsLoading] =
    useState(true);


  const [error, setError] =
    useState("");

  const [versionsError, setVersionsError] =
    useState("");

  const [historyError, setHistoryError] =
    useState("");

  const [timelineError, setTimelineError] =
    useState("");

  const [alternativesError, setAlternativesError] =
    useState("");

  const [tagsError, setTagsError] =
    useState("");


  const [showVersions, setShowVersions] =
    useState(true);

  const [showHistory, setShowHistory] =
    useState(true);

  const [showTimeline, setShowTimeline] =
    useState(true);

  const [showAlternatives, setShowAlternatives] =
    useState(true);


  // =======================================================
  // LOAD DECISION
  // =======================================================

  async function loadDecision() {
    if (!decisionId) {
      setError("Decision ID is missing.");
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError("");

      const data =
        await getDecision(decisionId);

      const rawDecision =
        data?.decision ||
        data?.data ||
        data;

      if (
        !rawDecision ||
        typeof rawDecision !== "object"
      ) {
        throw new Error(
          "Invalid decision data received from the server."
        );
      }

      const normalizedDecision = {
        id:
          rawDecision.id ??
          rawDecision.decision_id ??
          Number(decisionId),

        title:
          rawDecision.title ??
          rawDecision.name ??
          "",

        problem_statement:
          rawDecision.problem_statement ??
          rawDecision.problemStatement ??
          "",

        rationale:
          rawDecision.rationale ??
          "",

        category:
          rawDecision.category ??
          "",

        status:
          rawDecision.status?.value ??
          rawDecision.status ??
          "",

        created_by:
          rawDecision.created_by ??
          rawDecision.creator_id ??
          rawDecision.createdBy ??
          null,

        created_at:
          rawDecision.created_at ??
          rawDecision.createdAt ??
          null,

        updated_at:
          rawDecision.updated_at ??
          rawDecision.updatedAt ??
          null,
      };

      setDecision(normalizedDecision);

    } catch (err) {
      console.error(
        "Failed to load decision:",
        err
      );

      const status =
        err?.response?.status;

      if (status === 401) {
        setError(
          "Your session has expired. Please log in again."
        );
      } else if (status === 403) {
        setError(
          "You do not have permission to view this decision."
        );
      } else if (status === 404) {
        setError("Decision not found.");
      } else if (status === 422) {
        setError("Invalid decision ID.");
      } else if (status >= 500) {
        setError(
          "Server error while loading the decision."
        );
      } else {
        setError(
          err?.response?.data?.detail ||
          err?.message ||
          "Failed to load decision."
        );
      }

    } finally {
      setLoading(false);
    }
  }


  // =======================================================
  // LOAD VERSIONS
  // =======================================================

  async function loadVersions() {
    if (!decisionId) return;

    try {
      setVersionsLoading(true);
      setVersionsError("");

      const data =
        await getDecisionVersions(decisionId);

      setVersions(
        getArray(data, [
          "versions",
          "items",
          "results",
          "data",
        ])
      );

    } catch (err) {
      console.error(
        "Failed to load versions:",
        err
      );

      setVersionsError(
        err?.response?.data?.detail ||
        err?.message ||
        "Failed to load version history."
      );

    } finally {
      setVersionsLoading(false);
    }
  }


  // =======================================================
  // LOAD HISTORY
  // =======================================================

  async function loadHistory() {
    if (!decisionId) return;

    try {
      setHistoryLoading(true);
      setHistoryError("");

      const data =
        await getDecisionHistory(decisionId);

      setHistory(
        getArray(data, [
          "history",
          "items",
          "results",
          "data",
        ])
      );

    } catch (err) {
      console.error(
        "Failed to load history:",
        err
      );

      setHistoryError(
        err?.response?.data?.detail ||
        err?.message ||
        "Failed to load decision history."
      );

    } finally {
      setHistoryLoading(false);
    }
  }


  // =======================================================
  // LOAD TIMELINE
  // =======================================================

  async function loadTimeline() {
    if (!decisionId) return;

    try {
      setTimelineLoading(true);
      setTimelineError("");

      const data =
        await getDecisionTimeline(decisionId);

      setTimeline(
        getArray(data, [
          "timeline",
          "items",
          "results",
          "data",
        ])
      );

    } catch (err) {
      console.error(
        "Failed to load timeline:",
        err
      );

      setTimelineError(
        err?.response?.data?.detail ||
        err?.message ||
        "Failed to load decision timeline."
      );

    } finally {
      setTimelineLoading(false);
    }
  }


  // =======================================================
  // LOAD ALTERNATIVES
  // =======================================================

  async function loadAlternatives() {
    if (!decisionId) return;

    try {
      setAlternativesLoading(true);
      setAlternativesError("");

      const data =
        await compareAlternatives(
          decisionId
        );

      setAlternatives(
        getArray(data, [
          "alternatives",
          "items",
          "results",
          "data",
        ])
      );

    } catch (err) {
      console.error(
        "Failed to load alternatives:",
        err
      );

      setAlternativesError(
        err?.response?.data?.detail ||
        err?.message ||
        "Failed to load alternatives."
      );

    } finally {
      setAlternativesLoading(false);
    }
  }


  // =======================================================
  // LOAD TAGS
  // =======================================================

  async function loadTags() {
    if (!decisionId) return;

    try {
      setTagsLoading(true);
      setTagsError("");

      const data =
        await getDecisionTags(decisionId);

      setTags(
        getArray(data, [
          "tags",
          "items",
          "results",
          "data",
        ])
      );

    } catch (err) {
      console.error(
        "Failed to load tags:",
        err
      );

      setTagsError(
        err?.response?.data?.detail ||
        err?.message ||
        "Failed to load tags."
      );

    } finally {
      setTagsLoading(false);
    }
  }


  // =======================================================
  // INITIAL LOAD
  // =======================================================

  useEffect(() => {
    loadDecision();
    loadVersions();
    loadHistory();
    loadTimeline();
    loadAlternatives();
    loadTags();
  }, [decisionId]);


  // =======================================================
  // ACTUAL ID
  // =======================================================

  const actualDecisionId =
    useMemo(() => {
      return (
        decision?.id ??
        decision?.decision_id ??
        decisionId
      );
    }, [
      decision,
      decisionId,
    ]);


  // =======================================================
  // LOADING
  // =======================================================

  if (loading) {
    return (
      <div className="decision-details-page">
        <div className="decision-loading">
          <div className="loading-spinner" />
          <h2>Loading decision</h2>
          <p>
            Preparing the complete decision
            replay...
          </p>
        </div>
      </div>
    );
  }


  // =======================================================
  // ERROR
  // =======================================================

  if (error) {
    return (
      <div className="decision-details-page">

        <div className="decision-error">

          <div className="error-icon">
            <ShieldAlert size={28} />
          </div>

          <h2>
            Unable to load decision
          </h2>

          <p>
            {error}
          </p>

          <div className="decision-error-actions">

            <button
              type="button"
              className="primary-button"
              onClick={loadDecision}
            >
              Try Again
            </button>

            <button
              type="button"
              className="secondary-button"
              onClick={() =>
                navigate("/decisions")
              }
            >
              Back to Decisions
            </button>

          </div>

        </div>

      </div>
    );
  }


  if (!decision) {
    return (
      <div className="decision-details-page">
        <div className="empty-state">
          Decision not found.
        </div>
      </div>
    );
  }


  // =======================================================
  // VALUES
  // =======================================================

  const title =
    decision.title || "Decision";

  const status =
    decision.status || "Unknown";

  const category =
    decision.category || "—";

  const problemStatement =
    decision.problem_statement ||
    "No problem statement has been provided.";

  const rationale =
    decision.rationale ||
    "No rationale has been provided.";


  // =======================================================
  // RENDER
  // =======================================================

  return (
    <div className="decision-details-page">

      {/* =================================================
          BREADCRUMB
      ================================================== */}

      <div className="decision-breadcrumb">

        <Link to="/decisions">
          <ArrowLeft size={15} />
          Decisions
        </Link>

        <span>/</span>

        <span>
          Decision #{actualDecisionId}
        </span>

      </div>


      {/* =================================================
          HERO
      ================================================== */}

      <section className="decision-hero">

        <div className="decision-hero-main">

          <div className="decision-hero-icon">
            <Scale size={26} />
          </div>

          <div>

            <div className="decision-eyebrow">
              DECISION RECORD
            </div>

            <h1>
              {title}
            </h1>

            <p className="decision-subtitle">
              Decision #{actualDecisionId}
              <span>•</span>
              {category}
            </p>

          </div>

        </div>


        <div className="decision-hero-actions">

          <Link
            to={`/decisions/${actualDecisionId}/history`}
            className="secondary-button"
          >
            <History size={16} />
            Full History
          </Link>

          <Link
            to={`/decisions/${actualDecisionId}/edit`}
            className="primary-button"
          >
            <Edit3 size={16} />
            Edit Decision
          </Link>

        </div>

      </section>


      {/* =================================================
          STATUS STRIP
      ================================================== */}

      <div className="decision-status-strip">

        <div className="status-strip-item">

          <span className="status-strip-label">
            Current Status
          </span>

          <span
            className={`status-badge ${getStatusClass(
              status
            )}`}
          >
            {getStatusIcon(status)}
            {status}
          </span>

        </div>


        <div className="status-strip-divider" />


        <div className="status-strip-item">

          <span className="status-strip-label">
            Created
          </span>

          <span className="status-strip-value">
            <CalendarDays size={15} />
            {formatDate(
              decision.created_at
            )}
          </span>

        </div>


        <div className="status-strip-divider" />


        <div className="status-strip-item">

          <span className="status-strip-label">
            Last Updated
          </span>

          <span className="status-strip-value">
            <Clock3 size={15} />
            {formatDate(
              decision.updated_at
            )}
          </span>

        </div>


        <div className="status-strip-divider" />


        <div className="status-strip-item">

          <span className="status-strip-label">
            Created By
          </span>

          <span className="status-strip-value">
            <User size={15} />
            User {decision.created_by ?? "—"}
          </span>

        </div>

      </div>


      {/* =================================================
          TAGS
      ================================================== */}

      <section className="decision-section">

        <div className="section-heading">

          <div className="section-heading-icon">
            <Tag size={18} />
          </div>

          <div>
            <h2>Decision Tags</h2>
            <p>
              Categories and labels associated
              with this decision.
            </p>
          </div>

        </div>


        {tagsLoading ? (
          <div className="section-loading">
            Loading tags...
          </div>
        ) : tagsError ? (
          <div className="inline-error">
            {tagsError}
          </div>
        ) : tags.length === 0 ? (
          <div className="section-empty">
            No tags assigned to this decision.
          </div>
        ) : (
          <div className="tags-container">

            {tags.map((tag, index) => {

              const tagName =
                typeof tag === "string"
                  ? tag
                  : tag.name ??
                    tag.tag ??
                    tag.label ??
                    `Tag ${index + 1}`;

              const key =
                tag?.id ??
                tag?.tag_id ??
                `${tagName}-${index}`;

              return (
                <span
                  key={key}
                  className="decision-tag"
                >
                  <Tag size={13} />
                  {tagName}
                </span>
              );
            })}

          </div>
        )}

      </section>


      {/* =================================================
          CORE INFORMATION
      ================================================== */}

      <div className="decision-two-column">

        {/* Problem */}

        <section className="decision-section">

          <div className="section-heading">

            <div className="section-heading-icon blue">
              <FileText size={18} />
            </div>

            <div>
              <h2>Problem Statement</h2>
              <p>
                What problem is this decision
                addressing?
              </p>
            </div>

          </div>

          <div className="decision-content">
            {problemStatement}
          </div>

        </section>


        {/* Rationale */}

        <section className="decision-section">

          <div className="section-heading">

            <div className="section-heading-icon green">
              <CheckCircle2 size={18} />
            </div>

            <div>
              <h2>Rationale</h2>
              <p>
                Why was this decision made?
              </p>
            </div>

          </div>

          <div className="decision-content">
            {rationale}
          </div>

        </section>

      </div>


      {/* =================================================
          VERSION HISTORY
      ================================================== */}

      <section className="decision-section">

        <div className="section-header-row">

          <div className="section-heading">

            <div className="section-heading-icon purple">
              <History size={18} />
            </div>

            <div>
              <h2>Version History</h2>
              <p>
                Track how the decision evolved
                over time.
              </p>
            </div>

          </div>


          <button
            type="button"
            className="section-toggle-modern"
            onClick={() =>
              setShowVersions(
                (value) => !value
              )
            }
          >
            {showVersions ? (
              <>
                <ChevronUp size={16} />
                Hide
              </>
            ) : (
              <>
                <ChevronDown size={16} />
                Show
              </>
            )}
          </button>

        </div>


        {showVersions && (
          <>
            {versionsLoading ? (
              <div className="section-loading">
                Loading versions...
              </div>
            ) : versionsError ? (
              <div className="inline-error">
                {versionsError}
              </div>
            ) : versions.length === 0 ? (
              <div className="section-empty">
                No versions found.
              </div>
            ) : (
              <div className="modern-table-wrapper">

                <table className="modern-table">

                  <thead>
                    <tr>
                      <th>Version</th>
                      <th>Decision Title</th>
                      <th>Status</th>
                      <th>Created By</th>
                      <th>Date</th>
                    </tr>
                  </thead>

                  <tbody>

                    {versions.map(
                      (version, index) => {

                        const versionNumber =
                          version.version_number ??
                          version.version ??
                          version.number ??
                          index + 1;

                        return (
                          <tr
                            key={
                              version.id ??
                              `${versionNumber}-${index}`
                            }
                          >

                            <td>
                              <span className="version-badge">
                                V{versionNumber}
                              </span>
                            </td>

                            <td>
                              <strong>
                                {version.title ||
                                  "—"}
                              </strong>
                            </td>

                            <td>
                              <span
                                className={`status-badge ${getStatusClass(
                                  version.status
                                )}`}
                              >
                                {version.status ||
                                  "—"}
                              </span>
                            </td>

                            <td>
                              User{" "}
                              {version.created_by ??
                                version.user_id ??
                                "—"}
                            </td>

                            <td>
                              {formatDate(
                                version.created_at ??
                                  version.createdAt
                              )}
                            </td>

                          </tr>
                        );
                      }
                    )}

                  </tbody>

                </table>

              </div>
            )}
          </>
        )}

      </section>


      {/* =================================================
          ALTERNATIVES
      ================================================== */}

      <section className="decision-section">

        <div className="section-header-row">

          <div className="section-heading">

            <div className="section-heading-icon orange">
              <Layers3 size={18} />
            </div>

            <div>
              <h2>Alternative Analysis</h2>
              <p>
                Compare the available options
                considered for this decision.
              </p>
            </div>

          </div>


          <div className="section-button-group">

            <Link
              to={`/decisions/${actualDecisionId}/alternatives`}
              className="secondary-button"
            >
              Manage
            </Link>

            <Link
              to={`/decisions/${actualDecisionId}/alternatives/compare`}
              className="primary-button"
            >
              <Scale size={16} />
              Compare
            </Link>

            <button
              type="button"
              className="section-toggle-modern"
              onClick={() =>
                setShowAlternatives(
                  (value) => !value
                )
              }
            >
              {showAlternatives ? (
                <ChevronUp size={16} />
              ) : (
                <ChevronDown size={16} />
              )}
            </button>

          </div>

        </div>


        {showAlternatives && (
          <>
            {alternativesLoading ? (
              <div className="section-loading">
                Loading alternatives...
              </div>
            ) : alternativesError ? (
              <div className="inline-error">
                {alternativesError}
              </div>
            ) : alternatives.length === 0 ? (
              <div className="section-empty">
                No alternatives found for this
                decision.
              </div>
            ) : (
              <div className="alternative-grid">

                {alternatives.map(
                  (alternative, index) => {

                    const risk =
                      alternative.risk_level ||
                      "—";

                    const riskClass =
                      String(risk)
                        .toLowerCase()
                        .includes("high")
                        ? "risk-high"
                        : String(risk)
                            .toLowerCase()
                            .includes("medium")
                        ? "risk-medium"
                        : "risk-low";

                    return (
                      <div
                        className="alternative-card"
                        key={
                          alternative.id ??
                          alternative.alternative_id ??
                          index
                        }
                      >

                        <div className="alternative-card-header">

                          <div className="alternative-number">
                            {String(
                              index + 1
                            ).padStart(2, "0")}
                          </div>

                          <div>
                            <h3>
                              {alternative.name ||
                                "Alternative"}
                            </h3>

                            <span
                              className={`risk-badge ${riskClass}`}
                            >
                              {risk}
                            </span>
                          </div>

                        </div>


                        <p className="alternative-description">
                          {alternative.description ||
                            "No description provided."}
                        </p>


                        <div className="alternative-metrics">

                          <div>
                            <span>
                              Estimated Cost
                            </span>

                            <strong>
                              {alternative.estimated_cost !=
                              null
                                ? Number(
                                    alternative.estimated_cost
                                  ).toLocaleString()
                                : "—"}
                            </strong>
                          </div>


                          <div>
                            <span>
                              Feasibility
                            </span>

                            <strong>
                              {alternative.feasibility_score ??
                                "—"}
                              <small>
                                /5
                              </small>
                            </strong>
                          </div>

                        </div>


                        <div className="alternative-pros-cons">

                          <div className="pros-box">
                            <strong>
                              Pros
                            </strong>

                            <p>
                              {alternative.pros ||
                                "—"}
                            </p>
                          </div>


                          <div className="cons-box">
                            <strong>
                              Cons
                            </strong>

                            <p>
                              {alternative.cons ||
                                "—"}
                            </p>
                          </div>

                        </div>

                      </div>
                    );
                  }
                )}

              </div>
            )}
          </>
        )}

      </section>


      {/* =================================================
          TIMELINE
      ================================================== */}

      <section className="decision-section">

        <div className="section-header-row">

          <div className="section-heading">

            <div className="section-heading-icon blue">
              <FileClock size={18} />
            </div>

            <div>
              <h2>Decision Timeline</h2>
              <p>
                Replay the major events in this
                decision's lifecycle.
              </p>
            </div>

          </div>


          <button
            type="button"
            className="section-toggle-modern"
            onClick={() =>
              setShowTimeline(
                (value) => !value
              )
            }
          >
            {showTimeline ? (
              <>
                <ChevronUp size={16} />
                Hide
              </>
            ) : (
              <>
                <ChevronDown size={16} />
                Show
              </>
            )}
          </button>

        </div>


        {showTimeline && (
          <>
            {timelineLoading ? (
              <div className="section-loading">
                Loading timeline...
              </div>
            ) : timelineError ? (
              <div className="inline-error">
                {timelineError}
              </div>
            ) : timeline.length === 0 ? (
              <div className="section-empty">
                No timeline events found.
              </div>
            ) : (
              <div className="decision-timeline">

                {timeline.map(
                  (event, index) => {

                    const eventTitle =
                      event.action ??
                      event.event ??
                      event.event_type ??
                      event.title ??
                      "Activity";

                    const eventDescription =
                      event.description ??
                      event.details ??
                      event.message ??
                      "";

                    const eventDate =
                      event.created_at ??
                      event.timestamp ??
                      event.event_time ??
                      event.date;

                    const eventUser =
                      event.user_id ??
                      event.created_by ??
                      event.actor_id;

                    return (
                      <div
                        className="timeline-event"
                        key={
                          event.id ??
                          `timeline-${index}`
                        }
                      >

                        <div className="timeline-line" />

                        <div className="timeline-node">
                          {index === 0 ? (
                            <CheckCircle2 size={14} />
                          ) : (
                            <Clock3 size={14} />
                          )}
                        </div>

                        <div className="timeline-event-card">

                          <div className="timeline-event-header">

                            <h3>
                              {eventTitle}
                            </h3>

                            <span>
                              {eventDate
                                ? formatDate(
                                    eventDate
                                  )
                                : "—"}
                            </span>

                          </div>

                          {eventDescription && (
                            <p>
                              {eventDescription}
                            </p>
                          )}

                          {eventUser != null && (
                            <div className="timeline-user">
                              <User size={13} />
                              User {eventUser}
                            </div>
                          )}

                        </div>

                      </div>
                    );
                  }
                )}

              </div>
            )}
          </>
        )}

      </section>


      {/* =================================================
          AUDIT HISTORY
      ================================================== */}

      <section className="decision-section">

        <div className="section-header-row">

          <div className="section-heading">

            <div className="section-heading-icon red">
              <ShieldAlert size={18} />
            </div>

            <div>
              <h2>Audit History</h2>
              <p>
                Track system activity associated
                with this decision.
              </p>
            </div>

          </div>


          <button
            type="button"
            className="section-toggle-modern"
            onClick={() =>
              setShowHistory(
                (value) => !value
              )
            }
          >
            {showHistory ? (
              <>
                <ChevronUp size={16} />
                Hide
              </>
            ) : (
              <>
                <ChevronDown size={16} />
                Show
              </>
            )}
          </button>

        </div>


        {showHistory && (
          <>
            {historyLoading ? (
              <div className="section-loading">
                Loading audit history...
              </div>
            ) : historyError ? (
              <div className="inline-error">
                {historyError}
              </div>
            ) : history.length === 0 ? (
              <div className="section-empty">
                No audit history found.
              </div>
            ) : (
              <div className="modern-table-wrapper">

                <table className="modern-table">

                  <thead>
                    <tr>
                      <th>Action</th>
                      <th>Entity</th>
                      <th>User</th>
                      <th>Date</th>
                      <th>Details</th>
                    </tr>
                  </thead>

                  <tbody>

                    {history.map(
                      (item, index) => {

                        const action =
                          item.action ??
                          item.event ??
                          item.event_type ??
                          "—";

                        const entity =
                          item.entity_type ??
                          item.entity ??
                          "—";

                        const user =
                          item.user_id ??
                          item.created_by ??
                          item.actor_id ??
                          "—";

                        const date =
                          item.created_at ??
                          item.timestamp ??
                          item.date;

                        const details =
                          item.details ??
                          item.description ??
                          item.message ??
                          "—";

                        return (
                          <tr
                            key={
                              item.id ??
                              `history-${index}`
                            }
                          >

                            <td>
                              <strong>
                                {action}
                              </strong>
                            </td>

                            <td>
                              {entity}
                            </td>

                            <td>
                              User {user}
                            </td>

                            <td>
                              {formatDate(date)}
                            </td>

                            <td className="audit-details">
                              {typeof details ===
                              "object"
                                ? JSON.stringify(
                                    details
                                  )
                                : details}
                            </td>

                          </tr>
                        );
                      }
                    )}

                  </tbody>

                </table>

              </div>
            )}
          </>
        )}

      </section>


      {/* =================================================
          FOOTER ACTIONS
      ================================================== */}

      <div className="decision-footer">

        <Link
          to="/decisions"
          className="secondary-button"
        >
          <ArrowLeft size={16} />
          Back to Decisions
        </Link>

        <div>

          <Link
            to={`/decisions/${actualDecisionId}/discussions`}
            className="secondary-button"
          >
            <MessageSquare size={16} />
            Discussions
          </Link>

          <Link
            to={`/decisions/${actualDecisionId}/edit`}
            className="primary-button"
          >
            <Pencil size={16} />
            Edit Decision
          </Link>

        </div>

      </div>


      {/* =================================================
          PAGE STYLES
      ================================================== */}

      <style>{`

        .decision-details-page {
          max-width: 1280px;
          margin: 0 auto;
          padding: 28px 32px 45px;
        }


        /* ================================================
           BREADCRUMB
        ================================================ */

        .decision-breadcrumb {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 18px;
          font-size: 13px;
          color: #667085;
        }

        .decision-breadcrumb a {
          display: inline-flex;
          align-items: center;
          gap: 5px;
          color: #2563eb;
          text-decoration: none;
          font-weight: 600;
        }

        .decision-breadcrumb a:hover {
          text-decoration: underline;
        }


        /* ================================================
           HERO
        ================================================ */

        .decision-hero {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 25px;
          padding: 28px;
          margin-bottom: 18px;
          background: linear-gradient(
            135deg,
            #172033 0%,
            #1e2b46 100%
          );
          border-radius: 16px;
          color: white;
          box-shadow:
            0 12px 30px
            rgba(15, 23, 42, 0.12);
        }

        .decision-hero-main {
          display: flex;
          align-items: center;
          gap: 18px;
          min-width: 0;
        }

        .decision-hero-icon {
          width: 54px;
          height: 54px;
          flex-shrink: 0;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 14px;
          background: rgba(255,255,255,0.12);
          border: 1px solid rgba(255,255,255,0.16);
        }

        .decision-eyebrow {
          margin-bottom: 5px;
          color: #93c5fd;
          font-size: 11px;
          font-weight: 800;
          letter-spacing: 1.4px;
        }

        .decision-hero h1 {
          margin: 0;
          color: white;
          font-size: 29px;
          line-height: 1.2;
          letter-spacing: -0.5px;
        }

        .decision-subtitle {
          display: flex;
          align-items: center;
          gap: 8px;
          margin: 9px 0 0;
          color: #cbd5e1;
          font-size: 13px;
        }

        .decision-hero-actions {
          display: flex;
          gap: 10px;
          flex-shrink: 0;
        }

        .decision-hero .secondary-button {
          background: rgba(255,255,255,0.08);
          color: white;
          border-color: rgba(255,255,255,0.2);
        }

        .decision-hero .secondary-button:hover {
          background: rgba(255,255,255,0.14);
        }


        /* ================================================
           STATUS STRIP
        ================================================ */

        .decision-status-strip {
          display: grid;
          grid-template-columns:
            1.1fr
            1px
            1fr
            1px
            1fr
            1px
            1fr;
          align-items: center;
          gap: 18px;
          padding: 18px 22px;
          margin-bottom: 20px;
          background: white;
          border: 1px solid #e4e7ec;
          border-radius: 12px;
          box-shadow:
            0 2px 7px
            rgba(16,24,40,0.04);
        }

        .status-strip-item {
          display: flex;
          flex-direction: column;
          gap: 7px;
          min-width: 0;
        }

        .status-strip-label {
          color: #667085;
          font-size: 11px;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .status-strip-value {
          display: flex;
          align-items: center;
          gap: 6px;
          color: #172033;
          font-size: 13px;
          font-weight: 600;
        }

        .status-strip-value svg {
          color: #64748b;
        }

        .status-strip-divider {
          width: 1px;
          height: 38px;
          background: #eaecf0;
        }


        /* ================================================
           SECTIONS
        ================================================ */

        .decision-section {
          padding: 23px;
          margin-bottom: 20px;
          background: white;
          border: 1px solid #e4e7ec;
          border-radius: 13px;
          box-shadow:
            0 2px 7px
            rgba(16,24,40,0.035);
        }

        .section-heading {
          display: flex;
          align-items: flex-start;
          gap: 12px;
        }

        .section-heading-icon {
          width: 38px;
          height: 38px;
          flex-shrink: 0;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 10px;
          background: #eff6ff;
          color: #2563eb;
        }

        .section-heading-icon.blue {
          background: #eff6ff;
          color: #2563eb;
        }

        .section-heading-icon.green {
          background: #ecfdf3;
          color: #067647;
        }

        .section-heading-icon.purple {
          background: #f4f3ff;
          color: #6941c6;
        }

        .section-heading-icon.orange {
          background: #fff7ed;
          color: #c2410c;
        }

        .section-heading-icon.red {
          background: #fef3f2;
          color: #b42318;
        }

        .section-heading h2 {
          margin: 0 0 4px;
          color: #172033;
          font-size: 18px;
          letter-spacing: -0.2px;
        }

        .section-heading p {
          margin: 0;
          color: #667085;
          font-size: 13px;
          line-height: 1.5;
        }

        .section-header-row {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 18px;
          margin-bottom: 20px;
        }

        .section-button-group {
          display: flex;
          align-items: center;
          gap: 8px;
          flex-wrap: wrap;
        }

        .section-toggle-modern {
          display: inline-flex;
          align-items: center;
          gap: 5px;
          padding: 8px 11px;
          border: 1px solid #d0d5dd;
          border-radius: 8px;
          background: white;
          color: #344054;
          font-size: 12px;
          font-weight: 700;
          cursor: pointer;
        }

        .section-toggle-modern:hover {
          background: #f8fafc;
        }


        /* ================================================
           TAGS
        ================================================ */

        .tags-container {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          margin-top: 18px;
        }

        .decision-tag {
          display: inline-flex;
          align-items: center;
          gap: 5px;
          padding: 6px 10px;
          border: 1px solid #b2ddff;
          border-radius: 999px;
          background: #eff8ff;
          color: #175cd3;
          font-size: 12px;
          font-weight: 700;
        }


        /* ================================================
           TWO COLUMN CONTENT
        ================================================ */

        .decision-two-column {
          display: grid;
          grid-template-columns: repeat(2, minmax(0, 1fr));
          gap: 20px;
        }

        .decision-content {
          margin-top: 18px;
          min-height: 100px;
          padding: 17px;
          border: 1px solid #eaecf0;
          border-radius: 10px;
          background: #f8fafc;
          color: #344054;
          font-size: 14px;
          line-height: 1.7;
          white-space: pre-wrap;
        }


        /* ================================================
           STATUS
        ================================================ */

        .status-badge {
          display: inline-flex;
          align-items: center;
          gap: 5px;
          width: fit-content;
          padding: 5px 9px;
          border-radius: 999px;
          font-size: 11px;
          font-weight: 800;
          white-space: nowrap;
        }

        .status-approved {
          background: #dcfae6;
          color: #067647;
        }

        .status-rejected {
          background: #fee4e2;
          color: #b42318;
        }

        .status-review {
          background: #fef0c7;
          color: #b54708;
        }

        .status-draft {
          background: #f2f4f7;
          color: #344054;
        }

        .status-archived {
          background: #eaecf0;
          color: #475467;
        }

        .status-default {
          background: #f2f4f7;
          color: #344054;
        }


        /* ================================================
           TABLES
        ================================================ */

        .modern-table-wrapper {
          width: 100%;
          overflow-x: auto;
          border: 1px solid #eaecf0;
          border-radius: 10px;
        }

        .modern-table {
          width: 100%;
          min-width: 760px;
          border-collapse: collapse;
        }

        .modern-table th,
        .modern-table td {
          padding: 13px 14px;
          text-align: left;
          vertical-align: top;
          border-bottom: 1px solid #eaecf0;
          font-size: 13px;
        }

        .modern-table th {
          background: #f8fafc;
          color: #475467;
          font-size: 11px;
          font-weight: 800;
          text-transform: uppercase;
          letter-spacing: 0.4px;
        }

        .modern-table td {
          color: #344054;
        }

        .modern-table tbody tr:last-child td {
          border-bottom: none;
        }

        .modern-table tbody tr:hover {
          background: #fafcff;
        }

        .version-badge {
          display: inline-flex;
          padding: 4px 8px;
          border-radius: 6px;
          background: #eef4ff;
          color: #3538cd;
          font-size: 11px;
          font-weight: 800;
        }

        .audit-details {
          max-width: 420px;
          line-height: 1.5;
          word-break: break-word;
        }


        /* ================================================
           ALTERNATIVES
        ================================================ */

        .alternative-grid {
          display: grid;
          grid-template-columns:
            repeat(2, minmax(0, 1fr));
          gap: 16px;
        }

        .alternative-card {
          padding: 18px;
          border: 1px solid #e4e7ec;
          border-radius: 11px;
          background: #fbfcfe;
        }

        .alternative-card:hover {
          border-color: #b2ddff;
          box-shadow:
            0 5px 15px
            rgba(37,99,235,0.07);
        }

        .alternative-card-header {
          display: flex;
          align-items: flex-start;
          gap: 12px;
        }

        .alternative-number {
          width: 34px;
          height: 34px;
          flex-shrink: 0;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 9px;
          background: #172033;
          color: white;
          font-size: 11px;
          font-weight: 800;
        }

        .alternative-card h3 {
          margin: 0 0 7px;
          color: #172033;
          font-size: 16px;
        }

        .alternative-description {
          margin: 16px 0;
          color: #667085;
          font-size: 13px;
          line-height: 1.55;
        }

        .risk-badge {
          display: inline-flex;
          padding: 4px 8px;
          border-radius: 999px;
          font-size: 10px;
          font-weight: 800;
          text-transform: uppercase;
        }

        .risk-low {
          background: #dcfae6;
          color: #067647;
        }

        .risk-medium {
          background: #fef0c7;
          color: #b54708;
        }

        .risk-high {
          background: #fee4e2;
          color: #b42318;
        }

        .alternative-metrics {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 10px;
          margin-bottom: 14px;
        }

        .alternative-metrics > div {
          padding: 11px;
          border: 1px solid #eaecf0;
          border-radius: 8px;
          background: white;
        }

        .alternative-metrics span {
          display: block;
          margin-bottom: 5px;
          color: #667085;
          font-size: 10px;
          font-weight: 700;
          text-transform: uppercase;
        }

        .alternative-metrics strong {
          color: #172033;
          font-size: 16px;
        }

        .alternative-metrics small {
          color: #667085;
          font-size: 11px;
          margin-left: 2px;
        }

        .alternative-pros-cons {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 10px;
        }

        .pros-box,
        .cons-box {
          padding: 11px;
          border-radius: 8px;
        }

        .pros-box {
          background: #f0fdf4;
        }

        .cons-box {
          background: #fff7ed;
        }

        .pros-box strong {
          color: #15803d;
        }

        .cons-box strong {
          color: #c2410c;
        }

        .pros-box p,
        .cons-box p {
          margin: 6px 0 0;
          color: #475467;
          font-size: 12px;
          line-height: 1.5;
        }


        /* ================================================
           TIMELINE
        ================================================ */

        .decision-timeline {
          position: relative;
          padding-left: 12px;
        }

        .timeline-event {
          position: relative;
          display: flex;
          gap: 14px;
          padding-bottom: 18px;
        }

        .timeline-event:last-child {
          padding-bottom: 0;
        }

        .timeline-line {
          position: absolute;
          left: 14px;
          top: 27px;
          bottom: -3px;
          width: 2px;
          background: #e4e7ec;
        }

        .timeline-event:last-child .timeline-line {
          display: none;
        }

        .timeline-node {
          position: relative;
          z-index: 2;
          width: 29px;
          height: 29px;
          flex-shrink: 0;
          display: flex;
          align-items: center;
          justify-content: center;
          border: 3px solid white;
          border-radius: 50%;
          background: #2563eb;
          color: white;
          box-shadow:
            0 0 0 1px #bfdbfe;
        }

        .timeline-event-card {
          flex: 1;
          padding: 13px 15px;
          border: 1px solid #e4e7ec;
          border-radius: 9px;
          background: #fbfcfe;
        }

        .timeline-event-header {
          display: flex;
          align-items: flex-start;
          justify-content: space-between;
          gap: 15px;
        }

        .timeline-event-header h3 {
          margin: 0;
          color: #172033;
          font-size: 14px;
        }

        .timeline-event-header span {
          color: #667085;
          font-size: 11px;
          white-space: nowrap;
        }

        .timeline-event-card p {
          margin: 7px 0;
          color: #475467;
          font-size: 13px;
          line-height: 1.5;
        }

        .timeline-user {
          display: inline-flex;
          align-items: center;
          gap: 5px;
          color: #667085;
          font-size: 11px;
        }


        /* ================================================
           STATES
        ================================================ */

        .section-loading,
        .section-empty {
          padding: 28px 15px;
          text-align: center;
          color: #667085;
          font-size: 13px;
        }

        .inline-error {
          padding: 12px 14px;
          border: 1px solid #fecdca;
          border-radius: 8px;
          background: #fef3f2;
          color: #b42318;
          font-size: 13px;
        }

        .decision-loading {
          min-height: 400px;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          text-align: center;
        }

        .decision-loading h2 {
          margin: 10px 0 5px;
          color: #172033;
        }

        .decision-loading p {
          margin: 0;
          color: #667085;
        }

        .decision-error {
          max-width: 600px;
          margin: 70px auto;
          padding: 35px;
          text-align: center;
          background: white;
          border: 1px solid #e4e7ec;
          border-radius: 14px;
          box-shadow:
            0 8px 25px
            rgba(16,24,40,0.06);
        }

        .error-icon {
          width: 55px;
          height: 55px;
          margin: 0 auto 15px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 50%;
          background: #fef3f2;
          color: #b42318;
        }

        .decision-error h2 {
          margin: 0 0 8px;
          color: #172033;
        }

        .decision-error p {
          margin: 0;
          color: #667085;
          line-height: 1.6;
        }

        .decision-error-actions {
          display: flex;
          justify-content: center;
          gap: 10px;
          margin-top: 22px;
        }


        /* ================================================
           FOOTER
        ================================================ */

        .decision-footer {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 12px;
          padding-top: 5px;
        }

        .decision-footer > div {
          display: flex;
          gap: 9px;
        }


        /* ================================================
           RESPONSIVE
        ================================================ */

        @media (max-width: 1000px) {

          .decision-status-strip {
            grid-template-columns:
              repeat(2, 1fr);
          }

          .status-strip-divider {
            display: none;
          }

          .alternative-grid {
            grid-template-columns: 1fr;
          }

        }


        @media (max-width: 800px) {

          .decision-details-page {
            padding: 22px 20px 35px;
          }

          .decision-hero {
            flex-direction: column;
            align-items: flex-start;
          }

          .decision-hero-actions {
            width: 100%;
          }

          .decision-hero-actions a {
            flex: 1;
          }

          .decision-two-column {
            grid-template-columns: 1fr;
          }

          .section-header-row {
            align-items: flex-start;
            flex-direction: column;
          }

          .section-button-group {
            width: 100%;
          }

        }


        @media (max-width: 600px) {

          .decision-details-page {
            padding: 18px 14px 30px;
          }

          .decision-hero {
            padding: 21px;
          }

          .decision-hero-main {
            align-items: flex-start;
          }

          .decision-hero h1 {
            font-size: 23px;
          }

          .decision-status-strip {
            grid-template-columns: 1fr;
            gap: 13px;
          }

          .decision-section {
            padding: 18px;
          }

          .alternative-metrics,
          .alternative-pros-cons {
            grid-template-columns: 1fr;
          }

          .decision-footer {
            flex-direction: column;
            align-items: stretch;
          }

          .decision-footer > div {
            width: 100%;
          }

          .decision-footer > a,
          .decision-footer > div a {
            flex: 1;
            justify-content: center;
          }

          .decision-error-actions {
            flex-direction: column;
          }

        }

      `}</style>

    </div>
  );
}