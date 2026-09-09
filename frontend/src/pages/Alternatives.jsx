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
  if (!dateValue) return "—";

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
      setAlternatives(alternativesData || []);
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

        <h2>
          Unable to Load Alternatives
        </h2>

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
    <div className="page-container">

      {/* =====================================================
          HEADER
      ===================================================== */}

      <div className="page-header">

        <div>

          <Link
            to={`/decisions/${decisionId}`}
            className="back-link"
          >
            ← Back to Decision
          </Link>

          <h1>
            Alternatives
          </h1>

          <p>
            Decision #{decisionId}:{" "}
            <strong>
              {decision?.title}
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


      {/* =====================================================
          ERROR
      ===================================================== */}

      {error && (
        <div className="error-state">
          <p>{error}</p>
        </div>
      )}


      {/* =====================================================
          SUMMARY
      ===================================================== */}

      <div className="card">

        <div className="section-header">

          <div>
            <h2>
              Decision Alternatives
            </h2>

            <p>
              {alternatives.length} alternative
              {alternatives.length !== 1
                ? "s"
                : ""} available.
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


      {/* =====================================================
          EMPTY STATE
      ===================================================== */}

      {alternatives.length === 0 && (
        <div className="empty-state">

          <h2>
            No Alternatives Yet
          </h2>

          <p>
            Add alternatives to compare the
            available options for this decision.
          </p>

          <Link
            to={`/decisions/${decisionId}/alternatives/create`}
            className="primary-button"
          >
            Add First Alternative
          </Link>

        </div>
      )}


      {/* =====================================================
          ALTERNATIVE CARDS
      ===================================================== */}

      {alternatives.length > 0 && (
        <div className="alternative-grid">

          {alternatives.map(
            (alternative) => (
              <div
                key={alternative.id}
                className="card alternative-card"
              >

                <div className="alternative-card-header">

                  <div>

                    <h2>
                      {alternative.name}
                    </h2>

                    <small>
                      Alternative #
                      {alternative.id}
                    </small>

                  </div>

                  <span
                    className={`risk-badge ${getRiskClass(
                      alternative.risk_level
                    )}`}
                  >
                    {alternative.risk_level}
                  </span>

                </div>


                {/* DESCRIPTION */}

                <div className="alternative-detail">

                  <strong>
                    Description
                  </strong>

                  <p>
                    {alternative.description}
                  </p>

                </div>


                {/* PROS */}

                <div className="alternative-detail">

                  <strong>
                    Pros
                  </strong>

                  <p>
                    {alternative.pros}
                  </p>

                </div>


                {/* CONS */}

                <div className="alternative-detail">

                  <strong>
                    Cons
                  </strong>

                  <p>
                    {alternative.cons}
                  </p>

                </div>


                {/* SCORES */}

                <div className="alternative-metrics">

                  <div>
                    <span>
                      Estimated Cost
                    </span>

                    <strong>
                      ₹{" "}
                      {Number(
                        alternative.estimated_cost
                      ).toLocaleString()}
                    </strong>
                  </div>

                  <div>
                    <span>
                      Feasibility
                    </span>

                    <strong>
                      {alternative.feasibility_score}
                      /5
                    </strong>
                  </div>

                  <div>
                    <span>
                      Risk
                    </span>

                    <strong>
                      {alternative.risk_level}
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
                  >
                    Delete
                  </button>

                </div>


                {/* DELETE CONFIRMATION */}

                {deleteId === alternative.id && (
                  <div className="delete-confirmation">

                    <strong>
                      Delete this alternative?
                    </strong>

                    <p>
                      This action cannot be undone.
                    </p>

                    <div className="form-actions">

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
            )
          )}

        </div>
      )}


      {/* =====================================================
          COMPARISON ERROR
      ===================================================== */}

      {comparisonError && (
        <div className="error-state">
          <p>{comparisonError}</p>
        </div>
      )}


      {/* =====================================================
          SIDE-BY-SIDE COMPARISON
      ===================================================== */}

      {showComparison &&
        comparison &&
        comparison.alternatives?.length > 0 && (
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
                Hide
              </button>

            </div>


            <div className="comparison-wrapper">

              <table className="comparison-table">

                <thead>

                  <tr>

                    <th>
                      Criteria
                    </th>

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

                    <th>
                      Description
                    </th>

                    {comparison.alternatives.map(
                      (alternative) => (
                        <td
                          key={alternative.id}
                        >
                          {alternative.description}
                        </td>
                      )
                    )}

                  </tr>


                  <tr>

                    <th>
                      Pros
                    </th>

                    {comparison.alternatives.map(
                      (alternative) => (
                        <td
                          key={alternative.id}
                        >
                          {alternative.pros}
                        </td>
                      )
                    )}

                  </tr>


                  <tr>

                    <th>
                      Cons
                    </th>

                    {comparison.alternatives.map(
                      (alternative) => (
                        <td
                          key={alternative.id}
                        >
                          {alternative.cons}
                        </td>
                      )
                    )}

                  </tr>


                  <tr>

                    <th>
                      Estimated Cost
                    </th>

                    {comparison.alternatives.map(
                      (alternative) => (
                        <td
                          key={alternative.id}
                        >
                          ₹{" "}
                          {Number(
                            alternative.estimated_cost
                          ).toLocaleString()}
                        </td>
                      )
                    )}

                  </tr>


                  <tr>

                    <th>
                      Feasibility
                    </th>

                    {comparison.alternatives.map(
                      (alternative) => (
                        <td
                          key={alternative.id}
                        >
                          {
                            alternative.feasibility_score
                          }
                          /5
                        </td>
                      )
                    )}

                  </tr>


                  <tr>

                    <th>
                      Risk
                    </th>

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
                            {
                              alternative.risk_level
                            }
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


      {/* =====================================================
          FOOTER
      ===================================================== */}

      <div className="page-footer-actions">

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
  );
}

export default Alternatives;