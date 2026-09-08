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

  return (
    <div>
      <h1>Compare Alternatives</h1>

      <p>
        <strong>Decision ID:</strong> {id}
      </p>

      <hr />

      {loading && <p>Loading comparison...</p>}

      {!loading && error && <p>{error}</p>}

      {!loading && !error && alternatives.length === 0 && (
        <p>No alternatives available for comparison.</p>
      )}

      {!loading && !error && alternatives.length > 0 && (
        <table border="1" cellPadding="10">
          <thead>
            <tr>
              <th>Criteria</th>

              {alternatives.map((alternative, index) => (
                <th key={index}>{alternative.name}</th>
              ))}
            </tr>
          </thead>

          <tbody>
            <tr>
              <td>
                <strong>Estimated Cost</strong>
              </td>

              {alternatives.map((alternative, index) => (
                <td key={index}>
                  {alternative.estimated_cost ?? "-"}
                </td>
              ))}
            </tr>

            <tr>
              <td>
                <strong>Feasibility Score</strong>
              </td>

              {alternatives.map((alternative, index) => (
                <td key={index}>
                  {alternative.feasibility_score ?? "-"}
                </td>
              ))}
            </tr>

            <tr>
              <td>
                <strong>Risk Level</strong>
              </td>

              {alternatives.map((alternative, index) => (
                <td key={index}>
                  {alternative.risk_level || "-"}
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      )}

      <br />

      <button
        onClick={() =>
          navigate(`/decisions/${id}/alternatives`)
        }
      >
        Back to Alternatives
      </button>

      <br />
      <br />

      <button
        onClick={() =>
          navigate(`/decisions/${id}`)
        }
      >
        Back to Decision
      </button>
    </div>
  );
}

export default AlternativeComparison;