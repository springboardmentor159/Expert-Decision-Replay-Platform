import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../services/api";

function AlternativeComparison() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [alternatives, setAlternatives] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchComparison = async () => {
      try {
        setLoading(true);
        setError("");

        const response = await api.get(
          `/decisions/${id}/alternatives/compare`
        );

        setAlternatives(response.data.alternatives || []);
      } catch (err) {
        console.error("Comparison error:", err);
        setError("Unable to load alternative comparison.");
      } finally {
        setLoading(false);
      }
    };

    fetchComparison();
  }, [id]);

  const getBestFeasibility = () => {
    const scores = alternatives
      .map((alternative) => Number(alternative.feasibility_score))
      .filter((score) => !Number.isNaN(score));

    return scores.length > 0 ? Math.max(...scores) : null;
  };

  const bestScore = getBestFeasibility();

  return (
    <div className="comparison-page">

      {/* Header */}
      <div className="comparison-header">
        <div>
          <div className="page-breadcrumb">
            Decisions / Alternatives / Comparison
          </div>

          <h1>Compare Alternatives</h1>

          <p>
            Compare the available options and evaluate which alternative
            is most suitable for Decision #{id}.
          </p>
        </div>

        <div className="comparison-header-actions">
          <button
            className="secondary-page-button"
            onClick={() =>
              navigate(`/decisions/${id}/alternatives`)
            }
          >
            ← Alternatives
          </button>

          <button
            className="primary-submit-button"
            onClick={() => navigate(`/decisions/${id}`)}
          >
            Decision Details
          </button>
        </div>
      </div>

      {/* Summary */}
      <div className="comparison-summary">

        <div className="comparison-summary-card">
          <div className="comparison-summary-icon">↔</div>
          <div>
            <span>Options Compared</span>
            <strong>{alternatives.length}</strong>
          </div>
        </div>

        <div className="comparison-summary-card">
          <div className="comparison-summary-icon">★</div>
          <div>
            <span>Highest Feasibility</span>
            <strong>
              {bestScore !== null ? `${bestScore}/5` : "—"}
            </strong>
          </div>
        </div>

        <div className="comparison-summary-card">
          <div className="comparison-summary-icon">#</div>
          <div>
            <span>Decision</span>
            <strong>#{id}</strong>
          </div>
        </div>

      </div>

      {/* Content */}
      <div className="comparison-card">

        <div className="comparison-card-header">
          <div>
            <h2>Alternative Comparison Matrix</h2>
            <p>
              Review the key criteria for each available option.
            </p>
          </div>
        </div>

        {loading && (
          <div className="page-loading">
            <div className="loading-spinner"></div>
            <p>Loading comparison...</p>
          </div>
        )}

        {!loading && error && (
          <div className="comparison-error">
            <div>!</div>
            <h3>Unable to Load Comparison</h3>
            <p>{error}</p>
          </div>
        )}

        {!loading && !error && alternatives.length === 0 && (
          <div className="comparison-empty">
            <div className="comparison-empty-icon">↔</div>
            <h3>No Alternatives Available</h3>
            <p>
              Add alternatives before comparing the available options.
            </p>

            <button
              className="primary-submit-button"
              onClick={() =>
                navigate(`/decisions/${id}/alternatives`)
              }
            >
              Add Alternatives
            </button>
          </div>
        )}

        {!loading && !error && alternatives.length > 0 && (
          <div className="comparison-table-wrapper">
            <table className="comparison-table">

              <thead>
                <tr>
                  <th className="criteria-column">
                    Criteria
                  </th>

                  {alternatives.map((alternative, index) => {
                    const isBest =
                      bestScore !== null &&
                      Number(alternative.feasibility_score) === bestScore;

                    return (
                      <th key={index}>
                        <div className="comparison-option-header">

                          <div className="comparison-option-number">
                            {index + 1}
                          </div>

                          <div>
                            <strong>{alternative.name}</strong>

                            {isBest && (
                              <span className="recommended-badge">
                                Recommended
                              </span>
                            )}
                          </div>

                        </div>
                      </th>
                    );
                  })}
                </tr>
              </thead>

              <tbody>

                {/* Description */}
                <tr>
                  <td className="criteria-cell">
                    Description
                  </td>

                  {alternatives.map((alternative, index) => (
                    <td key={index}>
                      <div className="comparison-description">
                        {alternative.description || "Not provided"}
                      </div>
                    </td>
                  ))}
                </tr>

                {/* Pros */}
                <tr>
                  <td className="criteria-cell">
                    <span className="criteria-label positive">
                      ✓ Pros
                    </span>
                  </td>

                  {alternatives.map((alternative, index) => (
                    <td key={index}>
                      <div className="comparison-pros">
                        {alternative.pros || "Not provided"}
                      </div>
                    </td>
                  ))}
                </tr>

                {/* Cons */}
                <tr>
                  <td className="criteria-cell">
                    <span className="criteria-label negative">
                      ✕ Cons
                    </span>
                  </td>

                  {alternatives.map((alternative, index) => (
                    <td key={index}>
                      <div className="comparison-cons">
                        {alternative.cons || "Not provided"}
                      </div>
                    </td>
                  ))}
                </tr>

                {/* Cost */}
                <tr>
                  <td className="criteria-cell">
                    Estimated Cost
                  </td>

                  {alternatives.map((alternative, index) => (
                    <td key={index}>
                      <strong className="comparison-value">
                        {alternative.estimated_cost ?? "—"}
                      </strong>
                    </td>
                  ))}
                </tr>

                {/* Feasibility */}
                <tr>
                  <td className="criteria-cell">
                    Feasibility Score
                  </td>

                  {alternatives.map((alternative, index) => {
                    const score =
                      alternative.feasibility_score;

                    const isBest =
                      bestScore !== null &&
                      Number(score) === bestScore;

                    return (
                      <td key={index}>
                        <div className="feasibility-display">

                          <strong>
                            {score ?? "—"}
                          </strong>

                          {score && (
                            <span>/5</span>
                          )}

                          {isBest && (
                            <small>Highest</small>
                          )}

                        </div>
                      </td>
                    );
                  })}
                </tr>

                {/* Risk */}
                <tr>
                  <td className="criteria-cell">
                    Risk Level
                  </td>

                  {alternatives.map((alternative, index) => {
                    const risk =
                      alternative.risk_level || "";

                    return (
                      <td key={index}>
                        <span
                          className={`comparison-risk ${
                            risk.toLowerCase()
                          }`}
                        >
                          {risk || "—"}
                        </span>
                      </td>
                    );
                  })}
                </tr>

              </tbody>
            </table>
          </div>
        )}

      </div>

      {/* Bottom Actions */}
      <div className="comparison-bottom-actions">

        <button
          className="secondary-page-button"
          onClick={() =>
            navigate(`/decisions/${id}/alternatives`)
          }
        >
          ← Back to Alternatives
        </button>

        <button
          className="primary-submit-button"
          onClick={() => navigate(`/decisions/${id}`)}
        >
          Back to Decision
        </button>

      </div>

    </div>
  );
}

export default AlternativeComparison;