import { useState } from "react";
import { useAuth } from "../../context/AuthContext";

import {
  getDecisionReport,
  getApprovalReport,
  getTeamReport,
  getAuditReport,
  exportDecisionPDF,
  exportDecisionExcel,
  exportApprovalPDF,
  exportApprovalExcel,
  exportTeamPDF,
  exportTeamExcel,
  exportAuditPDF,
  exportAuditExcel,
} from "../../services/reportService";

import PageHeader from "../../components/PageHeader";
import Button from "../../components/Button";
import Alert from "../../components/Alert";
import EmptyState from "../../components/EmptyState";

const Reports = () => {
  const { role } = useAuth();

  const [reportType, setReportType] = useState("decision");

  const [report, setReport] = useState(null);

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  const [success, setSuccess] = useState("");

  const [page, setPage] = useState(1);

  const pageSize = 20;


  // =========================================================
  // FILTER STATE
  // =========================================================

  const [filters, setFilters] = useState({
    category: "",
    status: "",
    createdBy: "",
    tag: "",
    reviewer: "",
    decisionId: "",
    level: "",
    teamId: "",
    userId: "",
    action: "",
    entityType: "",
    entityId: "",
    startDate: "",
    endDate: "",
    sortBy: "created_at",
    sortOrder: "desc",
  });


  // =========================================================
  // AVAILABLE REPORTS BASED ON ROLE
  // =========================================================

  const availableReports = [
    {
      value: "decision",
      label: "Decision Report",
      allowed: true,
    },
    {
      value: "approval",
      label: "Approval Report",
      allowed: true,
    },
    {
      value: "team",
      label: "Team Report",
      allowed:
        role === "Manager" ||
        role === "Administrator",
    },
    {
      value: "audit",
      label: "Audit Report",
      allowed:
        role === "Administrator",
    },
  ].filter((item) => item.allowed);


  // =========================================================
  // CHANGE FILTER
  // =========================================================

  const handleFilterChange = (event) => {
    const { name, value } = event.target;

    setFilters((current) => ({
      ...current,
      [name]: value,
    }));

    setPage(1);
  };


  // =========================================================
  // CLEAR FILTERS
  // =========================================================

  const clearFilters = () => {
    setFilters({
      category: "",
      status: "",
      createdBy: "",
      tag: "",
      reviewer: "",
      decisionId: "",
      level: "",
      teamId: "",
      userId: "",
      action: "",
      entityType: "",
      entityId: "",
      startDate: "",
      endDate: "",
      sortBy: "created_at",
      sortOrder: "desc",
    });

    setPage(1);
    setReport(null);
    setError("");
    setSuccess("");
  };


  // =========================================================
  // BUILD BACKEND PARAMETERS
  // =========================================================

  const buildParams = (exportMode = false) => {
    const params = {
      page: exportMode ? 1 : page,
      page_size: exportMode ? 100 : pageSize,
    };


    // Decision Report

    if (reportType === "decision") {

      if (filters.category.trim()) {
        params.category =
          filters.category.trim();
      }

      if (filters.status) {
        params.status =
          filters.status;
      }

      if (filters.createdBy.trim()) {
        params.created_by =
          Number(filters.createdBy);
      }

      if (filters.tag.trim()) {
        params.tag =
          filters.tag.trim();
      }

      if (filters.startDate) {
        params.start_date =
          `${filters.startDate}T00:00:00`;
      }

      if (filters.endDate) {
        params.end_date =
          `${filters.endDate}T23:59:59`;
      }

      params.sort_by =
        filters.sortBy || "created_at";

      params.sort_order =
        filters.sortOrder || "desc";
    }


    // Approval Report

    if (reportType === "approval") {

      if (filters.status) {
        params.status =
          filters.status;
      }

      if (filters.reviewer.trim()) {
        params.reviewer =
          Number(filters.reviewer);
      }

      if (filters.decisionId.trim()) {
        params.decision_id =
          Number(filters.decisionId);
      }

      if (filters.level.trim()) {
        params.level =
          Number(filters.level);
      }

      if (filters.startDate) {
        params.start_date =
          `${filters.startDate}T00:00:00`;
      }

      if (filters.endDate) {
        params.end_date =
          `${filters.endDate}T23:59:59`;
      }

      params.sort_by =
        filters.sortBy || "created_at";

      params.sort_order =
        filters.sortOrder || "desc";
    }


    // Team Report

    if (reportType === "team") {

      if (filters.teamId.trim()) {
        params.team_id =
          Number(filters.teamId);
      }

      if (filters.category.trim()) {
        params.category =
          filters.category.trim();
      }

      if (filters.status) {
        params.status =
          filters.status;
      }

      if (filters.startDate) {
        params.start_date =
          `${filters.startDate}T00:00:00`;
      }

      if (filters.endDate) {
        params.end_date =
          `${filters.endDate}T23:59:59`;
      }

      params.sort_by = "name";

      params.sort_order =
        filters.sortOrder || "asc";
    }


    // Audit Report

    if (reportType === "audit") {

      if (filters.userId.trim()) {
        params.user_id =
          Number(filters.userId);
      }

      if (filters.action.trim()) {
        params.action =
          filters.action.trim();
      }

      if (filters.entityType.trim()) {
        params.entity_type =
          filters.entityType.trim();
      }

      if (filters.entityId.trim()) {
        params.entity_id =
          Number(filters.entityId);
      }

      if (filters.startDate) {
        params.start_date =
          `${filters.startDate}T00:00:00`;
      }

      if (filters.endDate) {
        params.end_date =
          `${filters.endDate}T23:59:59`;
      }

      params.sort_by =
        filters.sortBy || "created_at";

      params.sort_order =
        filters.sortOrder || "desc";
    }


    return params;
  };


  // =========================================================
  // GET REPORT FUNCTION
  // =========================================================

  const getReportFunction = () => {
    switch (reportType) {
      case "decision":
        return getDecisionReport;

      case "approval":
        return getApprovalReport;

      case "team":
        return getTeamReport;

      case "audit":
        return getAuditReport;

      default:
        return getDecisionReport;
    }
  };


  // =========================================================
  // GENERATE REPORT
  // =========================================================

  const handleGenerateReport = async () => {
    try {
      setLoading(true);
      setError("");
      setSuccess("");
      setReport(null);

      const getReport =
        getReportFunction();

      const params =
        buildParams(false);

      const data =
        await getReport(params);

      setReport(data);

      setSuccess(
        "Report generated successfully."
      );

    } catch (err) {
      console.error(
        "Report generation error:",
        err
      );

      if (err.response?.status === 401) {
        setError(
          "You are not authenticated. Please login again."
        );
      } else if (err.response?.status === 403) {
        setError(
          "You do not have permission to view this report."
        );
      } else if (err.response?.status === 422) {
        setError(
          err.response?.data?.detail ||
            "Invalid filter or report parameters."
        );
      } else if (err.response?.status === 500) {
        setError(
          "Server error while generating the report."
        );
      } else {
        setError(
          "Failed to generate report."
        );
      }

    } finally {
      setLoading(false);
    }
  };


  // =========================================================
  // EXPORT FUNCTION
  // =========================================================

  const getExportFunction = (format) => {

    switch (reportType) {

      case "decision":
        return format === "pdf"
          ? exportDecisionPDF
          : exportDecisionExcel;

      case "approval":
        return format === "pdf"
          ? exportApprovalPDF
          : exportApprovalExcel;

      case "team":
        return format === "pdf"
          ? exportTeamPDF
          : exportTeamExcel;

      case "audit":
        return format === "pdf"
          ? exportAuditPDF
          : exportAuditExcel;

      default:
        return null;
    }
  };


  // =========================================================
  // EXPORT REPORT
  // =========================================================

  const handleExport = async (format) => {

    try {
      setLoading(true);
      setError("");
      setSuccess("");

      const exportFunction =
        getExportFunction(format);

      if (!exportFunction) {
        throw new Error(
          "Export function not available."
        );
      }

      const params =
        buildParams(true);

      const blob =
        await exportFunction(params);

      const fileBlob =
        blob instanceof Blob
          ? blob
          : new Blob([blob]);

      const url =
        window.URL.createObjectURL(
          fileBlob
        );

      const link =
        document.createElement("a");

      link.href = url;

      link.download =
        `${reportType}-report.${format}`;

      document.body.appendChild(link);

      link.click();

      document.body.removeChild(link);

      window.URL.revokeObjectURL(url);

      setSuccess(
        `${format.toUpperCase()} report downloaded successfully.`
      );

    } catch (err) {

      console.error(
        "Report export error:",
        err
      );

      if (err.response?.status === 401) {
        setError(
          "You are not authenticated. Please login again."
        );
      } else if (err.response?.status === 403) {
        setError(
          "You do not have permission to export this report."
        );
      } else if (err.response?.status === 422) {
        setError(
          err.response?.data?.detail ||
            "Invalid export parameters."
        );
      } else if (err.response?.status === 500) {
        setError(
          "Server error while exporting the report."
        );
      } else {
        setError(
          "Failed to export the report."
        );
      }

    } finally {
      setLoading(false);
    }
  };


  // =========================================================
  // CHANGE REPORT TYPE
  // =========================================================

  const handleReportTypeChange = (event) => {

    setReportType(
      event.target.value
    );

    setReport(null);
    setError("");
    setSuccess("");
    setPage(1);

  };


  // =========================================================
  // FORMAT DATE
  // =========================================================

  const formatDate = (value) => {

    if (!value) {
      return "-";
    }

    try {
      return new Date(
        value
      ).toLocaleString();

    } catch {
      return value;
    }
  };


  // =========================================================
  // STATUS BADGE
  // =========================================================

  const renderStatus = (status) => {

    if (!status) {
      return "-";
    }

    let className =
      "report-status";

    const normalized =
      status
        .toLowerCase()
        .replace(/\s+/g, "-");

    if (
      normalized === "approved"
    ) {
      className +=
        " approved";
    } else if (
      normalized === "rejected"
    ) {
      className +=
        " rejected";
    } else if (
      normalized === "pending"
    ) {
      className +=
        " pending";
    } else if (
      normalized === "draft"
    ) {
      className +=
        " draft";
    } else if (
      normalized === "under-review"
    ) {
      className +=
        " review";
    } else if (
      normalized === "archived"
    ) {
      className +=
        " archived";
    }

    return (
      <span className={className}>
        {status}
      </span>
    );
  };


  // =========================================================
  // DECISION REPORT
  // =========================================================

  const renderDecisionReport = () => {

    const data =
      report?.data || [];

    if (data.length === 0) {
      return (
        <EmptyState
          title="No Decision Records"
          message="No decision records match the selected filters."
        />
      );
    }

    return (
      <>
        {report.summary && (
          <div className="report-summary">

            <div className="report-summary-card">
              <strong>Total</strong>
              <span>
                {report.summary.total ?? 0}
              </span>
            </div>

            <div className="report-summary-card">
              <strong>Draft</strong>
              <span>
                {report.summary.Draft ?? 0}
              </span>
            </div>

            <div className="report-summary-card">
              <strong>Under Review</strong>
              <span>
                {report.summary["Under Review"] ?? 0}
              </span>
            </div>

            <div className="report-summary-card">
              <strong>Approved</strong>
              <span>
                {report.summary.Approved ?? 0}
              </span>
            </div>

            <div className="report-summary-card">
              <strong>Rejected</strong>
              <span>
                {report.summary.Rejected ?? 0}
              </span>
            </div>

            <div className="report-summary-card">
              <strong>Archived</strong>
              <span>
                {report.summary.Archived ?? 0}
              </span>
            </div>

          </div>
        )}


        <div className="report-table-wrapper">

          <table className="report-table">

            <thead>

              <tr>
                <th>Decision ID</th>
                <th>Title</th>
                <th>Category</th>
                <th>Status</th>
                <th>Created By</th>
                <th>Alternatives</th>
                <th>Approvals</th>
                <th>Created At</th>
              </tr>

            </thead>


            <tbody>

              {data.map((item) => (

                <tr
                  key={
                    item.decision_id
                  }
                >

                  <td>
                    {item.decision_id}
                  </td>

                  <td>
                    {item.title || "-"}
                  </td>

                  <td>
                    {item.category || "-"}
                  </td>

                  <td>
                    {renderStatus(
                      item.status
                    )}
                  </td>

                  <td>
                    {item.created_by || "-"}
                  </td>

                  <td>
                    {item.number_alternatives ?? 0}
                  </td>

                  <td>
                    {item.number_approvals ?? 0}
                  </td>

                  <td>
                    {formatDate(
                      item.created_at
                    )}
                  </td>

                </tr>

              ))}

            </tbody>

          </table>

        </div>
      </>
    );
  };


  // =========================================================
  // APPROVAL REPORT
  // =========================================================

  const renderApprovalReport = () => {

    const data =
      report?.data || [];

    if (data.length === 0) {
      return (
        <EmptyState
          title="No Approval Records"
          message="No approval records match the selected filters."
        />
      );
    }

    return (
      <>
        {report.summary && (
          <div className="report-summary">

            <div className="report-summary-card">
              <strong>Total</strong>
              <span>
                {report.summary.total ?? 0}
              </span>
            </div>

            <div className="report-summary-card">
              <strong>Pending</strong>
              <span>
                {report.summary.pending ?? 0}
              </span>
            </div>

            <div className="report-summary-card">
              <strong>Approved</strong>
              <span>
                {report.summary.approved ?? 0}
              </span>
            </div>

            <div className="report-summary-card">
              <strong>Rejected</strong>
              <span>
                {report.summary.rejected ?? 0}
              </span>
            </div>

            <div className="report-summary-card">
              <strong>Completion Rate</strong>
              <span>
                {report.summary.completion_rate ?? 0}%
              </span>
            </div>

          </div>
        )}


        <div className="report-table-wrapper">

          <table className="report-table">

            <thead>

              <tr>
                <th>Approval ID</th>
                <th>Decision ID</th>
                <th>Decision Title</th>
                <th>Reviewer</th>
                <th>Level</th>
                <th>Status</th>
                <th>Assigned Date</th>
                <th>Completed Date</th>
                <th>Turnaround Hours</th>
              </tr>

            </thead>


            <tbody>

              {data.map((item) => (

                <tr
                  key={
                    item.approval_id
                  }
                >

                  <td>
                    {item.approval_id}
                  </td>

                  <td>
                    {item.decision_id}
                  </td>

                  <td>
                    {item.decision_title || "-"}
                  </td>

                  <td>
                    {item.reviewer || "-"}
                  </td>

                  <td>
                    {item.approval_level ?? "-"}
                  </td>

                  <td>
                    {renderStatus(
                      item.status
                    )}
                  </td>

                  <td>
                    {formatDate(
                      item.assigned_date
                    )}
                  </td>

                  <td>
                    {formatDate(
                      item.completed_date
                    )}
                  </td>

                  <td>
                    {item.turnaround_time_hours ??
                      "-"}
                  </td>

                </tr>

              ))}

            </tbody>

          </table>

        </div>
      </>
    );
  };


  // =========================================================
  // TEAM REPORT
  // =========================================================

  const renderTeamReport = () => {

    const data =
      report?.data || [];

    if (data.length === 0) {
      return (
        <EmptyState
          title="No Team Records"
          message="No team records match the selected filters."
        />
      );
    }

    return (
      <div className="report-table-wrapper">

        <table className="report-table">

          <thead>

            <tr>
              <th>Team ID</th>
              <th>Team Name</th>
              <th>Members</th>
              <th>Total Decisions</th>
              <th>Approved Decisions</th>
              <th>Rejected Decisions</th>
              <th>Pending Decisions</th>
              <th>Total Approvals</th>
              <th>Approved Approvals</th>
              <th>Rejected Approvals</th>
            </tr>

          </thead>


          <tbody>

            {data.map((item) => (

              <tr
                key={
                  item.team_id
                }
              >

                <td>
                  {item.team_id}
                </td>

                <td>
                  {item.team_name || "-"}
                </td>

                <td>
                  {item.member_count ?? 0}
                </td>

                <td>
                  {item.total_decisions ?? 0}
                </td>

                <td>
                  {item.approved_decisions ?? 0}
                </td>

                <td>
                  {item.rejected_decisions ?? 0}
                </td>

                <td>
                  {item.pending_decisions ?? 0}
                </td>

                <td>
                  {item.total_approvals ?? 0}
                </td>

                <td>
                  {item.approved_approvals ?? 0}
                </td>

                <td>
                  {item.rejected_approvals ?? 0}
                </td>

              </tr>

            ))}

          </tbody>

        </table>

      </div>
    );
  };


  // =========================================================
  // AUDIT REPORT
  // =========================================================

  const renderAuditReport = () => {

    const data =
      report?.data || [];

    if (data.length === 0) {
      return (
        <EmptyState
          title="No Audit Records"
          message="No audit records match the selected filters."
        />
      );
    }

    return (
      <div className="report-table-wrapper">

        <table className="report-table">

          <thead>

            <tr>
              <th>ID</th>
              <th>User</th>
              <th>User ID</th>
              <th>Action</th>
              <th>Entity Type</th>
              <th>Entity ID</th>
              <th>Description</th>
              <th>Timestamp</th>
              <th>IP Address</th>
            </tr>

          </thead>


          <tbody>

            {data.map((item) => (

              <tr
                key={item.id}
              >

                <td>
                  {item.id}
                </td>

                <td>
                  {item.user || "-"}
                </td>

                <td>
                  {item.user_id || "-"}
                </td>

                <td>
                  {item.action || "-"}
                </td>

                <td>
                  {item.entity_type || "-"}
                </td>

                <td>
                  {item.entity_id || "-"}
                </td>

                <td>
                  {item.description || "-"}
                </td>

                <td>
                  {formatDate(
                    item.timestamp
                  )}
                </td>

                <td>
                  {item.ip_address || "-"}
                </td>

              </tr>

            ))}

          </tbody>

        </table>

      </div>
    );
  };


  // =========================================================
  // REPORT RENDERER
  // =========================================================

  const renderReport = () => {

    switch (reportType) {

      case "decision":
        return renderDecisionReport();

      case "approval":
        return renderApprovalReport();

      case "team":
        return renderTeamReport();

      case "audit":
        return renderAuditReport();

      default:
        return null;
    }
  };


  // =========================================================
  // FILTER UI
  // =========================================================

  const renderFilters = () => {

    return (
      <div className="reports-filters">

        {/* DECISION FILTERS */}

        {reportType === "decision" && (
          <>
            <div className="report-filter-group">
              <label>Category</label>

              <input
                type="text"
                name="category"
                value={filters.category}
                onChange={handleFilterChange}
                placeholder="e.g. Technology"
              />
            </div>


            <div className="report-filter-group">
              <label>Status</label>

              <select
                name="status"
                value={filters.status}
                onChange={handleFilterChange}
              >
                <option value="">
                  All Statuses
                </option>

                <option value="Draft">
                  Draft
                </option>

                <option value="Under Review">
                  Under Review
                </option>

                <option value="Approved">
                  Approved
                </option>

                <option value="Rejected">
                  Rejected
                </option>

                <option value="Archived">
                  Archived
                </option>
              </select>
            </div>


            <div className="report-filter-group">
              <label>Created By ID</label>

              <input
                type="number"
                min="1"
                name="createdBy"
                value={filters.createdBy}
                onChange={handleFilterChange}
                placeholder="User ID"
              />
            </div>


            <div className="report-filter-group">
              <label>Tag</label>

              <input
                type="text"
                name="tag"
                value={filters.tag}
                onChange={handleFilterChange}
                placeholder="e.g. database"
              />
            </div>
          </>
        )}


        {/* APPROVAL FILTERS */}

        {reportType === "approval" && (
          <>
            <div className="report-filter-group">
              <label>Status</label>

              <select
                name="status"
                value={filters.status}
                onChange={handleFilterChange}
              >
                <option value="">
                  All Statuses
                </option>

                <option value="Pending">
                  Pending
                </option>

                <option value="Approved">
                  Approved
                </option>

                <option value="Rejected">
                  Rejected
                </option>
              </select>
            </div>


            <div className="report-filter-group">
              <label>Reviewer ID</label>

              <input
                type="number"
                min="1"
                name="reviewer"
                value={filters.reviewer}
                onChange={handleFilterChange}
                placeholder="Reviewer ID"
              />
            </div>


            <div className="report-filter-group">
              <label>Decision ID</label>

              <input
                type="number"
                min="1"
                name="decisionId"
                value={filters.decisionId}
                onChange={handleFilterChange}
                placeholder="Decision ID"
              />
            </div>


            <div className="report-filter-group">
              <label>Approval Level</label>

              <input
                type="number"
                min="1"
                name="level"
                value={filters.level}
                onChange={handleFilterChange}
                placeholder="Level"
              />
            </div>
          </>
        )}


        {/* TEAM FILTERS */}

        {reportType === "team" && (
          <>
            <div className="report-filter-group">
              <label>Team ID</label>

              <input
                type="number"
                min="1"
                name="teamId"
                value={filters.teamId}
                onChange={handleFilterChange}
                placeholder="Team ID"
              />
            </div>


            <div className="report-filter-group">
              <label>Category</label>

              <input
                type="text"
                name="category"
                value={filters.category}
                onChange={handleFilterChange}
                placeholder="e.g. Technology"
              />
            </div>


            <div className="report-filter-group">
              <label>Status</label>

              <select
                name="status"
                value={filters.status}
                onChange={handleFilterChange}
              >
                <option value="">
                  All Statuses
                </option>

                <option value="Draft">
                  Draft
                </option>

                <option value="Under Review">
                  Under Review
                </option>

                <option value="Approved">
                  Approved
                </option>

                <option value="Rejected">
                  Rejected
                </option>

                <option value="Archived">
                  Archived
                </option>
              </select>
            </div>
          </>
        )}


        {/* AUDIT FILTERS */}

        {reportType === "audit" && (
          <>
            <div className="report-filter-group">
              <label>User ID</label>

              <input
                type="number"
                min="1"
                name="userId"
                value={filters.userId}
                onChange={handleFilterChange}
                placeholder="User ID"
              />
            </div>


            <div className="report-filter-group">
              <label>Action</label>

              <input
                type="text"
                name="action"
                value={filters.action}
                onChange={handleFilterChange}
                placeholder="e.g. LOGIN_SUCCESS"
              />
            </div>


            <div className="report-filter-group">
              <label>Entity Type</label>

              <input
                type="text"
                name="entityType"
                value={filters.entityType}
                onChange={handleFilterChange}
                placeholder="e.g. Decision"
              />
            </div>


            <div className="report-filter-group">
              <label>Entity ID</label>

              <input
                type="number"
                min="1"
                name="entityId"
                value={filters.entityId}
                onChange={handleFilterChange}
                placeholder="Entity ID"
              />
            </div>
          </>
        )}


        {/* DATE FILTERS */}

        <div className="report-filter-group">
          <label>Start Date</label>

          <input
            type="date"
            name="startDate"
            value={filters.startDate}
            onChange={handleFilterChange}
          />
        </div>


        <div className="report-filter-group">
          <label>End Date</label>

          <input
            type="date"
            name="endDate"
            value={filters.endDate}
            onChange={handleFilterChange}
          />
        </div>


        {/* SORT */}

        <div className="report-filter-group">
          <label>Sort By</label>

          <select
            name="sortBy"
            value={filters.sortBy}
            onChange={handleFilterChange}
          >

            {reportType === "decision" && (
              <>
                <option value="created_at">
                  Created Date
                </option>

                <option value="updated_at">
                  Updated Date
                </option>

                <option value="title">
                  Title
                </option>

                <option value="status">
                  Status
                </option>

                <option value="category">
                  Category
                </option>
              </>
            )}


            {reportType === "approval" && (
              <>
                <option value="created_at">
                  Created Date
                </option>

                <option value="completed_at">
                  Completed Date
                </option>

                <option value="approval_level">
                  Approval Level
                </option>

                <option value="status">
                  Status
                </option>
              </>
            )}


            {reportType === "team" && (
              <option value="name">
                Team Name
              </option>
            )}


            {reportType === "audit" && (
              <>
                <option value="created_at">
                  Created Date
                </option>

                <option value="action">
                  Action
                </option>

                <option value="entity_type">
                  Entity Type
                </option>
              </>
            )}

          </select>
        </div>


        <div className="report-filter-group">
          <label>Order</label>

          <select
            name="sortOrder"
            value={filters.sortOrder}
            onChange={handleFilterChange}
          >

            <option value="desc">
              Descending
            </option>

            <option value="asc">
              Ascending
            </option>

          </select>
        </div>


        {/* FILTER BUTTONS */}

        <div className="report-filter-actions">

          <Button
            variant="secondary"
            onClick={clearFilters}
          >
            Clear Filters
          </Button>

        </div>

      </div>
    );
  };


  // =========================================================
  // PAGINATION
  // =========================================================

  const totalPages =
    report?.total
      ? Math.max(
          1,
          Math.ceil(
            report.total /
              pageSize
          )
        )
      : 1;


  const handlePrevious = async () => {

    if (page <= 1) {
      return;
    }

    const newPage =
      page - 1;

    setPage(newPage);

    try {

      setLoading(true);
      setError("");

      const getReport =
        getReportFunction();

      const params =
        buildParams(false);

      params.page = newPage;

      const data =
        await getReport(params);

      setReport(data);

    } catch (err) {

      console.error(
        "Pagination error:",
        err
      );

      setError(
        "Failed to load the previous page."
      );

    } finally {

      setLoading(false);

    }
  };


  const handleNext = async () => {

    if (page >= totalPages) {
      return;
    }

    const newPage =
      page + 1;

    setPage(newPage);

    try {

      setLoading(true);
      setError("");

      const getReport =
        getReportFunction();

      const params =
        buildParams(false);

      params.page = newPage;

      const data =
        await getReport(params);

      setReport(data);

    } catch (err) {

      console.error(
        "Pagination error:",
        err
      );

      setError(
        "Failed to load the next page."
      );

    } finally {

      setLoading(false);

    }
  };


  // =========================================================
  // PAGE
  // =========================================================

  return (

    <div className="reports-page">

      <PageHeader
        title="Reports"
        subtitle={`Generate and export reports based on your ${role} role.`}
      />


      {/* REPORT TYPE */}

      <section className="reports-section">

        <div className="reports-section-header">

          <div>
            <h2>
              Report Selection
            </h2>

            <p>
              Select a report and apply
              filters before generating it.
            </p>
          </div>

        </div>


        <div className="report-controls">

          <div className="report-filter-group">

            <label htmlFor="report-type">
              Report Type
            </label>

            <select
              id="report-type"
              value={reportType}
              onChange={
                handleReportTypeChange
              }
            >

              {availableReports.map(
                (item) => (

                  <option
                    key={item.value}
                    value={item.value}
                  >
                    {item.label}
                  </option>

                )
              )}

            </select>

          </div>


          <div className="report-action-buttons">

            <Button
              onClick={
                handleGenerateReport
              }
              disabled={loading}
            >
              {loading
                ? "Generating..."
                : "Generate Report"}
            </Button>


            <Button
              variant="secondary"
              onClick={() =>
                handleExport("pdf")
              }
              disabled={loading}
            >
              Export PDF
            </Button>


            <Button
              variant="secondary"
              onClick={() =>
                handleExport("excel")
              }
              disabled={loading}
            >
              Export Excel
            </Button>

          </div>

        </div>

      </section>


      {/* FILTERS */}

      <section className="reports-section">

        <div className="reports-section-header">

          <div>
            <h2>
              Filters & Sorting
            </h2>

            <p>
              Refine the report using
              the available backend filters.
            </p>
          </div>

        </div>


        {renderFilters()}

      </section>


      {/* MESSAGES */}

      {error && (
        <Alert type="error">
          {error}
        </Alert>
      )}


      {success && (
        <Alert type="success">
          {success}
        </Alert>
      )}


      {/* LOADING */}

      {loading && (
        <section className="reports-section">

          <div className="report-loading">
            Generating report...
          </div>

        </section>
      )}


      {/* REPORT RESULT */}

      {report && !loading && (

        <section className="reports-section">

          <div className="reports-section-header">

            <div>

              <h2>
                {report.report ||
                  "Report"}
              </h2>

              <p>
                Total records:{" "}
                {report.total ?? 0}
              </p>

            </div>

          </div>


          {renderReport()}


          {report.total !== undefined &&
            report.total > 0 && (

              <div className="report-pagination">

                <Button
                  variant="secondary"
                  onClick={
                    handlePrevious
                  }
                  disabled={
                    page <= 1 ||
                    loading
                  }
                >
                  Previous
                </Button>


                <span>
                  Page {page} of{" "}
                  {totalPages}
                </span>


                <Button
                  variant="secondary"
                  onClick={
                    handleNext
                  }
                  disabled={
                    page >=
                      totalPages ||
                    loading
                  }
                >
                  Next
                </Button>

              </div>

            )}

        </section>

      )}


      {/* INITIAL STATE */}

      {!report &&
        !loading &&
        !error && (

          <section className="reports-section">

            <EmptyState
              title="No Report Generated"
              message="Select a report type, apply filters if required, and click Generate Report."
            />

          </section>

        )}

    </div>
  );
};

export default Reports;