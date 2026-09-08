import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../services/api";

function DecisionDetails() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [decision, setDecision] = useState(null);

  const [title, setTitle] = useState("");
  const [problemStatement, setProblemStatement] = useState("");
  const [category, setCategory] = useState("");
  const [status, setStatus] = useState("");

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    const fetchDecision = async () => {
      try {
        const response = await api.get(`/decisions/${id}`);

        setDecision(response.data);

        setTitle(response.data.title || "");
        setProblemStatement(response.data.problem_statement || "");
        setCategory(response.data.category || "");
        setStatus(response.data.status || "Draft");
      } catch (err) {
        console.error("Decision error:", err);
        setError("Unable to load decision.");
      } finally {
        setLoading(false);
      }
    };

    fetchDecision();
  }, [id]);

  const handleSave = async () => {
    setSaving(true);
    setError("");
    setMessage("");

    try {
      const response = await api.put(`/decisions/${id}`, {
        title: title,
        problem_statement: problemStatement,
        category: category,
        status: status,
      });

      setDecision(response.data);

      setTitle(response.data.title || "");
      setProblemStatement(response.data.problem_statement || "");
      setCategory(response.data.category || "");
      setStatus(response.data.status || "Draft");

      setMessage("Decision updated successfully.");
    } catch (err) {
      console.error("Update decision error:", err);

      if (err.response?.data?.detail) {
        setError(
          typeof err.response.data.detail === "string"
            ? err.response.data.detail
            : "Unable to update decision."
        );
      } else {
        setError("Unable to update decision.");
      }
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <p>Loading decision...</p>;
  }

  if (error && !decision) {
    return (
      <div>
        <p>{error}</p>

        <button onClick={() => navigate("/decisions")}>
          Back to Decisions
        </button>
      </div>
    );
  }

  return (
    <div>
      <h1>Decision Details</h1>

      <p>
        <strong>ID:</strong> {decision.id}
      </p>

      <hr />

      <h3>Edit Decision</h3>

      <div>
        <label>
          <strong>Title:</strong>
        </label>
        <br />

        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
      </div>

      <br />

      <div>
        <label>
          <strong>Problem Statement:</strong>
        </label>
        <br />

        <textarea
          rows="4"
          cols="50"
          value={problemStatement}
          onChange={(e) => setProblemStatement(e.target.value)}
        />
      </div>

      <br />

      <div>
        <label>
          <strong>Category:</strong>
        </label>
        <br />

        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
        >
          <option value="">Select Category</option>
          <option value="Technology">Technology</option>
          <option value="Finance">Finance</option>
          <option value="Operations">Operations</option>
          <option value="Human Resources">Human Resources</option>
          <option value="Security">Security</option>
          <option value="Product">Product</option>
          <option value="Infrastructure">Infrastructure</option>
          <option value="Strategy">Strategy</option>
        </select>
      </div>

      <br />

      <div>
        <label>
          <strong>Status:</strong>
        </label>
        <br />

        <select
          value={status}
          onChange={(e) => setStatus(e.target.value)}
        >
          <option value="Draft">Draft</option>
          <option value="Under Review">Under Review</option>
          <option value="Approved">Approved</option>
          <option value="Rejected">Rejected</option>
        </select>
      </div>

      <br />

      <button onClick={handleSave} disabled={saving}>
        {saving ? "Saving..." : "Save Changes"}
      </button>

      {message && (
        <p>
          <strong>{message}</strong>
        </p>
      )}

      {error && <p>{error}</p>}

      <hr />

      <h3>Current Decision</h3>

      <p>
        <strong>Title:</strong> {decision.title}
      </p>

      <p>
        <strong>Problem Statement:</strong>{" "}
        {decision.problem_statement}
      </p>

      <p>
        <strong>Category:</strong> {decision.category}
      </p>

      <p>
        <strong>Status:</strong> {decision.status}
      </p>

      <br />

      <button onClick={() => navigate("/decisions")}>
        Back to Decisions
      </button>
    </div>
  );
}

export default DecisionDetails;