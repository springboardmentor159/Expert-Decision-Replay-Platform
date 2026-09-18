import React, { useEffect, useState } from "react";
import approvalService from "../services/approvalService";

const Approvals = () => {
  const [approvals, setApprovals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [actionLoading, setActionLoading] = useState(null);

  const loadApprovals = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await approvalService.getApprovals();

      setApprovals(response.data || response || []);
    } catch (err) {
      console.error("Error loading approvals:", err);
      setError("Unable to load approvals.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadApprovals();
  }, []);

  const handleApprove = async (approvalId) => {
    try {
      setActionLoading(approvalId);

      await approvalService.approveApproval(approvalId);

      alert("Approval completed successfully.");
      loadApprovals();
    } catch (err) {
      console.error("Approval failed:", err);
      alert("Approval failed.");
    } finally {
      setActionLoading(null);
    }
  };

  const handleReject = async (approvalId) => {
    const confirmed = window.confirm(
      "Are you sure you want to reject this approval?"
    );

    if (!confirmed) {
      return;
    }

    try {
      setActionLoading(approvalId);

      await approvalService.rejectApproval(approvalId);

      alert("Approval rejected successfully.");
      loadApprovals();
    } catch (err) {
      console.error("Rejection failed:", err);
      alert("Rejection failed.");
    } finally {
      setActionLoading(null);
    }
  };

  const getStatusStyle = (status) => {
    switch (status?.toLowerCase()) {
      case "approved":
        return "bg-green-100 text-green-700";

      case "rejected":
        return "bg-red-100 text-red-700";

      case "pending":
        return "bg-yellow-100 text-yellow-700";

      default:
        return "bg-gray-100 text-gray-700";
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-4">Approvals</h1>
        <p className="text-gray-600">Loading approvals...</p>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-3">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">
            Approval Management
          </h1>

          <p className="text-gray-600 mt-1">
            Review and manage decision approval requests.
          </p>
        </div>

        <button
          onClick={loadApprovals}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          Refresh
        </button>
      </div>

      {error && (
        <div className="bg-red-100 text-red-700 p-4 rounded-lg mb-4">
          {error}
        </div>
      )}

      {approvals.length === 0 ? (
        <div className="bg-white rounded-xl shadow p-6 text-center">
          <p className="text-gray-600">No approval requests found.</p>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead className="bg-gray-100">
              <tr>
                <th className="p-4 border-b">ID</th>
                <th className="p-4 border-b">Decision ID</th>
                <th className="p-4 border-b">Approver ID</th>
                <th className="p-4 border-b">Level</th>
                <th className="p-4 border-b">Status</th>
                <th className="p-4 border-b">Comments</th>
                <th className="p-4 border-b">Actions</th>
              </tr>
            </thead>

            <tbody>
              {approvals.map((approval) => (
                <tr key={approval.id} className="hover:bg-gray-50">
                  <td className="p-4 border-b">
                    {approval.id}
                  </td>

                  <td className="p-4 border-b">
                    {approval.decision_id || "-"}
                  </td>

                  <td className="p-4 border-b">
                    {approval.approver_id || "-"}
                  </td>

                  <td className="p-4 border-b">
                    {approval.approval_level || approval.level || "-"}
                  </td>

                  <td className="p-4 border-b">
                    <span
                      className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusStyle(
                        approval.status
                      )}`}
                    >
                      {approval.status || "Pending"}
                    </span>
                  </td>

                  <td className="p-4 border-b">
                    {approval.comments || approval.comment || "-"}
                  </td>

                  <td className="p-4 border-b">
                    {approval.status?.toLowerCase() === "pending" ? (
                      <div className="flex flex-wrap gap-2">
                        <button
                          onClick={() => handleApprove(approval.id)}
                          disabled={actionLoading === approval.id}
                          className="bg-green-600 text-white px-3 py-1 rounded-lg hover:bg-green-700 disabled:opacity-50"
                        >
                          Approve
                        </button>

                        <button
                          onClick={() => handleReject(approval.id)}
                          disabled={actionLoading === approval.id}
                          className="bg-red-600 text-white px-3 py-1 rounded-lg hover:bg-red-700 disabled:opacity-50"
                        >
                          Reject
                        </button>
                      </div>
                    ) : (
                      <span className="text-gray-500 text-sm">
                        No actions
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default Approvals;