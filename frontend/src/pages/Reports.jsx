import { useEffect, useState } from "react";
import api from "../services/api";

function Reports() {
  const [reportType, setReportType] = useState("decisions");

  const [data, setData] = useState([]);
  const [summary, setSummary] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [filters, setFilters] = useState({
    category: "",
    status: "",
    created_by: "",
    start_date: "",
    end_date: "",
    tag: "",
    reviewer_id: "",
    decision_id: "",
    approval_level: "",
    action: "",
    entity_type: "",
    entity_id: "",
    user_id: "",
  });

  const fetchReport = async () => {
    try {
      setLoading(true);
      setError("");

      let endpoint = `/reports/${reportType}`;

      const params = {};

      if (reportType === "decisions") {
        if (filters.category) params.category = filters.category;
        if (filters.status) params.status = filters.status;
        if (filters.created_by) params.created_by = filters.created_by;
        if (filters.start_date) params.start_date = filters.start_date;
        if (filters.end_date) params.end_date = filters.end_date;
        if (filters.tag) params.tag = filters.tag;
      }

      if (reportType === "approvals") {
        if (filters.status) params.status = filters.status;
        if (filters.reviewer_id) params.reviewer_id = filters.reviewer_id;
        if (filters.decision_id) params.decision_id = filters.decision_id;
        if (filters.approval_level) {
          params.approval_level = filters.approval_level;
        }
        if (filters.start_date) params.start_date = filters.start_date;
        if (filters.end_date) params.end_date = filters.end_date;
      }

      if (reportType === "teams") {
        if (filters.category) params.category = filters.category;
        if (filters.status) params.status = filters.status;
        if (filters.start_date) params.start_date = filters.start_date;
        if (filters.end_date) params.end_date = filters.end_date;
      }

      if (reportType === "audit") {
        if (filters.user_id) params.user_id = filters.user_id;
        if (filters.action) params.action = filters.action;
        if (filters.entity_type) params.entity_type = filters.entity_type;
        if (filters.entity_id) params.entity_id = filters.entity_id;
        if (filters.start_date) params.start_date = filters.start_date;
        if (filters.end_date) params.end_date = filters.end_date;
      }

      const response = await api.get(endpoint, { params });

      setData(response.data.data || []);
      setSummary(response.data.summary || {});
    } catch (err) {
      console.error(err);
      setData([]);
      setSummary({});
      setError(
        err.response?.data?.detail ||
          "Unable to load the report."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReport();
  }, [reportType]);

  const handleFilterChange = (e) => {
    setFilters({
      ...filters,
      [e.target.name]: e.target.value,
    });
  };

  const clearFilters = () => {
    setFilters({
      category: "",
      status: "",
      created_by: "",
      start_date: "",
      end_date: "",
      tag: "",
      reviewer_id: "",
      decision_id: "",
      approval_level: "",
      action: "",
      entity_type: "",
      entity_id: "",
      user_id: "",
    });

    setTimeout(() => {
      fetchReport();
    }, 0);
  };

  const exportReport = async (format) => {
    try {
      // Backend endpoint format:
      // /reports/decisions/export/pdf
      // /reports/decisions/export/excel
      let endpoint = `/reports/${reportType}/export/${format}`;

      const params = {};

      Object.entries(filters).forEach(([key, value]) => {
        if (value) {
          params[key] = value;
        }
      });

      const response = await api.get(endpoint, {
        params,
        responseType: "blob",
      });

      const blob = new Blob([response.data]);

      const url = window.URL.createObjectURL(blob);

      const link = document.createElement("a");
      link.href = url;

      link.download = `${reportType}-report.${
        format === "pdf" ? "pdf" : "xlsx"
      }`;

      document.body.appendChild(link);
      link.click();
      link.remove();

      window.URL.revokeObjectURL(url);

      setError("");
    } catch (err) {
      console.error(err);

      setError(
        err.response?.data?.detail ||
          `Unable to export ${format.toUpperCase()} report.`
      );
    }
  };

  const renderFilters = () => {
    if (reportType === "decisions") {
      return (
        <>
          <input
            name="category"
            placeholder="Category"
            value={filters.category}
            onChange={handleFilterChange}
          />

          <select
            name="status"
            value={filters.status}
            onChange={handleFilterChange}
          >
            <option value="">All Status</option>
            <option value="Draft">Draft</option>
            <option value="Under Review">Under Review</option>
            <option value="Approved">Approved</option>
            <option value="Rejected">Rejected</option>
            <option value="Archived">Archived</option>
          </select>

          <input
            name="created_by"
            placeholder="Created By ID"
            value={filters.created_by}
            onChange={handleFilterChange}
          />

          <input
            type="date"
            name="start_date"
            value={filters.start_date}
            onChange={handleFilterChange}
          />

          <input
            type="date"
            name="end_date"
            value={filters.end_date}
            onChange={handleFilterChange}
          />

          <input
            name="tag"
            placeholder="Tag"
            value={filters.tag}
            onChange={handleFilterChange}
          />
        </>
      );
    }

    if (reportType === "approvals") {
      return (
        <>
          <select
            name="status"
            value={filters.status}
            onChange={handleFilterChange}
          >
            <option value="">All Status</option>
            <option value="Pending">Pending</option>
            <option value="Approved">Approved</option>
            <option value="Rejected">Rejected</option>
          </select>

          <input
            name="reviewer_id"
            placeholder="Reviewer ID"
            value={filters.reviewer_id}
            onChange={handleFilterChange}
          />

          <input
            name="decision_id"
            placeholder="Decision ID"
            value={filters.decision_id}
            onChange={handleFilterChange}
          />

          <input
            name="approval_level"
            placeholder="Approval Level"
            value={filters.approval_level}
            onChange={handleFilterChange}
          />

          <input
            type="date"
            name="start_date"
            value={filters.start_date}
            onChange={handleFilterChange}
          />

          <input
            type="date"
            name="end_date"
            value={filters.end_date}
            onChange={handleFilterChange}
          />
        </>
      );
    }

    if (reportType === "teams") {
      return (
        <>
          <input
            name="category"
            placeholder="Category"
            value={filters.category}
            onChange={handleFilterChange}
          />

          <select
            name="status"
            value={filters.status}
            onChange={handleFilterChange}
          >
            <option value="">All Status</option>
            <option value="Draft">Draft</option>
            <option value="Under Review">Under Review</option>
            <option value="Approved">Approved</option>
            <option value="Rejected">Rejected</option>
            <option value="Archived">Archived</option>
          </select>

          <input
            type="date"
            name="start_date"
            value={filters.start_date}
            onChange={handleFilterChange}
          />

          <input
            type="date"
            name="end_date"
            value={filters.end_date}
            onChange={handleFilterChange}
          />
        </>
      );
    }

    return (
      <>
        <input
          name="user_id"
          placeholder="User ID"
          value={filters.user_id}
          onChange={handleFilterChange}
        />

        <input
          name="action"
          placeholder="Action"
          value={filters.action}
          onChange={handleFilterChange}
        />

        <input
          name="entity_type"
          placeholder="Entity Type"
          value={filters.entity_type}
          onChange={handleFilterChange}
        />

        <input
          name="entity_id"
          placeholder="Entity ID"
          value={filters.entity_id}
          onChange={handleFilterChange}
        />

        <input
          type="date"
          name="start_date"
          value={filters.start_date}
          onChange={handleFilterChange}
        />

        <input
          type="date"
          name="end_date"
          value={filters.end_date}
          onChange={handleFilterChange}
        />
      </>
    );
  };

  const renderTable = () => {
    if (loading) {
      return <p>Loading report...</p>;
    }

    if (error) {
      return <p>{error}</p>;
    }

    if (!data.length) {
      return <p>No report data found.</p>;
    }

    const columns = Object.keys(data[0]);

    return (
      <div style={{ overflowX: "auto" }}>
        <table border="1" cellPadding="8" cellSpacing="0">
          <thead>
            <tr>
              {columns.map((column) => (
                <th key={column}>{column}</th>
              ))}
            </tr>
          </thead>

          <tbody>
            {data.map((row, index) => (
              <tr key={index}>
                {columns.map((column) => (
                  <td key={column}>
                    {typeof row[column] === "object"
                      ? JSON.stringify(row[column])
                      : String(row[column] ?? "")}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>Reports</h1>

      <div style={{ marginBottom: "20px" }}>
        <button onClick={() => setReportType("decisions")}>
          Decision Reports
        </button>

        <button onClick={() => setReportType("approvals")}>
          Approval Reports
        </button>

        <button onClick={() => setReportType("teams")}>
          Team Reports
        </button>

        <button onClick={() => setReportType("audit")}>
          Audit Reports
        </button>
      </div>

      <h2>
        {reportType.charAt(0).toUpperCase() + reportType.slice(1)} Report
      </h2>

      <div
        style={{
          display: "flex",
          gap: "10px",
          flexWrap: "wrap",
          marginBottom: "15px",
        }}
      >
        {renderFilters()}
      </div>

      <button onClick={fetchReport}>Apply Filters</button>

      <button
        onClick={clearFilters}
        style={{ marginLeft: "10px" }}
      >
        Clear Filters
      </button>

      <button
        onClick={() => exportReport("pdf")}
        style={{ marginLeft: "10px" }}
      >
        Export PDF
      </button>

      <button
        onClick={() => exportReport("excel")}
        style={{ marginLeft: "10px" }}
      >
        Export Excel
      </button>

      <h3>Summary</h3>

      {Object.keys(summary).length === 0 ? (
        <p>No summary available.</p>
      ) : (
        <div>
          {Object.entries(summary).map(([key, value]) => (
            <p key={key}>
              <strong>{key}:</strong> {String(value)}
            </p>
          ))}
        </div>
      )}

      <h3>Report Data</h3>

      {renderTable()}
    </div>
  );
}

export default Reports;