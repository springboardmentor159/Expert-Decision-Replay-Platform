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
        err.response?.data?.detail || "Unable to load the report."
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
    const emptyFilters = {
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
    };

    setFilters(emptyFilters);

    setTimeout(() => {
      fetchReport();
    }, 0);
  };

  const exportReport = async (format) => {
    try {
      setError("");

      const endpoint = `/reports/${reportType}/export/${format}`;
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
          <div className="report-filter-field">
            <label>Category</label>
            <input
              name="category"
              placeholder="Enter category"
              value={filters.category}
              onChange={handleFilterChange}
            />
          </div>

          <div className="report-filter-field">
            <label>Status</label>
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
          </div>

          <div className="report-filter-field">
            <label>Created By</label>
            <input
              name="created_by"
              placeholder="User ID"
              value={filters.created_by}
              onChange={handleFilterChange}
            />
          </div>

          <div className="report-filter-field">
            <label>Start Date</label>
            <input
              type="date"
              name="start_date"
              value={filters.start_date}
              onChange={handleFilterChange}
            />
          </div>

          <div className="report-filter-field">
            <label>End Date</label>
            <input
              type="date"
              name="end_date"
              value={filters.end_date}
              onChange={handleFilterChange}
            />
          </div>

          <div className="report-filter-field">
            <label>Tag</label>
            <input
              name="tag"
              placeholder="Enter tag"
              value={filters.tag}
              onChange={handleFilterChange}
            />
          </div>
        </>
      );
    }

    if (reportType === "approvals") {
      return (
        <>
          <div className="report-filter-field">
            <label>Status</label>
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
          </div>

          <div className="report-filter-field">
            <label>Reviewer ID</label>
            <input
              name="reviewer_id"
              placeholder="Reviewer ID"
              value={filters.reviewer_id}
              onChange={handleFilterChange}
            />
          </div>

          <div className="report-filter-field">
            <label>Decision ID</label>
            <input
              name="decision_id"
              placeholder="Decision ID"
              value={filters.decision_id}
              onChange={handleFilterChange}
            />
          </div>

          <div className="report-filter-field">
            <label>Approval Level</label>
            <input
              name="approval_level"
              placeholder="Level"
              value={filters.approval_level}
              onChange={handleFilterChange}
            />
          </div>

          <div className="report-filter-field">
            <label>Start Date</label>
            <input
              type="date"
              name="start_date"
              value={filters.start_date}
              onChange={handleFilterChange}
            />
          </div>

          <div className="report-filter-field">
            <label>End Date</label>
            <input
              type="date"
              name="end_date"
              value={filters.end_date}
              onChange={handleFilterChange}
            />
          </div>
        </>
      );
    }

    if (reportType === "teams") {
      return (
        <>
          <div className="report-filter-field">
            <label>Category</label>
            <input
              name="category"
              placeholder="Enter category"
              value={filters.category}
              onChange={handleFilterChange}
            />
          </div>

          <div className="report-filter-field">
            <label>Status</label>
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
          </div>

          <div className="report-filter-field">
            <label>Start Date</label>
            <input
              type="date"
              name="start_date"
              value={filters.start_date}
              onChange={handleFilterChange}
            />
          </div>

          <div className="report-filter-field">
            <label>End Date</label>
            <input
              type="date"
              name="end_date"
              value={filters.end_date}
              onChange={handleFilterChange}
            />
          </div>
        </>
      );
    }

    return (
      <>
        <div className="report-filter-field">
          <label>User ID</label>
          <input
            name="user_id"
            placeholder="User ID"
            value={filters.user_id}
            onChange={handleFilterChange}
          />
        </div>

        <div className="report-filter-field">
          <label>Action</label>
          <input
            name="action"
            placeholder="Action"
            value={filters.action}
            onChange={handleFilterChange}
          />
        </div>

        <div className="report-filter-field">
          <label>Entity Type</label>
          <input
            name="entity_type"
            placeholder="Entity type"
            value={filters.entity_type}
            onChange={handleFilterChange}
          />
        </div>

        <div className="report-filter-field">
          <label>Entity ID</label>
          <input
            name="entity_id"
            placeholder="Entity ID"
            value={filters.entity_id}
            onChange={handleFilterChange}
          />
        </div>

        <div className="report-filter-field">
          <label>Start Date</label>
          <input
            type="date"
            name="start_date"
            value={filters.start_date}
            onChange={handleFilterChange}
          />
        </div>

        <div className="report-filter-field">
          <label>End Date</label>
          <input
            type="date"
            name="end_date"
            value={filters.end_date}
            onChange={handleFilterChange}
          />
        </div>
      </>
    );
  };

  const formatKey = (key) => {
    return key
      .replace(/_/g, " ")
      .replace(/\b\w/g, (char) => char.toUpperCase());
  };

  const renderTable = () => {
    if (loading) {
      return (
        <div className="report-state">
          <div className="loading-spinner"></div>
          <p>Loading report data...</p>
        </div>
      );
    }

    if (error) {
      return (
        <div className="report-error">
          <span>!</span>
          <div>
            <strong>Unable to load report</strong>
            <p>{error}</p>
          </div>
        </div>
      );
    }

    if (!data.length) {
      return (
        <div className="report-empty">
          <div className="report-empty-icon">▤</div>
          <h3>No report data found</h3>
          <p>
            Try adjusting the filters or selecting a different report type.
          </p>
        </div>
      );
    }

    const columns = Object.keys(data[0]);

    return (
      <div className="report-table-wrapper">
        <table className="professional-report-table">
          <thead>
            <tr>
              {columns.map((column) => (
                <th key={column}>{formatKey(column)}</th>
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

  const reportTitle = {
    decisions: "Decision Reports",
    approvals: "Approval Reports",
    teams: "Team Reports",
    audit: "Audit Reports",
  };

  const reportDescription = {
    decisions:
      "Review decision records, statuses, categories and activity across the platform.",
    approvals:
      "Monitor approval workflows, reviewers, approval levels and outcomes.",
    teams:
      "Analyze decision activity and status information across teams.",
    audit:
      "Review system activity, user actions and entity-level audit information.",
  };

  return (
    <div className="reports-page">
      <div className="page-breadcrumb">
        Reports <span>/</span> {reportTitle[reportType]}
      </div>

      <div className="reports-header">
        <div>
          <h1>Reports & Analytics</h1>
          <p>
            Generate, filter and export enterprise reports from the decision
            management platform.
          </p>
        </div>

        <div className="reports-header-badge">
          <span className="reports-header-icon">▥</span>
          Reporting Center
        </div>
      </div>

      <div className="report-type-tabs">
        <button
          className={reportType === "decisions" ? "active" : ""}
          onClick={() => setReportType("decisions")}
        >
          <span>◈</span>
          Decision Reports
        </button>

        <button
          className={reportType === "approvals" ? "active" : ""}
          onClick={() => setReportType("approvals")}
        >
          <span>✓</span>
          Approval Reports
        </button>

        <button
          className={reportType === "teams" ? "active" : ""}
          onClick={() => setReportType("teams")}
        >
          <span>♟</span>
          Team Reports
        </button>

        <button
          className={reportType === "audit" ? "active" : ""}
          onClick={() => setReportType("audit")}
        >
          <span>◷</span>
          Audit Reports
        </button>
      </div>

      <div className="report-intro-card">
        <div>
          <div className="report-section-label">CURRENT REPORT</div>
          <h2>{reportTitle[reportType]}</h2>
          <p>{reportDescription[reportType]}</p>
        </div>

        <div className="report-record-count">
          <span>Records</span>
          <strong>{data.length}</strong>
        </div>
      </div>

      <div className="report-filter-card">
        <div className="report-card-heading">
          <div>
            <h3>Report Filters</h3>
            <p>Refine the report using the available criteria.</p>
          </div>
          <span className="filter-icon">⌕</span>
        </div>

        <div className="report-filters-grid">
          {renderFilters()}
        </div>

        <div className="report-filter-actions">
          <button
            className="report-apply-button"
            onClick={fetchReport}
            disabled={loading}
          >
            {loading ? "Loading..." : "Apply Filters"}
          </button>

          <button
            className="report-clear-button"
            onClick={clearFilters}
            disabled={loading}
          >
            Clear Filters
          </button>
        </div>
      </div>

      <div className="report-export-card">
        <div className="report-export-text">
          <div className="export-icon">⇩</div>
          <div>
            <h3>Export Report</h3>
            <p>
              Download the current report with the selected filters applied.
            </p>
          </div>
        </div>

        <div className="report-export-actions">
          <button
            className="export-pdf-button"
            onClick={() => exportReport("pdf")}
          >
            <span>PDF</span>
            Export PDF
          </button>

          <button
            className="export-excel-button"
            onClick={() => exportReport("excel")}
          >
            <span>XLSX</span>
            Export Excel
          </button>
        </div>
      </div>

      {Object.keys(summary).length > 0 && (
        <div className="report-summary-card">
          <div className="report-card-heading">
            <div>
              <h3>Report Summary</h3>
              <p>Key information returned by the reporting service.</p>
            </div>
          </div>

          <div className="report-summary-grid">
            {Object.entries(summary).map(([key, value]) => (
              <div className="report-summary-item" key={key}>
                <span>{formatKey(key)}</span>
                <strong>{String(value)}</strong>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="report-data-card">
        <div className="report-card-heading">
          <div>
            <h3>Report Data</h3>
            <p>
              Detailed records returned for the selected report and filters.
            </p>
          </div>

          {!loading && data.length > 0 && (
            <span className="report-data-badge">
              {data.length} {data.length === 1 ? "record" : "records"}
            </span>
          )}
        </div>

        {renderTable()}
      </div>
    </div>
  );
}

export default Reports;