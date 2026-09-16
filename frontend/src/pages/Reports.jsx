import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
  BarChart3,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  ClipboardList,
  Download,
  FileSpreadsheet,
  FileText,
  Filter,
  History,
  RefreshCw,
  RotateCcw,
  Search,
  ShieldCheck,
  Users,
} from "lucide-react";

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
      .map(
        ([key, item]) =>
          `${key}: ${formatValue(item)}`
      )
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
      return "report-status report-status-approved";

    case "Rejected":
      return "report-status report-status-rejected";

    case "Pending":
      return "report-status report-status-pending";

    case "Under Review":
      return "report-status report-status-review";

    case "Archived":
      return "report-status report-status-archived";

    case "Draft":
    default:
      return "report-status report-status-draft";
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
    { key: "id", label: "ID" },
    { key: "title", label: "Title" },
    { key: "category", label: "Category" },
    { key: "status", label: "Status" },
    { key: "created_by", label: "Created By" },
    { key: "created_at", label: "Created" },
    { key: "updated_at", label: "Updated" },
  ];
}


function getApprovalColumns() {
  return [
    { key: "id", label: "ID" },
    { key: "decision_id", label: "Decision" },
    { key: "assigned_to", label: "Reviewer" },
    { key: "assigned_by", label: "Assigned By" },
    { key: "assigned_role", label: "Approval Level" },
    { key: "status", label: "Status" },
    { key: "comments", label: "Comments" },
    { key: "assigned_at", label: "Assigned" },
    { key: "reviewed_at", label: "Reviewed" },
  ];
}


function getTeamColumns() {
  return [
    { key: "team", label: "Team" },
    { key: "member_count", label: "Members" },
    { key: "total_decisions", label: "Total Decisions" },
    { key: "approved", label: "Approved" },
    { key: "rejected", label: "Rejected" },
  ];
}


