import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
  compareAlternatives,
  getAlternatives,
} from "../../services/alternativeService";

import PageHeader from "../../components/PageHeader";
import Button from "../../components/Button";
import Card from "../../components/Card";
import Alert from "../../components/Alert";
import EmptyState from "../../components/EmptyState";

const AlternativeComparison = () => {
  const { decisionId } = useParams();
  const navigate = useNavigate();

  const [alternatives, setAlternatives] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadComparison = async () => {
      try {
        setLoading(true);
        setError("");

        // Get comparison data
        const comparisonData =
          await compareAlternatives(decisionId);

        const comparisonAlternatives =
          Array.isArray(comparisonData)
            ? comparisonData
            : comparisonData?.alternatives || [];

        // Get full alternative data
        const alternativeData =
          await getAlternatives(decisionId);

        const fullAlternatives =
          Array.isArray(alternativeData)
            ? alternativeData
            : alternativeData?.alternatives ||
              alternativeData?.items ||
              [];

        // Merge comparison data with full alternative data
        const mergedAlternatives =
          comparisonAlternatives.map(
            (comparisonAlternative) => {
              const fullAlternative =
                fullAlternatives.find(
                  (alternative) =>
                    alternative.name ===
                    comparisonAlternative.name
                );

              return {
                ...comparisonAlternative,
                pros:
                  fullAlternative?.pros || "-",
                cons:
                  fullAlternative?.cons || "-",
                description:
                  fullAlternative?.description || "",
              };
            }
          );

        setAlternatives(mergedAlternatives);
      } catch (err) {
        console.error(
          "Failed to load alternative comparison:",
          err
        );

        const status = err.response?.status;

        if (status === 401) {
          setError(
            "Your session has expired. Please login again."
          );
        } else if (status === 403) {
          setError(
            "You are not authorized to compare alternatives."
          );
        } else if (status === 404) {
          setError(
            "Decision or alternatives were not found."
          );
        } else if (status === 422) {
          setError("Invalid decision ID.");
        } else if (status >= 500) {
          setError(
            "Server error. Please try again later."
          );
        } else if (err.request) {
          setError(
            "Unable to connect to the backend. Please make sure FastAPI is running."
          );
        } else {
          setError(
            "Failed to load alternative comparison."
          );
        }
      } finally {
        setLoading(false);
      }
    };

    loadComparison();
  }, [decisionId]);

  if (loading) {
    return (
      <div className="alternative-comparison-page">
        <PageHeader
          title="Alternative Comparison"
          subtitle="Compare available decision alternatives"
        />

        <Card>
          <div className="loading-state">
            Loading comparison...
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="alternative-comparison-page">
      <PageHeader
        title="Alternative Comparison"
        subtitle="Compare alternatives side by side"
      />

      {error && (
        <Alert
          message={error}
          type="error"
          onClose={() => setError("")}
        />
      )}

      <div className="alternative-actions">
        <Button
          variant="secondary"
          onClick={() =>
            navigate(
              `/decisions/${decisionId}/alternatives`
            )
          }
        >
          Back to Alternatives
        </Button>

        <Button
          variant="secondary"
          onClick={() =>
            navigate(`/decisions/${decisionId}`)
          }
        >
          Back to Decision
        </Button>
      </div>

      {alternatives.length < 2 ? (
        <Card>
          <EmptyState
            title="Not enough alternatives"
            message="At least two alternatives are required for comparison."
            action={
              <Button
                onClick={() =>
                  navigate(
                    `/decisions/${decisionId}/alternatives/create`
                  )
                }
              >
                Add Alternative
              </Button>
            }
          />
        </Card>
      ) : (
        <Card title="Alternative Comparison">
          <div className="comparison-table-wrapper">
            <table className="comparison-table">
              <thead>
                <tr>
                  <th>Criteria</th>

                  {alternatives.map(
                    (alternative, index) => (
                      <th
                        key={
                          alternative.name ||
                          index
                        }
                      >
                        {alternative.name ||
                          `Alternative ${
                            index + 1
                          }`}
                      </th>
                    )
                  )}
                </tr>
              </thead>

              <tbody>
                <tr>
                  <td>
                    <strong>
                      Estimated Cost
                    </strong>
                  </td>

                  {alternatives.map(
                    (alternative, index) => (
                      <td key={index}>
                        {alternative.estimated_cost ??
                          "-"}
                      </td>
                    )
                  )}
                </tr>

                <tr>
                  <td>
                    <strong>
                      Feasibility
                    </strong>
                  </td>

                  {alternatives.map(
                    (alternative, index) => (
                      <td key={index}>
                        {alternative.feasibility_score ??
                          "-"}{" "}
                        / 5
                      </td>
                    )
                  )}
                </tr>

                <tr>
                  <td>
                    <strong>
                      Risk Level
                    </strong>
                  </td>

                  {alternatives.map(
                    (alternative, index) => (
                      <td key={index}>
                        {alternative.risk_level ||
                          "-"}
                      </td>
                    )
                  )}
                </tr>

                <tr>
                  <td>
                    <strong>Pros</strong>
                  </td>

                  {alternatives.map(
                    (alternative, index) => (
                      <td key={index}>
                        {alternative.pros ||
                          "-"}
                      </td>
                    )
                  )}
                </tr>

                <tr>
                  <td>
                    <strong>Cons</strong>
                  </td>

                  {alternatives.map(
                    (alternative, index) => (
                      <td key={index}>
                        {alternative.cons ||
                          "-"}
                      </td>
                    )
                  )}
                </tr>
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
};

export default AlternativeComparison;