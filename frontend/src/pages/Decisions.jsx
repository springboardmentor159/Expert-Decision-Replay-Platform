import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

function Decisions() {
  const [decisions, setDecisions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const navigate = useNavigate();

  useEffect(() => {
    fetchDecisions();
  }, []);

  const fetchDecisions = async () => {
    try {
      setLoading(true);

      const response = await api.get("/decisions");

      setDecisions(response.data);
    } catch (err) {
      if (err.response?.status === 401) {
        setError("Your session has expired. Please login again.");
      } else if (err.response?.status === 403) {
        setError("You don't have permission to view decisions.");
      } else {
        setError("Unable to load decisions.");
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <p>Loading decisions...</p>;
  }

  return (
    <div>
      <h1>Decision Management</h1>

      <button onClick={() => navigate("/decisions/create")}>
        Create Decision
      </button>

      <br />
      <br />

      {error && <p>{error}</p>}

      {decisions.length === 0 ? (
        <p>No decisions found.</p>
      ) : (
        <table border="1" cellPadding="10">
          <thead>
            <tr>
              <th>ID</th>
              <th>Title</th>
              <th>Category</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>

          <tbody>
            {decisions.map((decision) => (
              <tr key={decision.id}>
                <td>{decision.id}</td>
                <td>{decision.title}</td>
                <td>{decision.category}</td>
                <td>{decision.status}</td>

                <td>
                  <button
                    onClick={() =>
                      navigate(`/decisions/${decision.id}`)
                    }
                  >
                    View
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default Decisions;