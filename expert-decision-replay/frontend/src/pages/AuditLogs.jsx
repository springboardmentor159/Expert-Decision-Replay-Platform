import React, { useEffect, useState } from "react";
import auditLogService from "../services/auditLogService";

const Auditlogs = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadAuditLogs = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await auditLogService.getAuditLogs();

      setLogs(response.data || response || []);
    } catch (err) {
      console.error("Error loading audit logs:", err);
      setError("Unable to load audit logs.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAuditLogs();
  }, []);

  const getActionStyle = (action) => {
    const value = action?.toLowerCase() || "";

    if (value.includes("delete") || value.includes("reject")) {
      return "bg-red-100 text-red-700";
    }

    if (value.includes("create") || value.includes("approve")) {
      return "bg-green-100 text-green-700";
    }

    if (value.includes("update") || value.includes("edit")) {
      return "bg-blue-100 text-blue-700";
    }

    return "bg-gray-100 text-gray-700";
  };

  return (
    <div className="p-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">
            Audit Logs
          </h1>

          <p className="text-gray-600 mt-1">
            Track important actions performed in the system.
          </p>
        </div>

        <button
          onClick={loadAuditLogs}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          Refresh
        </button>
      </div>

      {loading && (
        <div className="bg-white rounded-xl shadow p-6">
          <p className="text-gray-600">Loading audit logs...</p>
        </div>
      )}

      {error && (
        <div className="bg-red-100 text-red-700 rounded-lg p-4 mb-4">
          {error}
        </div>
      )}

      {!loading && logs.length === 0 && !error && (
        <div className="bg-white rounded-xl shadow p-6 text-center">
          <p className="text-gray-600">No audit logs found.</p>
        </div>
      )}

      {!loading && logs.length > 0 && (
        <div className="bg-white rounded-xl shadow overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead className="bg-gray-100">
              <tr>
                <th className="p-4 border-b">ID</th>
                <th className="p-4 border-b">User ID</th>
                <th className="p-4 border-b">Action</th>
                <th className="p-4 border-b">Entity</th>
                <th className="p-4 border-b">Entity ID</th>
                <th className="p-4 border-b">Description</th>
                <th className="p-4 border-b">Date</th>
              </tr>
            </thead>

            <tbody>
              {logs.map((log) => (
                <tr key={log.id} className="hover:bg-gray-50">
                  <td className="p-4 border-b">
                    {log.id}
                  </td>

                  <td className="p-4 border-b">
                    {log.user_id || "-"}
                  </td>

                  <td className="p-4 border-b">
                    <span
                      className={`px-3 py-1 rounded-full text-sm font-medium ${getActionStyle(
                        log.action
                      )}`}
                    >
                      {log.action || "-"}
                    </span>
                  </td>

                  <td className="p-4 border-b">
                    {log.entity_type || log.entity || "-"}
                  </td>

                  <td className="p-4 border-b">
                    {log.entity_id || "-"}
                  </td>

                  <td className="p-4 border-b">
                    {log.description ||
                      log.details ||
                      log.message ||
                      "-"}
                  </td>

                  <td className="p-4 border-b whitespace-nowrap">
                    {log.created_at
                      ? new Date(log.created_at).toLocaleString()
                      : "-"}
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

export default Auditlogs;