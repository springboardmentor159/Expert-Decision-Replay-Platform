import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
  getAlternatives,
} from "../../services/alternativeService";

import PageHeader from "../../components/PageHeader";
import Button from "../../components/Button";
import Card from "../../components/Card";
import Alert from "../../components/Alert";
import EmptyState from "../../components/EmptyState";

const AlternativeList = () => {
  const { decisionId } = useParams();
  const navigate = useNavigate();

  const [alternatives, setAlternatives] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadAlternatives = async () => {
    try {
      setLoading(true);
      setError("");

      const data = await getAlternatives(decisionId);

      const list = Array.isArray(data)
        ? data
        : data?.alternatives || data?.items || [];

      setAlternatives(list);
    } catch (err) {
      console.error(
        "Failed to load alternatives:",
        err
      );

      const status = err.response?.status;

      if (status === 401) {
        setError(
          "Your session has expired. Please login again."
        );
      } else if (status === 403) {
        setError(
          "You are not authorized to view alternatives."
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
        setError("Failed to load alternatives.");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAlternatives();
  }, [decisionId]);

  if (loading) {
    return (
      <div className="alternatives-page">
        <PageHeader
          title="Alternatives"
          subtitle="Review and manage decision alternatives"
        />

        <Card>
          <div className="loading-state">
            Loading alternatives...
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="alternatives-page">
      <PageHeader
        title="Alternatives"
        subtitle="Review and manage decision alternatives"
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
          onClick={() =>
            navigate(
              `/decisions/${decisionId}/alternatives/create`
            )
          }
        >
          + Add Alternative
        </Button>

        <Button
          variant="secondary"
          onClick={() =>
            navigate(
              `/decisions/${decisionId}/alternatives/compare`
            )
          }
          disabled={alternatives.length < 2}
        >
          Compare Alternatives
        </Button>

        <Button
          variant="secondary"
          onClick={loadAlternatives}
        >
          Refresh
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

      {alternatives.length === 0 ? (
        <Card>
          <EmptyState
            title="No alternatives found"
            message="Add alternatives to evaluate different solutions for this decision."
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
        <div className="alternative-grid">
          {alternatives.map((alternative) => (
            <Card
              key={alternative.id}
              className="alternative-card"
            >
              <div className="alternative-card-header">
                <div>
                  <h2>
                    {alternative.name ||
                      `Alternative ${alternative.id}`}
                  </h2>

                  {alternative.description && (
                    <p>{alternative.description}</p>
                  )}
                </div>

                <span className="alternative-id">
                  #{alternative.id}
                </span>
              </div>

              <div className="alternative-details">
                <div>
                  <strong>Pros</strong>
                  <p>
                    {alternative.pros || "-"}
                  </p>
                </div>

                <div>
                  <strong>Cons</strong>
                  <p>
                    {alternative.cons || "-"}
                  </p>
                </div>

                <div>
                  <strong>Estimated Cost</strong>
                  <p>
                    {alternative.estimated_cost ??
                      "-"}
                  </p>
                </div>

                <div>
                  <strong>Feasibility Score</strong>
                  <p>
                    {alternative.feasibility_score ??
                      "-"}{" "}
                    / 5
                  </p>
                </div>

                <div>
                  <strong>Risk Level</strong>
                  <p>
                    {alternative.risk_level || "-"}
                  </p>
                </div>
              </div>

              <div className="alternative-card-actions">
                <Button
                  variant="secondary"
                  onClick={() =>
                    navigate(
                      `/decisions/${decisionId}/alternatives/${alternative.id}/edit`
                    )
                  }
                >
                  Edit
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default AlternativeList;