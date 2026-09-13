import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../services/api";

function DecisionDetails() {
const { id } = useParams();
const navigate = useNavigate();

const [decision, setDecision] = useState(null);
const [loading, setLoading] = useState(true);
const [error, setError] = useState("");

useEffect(() => {
const fetchDecision = async () => {
try {
console.log("Decision ID:", id);

    const response = await api.get(`/decisions/${id}`);

    console.log("Decision response:", response.data);

    setDecision(response.data);
  } catch (err) {
    console.error("Decision error:", err);
    setError("Unable to load decision.");
  } finally {
    setLoading(false);
  }
};

fetchDecision();

}, [id]);

if (loading) {
return <p>Loading decision...</p>;
}

if (error) {
return (
<div>
<p>{error}</p>

    <button onClick={() => navigate("/decisions")}>
      Back to Decisions
    </button>
  </div>
);

}

if (!decision) {
return <p>No decision found.</p>;
}

return (
<div>
<h1>Decision Details</h1>

  <hr />

  <h2>{decision.title}</h2>

  <p>
    <strong>ID:</strong> {decision.id}
  </p>

  <p>
    <strong>Problem Statement:</strong>
  </p>

  <p>{decision.problem_statement || "Not available"}</p>

  <hr />

  <h3>Decision Information</h3>

  <p>
    <strong>Category:</strong>{" "}
    {decision.category || "Not specified"}
  </p>

  <p>
    <strong>Status:</strong>{" "}
    {decision.status || "Draft"}
  </p>

  <hr />

  <h3>Additional Information</h3>

  <p>
    <strong>Created Date:</strong>{" "}
    {decision.created_at
      ? new Date(decision.created_at).toLocaleString()
      : "Not available"}
  </p>

  <p>
    <strong>Last Updated:</strong>{" "}
    {decision.updated_at
      ? new Date(decision.updated_at).toLocaleString()
      : "Not available"}
  </p>

  <hr />

  <h3>Actions</h3>

  <button onClick={() => navigate(`/decisions/${id}/edit`)}>
    Edit Decision
  </button>

  <hr />

  <h3>Decision Modules</h3>

  <button
    onClick={() => navigate(`/decisions/${id}/alternatives`)}
  >
    Alternatives
  </button>

  <br />
  <br />

  <button
    onClick={() =>
      navigate(`/decisions/${id}/alternatives/compare`)
    }
  >
    Compare Alternatives
  </button>

  <br />
  <br />

  <button
    onClick={() => navigate(`/decisions/${id}/comments`)}
  >
    Discussions & Comments
  </button>

  <br />
  <br />

  <button
    onClick={() => navigate(`/decisions/${id}/approvals`)}
  >
    Approval Workflow
  </button>

  <br />
  <br />

  <button
    onClick={() => navigate(`/decisions/${id}/history`)}
  >
    Version History
  </button>

  <hr />

  <button onClick={() => navigate("/decisions")}>
    Back to Decisions
  </button>
</div>

);
}

export default DecisionDetails;