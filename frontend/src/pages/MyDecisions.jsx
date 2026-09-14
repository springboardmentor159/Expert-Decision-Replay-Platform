import { useEffect, useState } from "react";
import api from "../services/api";
import DecisionTable from "../components/DecisionTable";
import { useNavigate } from "react-router-dom";

function MyDecisions() {
  const navigate = useNavigate();
  
  const [decisions, setDecisions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");

  useEffect(() => {
    fetchDecisions();
  }, []);

  const fetchDecisions = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await api.get("/decisions");

      setDecisions(response.data);
    } catch (error) {
      console.error("Failed to load decisions:", error);

      if (error.response?.status === 401) {
        setError("Your session has expired. Please login again.");
      } else if (error.response?.status === 403) {
        setError("You are not authorized to view decisions.");
      } else if (error.response?.status >= 500) {
        setError("Server error. Please try again later.");
      } else {
        setError(
          error.response?.data?.detail ||
            "Unable to load decisions."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  // Search + status filtering
  const filteredDecisions = decisions.filter((decision) => {
    const matchesSearch =
      decision.title
        ?.toLowerCase()
        .includes(search.toLowerCase()) ||
      decision.category
        ?.toLowerCase()
        .includes(search.toLowerCase());

    const matchesStatus =
      statusFilter === "All" ||
      decision.status === statusFilter;

    return matchesSearch && matchesStatus;
  });

  // Temporary action handlers
  
    const handleEdit = (decision) => {
    navigate(`/decisions/${decision.id}/edit`);
  };
  const handleDelete = async (decision) => {
  const confirmed = window.confirm(
    `Are you sure you want to delete "${decision.title}"?`
  );

  if (!confirmed) {
    return;
  }

  try {
    setError("");

    await api.delete(`/decisions/${decision.id}`);

    // Remove deleted decision from the current list
    setDecisions((previous) =>
      previous.filter((item) => item.id !== decision.id)
    );
  } catch (error) {
    console.error("Failed to delete decision:", error);

    if (error.response?.status === 401) {
      setError("Your session has expired. Please login again.");
    } else if (error.response?.status === 403) {
      setError("You are not authorized to delete this decision.");
    } else if (error.response?.status === 404) {
      setError("Decision not found.");
    } else if (error.response?.status === 422) {
      setError("Invalid decision ID.");
    } else if (error.response?.status >= 500) {
      setError("Server error. Please try again later.");
    } else {
      setError(
        error.response?.data?.detail ||
          "Unable to delete decision."
      );
    }
  }
};

  if (loading) {
    return (
      <div>
        <h1>My Decisions</h1>
        <p>Loading decisions...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <h1>My Decisions</h1>
        <p>{error}</p>
        <button onClick={fetchDecisions}>Try Again</button>
      </div>
    );
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>My Decisions</h1>
          <p>Manage and review your decisions.</p>
        </div>
      </div>

      {/* Filters */}
      <div className="decision-filters">
        <input
          type="text"
          placeholder="Search by title or category..."
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />

        <select
          value={statusFilter}
          onChange={(event) =>
            setStatusFilter(event.target.value)
          }
        >
          <option value="All">All Statuses</option>
          <option value="Draft">Draft</option>
          <option value="Under Review">Under Review</option>
          <option value="Approved">Approved</option>
          <option value="Rejected">Rejected</option>
          <option value="Archived">Archived</option>
        </select>
      </div>

      {/* Results */}
      {filteredDecisions.length === 0 ? (
        <div className="empty-state">
          <h3>No decisions found</h3>
          <p>
            Try changing your search or status filter.
          </p>
        </div>
      ) : (
        <DecisionTable
          decisions={filteredDecisions}
          onEdit={handleEdit}
          onDelete={handleDelete}
        />
      )}
    </div>
  );
}

export default MyDecisions;