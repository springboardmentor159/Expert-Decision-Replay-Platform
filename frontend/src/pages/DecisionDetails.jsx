import React, { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import {
  getDecision,
  getDecisionTags,
  getDecisionVersions,
  getDecisionHistory,
  getDecisionTimeline,
  compareAlternatives,
} from "../api/decisionApi";


// ---------------------------------------------------------
// Helpers
// ---------------------------------------------------------

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


// ---------------------------------------------------------
// Component
// ---------------------------------------------------------

export default function DecisionDetails() {
  const { decisionId } = useParams();
  const navigate = useNavigate();

  const [decision, setDecision] = useState(null);

  const [versions, setVersions] = useState([]);
  const [history, setHistory] = useState([]);
  const [timeline, setTimeline] = useState([]);
  const [alternatives, setAlternatives] = useState([]);
  const [tags, setTags] = useState([]);

  const [loading, setLoading] = useState(true);

  const [versionsLoading, setVersionsLoading] = useState(true);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [timelineLoading, setTimelineLoading] = useState(true);
  const [alternativesLoading, setAlternativesLoading] = useState(true);
  const [tagsLoading, setTagsLoading] = useState(true);

  const [error, setError] = useState("");
  const [versionsError, setVersionsError] = useState("");
  const [historyError, setHistoryError] = useState("");
  const [timelineError, setTimelineError] = useState("");
  const [alternativesError, setAlternativesError] = useState("");
  const [tagsError, setTagsError] = useState("");

  const [showVersions, setShowVersions] = useState(true);
  const [showHistory, setShowHistory] = useState(true);
  const [showTimeline, setShowTimeline] = useState(true);
  const [showAlternatives, setShowAlternatives] = useState(true);

  // -------------------------------------------------------
  // Load main decision
  // -------------------------------------------------------

  async function loadDecision() {
    if (!decisionId) {
      setError("Decision ID is missing.");
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError("");

      const data = await getDecision(decisionId);

      console.log("Decision API response:", data);

      /*
       * The backend normally returns the Decision object directly.
       * This also handles wrapped responses just in case.
       */
      const rawDecision =
        data?.decision ||
        data?.data ||
        data;

      if (!rawDecision || typeof rawDecision !== "object") {
        throw new Error("Invalid decision data received from the server.");
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

      console.log("Normalized decision:", normalizedDecision);

      setDecision(normalizedDecision);
    } catch (err) {
      console.error("Failed to load decision:", err);

      const status = err?.response?.status;

      if (status === 401) {
        setError("Your session has expired. Please log in again.");
      } else if (status === 403) {
        setError("You do not have permission to view this decision.");
      } else if (status === 404) {
        setError("Decision not found.");
      } else if (status === 422) {
        setError("Invalid decision ID.");
      } else if (status >= 500) {
        setError("Server error while loading the decision.");
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


  // -------------------------------------------------------
  // Load versions
  // -------------------------------------------------------

  async function loadVersions() {
    if (!decisionId) return;

    try {
      setVersionsLoading(true);
      setVersionsError("");

      const data = await getDecisionVersions(decisionId);

      console.log("Versions response:", data);

      setVersions(
        getArray(data, [
          "versions",
          "items",
          "results",
          "data",
        ])
      );
    } catch (err) {
      console.error("Failed to load versions:", err);

      setVersionsError(
        err?.response?.data?.detail ||
          err?.message ||
          "Failed to load version history."
      );
    } finally {
      setVersionsLoading(false);
    }
  }


  // -------------------------------------------------------
  // Load history
  // -------------------------------------------------------

  async function loadHistory() {
    if (!decisionId) return;

    try {
      setHistoryLoading(true);
      setHistoryError("");

      const data = await getDecisionHistory(decisionId);

      console.log("History response:", data);

      setHistory(
        getArray(data, [
          "history",
          "items",
          "results",
          "data",
        ])
      );
    } catch (err) {
      console.error("Failed to load history:", err);

      setHistoryError(
        err?.response?.data?.detail ||
          err?.message ||
          "Failed to load decision history."
      );
    } finally {
      setHistoryLoading(false);
    }
  }


  // -------------------------------------------------------
  // Load timeline
  // -------------------------------------------------------

  async function loadTimeline() {
    if (!decisionId) return;

    try {
      setTimelineLoading(true);
      setTimelineError("");

      const data = await getDecisionTimeline(decisionId);

      console.log("Timeline response:", data);

      setTimeline(
        getArray(data, [
          "timeline",
          "items",
          "results",
          "data",
        ])
      );
    } catch (err) {
      console.error("Failed to load timeline:", err);

      setTimelineError(
        err?.response?.data?.detail ||
          err?.message ||
          "Failed to load decision timeline."
      );
    } finally {
      setTimelineLoading(false);
    }
  }


  // -------------------------------------------------------
  // Load alternatives
  // -------------------------------------------------------

  async function loadAlternatives() {
    if (!decisionId) return;

    try {
      setAlternativesLoading(true);
      setAlternativesError("");

      const data = await compareAlternatives(decisionId);

      console.log("Alternatives comparison response:", data);

      setAlternatives(
        getArray(data, [
          "alternatives",
          "items",
          "results",
          "data",
        ])
      );
    } catch (err) {
      console.error("Failed to load alternatives:", err);

      setAlternativesError(
        err?.response?.data?.detail ||
          err?.message ||
          "Failed to load alternatives."
      );
    } finally {
      setAlternativesLoading(false);
    }
  }


  // -------------------------------------------------------
  // Load tags
  // -------------------------------------------------------

  async function loadTags() {
    if (!decisionId) return;

    try {
      setTagsLoading(true);
      setTagsError("");

      const data = await getDecisionTags(decisionId);

      console.log("Tags response:", data);

      setTags(
        getArray(data, [
          "tags",
          "items",
          "results",
          "data",
        ])
      );
    } catch (err) {
      console.error("Failed to load tags:", err);

      setTagsError(
        err?.response?.data?.detail ||
          err?.message ||
          "Failed to load tags."
      );
    } finally {
      setTagsLoading(false);
    }
  }


  // -------------------------------------------------------
  // Initial load
  // -------------------------------------------------------

  useEffect(() => {
    loadDecision();
    loadVersions();
    loadHistory();
    loadTimeline();
    loadAlternatives();
    loadTags();
  }, [decisionId]);


  // -------------------------------------------------------
  // Actual ID
  // -------------------------------------------------------

  const actualDecisionId = useMemo(() => {
    return decision?.id ?? decision?.decision_id ?? decisionId;
  }, [decision, decisionId]);


  // -------------------------------------------------------
  // Loading state
  // -------------------------------------------------------

  if (loading) {
    return (
      <div className="decision-details-page">
        <div className="page-header">
          <h1>Decision Details</h1>
        </div>

        <div className="loading-state">
          Loading decision...
        </div>
      </div>
    );
  }


  // -------------------------------------------------------
  // Error state
  // -------------------------------------------------------

  if (error) {
    return (
      <div className="decision-details-page">
        <div className="page-header">
          <h1>Decision Details</h1>
        </div>

        <div className="error-box">
          <strong>Error:</strong> {error}
        </div>

        <div className="page-actions">
          <button
            type="button"
            onClick={loadDecision}
            className="btn btn-primary"
          >
            Try Again
          </button>

          <button
            type="button"
            onClick={() => navigate("/decisions")}
            className="btn btn-secondary"
          >
            Back to Decisions
          </button>
        </div>
      </div>
    );
  }


  // -------------------------------------------------------
  // No decision
  // -------------------------------------------------------

  if (!decision) {
    return (
      <div className="decision-details-page">
        <div className="empty-state">
          Decision not found.
        </div>
      </div>
    );
  }


  // -------------------------------------------------------
  // Main values
  // -------------------------------------------------------

  const title = decision.title || "Decision";

  const status = decision.status || "Unknown";

  const category = decision.category || "—";

  const problemStatement =
    decision.problem_statement ||
    "No problem statement has been provided.";

  const rationale =
    decision.rationale ||
    "No rationale has been provided.";


  // -------------------------------------------------------
  // Render
  // -------------------------------------------------------

  return (
    <div className="decision-details-page">

      {/* ------------------------------------------------ */}
      {/* Header */}
      {/* ------------------------------------------------ */}

      <div className="page-header">

        <div>
          <div className="breadcrumb">
            <Link to="/decisions">
              Decisions
            </Link>

            <span> / </span>

            <span>Decision #{actualDecisionId}</span>
          </div>

          <h1>{title}</h1>

          <p className="decision-number">
            Decision #{actualDecisionId}
          </p>
        </div>

        <div className="page-actions">

          <Link
            to={`/decisions/${actualDecisionId}/history`}
            className="btn btn-secondary"
          >
            View Full History
          </Link>

          <Link
            to={`/decisions/${actualDecisionId}/edit`}
            className="btn btn-primary"
          >
            Edit
          </Link>

        </div>
      </div>


      {/* ------------------------------------------------ */}
      {/* Decision Summary */}
      {/* ------------------------------------------------ */}

      <section className="details-card">

        <h2>Decision Summary</h2>

        <div className="details-grid">

          <div className="detail-item">
            <span className="detail-label">
              Status
            </span>

            <span
              className={`status-badge ${getStatusClass(status)}`}
            >
              {status}
            </span>
          </div>


          <div className="detail-item">
            <span className="detail-label">
              Category
            </span>

            <span className="detail-value">
              {category}
            </span>
          </div>


          <div className="detail-item">
            <span className="detail-label">
              Created
            </span>

            <span className="detail-value">
              {formatDate(decision.created_at)}
            </span>
          </div>


          <div className="detail-item">
            <span className="detail-label">
              Last Updated
            </span>

            <span className="detail-value">
              {formatDate(decision.updated_at)}
            </span>
          </div>


          <div className="detail-item">
            <span className="detail-label">
              Created By
            </span>

            <span className="detail-value">
              {decision.created_by ?? "—"}
            </span>
          </div>

        </div>
      </section>


      {/* ------------------------------------------------ */}
      {/* Tags */}
      {/* ------------------------------------------------ */}

      <section className="details-card">

        <div className="section-header">

          <h2>Tags</h2>

        </div>


        {tagsLoading ? (
          <div className="loading-state">
            Loading tags...
          </div>
        ) : tagsError ? (
          <div className="error-box">
            {tagsError}
          </div>
        ) : tags.length === 0 ? (
          <p className="muted-text">
            No tags assigned to this decision.
          </p>
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
                  className="tag"
                >
                  {tagName}
                </span>
              );
            })}

          </div>
        )}

      </section>


      {/* ------------------------------------------------ */}
      {/* Problem Statement */}
      {/* ------------------------------------------------ */}

      <section className="details-card">

        <h2>Problem Statement</h2>

        <div className="content-box">
          {problemStatement}
        </div>

      </section>


      {/* ------------------------------------------------ */}
      {/* Rationale */}
      {/* ------------------------------------------------ */}

      <section className="details-card">

        <h2>Rationale</h2>

        <div className="content-box">
          {rationale}
        </div>

      </section>


      {/* ------------------------------------------------ */}
      {/* Version History */}
      {/* ------------------------------------------------ */}

      <section className="details-card">

        <div className="section-header">

          <h2>Version History</h2>

          <button
            type="button"
            className="section-toggle"
            onClick={() =>
              setShowVersions((value) => !value)
            }
          >
            {showVersions ? "Hide" : "Show"}
          </button>

        </div>


        {showVersions && (
          <>
            {versionsLoading ? (
              <div className="loading-state">
                Loading versions...
              </div>
            ) : versionsError ? (
              <div className="error-box">
                {versionsError}
              </div>
            ) : versions.length === 0 ? (
              <div className="empty-state">
                No versions found.
              </div>
            ) : (
              <div className="table-container">

                <table className="details-table">

                  <thead>
                    <tr>
                      <th>Version</th>
                      <th>Title</th>
                      <th>Status</th>
                      <th>Created By</th>
                      <th>Created At</th>
                    </tr>
                  </thead>

                  <tbody>

                    {versions.map((version, index) => {

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
                            <strong>
                              V{versionNumber}
                            </strong>
                          </td>

                          <td>
                            {version.title || "—"}
                          </td>

                          <td>
                            <span
                              className={`status-badge ${getStatusClass(
                                version.status
                              )}`}
                            >
                              {version.status || "—"}
                            </span>
                          </td>

                          <td>
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
                    })}

                  </tbody>

                </table>

              </div>
            )}
          </>
        )}

      </section>


      {/* ------------------------------------------------ */}
      {/* Alternatives */}
      {/* ------------------------------------------------ */}

      <section className="details-card">

        <div className="section-header">

          <h2>Alternatives</h2>

          <div className="section-actions">

            <Link
              to={`/decisions/${actualDecisionId}/alternatives`}
              className="btn btn-secondary"
            >
              Manage Alternatives
            </Link>

            <Link
              to={`/decisions/${actualDecisionId}/alternatives/compare`}
              className="btn btn-primary"
            >
              Compare
            </Link>

            <button
              type="button"
              className="section-toggle"
              onClick={() =>
                setShowAlternatives((value) => !value)
              }
            >
              {showAlternatives ? "Hide" : "Show"}
            </button>

          </div>

        </div>


        {showAlternatives && (
          <>
            {alternativesLoading ? (
              <div className="loading-state">
                Loading alternatives...
              </div>
            ) : alternativesError ? (
              <div className="error-box">
                {alternativesError}
              </div>
            ) : alternatives.length === 0 ? (
              <div className="empty-state">
                No alternatives found for this decision.
              </div>
            ) : (
              <div className="table-container">

                <table className="details-table">

                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Description</th>
                      <th>Pros</th>
                      <th>Cons</th>
                      <th>Estimated Cost</th>
                      <th>Feasibility</th>
                      <th>Risk</th>
                    </tr>
                  </thead>

                  <tbody>

                    {alternatives.map(
                      (alternative, index) => (

                        <tr
                          key={
                            alternative.id ??
                            alternative.alternative_id ??
                            index
                          }
                        >

                          <td>
                            <strong>
                              {alternative.name || "—"}
                            </strong>
                          </td>

                          <td>
                            {alternative.description ||
                              "—"}
                          </td>

                          <td>
                            {alternative.pros || "—"}
                          </td>

                          <td>
                            {alternative.cons || "—"}
                          </td>

                          <td>
                            {alternative.estimated_cost !=
                            null
                              ? alternative.estimated_cost
                              : "—"}
                          </td>

                          <td>
                            {alternative.feasibility_score ??
                              "—"}
                          </td>

                          <td>
                            {alternative.risk_level ||
                              "—"}
                          </td>

                        </tr>
                      )
                    )}

                  </tbody>

                </table>

              </div>
            )}
          </>
        )}

      </section>


      {/* ------------------------------------------------ */}
      {/* Decision Timeline */}
      {/* ------------------------------------------------ */}

      <section className="details-card">

        <div className="section-header">

          <h2>Decision Timeline</h2>

          <button
            type="button"
            className="section-toggle"
            onClick={() =>
              setShowTimeline((value) => !value)
            }
          >
            {showTimeline ? "Hide" : "Show"}
          </button>

        </div>


        {showTimeline && (
          <>
            {timelineLoading ? (
              <div className="loading-state">
                Loading timeline...
              </div>
            ) : timelineError ? (
              <div className="error-box">
                {timelineError}
              </div>
            ) : timeline.length === 0 ? (
              <div className="empty-state">
                No timeline events found.
              </div>
            ) : (
              <div className="timeline">

                {timeline.map((event, index) => {

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
                      className="timeline-item"
                      key={
                        event.id ??
                        `timeline-${index}`
                      }
                    >

                      <div className="timeline-marker">
                        ●
                      </div>

                      <div className="timeline-content">

                        <div className="timeline-title">
                          {eventTitle}
                        </div>

                        {eventDescription && (
                          <div className="timeline-description">
                            {eventDescription}
                          </div>
                        )}

                        <div className="timeline-meta">

                          {eventDate && (
                            <span>
                              {formatDate(eventDate)}
                            </span>
                          )}

                          {eventUser != null && (
                            <span>
                              User {eventUser}
                            </span>
                          )}

                        </div>

                      </div>

                    </div>
                  );
                })}

              </div>
            )}
          </>
        )}

      </section>


      {/* ------------------------------------------------ */}
      {/* Audit History */}
      {/* ------------------------------------------------ */}

      <section className="details-card">

        <div className="section-header">

          <h2>Audit History</h2>

          <button
            type="button"
            className="section-toggle"
            onClick={() =>
              setShowHistory((value) => !value)
            }
          >
            {showHistory ? "Hide" : "Show"}
          </button>

        </div>


        {showHistory && (
          <>
            {historyLoading ? (
              <div className="loading-state">
                Loading audit history...
              </div>
            ) : historyError ? (
              <div className="error-box">
                {historyError}
              </div>
            ) : history.length === 0 ? (
              <div className="empty-state">
                No audit history found.
              </div>
            ) : (
              <div className="table-container">

                <table className="details-table">

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

                    {history.map((item, index) => {

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
                            {action}
                          </td>

                          <td>
                            {entity}
                          </td>

                          <td>
                            {user}
                          </td>

                          <td>
                            {formatDate(date)}
                          </td>

                          <td>
                            {typeof details === "object"
                              ? JSON.stringify(details)
                              : details}
                          </td>

                        </tr>
                      );
                    })}

                  </tbody>

                </table>

              </div>
            )}
          </>
        )}

      </section>


      {/* ------------------------------------------------ */}
      {/* Footer Actions */}
      {/* ------------------------------------------------ */}

      <div className="page-footer-actions">

        <Link
          to="/decisions"
          className="btn btn-secondary"
        >
          Back to Decisions
        </Link>

        <Link
          to={`/decisions/${actualDecisionId}/discussions`}
          className="btn btn-secondary"
        >
          Discussions
        </Link>

        <Link
          to={`/decisions/${actualDecisionId}/edit`}
          className="btn btn-primary"
        >
          Edit Decision
        </Link>

      </div>


      {/* ------------------------------------------------ */}
      {/* Page-specific styling */}
      {/* ------------------------------------------------ */}

      <style>{`

        .decision-details-page {
          max-width: 1200px;
          margin: 0 auto;
          padding: 24px;
        }

        .page-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          gap: 24px;
          margin-bottom: 28px;
        }

        .page-header h1 {
          margin: 8px 0;
          font-size: 32px;
          color: #172033;
        }

        .breadcrumb {
          font-size: 14px;
          color: #667085;
        }

        .breadcrumb a {
          color: #2563eb;
          text-decoration: none;
        }

        .decision-number {
          margin: 0;
          color: #667085;
        }

        .page-actions,
        .section-actions {
          display: flex;
          gap: 10px;
          flex-wrap: wrap;
        }

        .btn {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          padding: 9px 14px;
          border-radius: 7px;
          text-decoration: none;
          border: 1px solid #d0d5dd;
          cursor: pointer;
          font-size: 14px;
          font-weight: 600;
          background: white;
        }

        .btn-primary {
          background: #2563eb;
          color: white;
          border-color: #2563eb;
        }

        .btn-secondary {
          background: white;
          color: #344054;
          border-color: #d0d5dd;
        }

        .details-card {
          background: white;
          border: 1px solid #e4e7ec;
          border-radius: 10px;
          padding: 22px;
          margin-bottom: 20px;
          box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
        }

        .details-card h2 {
          margin-top: 0;
          margin-bottom: 18px;
          color: #172033;
          font-size: 21px;
        }

        .section-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 15px;
          margin-bottom: 16px;
        }

        .section-header h2 {
          margin-bottom: 0;
        }

        .section-toggle {
          border: 1px solid #d0d5dd;
          background: white;
          padding: 7px 12px;
          border-radius: 6px;
          cursor: pointer;
          font-weight: 600;
        }

        .details-grid {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 18px;
        }

        .detail-item {
          display: flex;
          flex-direction: column;
          gap: 7px;
        }

        .detail-label {
          font-size: 13px;
          color: #667085;
          font-weight: 600;
        }

        .detail-value {
          color: #172033;
          font-size: 15px;
        }

        .status-badge {
          display: inline-flex;
          width: fit-content;
          padding: 4px 9px;
          border-radius: 999px;
          font-size: 12px;
          font-weight: 700;
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

        .tags-container {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }

        .tag {
          background: #eff8ff;
          color: #175cd3;
          border: 1px solid #b2ddff;
          border-radius: 999px;
          padding: 5px 10px;
          font-size: 13px;
          font-weight: 600;
        }

        .content-box {
          white-space: pre-wrap;
          line-height: 1.7;
          color: #344054;
          background: #f9fafb;
          border: 1px solid #eaecf0;
          border-radius: 8px;
          padding: 16px;
          min-height: 50px;
        }

        .table-container {
          width: 100%;
          overflow-x: auto;
        }

        .details-table {
          width: 100%;
          border-collapse: collapse;
          min-width: 750px;
        }

        .details-table th,
        .details-table td {
          padding: 12px;
          border-bottom: 1px solid #eaecf0;
          text-align: left;
          vertical-align: top;
          font-size: 14px;
        }

        .details-table th {
          background: #f9fafb;
          color: #475467;
          font-weight: 700;
        }

        .details-table td {
          color: #344054;
        }

        .timeline {
          position: relative;
          padding-left: 25px;
        }

        .timeline-item {
          display: flex;
          gap: 14px;
          position: relative;
          padding-bottom: 22px;
        }

        .timeline-item:not(:last-child)::before {
          content: "";
          position: absolute;
          left: 5px;
          top: 18px;
          bottom: 0;
          width: 2px;
          background: #eaecf0;
        }

        .timeline-marker {
          position: relative;
          z-index: 1;
          width: 12px;
          height: 12px;
          margin-top: 4px;
          color: #2563eb;
          font-size: 12px;
        }

        .timeline-content {
          flex: 1;
        }

        .timeline-title {
          font-weight: 700;
          color: #172033;
          margin-bottom: 5px;
        }

        .timeline-description {
          color: #475467;
          line-height: 1.5;
          margin-bottom: 5px;
        }

        .timeline-meta {
          display: flex;
          gap: 15px;
          flex-wrap: wrap;
          color: #667085;
          font-size: 12px;
        }

        .loading-state,
        .empty-state {
          padding: 22px;
          text-align: center;
          color: #667085;
        }

        .error-box {
          background: #fef3f2;
          border: 1px solid #fecdca;
          color: #b42318;
          padding: 14px;
          border-radius: 7px;
          margin-bottom: 15px;
        }

        .muted-text {
          color: #667085;
        }

        .page-footer-actions {
          display: flex;
          justify-content: flex-end;
          gap: 10px;
          flex-wrap: wrap;
          margin-top: 25px;
          padding-bottom: 30px;
        }

        @media (max-width: 900px) {
          .details-grid {
            grid-template-columns: repeat(2, 1fr);
          }

          .page-header {
            flex-direction: column;
          }
        }

        @media (max-width: 600px) {
          .decision-details-page {
            padding: 15px;
          }

          .details-grid {
            grid-template-columns: 1fr;
          }

          .page-header h1 {
            font-size: 26px;
          }

          .page-actions,
          .section-actions {
            width: 100%;
          }

          .page-actions .btn,
          .section-actions .btn {
            flex: 1;
          }
        }

      `}</style>

    </div>
  );
}