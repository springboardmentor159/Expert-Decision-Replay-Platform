import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import apiClient from "../api/apiClient";

function formatCost(value) {
  if (value === null || value === undefined || value === "") {
    return "—";
  }

  const number = Number(value);

  if (Number.isNaN(number)) {
    return String(value);
  }

  return number.toLocaleString(undefined, {
    maximumFractionDigits: 2,
  });
}

function getRiskClass(riskLevel) {
  switch (riskLevel) {
    case "Low":
      return "status-approved";

    case "Medium":
      return "status-review";

    case "High":
      return "status-rejected";

    case "Critical":
      return "status-rejected";

    default:
      return "status-draft";
  }
}

function extractAlternatives(data) {
  if (Array.isArray(data)) {
    return data;
  }

  if (Array.isArray(data?.alternatives)) {
    return data.alternatives;
  }

  if (Array.isArray(data?.items)) {
    return data.items;
  }

  if (Array.isArray(data?.results)) {
    return data.results;
  }

  return [];
}

function getErrorMessage(error) {
  const status = error?.response?.status;
  const detail = error?.response?.data?.detail;

  if (status === 400) {
    return detail || "The comparison request is invalid.";
  }

  if (status === 401) {
    return "Your session has expired. Please log in again.";
  }

  if (status === 403) {
    return (
      detail ||
      "You do not have permission to compare these alternatives."
    );
  }

  if (status === 404) {
    return detail || "The decision or alternatives were not found.";
  }

  if (status === 422) {
    return (
      detail ||
      "The comparison request contains invalid information."
    );
  }

  if (status >= 500) {
    return "A server error occurred while loading the comparison.";
  }

  return (
    detail ||
    error?.message ||
    "Unable to load the alternative comparison."
  );
}

export default function AlternativeComparison() {
  const { decisionId } = useParams();

  const [decision, setDecision] = useState(null);
  const [alternatives, setAlternatives] = useState([]);

  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    loadComparison();
  }, [decisionId]);

  async function loadComparison() {
    try {
      setLoading(true);
      setErrorMessage("");

      const [decisionResponse, alternativesResponse] =
        await Promise.all([
          apiClient.get(`/decisions/${decisionId}`),
          apiClient.get(`/alternatives/decision/${decisionId}`),
        ]);

      setDecision(decisionResponse.data);

      setAlternatives(
        extractAlternatives(alternativesResponse.data)
      );
    } catch (error) {
      console.error(
        "Failed to load alternative comparison:",
        error
      );

      setErrorMessage(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="page-container">
        <div className="loading-state">
          Loading alternative comparison...
        </div>
      </div>
    );
  }

  if (errorMessage) {
    return (
      <div className="page-container">
        <div className="page-header">
          <div>
            <h1>Alternative Comparison</h1>

            <p>
              Compare the available alternatives for this
              decision.
            </p>
          </div>
        </div>

        <div className="card">
          <div className="error-state">
            <h2>Unable to load comparison</h2>

            <p>{errorMessage}</p>

            <button
              type="button"
              className="button"
              onClick={loadComparison}
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1>Alternative Comparison</h1>

          <p>
            Compare alternatives side by side to understand
            their strengths, weaknesses, cost, feasibility,
            and risk.
          </p>
        </div>

        <div className="page-actions">
          <Link
            to={`/decisions/${decisionId}/alternatives`}
            className="button secondary"
          >
            Back to Alternatives
          </Link>

          <Link
            to={`/decisions/${decisionId}`}
            className="button secondary"
          >
            View Decision
          </Link>
        </div>
      </div>

      {decision && (
        <div className="card">
          <div className="section-header">
            <div>
              <h2>
                {decision.title ||
                  `Decision #${decisionId}`}
              </h2>

              <p>
                {decision.problem_statement ||
                  "No problem statement available."}
              </p>
            </div>

            {decision.status && (
              <span className="status-badge">
                {decision.status}
              </span>
            )}
          </div>
        </div>
      )}

      {alternatives.length === 0 ? (
        <div className="card">
          <div className="empty-state">
            <h2>No Alternatives Available</h2>

            <p>
              This decision does not have any alternatives
              available for comparison yet.
            </p>

            <Link
              to={`/decisions/${decisionId}/alternatives`}
              className="button"
            >
              Manage Alternatives
            </Link>
          </div>
        </div>
      ) : (
        <div className="card">
          <div className="section-header">
            <div>
              <h2>Side-by-Side Comparison</h2>

              <p>
                {alternatives.length} alternative
                {alternatives.length !== 1 ? "s" : ""} available
              </p>
            </div>
          </div>

          <div className="table-container">
            <table className="data-table comparison-table">
              <thead>
                <tr>
                  <th>Criteria</th>

                  {alternatives.map((alternative) => (
                    <th key={alternative.id}>
                      {alternative.name ||
                        `Alternative #${alternative.id}`}
                    </th>
                  ))}
                </tr>
              </thead>

              <tbody>
                <tr>
                  <td>
                    <strong>Description</strong>
                  </td>

                  {alternatives.map((alternative) => (
                    <td key={alternative.id}>
                      {alternative.description || "—"}
                    </td>
                  ))}
                </tr>

                <tr>
                  <td>
                    <strong>Pros</strong>
                  </td>

                  {alternatives.map((alternative) => (
                    <td key={alternative.id}>
                      {alternative.pros || "—"}
                    </td>
                  ))}
                </tr>

                <tr>
                  <td>
                    <strong>Cons</strong>
                  </td>

                  {alternatives.map((alternative) => (
                    <td key={alternative.id}>
                      {alternative.cons || "—"}
                    </td>
                  ))}
                </tr>

                <tr>
                  <td>
                    <strong>Estimated Cost</strong>
                  </td>

                  {alternatives.map((alternative) => (
                    <td key={alternative.id}>
                      {formatCost(
                        alternative.estimated_cost
                      )}
                    </td>
                  ))}
                </tr>

                <tr>
                  <td>
                    <strong>Feasibility Score</strong>
                  </td>

                  {alternatives.map((alternative) => (
                    <td key={alternative.id}>
                      {alternative.feasibility_score ??
                        "—"}

                      {alternative.feasibility_score !==
                        null &&
                        alternative.feasibility_score !==
                          undefined &&
                        " / 5"}
                    </td>
                  ))}
                </tr>

                <tr>
                  <td>
                    <strong>Risk Level</strong>
                  </td>

                  {alternatives.map((alternative) => (
                    <td key={alternative.id}>
                      <span
                        className={`status-badge ${getRiskClass(
                          alternative.risk_level
                        )}`}
                      >
                        {alternative.risk_level || "—"}
                      </span>
                    </td>
                  ))}
                </tr>

                <tr>
                  <td>
                    <strong>Alternative ID</strong>
                  </td>

                  {alternatives.map((alternative) => (
                    <td key={alternative.id}>
                      #{alternative.id}
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}

      <div className="card">
        <div className="section-header">
          <div>
            <h2>Comparison Guidance</h2>

            <p>
              Use the comparison to evaluate the trade-offs
              between available alternatives.
            </p>
          </div>
        </div>

        <div className="comparison-guidance">
          <div>
            <strong>Feasibility</strong>

            <p>
              Higher feasibility scores indicate that an
              alternative is easier to implement.
            </p>
          </div>

          <div>
            <strong>Risk</strong>

            <p>
              Consider the risk level together with the
              expected benefits and estimated cost.
            </p>
          </div>

          <div>
            <strong>Pros & Cons</strong>

            <p>
              Review the advantages and disadvantages before
              selecting the preferred option.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}