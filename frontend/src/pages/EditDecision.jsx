import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../services/api";

function EditDecision() {
const { id } = useParams();
const navigate = useNavigate();

const [title, setTitle] = useState("");
const [problemStatement, setProblemStatement] = useState("");
const [category, setCategory] = useState("");

const [loading, setLoading] = useState(true);
const [saving, setSaving] = useState(false);

const [error, setError] = useState("");
const [message, setMessage] = useState("");

useEffect(() => {
const fetchDecision = async () => {
try {
const response = await api.get("/decisions/${id}");

    setTitle(response.data.title || "");
    setProblemStatement(response.data.problem_statement || "");
    setCategory(response.data.category || "");
  } catch (err) {
    console.error("Load decision error:", err);
    setError("Unable to load decision.");
  } finally {
    setLoading(false);
  }
};

fetchDecision();

}, [id]);

const handleSubmit = async (e) => {
e.preventDefault();

setError("");
setMessage("");

if (!title.trim()) {
  setError("Decision title is required.");
  return;
}

if (!problemStatement.trim()) {
  setError("Problem statement is required.");
  return;
}

if (!category) {
  setError("Please select a category.");
  return;
}

setSaving(true);

try {
  const response = await api.put(`/decisions/${id}`, {
    title: title,
    problem_statement: problemStatement,
    category: category,
  });

  setMessage("Decision updated successfully.");

  setTimeout(() => {
    navigate(`/decisions/${id}`);
  }, 1000);

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

return (
<div>
<h1>Edit Decision</h1>

  {error && (
    <p>
      <strong>{error}</strong>
    </p>
  )}

  {message && (
    <p>
      <strong>{message}</strong>
    </p>
  )}

  <form onSubmit={handleSubmit}>
    <div>
      <label>
        <strong>Decision Title:</strong>
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
        rows="5"
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
        <option value="Human Resources">
          Human Resources
        </option>
        <option value="Security">Security</option>
        <option value="Product">Product</option>
        <option value="Infrastructure">
          Infrastructure
        </option>
        <option value="Strategy">Strategy</option>
      </select>
    </div>

    <br />

    <button type="submit" disabled={saving}>
      {saving ? "Saving..." : "Save Changes"}
    </button>

    <button
      type="button"
      onClick={() => navigate(`/decisions/${id}`)}
      style={{ marginLeft: "10px" }}
    >
      Cancel
    </button>
  </form>
</div>

);
}

export default EditDecision;