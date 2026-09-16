import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import {
  getDecision,
} from "../api/decisionApi";

import {
  getAlternatives,
  deleteAlternative,
  compareDecisionAlternatives,
} from "../api/alternativeApi";

function formatDate(dateValue) {
  if (!dateValue) {
    return "—";
  }

  const date = new Date(dateValue);

  if (Number.isNaN(date.getTime())) {
    return "—";
  }

  return date.toLocaleString();
}

function getRiskClass(riskLevel) {
  switch (riskLevel) {
    case "Low":
      return "risk-low";

    case "Medium":
      return "risk-medium";

    case "High":
      return "risk-high";

    case "Critical":
      return "risk-critical";

    default:
      return "";
  }
}

function Alternatives() {
  const { decisionId } = useParams();

  const [decision, setDecision] = useState(null);
  const [alternatives, setAlternatives] = useState([]);
  const [comparison, setComparison] = useState(null);

  const [loading, setLoading] = useState(true);
  const [comparisonLoading, setComparisonLoading] =
    useState(false);

  const [error, setError] = useState("");
  const [comparisonError, setComparisonError] =
    useState("");

  const [deleteId, setDeleteId] = useState(null);
  const [deleting, setDeleting] = useState(false);

  const [showComparison, setShowComparison] =
    useState(false);

  useEffect(() => {
    loadPage();
  }, [decisionId]);

  async function loadPage() {
    try {
      setLoading(true);
      setError("");

      const [decisionData, alternativesData] =
        await Promise.all([
          getDecision(decisionId),
          getAlternatives(decisionId),
        ]);

      setDecision(decisionData);

      setAlternatives(
        Array.isArray(alternativesData)
          ? alternativesData
          : []
      );
    } catch (err) {
      console.error(
        "Failed to load alternatives:",
        err
      );

      if (err.response?.status === 401) {
        setError(
          "Your session has expired. Please log in again."
        );
      } else if (err.response?.status === 403) {
        setError(
          "You do not have permission to view alternatives."
        );
      } else if (err.response?.status === 404) {
        setError(
          "The decision or alternatives could not be found."
        );
      } else if (err.response?.status >= 500) {
        setError(
          "The server encountered an error. Please try again."
        );
      } else {
        setError(
          "Unable to load alternatives. Please try again."
        );
      }
    } finally {
      setLoading(false);
    }
  }

  async function handleCompare() {
    try {
      setComparisonLoading(true);
      setComparisonError("");

      const data =
        await compareDecisionAlternatives(
          decisionId
        );

      setComparison(data);
      setShowComparison(true);
    } catch (err) {
      console.error(
        "Failed to compare alternatives:",
        err
      );

      if (err.response?.status === 401) {
        setComparisonError(
          "Your session has expired. Please log in again."
        );
      } else if (err.response?.status === 403) {
        setComparisonError(
          "You do not have permission to compare alternatives."
        );
      } else if (err.response?.status === 404) {
        setComparisonError(
          "The decision could not be found."
        );
      } else {
        setComparisonError(
          "Unable to compare alternatives."
        );
      }
    } finally {
      setComparisonLoading(false);
    }
  }

  async function handleDelete(alternativeId) {
    try {
      setDeleting(true);
      setError("");

      await deleteAlternative(alternativeId);

      setAlternatives((current) =>
        current.filter(
          (alternative) =>
            alternative.id !== alternativeId
        )
      );

      setDeleteId(null);

      if (showComparison) {
        await handleCompare();
      }
    } catch (err) {
      console.error(
        "Failed to delete alternative:",
        err
      );

      if (err.response?.status === 401) {
        setError(
          "Your session has expired. Please log in again."
        );
      } else if (err.response?.status === 403) {
        setError(
          "You do not have permission to delete this alternative."
        );
      } else if (err.response?.status === 404) {
        setError("Alternative not found.");
      } else if (err.response?.status >= 500) {
        setError(
          "The server encountered an error. Please try again."
        );
      } else {
        setError(
          "Unable to delete the alternative."
        );
      }
    } finally {
      setDeleting(false);
    }
  }

  if (loading) {
    return (
      <div className="loading-state">
        Loading alternatives...
      </div>
    );
  }

  if (error && !decision) {
    return (
      <div className="error-state">
        <h2>Unable to Load Alternatives</h2>

        <p>{error}</p>

        <button
          type="button"
          className="primary-button"
          onClick={loadPage}
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <>
      <style>
        {`
          .alternatives-page {
            width: 100%;
          }

          .alternative-summary {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 20px;
          }

          .alternative-summary-text h2 {
            margin-bottom: 6px;
          }

          .alternative-summary-text p {
            margin: 0;
            color: #64748b;
          }

          .alternative-grid {
            display: grid;
            grid-template-columns:
              repeat(2, minmax(0, 1fr));
            gap: 20px;
            margin-top: 20px;
          }

          .alternative-card {
            display: flex;
            flex-direction: column;
            min-width: 0;
            padding: 24px;
            border: 1px solid #e2e8f0;
            transition:
              transform 0.2s ease,
              box-shadow 0.2s ease;
          }

          .alternative-card:hover {
            transform: translateY(-2px);
            box-shadow:
              0 8px 24px
              rgba(15, 23, 42, 0.08);
          }

          .alternative-card-header {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 16px;
            padding-bottom: 18px;
            border-bottom: 1px solid #e2e8f0;
          }

          .alternative-title {
            min-width: 0;
          }

          .alternative-title h2 {
            margin: 0 0 6px;
            color: #0f172a;
            font-size: 20px;
            line-height: 1.3;
            overflow-wrap: anywhere;
          }

          .alternative-title small {
            color: #64748b;
            font-size: 13px;
          }

          .risk-badge {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            min-height: 28px;
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 700;
          }

          .risk-low {
            background: #dcfce7;
            color: #166534;
          }

          .risk-medium {
            background: #fef3c7;
            color: #92400e;
          }

          .risk-high {
            background: #fee2e2;
            color: #b91c1c;
          }

          .risk-critical {
            background: #fecaca;
            color: #7f1d1d;
          }

          .alternative-detail {
            margin-top: 18px;
          }

          .alternative-detail strong {
            display: block;
            margin-bottom: 7px;
            color: #334155;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.04em;
          }

          .alternative-detail p {
            margin: 0;
            color: #475569;
            font-size: 14px;
            line-height: 1.65;
            white-space: pre-wrap;
            overflow-wrap: anywhere;
          }

          .alternative-metrics {
            display: grid;
            grid-template-columns:
              repeat(3, minmax(0, 1fr));
            gap: 10px;
            margin-top: 22px;
            padding-top: 18px;
            border-top: 1px solid #e2e8f0;
          }

          .alternative-metric {
            min-width: 0;
            padding: 12px;
            border-radius: 9px;
            background: #f8fafc;
          }

          .alternative-metric span {
            display: block;
            margin-bottom: 5px;
            color: #64748b;
            font-size: 12px;
            line-height: 1.4;
          }

          .alternative-metric strong {
            color: #0f172a;
            font-size: 15px;
          }

          .alternative-dates {
            display: flex;
            flex-direction: column;
            gap: 5px;
            margin-top: 18px;
            padding-top: 15px;
            border-top: 1px solid #f1f5f9;
            color: #94a3b8;
            font-size: 12px;
          }

          .alternative-actions {
            display: flex;
            gap: 10px;
            margin-top: 20px;
          }

          .alternative-actions a,
          .alternative-actions button {
            min-height: 42px;
          }

          .alternative-actions .secondary-button {
            flex: 1;
            text-align: center;
          }

          .alternative-actions .danger-button {
            flex: 1;
          }

          .alternative-delete-confirmation {
            margin-top: 16px;
            padding: 16px;
            border: 1px solid #fecaca;
            border-radius: 10px;
            background: #fef2f2;
          }

          .alternative-delete-confirmation strong {
            display: block;
            margin-bottom: 7px;
            color: #991b1b;
          }

          .alternative-delete-confirmation p {
            margin: 0 0 14px;
            color: #64748b;
            font-size: 14px;
          }

          .alternative-delete-actions {
            display: flex;
            gap: 10px;
          }

          .comparison-section {
            margin-top: 24px;
          }

          .comparison-wrapper {
            width: 100%;
            margin-top: 20px;
            overflow-x: auto;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
          }

          .comparison-table {
            width: 100%;
            min-width: 760px;
            border-collapse: collapse;
            background: #ffffff;
          }

          .comparison-table th,
          .comparison-table td {
            padding: 15px 16px;
            border-bottom: 1px solid #e2e8f0;
            text-align: left;
            vertical-align: top;
            line-height: 1.55;
          }

          .comparison-table thead th {
            background: #f8fafc;
            color: #0f172a;
            font-size: 14px;
            font-weight: 700;
          }

          .comparison-table tbody th {
            width: 150px;
            background: #f8fafc;
            color: #334155;
            font-size: 13px;
            font-weight: 700;
          }

          .comparison-table tbody td {
            color: #475569;
            font-size: 14px;
            white-space: pre-wrap;
            overflow-wrap: anywhere;
          }

          .comparison-table tr:last-child th,
          .comparison-table tr:last-child td {
            border-bottom: none;
          }

          .comparison-table .risk-badge {
            white-space: nowrap;
          }

          .alternatives-empty {
            margin-top: 20px;
            padding: 48px 24px;
            text-align: center;
            border: 1px dashed #cbd5e1;
            border-radius: 12px;
            background: #f8fafc;
          }

          .alternatives-empty h2 {
            margin-bottom: 8px;
            color: #0f172a;
          }

          .alternatives-empty p {
            max-width: 520px;
            margin: 0 auto 20px;
            color: #64748b;
            line-height: 1.6;
          }

          .alternatives-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
            margin-top: 24px;
          }

          @media (max-width: 900px) {
            .alternative-grid {
              grid-template-columns: 1fr;
            }
          }

          @media (max-width: 700px) {
            .alternative-summary {
              align-items: stretch;
              flex-direction: column;
            }

            .alternative-summary button {
              width: 100%;
            }

            .alternative-metrics {
              grid-template-columns: 1fr;
            }

            .alternative-card {
              padding: 18px;
            }

            .alternative-card-header {
              flex-direction: column;
            }

            .alternative-actions {
              flex-direction: column;
            }

            .alternative-actions a,
            .alternative-actions button {
              width: 100%;
            }

            .alternative-delete-actions {
              flex-direction: column;
            }

            .alternative-delete-actions button {
              width: 100%;
            }

            .alternatives-footer {
              align-items: stretch;
              flex-direction: column;
            }

            .alternatives-footer a {
              width: 100%;
              text-align: center;
            }
          }
        `}
      </style>

      <div className="page-container alternatives-page">

        {/* HEADER */}
        <div className="page-header">
          <div>
            <Link
              to={`/decisions/${decisionId}`}
              className="back-link"
            >
              ← Back to Decision
            </Link>

            <h1>Alternatives</h1>

            <p>
              Decision #{decisionId}:{" "}
              <strong>
                {decision?.title || "Untitled Decision"}
              </strong>
            </p>
          </div>

          <div className="page-header-actions">
            <Link
              to={`/decisions/${decisionId}/alternatives/create`}
              className="primary-button"
            >
              + Add Alternative
            </Link>
          </div>
        </div>

        {/* ERROR */}
        {error && (
          <div className="error-state">
            <h3>Unable to Load Alternatives</h3>
            <p>{error}</p>
          </div>
        )}

        {/* SUMMARY */}
        <div className="card">
          <div className="alternative-summary">
            <div className="alternative-summary-text">
              <h2>Decision Alternatives</h2>

              <p>
                {alternatives.length} alternative
                {alternatives.length !== 1
                  ? "s"
                  : ""}{" "}
                available for comparison.
              </p>
            </div>

            <button
              type="button"
              className="secondary-button"
              onClick={handleCompare}
              disabled={
                comparisonLoading ||
                alternatives.length === 0
              }
            >
              {comparisonLoading
                ? "Comparing..."
                : "Compare Alternatives"}
            </button>
          </div>
        </div>

        {/* EMPTY STATE */}
        {alternatives.length === 0 && (
          <div className="alternatives-empty">
            <h2>No Alternatives Yet</h2>

            <p>
              Add alternatives to compare the available
              options for this decision.
            </p>

            <Link
              to={`/decisions/${decisionId}/alternatives/create`}
              className="primary-button"
            >
              + Add First Alternative
            </Link>
          </div>
        )}

        {/* ALTERNATIVE CARDS */}
        {alternatives.length > 0 && (
          <div className="alternative-grid">
            {alternatives.map((alternative) => (
              <div
                key={alternative.id}
                className="card alternative-card"
              >

                <div className="alternative-card-header">
                  <div className="alternative-title">
                    <h2>
                      {alternative.name}
                    </h2>

                    <small>
                      Alternative #{alternative.id}
                    </small>
                  </div>

                  <span
                    className={`risk-badge ${getRiskClass(
                      alternative.risk_level
                    )}`}
                  >
                    {alternative.risk_level || "Unknown"}
                  </span>
                </div>

                {/* DESCRIPTION */}
                <div className="alternative-detail">
                  <strong>Description</strong>

                  <p>
                    {alternative.description || "—"}
                  </p>
                </div>

                {/* PROS */}
                <div className="alternative-detail">
                  <strong>Pros</strong>

                  <p>
                    {alternative.pros || "—"}
                  </p>
                </div>

                {/* CONS */}
                <div className="alternative-detail">
                  <strong>Cons</strong>

                  <p>
                    {alternative.cons || "—"}
                  </p>
                </div>

                {/* METRICS */}
                <div className="alternative-metrics">

                  <div className="alternative-metric">
                    <span>
                      Estimated Cost
                    </span>

                    <strong>
                      ₹{" "}
                      {Number(
                        alternative.estimated_cost || 0
                      ).toLocaleString("en-IN")}
                    </strong>
                  </div>

                  <div className="alternative-metric">
                    <span>
                      Feasibility
                    </span>

                    <strong>
                      {alternative.feasibility_score ??
                        "—"}
                      /5
                    </strong>
                  </div>

                  <div className="alternative-metric">
                    <span>
                      Risk
                    </span>

                    <strong>
                      {alternative.risk_level || "—"}
                    </strong>
                  </div>

                </div>

                {/* DATES */}
                <div className="alternative-dates">
                  <span>
                    Created:{" "}
                    {formatDate(
                      alternative.created_at
                    )}
                  </span>

                  <span>
                    Updated:{" "}
                    {formatDate(
                      alternative.updated_at
                    )}
                  </span>
                </div>

                {/* ACTIONS */}
                <div className="alternative-actions">
                  <Link
                    to={`/alternatives/${alternative.id}/edit`}
                    className="secondary-button"
                  >
                    Edit
                  </Link>

                  <button
                    type="button"
                    className="danger-button"
                    onClick={() =>
                      setDeleteId(
                        alternative.id
                      )
                    }
                    disabled={deleting}
                  >
                    Delete
                  </button>
                </div>

                {/* DELETE CONFIRMATION */}
                {deleteId === alternative.id && (
                  <div className="alternative-delete-confirmation">
                    <strong>
                      Delete this alternative?
                    </strong>

                    <p>
                      This action cannot be undone.
                    </p>

                    <div className="alternative-delete-actions">
                      <button
                        type="button"
                        className="secondary-button"
                        onClick={() =>
                          setDeleteId(null)
                        }
                        disabled={deleting}
                      >
                        Cancel
                      </button>

                      <button
                        type="button"
                        className="danger-button"
                        onClick={() =>
                          handleDelete(
                            alternative.id
                          )
                        }
                        disabled={deleting}
                      >
                        {deleting
                          ? "Deleting..."
                          : "Yes, Delete"}
                      </button>
                    </div>
                  </div>
                )}

              </div>
            ))}
          </div>
        )}

        {/* COMPARISON ERROR */}
        {comparisonError && (
          <div className="error-state">
            <h3>Unable to Compare Alternatives</h3>
            <p>{comparisonError}</p>
          </div>
        )}

        {/* COMPARISON */}
        {showComparison &&
          comparison &&
          Array.isArray(comparison.alternatives) &&
          comparison.alternatives.length > 0 && (
            <div className="card comparison-section">

              <div className="section-header">
                <div>
                  <h2>
                    Side-by-Side Comparison
                  </h2>

                  <p>
                    Compare all available alternatives
                    for this decision.
                  </p>
                </div>

                <button
                  type="button"
                  className="secondary-button"
                  onClick={() =>
                    setShowComparison(false)
                  }
                >
                  Hide Comparison
                </button>
              </div>

              <div className="comparison-wrapper">
                <table className="comparison-table">

                  <thead>
                    <tr>
                      <th>Criteria</th>

                      {comparison.alternatives.map(
                        (alternative) => (
                          <th
                            key={alternative.id}
                          >
                            {alternative.name}
                          </th>
                        )
                      )}
                    </tr>
                  </thead>

                  <tbody>

                    <tr>
                      <th>Description</th>

                      {comparison.alternatives.map(
                        (alternative) => (
                          <td
                            key={alternative.id}
                          >
                            {alternative.description ||
                              "—"}
                          </td>
                        )
                      )}
                    </tr>

                    <tr>
                      <th>Pros</th>

                      {comparison.alternatives.map(
                        (alternative) => (
                          <td
                            key={alternative.id}
                          >
                            {alternative.pros || "—"}
                          </td>
                        )
                      )}
                    </tr>

                    <tr>
                      <th>Cons</th>

                      {comparison.alternatives.map(
                        (alternative) => (
                          <td
                            key={alternative.id}
                          >
                            {alternative.cons || "—"}
                          </td>
                        )
                      )}
                    </tr>

                    <tr>
                      <th>Estimated Cost</th>

                      {comparison.alternatives.map(
                        (alternative) => (
                          <td
                            key={alternative.id}
                          >
                            ₹{" "}
                            {Number(
                              alternative.estimated_cost ||
                                0
                            ).toLocaleString("en-IN")}
                          </td>
                        )
                      )}
                    </tr>

                    <tr>
                      <th>Feasibility</th>

                      {comparison.alternatives.map(
                        (alternative) => (
                          <td
                            key={alternative.id}
                          >
                            {alternative.feasibility_score ??
                              "—"}
                            /5
                          </td>
                        )
                      )}
                    </tr>

                    <tr>
                      <th>Risk</th>

                      {comparison.alternatives.map(
                        (alternative) => (
                          <td
                            key={alternative.id}
                          >
                            <span
                              className={`risk-badge ${getRiskClass(
                                alternative.risk_level
                              )}`}
                            >
                              {alternative.risk_level ||
                                "Unknown"}
                            </span>
                          </td>
                        )
                      )}
                    </tr>

                  </tbody>
                </table>
              </div>
            </div>
          )}

        {/* FOOTER */}
        <div className="alternatives-footer">

          <Link
            to={`/decisions/${decisionId}`}
            className="secondary-button"
          >
            ← Back to Decision
          </Link>

          <Link
            to={`/decisions/${decisionId}/alternatives/create`}
            className="primary-button"
          >
            + Add Alternative
          </Link>

        </div>

      </div>
    </>
  );
}

export default Alternatives;