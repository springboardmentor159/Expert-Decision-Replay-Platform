import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../services/api";

function Approvals() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [approvals, setApprovals] = useState([]);

  const [reviewerId, setReviewerId] = useState("");
  const [approvalLevel, setApprovalLevel] = useState("");

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const fetchApprovals = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await api.get("/approvals/");

      const decisionApprovals = response.data.filter(
        (approval) => approval.decision_id === Number(id)
      );

      setApprovals(decisionApprovals);
    } catch (err) {
      console.error("Approvals error:", err);
      setError("Unable to load approvals.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApprovals();
  }, [id]);

  const handleCreateApproval = async (e) => {
    e.preventDefault();

    setError("");
    setMessage("");

    if (!reviewerId) {
      setError("Reviewer ID is required.");
      return;
    }

    if (!approvalLevel) {
      setError("Approval level is required.");
      return;
    }

    setSaving(true);

    try {
      const response = await api.post("/approvals/", {
        decision_id: Number(id),
        reviewer_id: Number(reviewerId),
        approval_level: Number(approvalLevel),
      });

      setApprovals((current) => [
        ...current,
        response.data,
      ]);

      setReviewerId("");
      setApprovalLevel("");

      setMessage("Approval request created successfully.");
    } catch (err) {
      console.error("Create approval error:", err);

      if (err.response?.data?.detail) {
        setError(
          typeof err.response.data.detail === "string"
            ? err.response.data.detail
            : "Unable to create approval."
        );
      } else {
        setError("Unable to create approval.");
      }
    } finally {
      setSaving(false);
    }
  };

  const handleApprovalUpdate = async (
    approvalId,
    newStatus
  ) => {
    setError("");
    setMessage("");

    try {
      const response = await api.put(
        `/approvals/${approvalId}`,
        {
          status: newStatus,
        }
      );

      setApprovals((current) =>
        current.map((approval) =>
          approval.id === approvalId
            ? response.data
            : approval
        )
      );

      setMessage(
        `Decision ${newStatus.toLowerCase()} successfully.`
      );
    } catch (err) {
      console.error("Approval update error:", err);

      if (err.response?.data?.detail) {
        setError(
          typeof err.response.data.detail === "string"
            ? err.response.data.detail
            : "Unable to update approval."
        );
      } else {
        setError("Unable to update approval.");
      }
    }
  };

  return (
    <div>
      <h1>Approval Workflow</h1>

      <p>
        <strong>Decision ID:</strong> {id}
      </p>

      <hr />

      <h2>Create Approval Request</h2>

      <form onSubmit={handleCreateApproval}>
        <div>
          <label>
            <strong>Reviewer ID:</strong>
          </label>
          <br />

          <input
            type="number"
            min="1"
            value={reviewerId}
            onChange={(e) =>
              setReviewerId(e.target.value)
            }
            placeholder="Enter reviewer user ID"
          />
        </div>

        <br />

        <div>
          <label>
            <strong>Approval Level:</strong>
          </label>
          <br />

          <select
            value={approvalLevel}
            onChange={(e) =>
              setApprovalLevel(e.target.value)
            }
          >
            <option value="">
              Select Approval Level
            </option>

            <option value="1">Level 1</option>

            <option value="2">Level 2</option>

            <option value="3">Level 3</option>
          </select>
        </div>

        <br />

        <button type="submit" disabled={saving}>
          {saving
            ? "Creating..."
            : "Create Approval Request"}
        </button>
      </form>

      <br />

      {message && (
        <p>
          <strong>{message}</strong>
        </p>
      )}

      {error && <p>{error}</p>}

      <hr />

      <h2>Approval Status</h2>

      {loading ? (
        <p>Loading approvals...</p>
      ) : approvals.length === 0 ? (
        <p>
          No approval requests found for this decision.
        </p>
      ) : (
        <table border="1" cellPadding="10">
          <thead>
            <tr>
              <th>ID</th>
              <th>Decision ID</th>
              <th>Reviewer ID</th>
              <th>Approval Level</th>
              <th>Status</th>
              <th>Assigned At</th>
              <th>Completed At</th>
              <th>Actions</th>
            </tr>
          </thead>

          <tbody>
            {approvals.map((approval) => (
              <tr key={approval.id}>
                <td>{approval.id}</td>

                <td>{approval.decision_id}</td>

                <td>{approval.reviewer_id}</td>

                <td>{approval.approval_level}</td>

                <td>{approval.status}</td>

                <td>
                  {approval.assigned_at
                    ? new Date(
                        approval.assigned_at
                      ).toLocaleString()
                    : "-"}
                </td>

                <td>
                  {approval.completed_at
                    ? new Date(
                        approval.completed_at
                      ).toLocaleString()
                    : "-"}
                </td>

                <td>
                  {approval.status === "Pending" ? (
                    <>
                      <button
                        onClick={() =>
                          handleApprovalUpdate(
                            approval.id,
                            "Approved"
                          )
                        }
                      >
                        Approve
                      </button>

                      <button
                        onClick={() =>
                          handleApprovalUpdate(
                            approval.id,
                            "Rejected"
                          )
                        }
                        style={{
                          marginLeft: "10px",
                        }}
                      >
                        Reject
                      </button>
                    </>
                  ) : (
                    <span>No action</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

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

export default Approvals;