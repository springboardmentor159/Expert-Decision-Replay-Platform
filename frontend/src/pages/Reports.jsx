import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

import {
  getDecisionReport,
  getApprovalReport,
  getTeamReport,
  getAuditReport,
  exportDecisionReportPdf,
  exportApprovalReportPdf,
  exportTeamReportPdf,
  exportAuditReportPdf,
  exportDecisionReportExcel,
  exportApprovalReportExcel,
  exportTeamReportExcel,
  exportAuditReportExcel,
  getReportsErrorMessage,
  downloadReportFile,
} from "../api/reportsApi";

const REPORT_TYPES = {
  DECISIONS: "decisions",
  APPROVALS: "approvals",
  TEAMS: "teams",
  AUDIT: "audit",
};

const DECISION_STATUSES = [
  "Draft",
  "Under Review",
  "Approved",
  "Rejected",
  "Archived",
];

const APPROVAL_STATUSES = [
  "Pending",
  "Approved",
  "Rejected",
];

const APPROVAL_LEVELS = [
  "Employee",
  "Reviewer",
  "Manager",
  "Administrator",
];

function formatDate(value) {
  if (!value) {
    return "—";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return String(value);
  }

  return date.toLocaleString();
}

function formatValue(value) {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return "—";
  }

  if (typeof value === "object") {
    if (Array.isArray(value)) {
      if (value.length === 0) {
        return "—";
      }

      return value
        .map((item) => formatValue(item))
        .join(", ");
    }

    if (value.name) {
      return String(value.name);
    }

    if (value.full_name) {
      return String(value.full_name);
    }

    if (value.email) {
      return String(value.email);
    }

    if (value.id !== undefined) {
      return `#${value.id}`;
    }

    return Object.entries(value)
      .map(([key, item]) => `${key}: ${formatValue(item)}`)
      .join(", ");
  }

  return String(value);
}

function formatUser(value) {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return "—";
  }

  if (typeof value !== "object") {
    return String(value);
  }

  const name =
    value.name ||
    value.full_name ||
    "";

  const email =
    value.email ||
    "";

  const id =
    value.id !== undefined &&
    value.id !== null
      ? value.id
      : null;

  if (name && email) {
    return `${name} (${email})`;
  }

  if (name) {
    return String(name);
  }

  if (email) {
    return String(email);
  }

  if (id !== null) {
    return `User #${id}`;
  }

  return "—";
}

function getStatusClass(status) {
  switch (status) {
    case "Approved":
      return "status-badge status-approved";

    case "Rejected":
      return "status-badge status-rejected";

    case "Pending":
      return "status-badge status-pending";

    case "Under Review":
      return "status-badge status-review";

    case "Archived":
      return "status-badge status-archived";

    case "Draft":
    default:
      return "status-badge status-draft";
  }
}

function extractRows(data) {
  if (!data) {
    return [];
  }

  if (Array.isArray(data)) {
    return data;
  }

  if (Array.isArray(data.results)) {
    return data.results;
  }

  if (Array.isArray(data.items)) {
    return data.items;
  }

  if (Array.isArray(data.records)) {
    return data.records;
  }

  if (Array.isArray(data.decisions)) {
    return data.decisions;
  }

  if (Array.isArray(data.approvals)) {
    return data.approvals;
  }

  if (Array.isArray(data.teams)) {
    return data.teams;
  }

  if (Array.isArray(data.activities)) {
    return data.activities;
  }

  if (Array.isArray(data.audit_logs)) {
    return data.audit_logs;
  }

  if (Array.isArray(data.audit)) {
    return data.audit;
  }

  if (Array.isArray(data.data)) {
    return data.data;
  }

  return [];
}

function extractTotal(data, rows) {
  if (
    data &&
    typeof data.total === "number"
  ) {
    return data.total;
  }

  if (
    data &&
    typeof data.count === "number"
  ) {
    return data.count;
  }

  return rows.length;
}

function getDecisionColumns() {
  return [
    {
      key: "id",
      label: "ID",
    },
    {
      key: "title",
      label: "Title",
    },
    {
      key: "category",
      label: "Category",
    },
    {
      key: "status",
      label: "Status",
    },
    {
      key: "created_by",
      label: "Created By",
    },
    {
      key: "created_at",
      label: "Created",
    },
    {
      key: "updated_at",
      label: "Updated",
    },
  ];
}

