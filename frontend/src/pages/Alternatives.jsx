import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../services/api";

function Alternatives() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [alternatives, setAlternatives] = useState([]);

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [pros, setPros] = useState("");
  const [cons, setCons] = useState("");
  const [estimatedCost, setEstimatedCost] = useState("");
  const [feasibilityScore, setFeasibilityScore] = useState("");
  const [riskLevel, setRiskLevel] = useState("");

  const [editingId, setEditingId] = useState(null);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const fetchAlternatives = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await api.get(
        `/decisions/${id}/alternatives`
      );

      setAlternatives(response.data);
    } catch (err) {
      console.error("Alternatives error:", err);
      setError("Unable to load alternatives.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlternatives();
  }, [id]);

  const clearForm = () => {
    setName("");
    setDescription("");
    setPros("");
    setCons("");
    setEstimatedCost("");
    setFeasibilityScore("");
    setRiskLevel("");
    setEditingId(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError("");
    setMessage("");

    if (!name.trim()) {
      setError("Alternative name is required.");
      return;
    }

    if (
      feasibilityScore !== "" &&
      (Number(feasibilityScore) < 1 ||
        Number(feasibilityScore) > 5)
    ) {
      setError("Feasibility score must be between 1 and 5.");
      return;
    }

    setSaving(true);

    const data = {
      name: name,
      description: description,
      pros: pros,
      cons: cons,
      estimated_cost:
        estimatedCost === "" ? null : Number(estimatedCost),
      feasibility_score:
        feasibilityScore === ""
          ? null
          : Number(feasibilityScore),
      risk_level: riskLevel,
    };

    try {
      if (editingId) {
        const response = await api.put(
          `/alternatives/${editingId}`,
          data
        );

        setAlternatives((current) =>
          current.map((alternative) =>
            alternative.id === editingId
              ? response.data
              : alternative
          )
        );

        setMessage("Alternative updated successfully.");
      } else {
        const response = await api.post(
          `/decisions/${id}/alternatives`,
          data
        );

        setAlternatives((current) => [
          ...current,
          response.data,
        ]);

        setMessage("Alternative added successfully.");
      }

      clearForm();
    } catch (err) {
      console.error("Alternative save error:", err);

      if (err.response?.data?.detail) {
        setError(
          typeof err.response.data.detail === "string"
            ? err.response.data.detail
            : "Unable to save alternative."
        );
      } else {
        setError("Unable to save alternative.");
      }
    } finally {
      setSaving(false);
    }
  };

  const handleEdit = (alternative) => {
    setEditingId(alternative.id);

    setName(alternative.name || "");
    setDescription(alternative.description || "");
    setPros(alternative.pros || "");
    setCons(alternative.cons || "");
    setEstimatedCost(
      alternative.estimated_cost ?? ""
    );
    setFeasibilityScore(
      alternative.feasibility_score ?? ""
    );
    setRiskLevel(alternative.risk_level || "");

    setMessage("");
    setError("");

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  return (
    <div>
      <h1>Alternative Analysis</h1>

      <p>
        <strong>Decision ID:</strong> {id}
      </p>

      <hr />

      <h2>
        {editingId
          ? "Edit Alternative"
          : "Add Alternative"}
      </h2>

      <form onSubmit={handleSubmit}>
        <div>
          <label>
            <strong>Name:</strong>
          </label>
          <br />

          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Enter alternative name"
          />
        </div>

        <br />

        <div>
          <label>
            <strong>Description:</strong>
          </label>
          <br />

          <textarea
            rows="4"
            cols="50"
            value={description}
            onChange={(e) =>
              setDescription(e.target.value)
            }
            placeholder="Describe the alternative"
          />
        </div>

        <br />

        <div>
          <label>
            <strong>Pros:</strong>
          </label>
          <br />

          <textarea
            rows="3"
            cols="50"
            value={pros}
            onChange={(e) => setPros(e.target.value)}
            placeholder="Advantages"
          />
        </div>

        <br />

        <div>
          <label>
            <strong>Cons:</strong>
          </label>
          <br />

          <textarea
            rows="3"
            cols="50"
            value={cons}
            onChange={(e) => setCons(e.target.value)}
            placeholder="Disadvantages"
          />
        </div>

        <br />

        <div>
          <label>
            <strong>Estimated Cost:</strong>
          </label>
          <br />

          <input
            type="number"
            min="0"
            value={estimatedCost}
            onChange={(e) =>
              setEstimatedCost(e.target.value)
            }
            placeholder="Enter estimated cost"
          />
        </div>

        <br />

        <div>
          <label>
            <strong>Feasibility Score (1-5):</strong>
          </label>
          <br />

          <input
            type="number"
            min="1"
            max="5"
            step="1"
            value={feasibilityScore}
            onChange={(e) =>
              setFeasibilityScore(e.target.value)
            }
            placeholder="1 to 5"
          />
        </div>

        <br />

        <div>
          <label>
            <strong>Risk Level:</strong>
          </label>
          <br />

          <select
            value={riskLevel}
            onChange={(e) =>
              setRiskLevel(e.target.value)
            }
          >
            <option value="">Select Risk Level</option>
            <option value="Low">Low</option>
            <option value="Medium">Medium</option>
            <option value="High">High</option>
          </select>
        </div>

        <br />

        <button type="submit" disabled={saving}>
          {saving
            ? "Saving..."
            : editingId
            ? "Update Alternative"
            : "Add Alternative"}
        </button>

        {editingId && (
          <button
            type="button"
            onClick={clearForm}
            style={{ marginLeft: "10px" }}
          >
            Cancel Edit
          </button>
        )}
      </form>

      <br />

      {message && (
        <p>
          <strong>{message}</strong>
        </p>
      )}

      {error && <p>{error}</p>}

      <hr />

      <h2>Existing Alternatives</h2>

      {loading ? (
        <p>Loading alternatives...</p>
      ) : alternatives.length === 0 ? (
        <p>No alternatives found for this decision.</p>
      ) : (
        <table border="1" cellPadding="10">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Description</th>
              <th>Pros</th>
              <th>Cons</th>
              <th>Estimated Cost</th>
              <th>Feasibility</th>
              <th>Risk</th>
              <th>Action</th>
            </tr>
          </thead>

          <tbody>
            {alternatives.map((alternative) => (
              <tr key={alternative.id}>
                <td>{alternative.id}</td>

                <td>{alternative.name}</td>

                <td>
                  {alternative.description || "-"}
                </td>

                <td>{alternative.pros || "-"}</td>

                <td>{alternative.cons || "-"}</td>

                <td>
                  {alternative.estimated_cost ?? "-"}
                </td>

                <td>
                  {alternative.feasibility_score ?? "-"}
                </td>

                <td>
                  {alternative.risk_level || "-"}
                </td>

                <td>
                  <button
                    onClick={() =>
                      handleEdit(alternative)
                    }
                  >
                    Edit
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <br />

      <button
        onClick={() =>
          navigate(
            `/decisions/${id}/alternatives/compare`
          )
        }
      >
        Compare Alternatives
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

export default Alternatives;