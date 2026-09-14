import { Link } from "react-router-dom";

function DecisionTable({ decisions, onEdit, onDelete }) {
  const getStatusClass = (status) => {
    switch (status) {
      case "Draft":
        return "status-badge draft";

      case "Under Review":
        return "status-badge under-review";

      case "Approved":
        return "status-badge approved";

      case "Rejected":
        return "status-badge rejected";

      case "Archived":
        return "status-badge archived";

      default:
        return "status-badge";
    }
  };

  return (
    <div className="decision-table-container">
      <table className="decision-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Title</th>
            <th>Category</th>
            <th>Status</th>
            <th>Created</th>
            <th>Actions</th>
          </tr>
        </thead>

        <tbody>
          {decisions.map((decision) => (
            <tr key={decision.id}>
              <td>{decision.id}</td>

              <td className="decision-title">
                {decision.title}
              </td>

              <td>
                {decision.category || "N/A"}
              </td>

              <td>
                <span className={getStatusClass(decision.status)}>
                  {decision.status}
                </span>
              </td>

              <td>
                {decision.created_at
                  ? new Date(
                      decision.created_at
                    ).toLocaleDateString()
                  : "N/A"}
              </td>

              <td className="decision-actions">

                {/* View */}
                <Link
                  to={`/decisions/${decision.id}`}
                  className="action-button view-button"
                >
                  View
                </Link>

                {/* Edit */}
                <button
                  type="button"
                  className="action-button edit-button"
                  onClick={() => onEdit(decision)}
                >
                  Edit
                </button>

                {/* Delete */}
                <button
                  type="button"
                  className="action-button delete-button"
                  onClick={() => onDelete(decision)}
                >
                  Delete
                </button>

              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default DecisionTable;