function getAuditColumns() {
  return [
    { key: "id", label: "ID" },
    { key: "action", label: "Action" },
    { key: "entity_type", label: "Entity" },
    { key: "entity_id", label: "Entity ID" },
    { key: "user_id", label: "User" },
    { key: "description", label: "Description" },
    { key: "created_at", label: "Date" },
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

  if (
    key === "created_by" ||
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
    <div className="report-pagination">

      <button
        type="button"
        className="pagination-button"
        disabled={page <= 1}
        onClick={() =>
          onPageChange(page - 1)
        }
      >
        <ChevronLeft size={16} />
        Previous
      </button>

      <div className="pagination-info">
        Page <strong>{page}</strong> of{" "}
        <strong>{totalPages}</strong>
      </div>

      <button
        type="button"
        className="pagination-button"
        disabled={page >= totalPages}
        onClick={() =>
          onPageChange(page + 1)
        }
      >
        Next
        <ChevronRight size={16} />
      </button>

    </div>
  );
}


export default function Reports() {
  const [reportType, setReportType] =
    useState(
      REPORT_TYPES.DECISIONS
    );

  const [rows, setRows] = useState([]);
  const [total, setTotal] = useState(0);

  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);

  const [loading, setLoading] =
    useState(true);

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


  const columns = useMemo(() => {
    if (
      reportType ===
      REPORT_TYPES.APPROVALS
    ) {
      return getApprovalColumns();
    }

    if (
      reportType ===
      REPORT_TYPES.TEAMS
    ) {
      return getTeamColumns();
    }

    if (
      reportType ===
      REPORT_TYPES.AUDIT
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
      setErrorMessage(
        validationError
      );
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
        response =
          await getDecisionReport({
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
        response =
          await getApprovalReport({
            status,
            reviewer:
              reviewer === ""
                ? ""
                : Number(reviewer),
            decision:
              decisionId === ""
                ? ""
                : Number(decisionId),
            approval_level:
              approvalLevel,
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
        response =
          await getTeamReport({
            team,
            start_date: startDate,
            end_date: endDate,
            decision_status:
              status,
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
        response =
          await getAuditReport({
            user_id:
              auditUserId === ""
                ? ""
                : Number(auditUserId),
            action,
            entity_type:
              entityType,
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
      reportType ===
        REPORT_TYPES.TEAMS
        ? "team"
        : reportType ===
          REPORT_TYPES.APPROVALS
        ? "assigned_at"
        : "created_at"
    );

    setOrder(
      reportType ===
        REPORT_TYPES.TEAMS
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
        approval_level:
          approvalLevel,
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
        decision_status:
          status,
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
      entity_type:
        entityType,
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
      setErrorMessage(
        validationError
      );
      return;
    }

    const exportKey =
      `${reportType}-${format}`;

    try {
      setExporting(exportKey);
      setErrorMessage("");

      const params =
        getExportParams();

      let response;

      if (
        reportType ===
        REPORT_TYPES.DECISIONS
      ) {
        response =
          format === "pdf"
            ? await exportDecisionReportPdf(
                params
              )
            : await exportDecisionReportExcel(
                params
              );
      }

      if (
        reportType ===
        REPORT_TYPES.APPROVALS
      ) {
        response =
          format === "pdf"
            ? await exportApprovalReportPdf(
                params
              )
            : await exportApprovalReportExcel(
                params
              );
      }

      if (
        reportType ===
        REPORT_TYPES.TEAMS
      ) {
        response =
          format === "pdf"
            ? await exportTeamReportPdf(
                params
              )
            : await exportTeamReportExcel(
                params
              );
      }

      if (
        reportType ===
        REPORT_TYPES.AUDIT
      ) {
        response =
          format === "pdf"
            ? await exportAuditReportPdf(
                params
              )
            : await exportAuditReportExcel(
                params
              );
      }

      const extension =
        format === "pdf"
          ? "pdf"
          : "xlsx";

      downloadReportFile(
        response,
        `${reportType}_report.${extension}`
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
        <ReportField
          label="Category"
          value={category}
          onChange={(value) => {
            setCategory(value);
            setPage(1);
          }}
          placeholder="Technology"
        />

        <ReportField
          label="Status"
          type="select"
          value={status}
          onChange={(value) => {
            setStatus(value);
            setPage(1);
          }}
          options={DECISION_STATUSES}
          emptyLabel="All statuses"
        />

        <ReportField
          label="Created By User ID"
          value={createdBy}
          onChange={(value) => {
            setCreatedBy(value);
            setPage(1);
          }}
          placeholder="24"
          numeric
        />

        <ReportField
          label="Tag"
          value={tag}
          onChange={(value) => {
            setTag(value);
            setPage(1);
          }}
          placeholder="security"
        />
      </>
    );
  }


  function renderApprovalFilters() {
    return (
      <>
        <ReportField
          label="Status"
          type="select"
          value={status}
          onChange={(value) => {
            setStatus(value);
            setPage(1);
          }}
          options={APPROVAL_STATUSES}
          emptyLabel="All statuses"
        />

        <ReportField
          label="Reviewer User ID"
          value={reviewer}
          onChange={(value) => {
            setReviewer(value);
            setPage(1);
          }}
          placeholder="20"
          numeric
        />

        <ReportField
          label="Decision ID"
          value={decisionId}
          onChange={(value) => {
            setDecisionId(value);
            setPage(1);
          }}
          placeholder="20"
          numeric
        />

        <ReportField
          label="Approval Level"
          type="select"
          value={approvalLevel}
          onChange={(value) => {
            setApprovalLevel(value);
            setPage(1);
          }}
          options={APPROVAL_LEVELS}
          emptyLabel="All levels"
        />
      </>
    );
  }


  function renderTeamFilters() {
    return (
      <>
        <ReportField
          label="Team / Department"
          value={team}
          onChange={(value) => {
            setTeam(value);
            setPage(1);
          }}
          placeholder="Engineering"
        />

        <ReportField
          label="Category"
          value={category}
          onChange={(value) => {
            setCategory(value);
            setPage(1);
          }}
          placeholder="Technology"
        />

        <ReportField
          label="Decision Status"
          type="select"
          value={status}
          onChange={(value) => {
            setStatus(value);
            setPage(1);
          }}
          options={DECISION_STATUSES}
          emptyLabel="All statuses"
        />
      </>
    );
  }


  function renderAuditFilters() {
    return (
      <>
        <ReportField
          label="User ID"
          value={auditUserId}
          onChange={(value) => {
            setAuditUserId(value);
            setPage(1);
          }}
          placeholder="24"
          numeric
        />

        <ReportField
          label="Action"
          value={action}
          onChange={(value) => {
            setAction(value);
            setPage(1);
          }}
          placeholder="Decision Updated"
        />

        <ReportField
          label="Entity Type"
          value={entityType}
          onChange={(value) => {
            setEntityType(value);
            setPage(1);
          }}
          placeholder="Decision"
        />

        <ReportField
          label="Entity ID"
          value={entityId}
          onChange={(value) => {
            setEntityId(value);
            setPage(1);
          }}
          placeholder="20"
          numeric
        />
      </>
    );
  }


  function renderFilters() {
    return (
      <div className="report-card">

        <div className="report-section-header">

          <div className="report-section-title">

            <div className="report-icon">
              <Filter size={19} />
            </div>

            <div>
              <h2>Filters</h2>
              <p>
                Narrow the report using
                supported fields.
              </p>
            </div>

          </div>

        </div>


        <div className="report-form-grid">

          {reportType ===
            REPORT_TYPES.DECISIONS &&
            renderDecisionFilters()}

          {reportType ===
            REPORT_TYPES.APPROVALS &&
            renderApprovalFilters()}

          {reportType ===
            REPORT_TYPES.TEAMS &&
            renderTeamFilters()}

          {reportType ===
            REPORT_TYPES.AUDIT &&
            renderAuditFilters()}


          <ReportField
            label="Start Date"
            type="date"
            value={startDate}
            onChange={(value) => {
              setStartDate(value);
              setPage(1);
            }}
          />


          <ReportField
            label="End Date"
            type="date"
            value={endDate}
            onChange={(value) => {
              setEndDate(value);
              setPage(1);
            }}
          />


          <ReportField
            label="Sort By"
            type="select"
            value={sortBy}
            onChange={(value) => {
              setSortBy(value);
              setPage(1);
            }}
            options={
              reportType ===
              REPORT_TYPES.DECISIONS
                ? [
                    ["created_at", "Created Date"],
                    ["updated_at", "Updated Date"],
                    ["title", "Title"],
                  ]
                : reportType ===
                  REPORT_TYPES.APPROVALS
                ? [
                    ["assigned_at", "Assigned Date"],
                    ["reviewed_at", "Reviewed Date"],
                    ["status", "Status"],
                    ["id", "ID"],
                  ]
                : reportType ===
                  REPORT_TYPES.TEAMS
                ? [
                    ["team", "Team"],
                    ["member_count", "Members"],
                    ["total_decisions", "Total Decisions"],
                    ["approved", "Approved"],
                    ["rejected", "Rejected"],
                  ]
                : [
                    ["created_at", "Created Date"],
                    ["id", "ID"],
                    ["action", "Action"],
                    ["entity_type", "Entity Type"],
                    ["entity_id", "Entity ID"],
                  ]
            }
          />


          <ReportField
            label="Order"
            type="select"
            value={order}
            onChange={(value) => {
              setOrder(value);
              setPage(1);
            }}
            options={[
              ["desc", "Descending"],
              ["asc", "Ascending"],
            ]}
          />

        </div>


        <div className="report-filter-actions">

          <button
            type="button"
            className="report-button secondary"
            onClick={resetFilters}
          >
            <RotateCcw size={16} />
            Reset Filters
          </button>


          <button
            type="button"
            className="report-button secondary"
            onClick={refreshReport}
            disabled={refreshing}
          >
            <RefreshCw
              size={16}
              className={
                refreshing
                  ? "spin"
                  : ""
              }
            />

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
        <div className="report-card">
          <div className="report-loading">
            <RefreshCw
              size={22}
              className="spin"
            />
            Loading report...
          </div>
        </div>
      );
    }


    if (rows.length === 0) {
      return (
        <div className="report-card">

          <div className="report-empty">

            <div className="empty-report-icon">
              <BarChart3 size={28} />
            </div>

            <h2>
              No Report Data
            </h2>

            <p>
              No records match the selected
              report and filters.
            </p>

          </div>

        </div>
      );
    }


    return (
      <div className="report-card">

        <div className="report-section-header">

          <div className="report-section-title">

            <div className="report-icon">
              <ClipboardList size={19} />
            </div>

            <div>
              <h2>
                Report Results
              </h2>

              <p>
                {total} record
                {total !== 1
                  ? "s"
                  : ""}{" "}
                found
              </p>
            </div>

          </div>

        </div>


        <div className="report-table-wrapper">

          <table className="report-table">

            <thead>
              <tr>

                {columns.map(
                  (column) => (
                    <th key={column.key}>
                      {column.label}
                    </th>
                  )
                )}

                {reportType ===
                  REPORT_TYPES.DECISIONS && (
                  <th>
                    Actions
                  </th>
                )}

              </tr>
            </thead>


            <tbody>

              {rows.map(
                (row, index) => {

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
                              className="view-report-button"
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
                }
              )}

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
    <div className="page-container reports-page">

      {/* Header */}

      <div className="page-header reports-header">

        <div>

          <div className="eyebrow">
            ANALYTICS & REPORTING
          </div>

          <h1>
            Reports
          </h1>

          <p>
            Generate, filter, review, and export
            decision, approval, team, and audit
            reports.
          </p>

        </div>


        <div className="export-actions">

          <button
            type="button"
            className="export-button pdf-button"
            onClick={() =>
              handleExport("pdf")
            }
            disabled={
              Boolean(exporting) ||
              loading
            }
          >
            <FileText size={17} />

            {exporting ===
            `${reportType}-pdf`
              ? "Exporting..."
              : "Export PDF"}
          </button>


          <button
            type="button"
            className="export-button excel-button"
            onClick={() =>
              handleExport("excel")
            }
            disabled={
              Boolean(exporting) ||
              loading
            }
          >
            <FileSpreadsheet size={17} />

            {exporting ===
            `${reportType}-excel`
              ? "Exporting..."
              : "Export Excel"}
          </button>

        </div>

      </div>


      {/* Report Types */}

      <div className="report-type-card">

        <div className="report-tabs">

          <ReportTab
            active={
              reportType ===
              REPORT_TYPES.DECISIONS
            }
            icon={<ClipboardList size={17} />}
            label="Decision Reports"
            onClick={() =>
              changeReportType(
                REPORT_TYPES.DECISIONS
              )
            }
          />


          <ReportTab
            active={
              reportType ===
              REPORT_TYPES.APPROVALS
            }
            icon={<CheckCircle2 size={17} />}
            label="Approval Reports"
            onClick={() =>
              changeReportType(
                REPORT_TYPES.APPROVALS
              )
            }
          />


          <ReportTab
            active={
              reportType ===
              REPORT_TYPES.TEAMS
            }
            icon={<Users size={17} />}
            label="Team Reports"
            onClick={() =>
              changeReportType(
                REPORT_TYPES.TEAMS
              )
            }
          />


          <ReportTab
            active={
              reportType ===
              REPORT_TYPES.AUDIT
            }
            icon={<History size={17} />}
            label="Audit Reports"
            onClick={() =>
              changeReportType(
                REPORT_TYPES.AUDIT
              )
            }
          />

        </div>

      </div>


      {/* Error */}

      {errorMessage && (
        <div className="report-error">

          <ShieldCheck size={19} />

          <div>
            <strong>
              Unable to load report
            </strong>

            <p>
              {errorMessage}
            </p>
          </div>

          <button
            type="button"
            className="report-button secondary"
            onClick={loadReport}
          >
            Try Again
          </button>

        </div>
      )}


      {renderFilters()}

      {renderTable()}


      <style>{`

        .reports-page {
          padding-bottom: 40px;
        }


        .reports-header {
          align-items: flex-end;
        }


        .eyebrow {
          color: #2563eb;
          font-size: 11px;
          font-weight: 700;
          letter-spacing: 0.12em;
          margin-bottom: 6px;
        }


        /* Export buttons */

        .export-actions {
          display: flex;
          gap: 9px;
          flex-wrap: wrap;
        }


        .export-button {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: 7px;
          min-height: 40px;
          padding: 0 14px;
          border-radius: 9px;
          font-size: 12px;
          font-weight: 700;
          cursor: pointer;
          transition: 0.15s ease;
        }


        .pdf-button {
          background: #ffffff;
          color: #dc2626;
          border: 1px solid #fecaca;
        }


        .pdf-button:hover {
          background: #fef2f2;
        }


        .excel-button {
          background: #ffffff;
          color: #15803d;
          border: 1px solid #bbf7d0;
        }


        .excel-button:hover {
          background: #f0fdf4;
        }


        .export-button:disabled {
          opacity: 0.55;
          cursor: not-allowed;
        }


        /* Report type tabs */

        .report-type-card {
          background: #ffffff;
          border: 1px solid #e5e7eb;
          border-radius: 15px;
          padding: 8px;
          margin-bottom: 16px;
          box-shadow:
            0 2px 8px
            rgba(15, 23, 42, 0.04);
        }


        .report-tabs {
          display: flex;
          gap: 6px;
          overflow-x: auto;
        }


        .report-tab {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: 7px;
          min-height: 40px;
          padding: 0 14px;
          border: 1px solid transparent;
          border-radius: 9px;
          background: transparent;
          color: #64748b;
          font-size: 12px;
          font-weight: 700;
          white-space: nowrap;
          cursor: pointer;
          transition: 0.15s ease;
        }


        .report-tab:hover {
          background: #f8fafc;
          color: #334155;
        }


        .report-tab.active {
          background: #2563eb;
          color: #ffffff;
          box-shadow:
            0 3px 8px
            rgba(37, 99, 235, 0.20);
        }


        /* Cards */

        .report-card {
          background: #ffffff;
          border: 1px solid #e5e7eb;
          border-radius: 16px;
          margin-bottom: 18px;
          box-shadow:
            0 2px 8px
            rgba(15, 23, 42, 0.04);
          overflow: hidden;
        }


        .report-section-header {
          padding: 21px 23px 17px;
        }


        .report-section-title {
          display: flex;
          align-items: flex-start;
          gap: 12px;
        }


        .report-icon {
          width: 40px;
          height: 40px;
          flex-shrink: 0;
          border-radius: 10px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: #eff6ff;
          color: #2563eb;
        }


        .report-section-title h2 {
          margin: 0 0 4px;
          color: #0f172a;
          font-size: 19px;
        }


        .report-section-title p {
          margin: 0;
          color: #64748b;
          font-size: 12px;
        }


        /* Filters */

        .report-form-grid {
          display: grid;
          grid-template-columns:
            repeat(4, minmax(0, 1fr));
          gap: 16px;
          padding: 0 23px 20px;
        }


        .report-field {
          display: flex;
          flex-direction: column;
          gap: 7px;
        }


        .report-field label {
          color: #334155;
          font-size: 12px;
          font-weight: 700;
        }


        .report-field input,
        .report-field select {
          width: 100%;
          height: 42px;
          box-sizing: border-box;
          padding: 0 11px;
          border: 1px solid #dbe3ef;
          border-radius: 9px;
          outline: none;
          background: #ffffff;
          color: #0f172a;
          font-size: 13px;
        }


        .report-field input::placeholder {
          color: #94a3b8;
        }


        .report-field input:focus,
        .report-field select:focus {
          border-color: #2563eb;
          box-shadow:
            0 0 0 3px
            rgba(37, 99, 235, 0.10);
        }


        .report-filter-actions {
          display: flex;
          justify-content: flex-end;
          gap: 9px;
          padding: 15px 23px;
          border-top: 1px solid #eef2f7;
          background: #fafcff;
        }


        .report-button {
          min-height: 36px;
          padding: 0 12px;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: 7px;
          border-radius: 8px;
          border: 1px solid #dbe3ef;
          background: #ffffff;
          color: #334155;
          font-size: 12px;
          font-weight: 700;
          cursor: pointer;
          transition: 0.15s ease;
        }


        .report-button:hover {
          background: #f8fafc;
        }


        .report-button:disabled {
          opacity: 0.55;
          cursor: not-allowed;
        }


        /* Error */

        .report-error {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 18px;
          padding: 14px 16px;
          border: 1px solid #fecaca;
          border-radius: 12px;
          background: #fef2f2;
          color: #b91c1c;
        }


        .report-error > div {
          flex: 1;
        }


        .report-error strong {
          display: block;
          margin-bottom: 3px;
          font-size: 13px;
        }


        .report-error p {
          margin: 0;
          font-size: 12px;
        }


        /* Table */

        .report-table-wrapper {
          width: 100%;
          overflow-x: auto;
          border-top: 1px solid #eef2f7;
        }


        .report-table {
          width: 100%;
          min-width: 1050px;
          border-collapse: collapse;
        }


        .report-table th {
          padding: 13px 15px;
          background: #f8fafc;
          border-bottom: 1px solid #e2e8f0;
          color: #64748b;
          font-size: 10px;
          font-weight: 800;
          text-align: left;
          white-space: nowrap;
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }


        .report-table td {
          padding: 14px 15px;
          border-bottom: 1px solid #eef2f7;
          color: #334155;
          font-size: 12px;
          vertical-align: middle;
          white-space: nowrap;
        }


        .report-table tbody tr:hover {
          background: #fafcff;
        }


        .report-table tbody tr:last-child td {
          border-bottom: 0;
        }


        .report-status {
          display: inline-flex;
          align-items: center;
          padding: 5px 9px;
          border-radius: 20px;
          font-size: 10px;
          font-weight: 700;
        }


        .report-status-approved {
          background: #f0fdf4;
          color: #15803d;
        }


        .report-status-rejected {
          background: #fef2f2;
          color: #dc2626;
        }


        .report-status-pending {
          background: #fff7ed;
          color: #c2410c;
        }


        .report-status-review {
          background: #eff6ff;
          color: #2563eb;
        }


        .report-status-archived {
          background: #f1f5f9;
          color: #475569;
        }


        .report-status-draft {
          background: #f8fafc;
          color: #64748b;
        }


        .view-report-button {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          min-height: 32px;
          padding: 0 10px;
          border: 1px solid #bfdbfe;
          border-radius: 8px;
          color: #2563eb;
          background: #ffffff;
          font-size: 11px;
          font-weight: 700;
          text-decoration: none;
        }


        .view-report-button:hover {
          background: #eff6ff;
        }


        /* Pagination */

        .report-pagination {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 16px;
          padding: 17px 20px;
          border-top: 1px solid #eef2f7;
          background: #fafcff;
        }


        .pagination-button {
          min-height: 35px;
          padding: 0 11px;
          display: inline-flex;
          align-items: center;
          gap: 5px;
          border: 1px solid #dbe3ef;
          border-radius: 8px;
          background: #ffffff;
          color: #334155;
          font-size: 12px;
          font-weight: 600;
          cursor: pointer;
        }


        .pagination-button:hover:not(:disabled) {
          background: #eff6ff;
          border-color: #bfdbfe;
          color: #2563eb;
        }


        .pagination-button:disabled {
          opacity: 0.45;
          cursor: not-allowed;
        }


        .pagination-info {
          color: #64748b;
          font-size: 12px;
        }


        .pagination-info strong {
          color: #0f172a;
        }


        /* Loading / Empty */

        .report-loading {
          min-height: 220px;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 10px;
          color: #64748b;
          font-size: 13px;
        }


        .report-empty {
          min-height: 240px;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          text-align: center;
          padding: 30px;
        }


        .empty-report-icon {
          width: 58px;
          height: 58px;
          margin-bottom: 14px;
          border-radius: 15px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: #eff6ff;
          color: #2563eb;
        }


        .report-empty h2 {
          margin: 0 0 6px;
          color: #0f172a;
          font-size: 18px;
        }


        .report-empty p {
          margin: 0;
          color: #64748b;
          font-size: 13px;
        }


        .spin {
          animation: report-spin 1s linear infinite;
        }


        @keyframes report-spin {
          from {
            transform: rotate(0deg);
          }

          to {
            transform: rotate(360deg);
          }
        }


        @media (max-width: 1100px) {

          .report-form-grid {
            grid-template-columns:
              repeat(3, minmax(0, 1fr));
          }

        }


        @media (max-width: 850px) {

          .report-form-grid {
            grid-template-columns:
              repeat(2, minmax(0, 1fr));
          }

          .reports-header {
            align-items: flex-start;
            flex-direction: column;
          }

          .export-actions {
            width: 100%;
          }

          .export-button {
            flex: 1;
          }

        }


        @media (max-width: 600px) {

          .report-form-grid {
            grid-template-columns: 1fr;
          }

          .report-tabs {
            flex-direction: column;
          }

          .report-tab {
            width: 100%;
          }

          .report-filter-actions {
            flex-direction: column;
          }

          .report-filter-actions
          .report-button {
            width: 100%;
          }

          .report-error {
            align-items: flex-start;
            flex-wrap: wrap;
          }

          .report-error
          .report-button {
            width: 100%;
          }

        }

      `}</style>

    </div>
  );
}


/* Report field component */

function ReportField({
  label,
  type = "text",
  value,
  onChange,
  placeholder = "",
  options = [],
  emptyLabel,
  numeric = false,
}) {
  return (
    <div className="report-field">

      <label>
        {label}
      </label>


      {type === "select" ? (
        <select
          value={value}
          onChange={(event) =>
            onChange(
              event.target.value
            )
          }
        >
          {emptyLabel && (
            <option value="">
              {emptyLabel}
            </option>
          )}

          {options.map((option) => {

            const isArray =
              Array.isArray(option);

            const optionValue =
              isArray
                ? option[0]
                : option;

            const optionLabel =
              isArray
                ? option[1]
                : option;

            return (
              <option
                key={optionValue}
                value={optionValue}
              >
                {optionLabel}
              </option>
            );
          })}
        </select>
      ) : (
        <input
          type={type}
          value={value}
          onChange={(event) =>
            onChange(
              event.target.value
            )
          }
          placeholder={placeholder}
          inputMode={
            numeric
              ? "numeric"
              : undefined
          }
        />
      )}

    </div>
  );
}


/* Report tab component */

function ReportTab({
  active,
  icon,
  label,
  onClick,
}) {
  return (
    <button
      type="button"
      className={`report-tab ${
        active ? "active" : ""
      }`}
      onClick={onClick}
    >
      {icon}
      {label}
    </button>
  );
}