function getApprovalColumns() {
  return [
    {
      key: "id",
      label: "ID",
    },
    {
      key: "decision_id",
      label: "Decision",
    },
    {
      key: "assigned_to",
      label: "Reviewer",
    },
    {
      key: "assigned_by",
      label: "Assigned By",
    },
    {
      key: "assigned_role",
      label: "Approval Level",
    },
    {
      key: "status",
      label: "Status",
    },
    {
      key: "comments",
      label: "Comments",
    },
    {
      key: "assigned_at",
      label: "Assigned",
    },
    {
      key: "reviewed_at",
      label: "Reviewed",
    },
  ];
}

function getTeamColumns() {
  return [
    {
      key: "team",
      label: "Team",
    },
    {
      key: "member_count",
      label: "Members",
    },
    {
      key: "total_decisions",
      label: "Total Decisions",
    },
    {
      key: "approved",
      label: "Approved",
    },
    {
      key: "rejected",
      label: "Rejected",
    },
  ];
}

function getAuditColumns() {
  return [
    {
      key: "id",
      label: "ID",
    },
    {
      key: "action",
      label: "Action",
    },
    {
      key: "entity_type",
      label: "Entity",
    },
    {
      key: "entity_id",
      label: "Entity ID",
    },
    {
      key: "user_id",
      label: "User",
    },
    {
      key: "description",
      label: "Description",
    },
    {
      key: "created_at",
      label: "Date",
    },
  ];
}

function renderCell(row, key) {
  const value = row?.[key];

  if (
    key === "created_at" ||
    key === "updated_at" ||
    key === "assigned_at" ||
    key === "reviewed_at"
  ) {
    return formatDate(value);
  }

  if (key === "created_by") {
    return formatUser(value);
  }

  if (
    key === "assigned_to" ||
    key === "assigned_by"
  ) {
    return formatUser(value);
  }

  if (key === "status") {
    return (
      <span className={getStatusClass(value)}>
        {formatValue(value)}
      </span>
    );
  }

  if (key === "tags") {
    return formatValue(value);
  }

  return formatValue(value);
}

function Pagination({
  page,
  pageSize,
  total,
  onPageChange,
}) {
  const totalPages = Math.max(
    1,
    Math.ceil(total / pageSize)
  );

  if (totalPages <= 1) {
    return null;
  }

  return (
    <div className="pagination">
      <button
        type="button"
        className="button secondary"
        disabled={page <= 1}
        onClick={() =>
          onPageChange(page - 1)
        }
      >
        Previous
      </button>

      <span>
        Page {page} of {totalPages}
      </span>

      <button
        type="button"
        className="button secondary"
        disabled={page >= totalPages}
        onClick={() =>
          onPageChange(page + 1)
        }
      >
        Next
      </button>
    </div>
  );
}

export default function Reports() {
  const [reportType, setReportType] = useState(
    REPORT_TYPES.DECISIONS
  );

  const [rows, setRows] = useState([]);
  const [total, setTotal] = useState(0);

  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] =
    useState(false);

  const [errorMessage, setErrorMessage] =
    useState("");

  const [exporting, setExporting] =
    useState("");

  const [category, setCategory] =
    useState("");

  const [status, setStatus] =
    useState("");

  const [createdBy, setCreatedBy] =
    useState("");

  const [tag, setTag] =
    useState("");

  const [reviewer, setReviewer] =
    useState("");

  const [decisionId, setDecisionId] =
    useState("");

  const [approvalLevel, setApprovalLevel] =
    useState("");

  const [team, setTeam] =
    useState("");

  const [auditUserId, setAuditUserId] =
    useState("");

  const [action, setAction] =
    useState("");

  const [entityType, setEntityType] =
    useState("");

  const [entityId, setEntityId] =
    useState("");

  const [startDate, setStartDate] =
    useState("");

  const [endDate, setEndDate] =
    useState("");

  const [sortBy, setSortBy] =
    useState("created_at");

  const [order, setOrder] =
    useState("desc");

  const isAuditReport =
    reportType === REPORT_TYPES.AUDIT;

  const columns = useMemo(() => {
    if (
      reportType === REPORT_TYPES.APPROVALS
    ) {
      return getApprovalColumns();
    }

    if (
      reportType === REPORT_TYPES.TEAMS
    ) {
      return getTeamColumns();
    }

    if (
      reportType === REPORT_TYPES.AUDIT
    ) {
      return getAuditColumns();
    }

    return getDecisionColumns();
  }, [reportType]);

  useEffect(() => {
    loadReport();
  }, [
    reportType,
    page,
    category,
    status,
    createdBy,
    tag,
    reviewer,
    decisionId,
    approvalLevel,
    team,
    auditUserId,
    action,
    entityType,
    entityId,
    startDate,
    endDate,
    sortBy,
    order,
  ]);

  function validateFilters() {
    if (
      startDate &&
      endDate &&
      startDate > endDate
    ) {
      return "Start date cannot be after end date.";
    }

    if (
      createdBy &&
      !/^\d+$/.test(createdBy)
    ) {
      return "Created By must be a valid user ID.";
    }

    if (
      reviewer &&
      !/^\d+$/.test(reviewer)
    ) {
      return "Reviewer must be a valid user ID.";
    }

    if (
      decisionId &&
      !/^\d+$/.test(decisionId)
    ) {
      return "Decision ID must be a valid number.";
    }

    if (
      auditUserId &&
      !/^\d+$/.test(auditUserId)
    ) {
      return "Audit User ID must be a valid number.";
    }

    if (
      entityId &&
      !/^\d+$/.test(entityId)
    ) {
      return "Entity ID must be a valid number.";
    }

    return "";
  }

  async function loadReport() {
    const validationError =
      validateFilters();

    if (validationError) {
      setRows([]);
      setTotal(0);
      setErrorMessage(validationError);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setErrorMessage("");

      let response;

      if (
        reportType ===
        REPORT_TYPES.DECISIONS
      ) {
        response = await getDecisionReport({
          category,
          status,
          created_by:
            createdBy === ""
              ? ""
              : Number(createdBy),
          start_date: startDate,
          end_date: endDate,
          tag,
          page,
          page_size: pageSize,
          sort_by: sortBy,
          order,
        });
      }

      if (
        reportType ===
        REPORT_TYPES.APPROVALS
      ) {
        response = await getApprovalReport({
          status,
          reviewer:
            reviewer === ""
              ? ""
              : Number(reviewer),
          decision:
            decisionId === ""
              ? ""
              : Number(decisionId),
          approval_level: approvalLevel,
          start_date: startDate,
          end_date: endDate,
          page,
          page_size: pageSize,
          sort_by: sortBy,
          order,
        });
      }

      if (
        reportType ===
        REPORT_TYPES.TEAMS
      ) {
        response = await getTeamReport({
          team,
          start_date: startDate,
          end_date: endDate,
          decision_status: status,
          category,
          page,
          page_size: pageSize,
          sort_by: sortBy,
          order,
        });
      }

      if (
        reportType ===
        REPORT_TYPES.AUDIT
      ) {
        response = await getAuditReport({
          user_id:
            auditUserId === ""
              ? ""
              : Number(auditUserId),
          action,
          entity_type: entityType,
          entity_id:
            entityId === ""
              ? ""
              : Number(entityId),
          start_date: startDate,
          end_date: endDate,
          page,
          page_size: pageSize,
          sort_by: sortBy,
          order,
        });
      }

      const extractedRows =
        extractRows(response);

      setRows(extractedRows);

      setTotal(
        extractTotal(
          response,
          extractedRows
        )
      );
    } catch (error) {
      console.error(
        "Failed to load report:",
        error
      );

      setRows([]);
      setTotal(0);

      setErrorMessage(
        getReportsErrorMessage(error)
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  async function refreshReport() {
    setRefreshing(true);
    await loadReport();
  }

  function resetFilters() {
    setCategory("");
    setStatus("");
    setCreatedBy("");
    setTag("");
    setReviewer("");
    setDecisionId("");
    setApprovalLevel("");
    setTeam("");
    setAuditUserId("");
    setAction("");
    setEntityType("");
    setEntityId("");
    setStartDate("");
    setEndDate("");

    setSortBy(
      reportType === REPORT_TYPES.TEAMS
        ? "team"
        : reportType ===
          REPORT_TYPES.APPROVALS
        ? "assigned_at"
        : reportType ===
          REPORT_TYPES.AUDIT
        ? "created_at"
        : "created_at"
    );

    setOrder(
      reportType === REPORT_TYPES.TEAMS
        ? "asc"
        : "desc"
    );

    setPage(1);
  }

  function changeReportType(type) {
    setReportType(type);
    setPage(1);
    setErrorMessage("");
  }

  function getExportParams() {
    if (
      reportType ===
      REPORT_TYPES.DECISIONS
    ) {
      return {
        category,
        status,
        created_by:
          createdBy === ""
            ? ""
            : Number(createdBy),
        start_date: startDate,
        end_date: endDate,
        tag,
        page_size: 1000,
        sort_by: sortBy,
        order,
      };
    }

    if (
      reportType ===
      REPORT_TYPES.APPROVALS
    ) {
      return {
        status,
        reviewer:
          reviewer === ""
            ? ""
            : Number(reviewer),
        decision:
          decisionId === ""
            ? ""
            : Number(decisionId),
        approval_level: approvalLevel,
        start_date: startDate,
        end_date: endDate,
        page_size: 1000,
        sort_by: sortBy,
        order,
      };
    }

    if (
      reportType ===
      REPORT_TYPES.TEAMS
    ) {
      return {
        team,
        start_date: startDate,
        end_date: endDate,
        decision_status: status,
        category,
        page_size: 1000,
        sort_by: sortBy,
        order,
      };
    }

    return {
      user_id:
        auditUserId === ""
          ? ""
          : Number(auditUserId),
      action,
      entity_type: entityType,
      entity_id:
        entityId === ""
          ? ""
          : Number(entityId),
      start_date: startDate,
      end_date: endDate,
      page_size: 1000,
      sort_by: sortBy,
      order,
    };
  }

  async function handleExport(format) {
    const validationError =
      validateFilters();

    if (validationError) {
      setErrorMessage(validationError);
      return;
    }

    const exportKey = `${reportType}-${format}`;

    try {
      setExporting(exportKey);
      setErrorMessage("");

      const params = getExportParams();

      let response;

      if (
        reportType ===
        REPORT_TYPES.DECISIONS
      ) {
        if (format === "pdf") {
          response =
            await exportDecisionReportPdf(
              params
            );
        } else {
          response =
            await exportDecisionReportExcel(
              params
            );
        }
      }

      if (
        reportType ===
        REPORT_TYPES.APPROVALS
      ) {
        if (format === "pdf") {
          response =
            await exportApprovalReportPdf(
              params
            );
        } else {
          response =
            await exportApprovalReportExcel(
              params
            );
        }
      }

      if (
        reportType ===
        REPORT_TYPES.TEAMS
      ) {
        if (format === "pdf") {
          response =
            await exportTeamReportPdf(
              params
            );
        } else {
          response =
            await exportTeamReportExcel(
              params
            );
        }
      }

      if (
        reportType ===
        REPORT_TYPES.AUDIT
      ) {
        if (format === "pdf") {
          response =
            await exportAuditReportPdf(
              params
            );
        } else {
          response =
            await exportAuditReportExcel(
              params
            );
        }
      }

      const extension =
        format === "pdf"
          ? "pdf"
          : "xlsx";

      const filename =
        `${reportType}_report.${extension}`;

      downloadReportFile(
        response,
        filename
      );
    } catch (error) {
      console.error(
        "Failed to export report:",
        error
      );

      setErrorMessage(
        getReportsErrorMessage(error)
      );
    } finally {
      setExporting("");
    }
  }

  function renderDecisionFilters() {
    return (
      <>
        <div className="form-group">
          <label htmlFor="category">
            Category
          </label>

          <input
            id="category"
            type="text"
            value={category}
            onChange={(event) => {
              setCategory(event.target.value);
              setPage(1);
            }}
            placeholder="Technology"
          />
        </div>

        <div className="form-group">
          <label htmlFor="status">
            Status
          </label>

          <select
            id="status"
            value={status}
            onChange={(event) => {
              setStatus(event.target.value);
              setPage(1);
            }}
          >
            <option value="">
              All statuses
            </option>

            {DECISION_STATUSES.map(
              (item) => (
                <option
                  key={item}
                  value={item}
                >
                  {item}
                </option>
              )
            )}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="createdBy">
            Created By User ID
          </label>

          <input
            id="createdBy"
            type="text"
            inputMode="numeric"
            value={createdBy}
            onChange={(event) => {
              setCreatedBy(
                event.target.value
              );
              setPage(1);
            }}
            placeholder="24"
          />
        </div>

        <div className="form-group">
          <label htmlFor="tag">
            Tag
          </label>

          <input
            id="tag"
            type="text"
            value={tag}
            onChange={(event) => {
              setTag(event.target.value);
              setPage(1);
            }}
            placeholder="security"
          />
        </div>
      </>
    );
  }

  function renderApprovalFilters() {
    return (
      <>
        <div className="form-group">
          <label htmlFor="approvalStatus">
            Status
          </label>

          <select
            id="approvalStatus"
            value={status}
            onChange={(event) => {
              setStatus(event.target.value);
              setPage(1);
            }}
          >
            <option value="">
              All statuses
            </option>

            {APPROVAL_STATUSES.map(
              (item) => (
                <option
                  key={item}
                  value={item}
                >
                  {item}
                </option>
              )
            )}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="reviewer">
            Reviewer User ID
          </label>

          <input
            id="reviewer"
            type="text"
            inputMode="numeric"
            value={reviewer}
            onChange={(event) => {
              setReviewer(
                event.target.value
              );
              setPage(1);
            }}
            placeholder="20"
          />
        </div>

        <div className="form-group">
          <label htmlFor="decisionId">
            Decision ID
          </label>

          <input
            id="decisionId"
            type="text"
            inputMode="numeric"
            value={decisionId}
            onChange={(event) => {
              setDecisionId(
                event.target.value
              );
              setPage(1);
            }}
            placeholder="20"
          />
        </div>

        <div className="form-group">
          <label htmlFor="approvalLevel">
            Approval Level
          </label>

          <select
            id="approvalLevel"
            value={approvalLevel}
            onChange={(event) => {
              setApprovalLevel(
                event.target.value
              );
              setPage(1);
            }}
          >
            <option value="">
              All levels
            </option>

            {APPROVAL_LEVELS.map(
              (item) => (
                <option
                  key={item}
                  value={item}
                >
                  {item}
                </option>
              )
            )}
          </select>
        </div>
      </>
    );
  }

  function renderTeamFilters() {
    return (
      <>
        <div className="form-group">
          <label htmlFor="team">
            Team / Department
          </label>

          <input
            id="team"
            type="text"
            value={team}
            onChange={(event) => {
              setTeam(event.target.value);
              setPage(1);
            }}
            placeholder="Engineering"
          />
        </div>

        <div className="form-group">
          <label htmlFor="teamCategory">
            Category
          </label>

          <input
            id="teamCategory"
            type="text"
            value={category}
            onChange={(event) => {
              setCategory(event.target.value);
              setPage(1);
            }}
            placeholder="Technology"
          />
        </div>

        <div className="form-group">
          <label htmlFor="teamStatus">
            Decision Status
          </label>

          <select
            id="teamStatus"
            value={status}
            onChange={(event) => {
              setStatus(event.target.value);
              setPage(1);
            }}
          >
            <option value="">
              All statuses
            </option>

            {DECISION_STATUSES.map(
              (item) => (
                <option
                  key={item}
                  value={item}
                >
                  {item}
                </option>
              )
            )}
          </select>
        </div>
      </>
    );
  }

  function renderAuditFilters() {
    return (
      <>
        <div className="form-group">
          <label htmlFor="auditUserId">
            User ID
          </label>

          <input
            id="auditUserId"
            type="text"
            inputMode="numeric"
            value={auditUserId}
            onChange={(event) => {
              setAuditUserId(
                event.target.value
              );
              setPage(1);
            }}
            placeholder="24"
          />
        </div>

        <div className="form-group">
          <label htmlFor="action">
            Action
          </label>

          <input
            id="action"
            type="text"
            value={action}
            onChange={(event) => {
              setAction(event.target.value);
              setPage(1);
            }}
            placeholder="Decision Updated"
          />
        </div>

        <div className="form-group">
          <label htmlFor="entityType">
            Entity Type
          </label>

          <input
            id="entityType"
            type="text"
            value={entityType}
            onChange={(event) => {
              setEntityType(
                event.target.value
              );
              setPage(1);
            }}
            placeholder="Decision"
          />
        </div>

        <div className="form-group">
          <label htmlFor="entityId">
            Entity ID
          </label>

          <input
            id="entityId"
            type="text"
            inputMode="numeric"
            value={entityId}
            onChange={(event) => {
              setEntityId(
                event.target.value
              );
              setPage(1);
            }}
            placeholder="20"
          />
        </div>
      </>
    );
  }

  function renderFilters() {
    return (
      <div className="card">
        <div className="section-header">
          <div>
            <h2>Filters</h2>

            <p>
              Filter the selected report using
              supported backend fields.
            </p>
          </div>
        </div>

        <div className="form-grid">
          {!isAuditReport &&
            reportType ===
              REPORT_TYPES.DECISIONS &&
            renderDecisionFilters()}

          {!isAuditReport &&
            reportType ===
              REPORT_TYPES.APPROVALS &&
            renderApprovalFilters()}

          {!isAuditReport &&
            reportType ===
              REPORT_TYPES.TEAMS &&
            renderTeamFilters()}

          {isAuditReport &&
            renderAuditFilters()}

          <div className="form-group">
            <label htmlFor="startDate">
              Start Date
            </label>

            <input
              id="startDate"
              type="date"
              value={startDate}
              onChange={(event) => {
                setStartDate(
                  event.target.value
                );
                setPage(1);
              }}
            />
          </div>

          <div className="form-group">
            <label htmlFor="endDate">
              End Date
            </label>

            <input
              id="endDate"
              type="date"
              value={endDate}
              onChange={(event) => {
                setEndDate(
                  event.target.value
                );
                setPage(1);
              }}
            />
          </div>

          <div className="form-group">
            <label htmlFor="sortBy">
              Sort By
            </label>

            <select
              id="sortBy"
              value={sortBy}
              onChange={(event) => {
                setSortBy(
                  event.target.value
                );
                setPage(1);
              }}
            >
              {reportType ===
                REPORT_TYPES.DECISIONS && (
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
                </>
              )}

              {reportType ===
                REPORT_TYPES.APPROVALS && (
                <>
                  <option value="assigned_at">
                    Assigned Date
                  </option>

                  <option value="reviewed_at">
                    Reviewed Date
                  </option>

                  <option value="status">
                    Status
                  </option>

                  <option value="id">
                    ID
                  </option>
                </>
              )}

              {reportType ===
                REPORT_TYPES.TEAMS && (
                <>
                  <option value="team">
                    Team
                  </option>

                  <option value="member_count">
                    Members
                  </option>

                  <option value="total_decisions">
                    Total Decisions
                  </option>

                  <option value="approved">
                    Approved
                  </option>

                  <option value="rejected">
                    Rejected
                  </option>
                </>
              )}

              {reportType ===
                REPORT_TYPES.AUDIT && (
                <>
                  <option value="created_at">
                    Created Date
                  </option>

                  <option value="id">
                    ID
                  </option>

                  <option value="action">
                    Action
                  </option>

                  <option value="entity_type">
                    Entity Type
                  </option>

                  <option value="entity_id">
                    Entity ID
                  </option>
                </>
              )}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="order">
              Order
            </label>

            <select
              id="order"
              value={order}
              onChange={(event) => {
                setOrder(
                  event.target.value
                );
                setPage(1);
              }}
            >
              <option value="desc">
                Descending
              </option>

              <option value="asc">
                Ascending
              </option>
            </select>
          </div>
        </div>

        <div className="page-actions">
          <button
            type="button"
            className="button secondary"
            onClick={resetFilters}
          >
            Reset Filters
          </button>

          <button
            type="button"
            className="button secondary"
            onClick={refreshReport}
            disabled={refreshing}
          >
            {refreshing
              ? "Refreshing..."
              : "Refresh"}
          </button>
        </div>
      </div>
    );
  }

  function renderTable() {
    if (loading) {
      return (
        <div className="card">
          <div className="loading-state">
            Loading report...
          </div>
        </div>
      );
    }

    if (rows.length === 0) {
      return (
        <div className="card">
          <div className="empty-state">
            <h2>No Report Data</h2>

            <p>
              No records match the selected
              report and filters.
            </p>
          </div>
        </div>
      );
    }

    return (
      <div className="card">
        <div className="section-header">
          <div>
            <h2>Report Results</h2>

            <p>
              {total} record
              {total !== 1 ? "s" : ""} found
            </p>
          </div>
        </div>

        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                {columns.map((column) => (
                  <th key={column.key}>
                    {column.label}
                  </th>
                ))}

                {reportType ===
                  REPORT_TYPES.DECISIONS && (
                  <th>Actions</th>
                )}
              </tr>
            </thead>

            <tbody>
              {rows.map((row, index) => {
                const rowKey =
                  row?.id ??
                  `${reportType}-${index}`;

                return (
                  <tr key={rowKey}>
                    {columns.map(
                      (column) => (
                        <td
                          key={
                            column.key
                          }
                        >
                          {renderCell(
                            row,
                            column.key
                          )}
                        </td>
                      )
                    )}

                    {reportType ===
                      REPORT_TYPES.DECISIONS && (
                      <td>
                        {row?.id ? (
                          <Link
                            to={`/decisions/${row.id}`}
                            className="button secondary"
                          >
                            View
                          </Link>
                        ) : (
                          "—"
                        )}
                      </td>
                    )}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        <Pagination
          page={page}
          pageSize={pageSize}
          total={total}
          onPageChange={setPage}
        />
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1>Reports</h1>

          <p>
            Generate, filter, review, and export
            decision, approval, team, and audit
            reports.
          </p>
        </div>

        <div className="page-actions">
          <button
            type="button"
            className="button"
            onClick={() =>
              handleExport("pdf")
            }
            disabled={
              Boolean(exporting) ||
              loading
            }
          >
            {exporting ===
            `${reportType}-pdf`
              ? "Exporting PDF..."
              : "Export PDF"}
          </button>

          <button
            type="button"
            className="button"
            onClick={() =>
              handleExport("excel")
            }
            disabled={
              Boolean(exporting) ||
              loading
            }
          >
            {exporting ===
            `${reportType}-excel`
              ? "Exporting Excel..."
              : "Export Excel"}
          </button>
        </div>
      </div>

      <div className="card">
        <div className="report-tabs">
          <button
            type="button"
            className={
              reportType ===
              REPORT_TYPES.DECISIONS
                ? "button"
                : "button secondary"
            }
            onClick={() =>
              changeReportType(
                REPORT_TYPES.DECISIONS
              )
            }
          >
            Decision Reports
          </button>

          <button
            type="button"
            className={
              reportType ===
              REPORT_TYPES.APPROVALS
                ? "button"
                : "button secondary"
            }
            onClick={() =>
              changeReportType(
                REPORT_TYPES.APPROVALS
              )
            }
          >
            Approval Reports
          </button>

          <button
            type="button"
            className={
              reportType ===
              REPORT_TYPES.TEAMS
                ? "button"
                : "button secondary"
            }
            onClick={() =>
              changeReportType(
                REPORT_TYPES.TEAMS
              )
            }
          >
            Team Reports
          </button>

          {!isAuditReport && (
            <button
              type="button"
              className={
                reportType ===
                REPORT_TYPES.AUDIT
                  ? "button"
                  : "button secondary"
              }
              onClick={() =>
                changeReportType(
                  REPORT_TYPES.AUDIT
                )
              }
            >
              Audit Reports
            </button>
          )}

          {isAuditReport && (
            <button
              type="button"
              className="button"
            >
              Audit Reports
            </button>
          )}
        </div>
      </div>

      {errorMessage && (
        <div className="card">
          <div className="error-state">
            <h2>
              Unable to load report
            </h2>

            <p>{errorMessage}</p>

            <button
              type="button"
              className="button"
              onClick={loadReport}
            >
              Try Again
            </button>
          </div>
        </div>
      )}

      {renderFilters()}

      {renderTable()}
    </div>
  );
}