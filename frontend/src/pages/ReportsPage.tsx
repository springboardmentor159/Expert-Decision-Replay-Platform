import { useCallback, useEffect, useMemo, useState } from "react";
import {
  BarChart3,
  CalendarDays,
  Download,
  FileSpreadsheet,
  FileText,
  Filter,
  RefreshCw,
} from "lucide-react";

import { useAuth } from "../auth/AuthContext";
import Alert from "../components/Alert";
import Button from "../components/Button";
import {
  downloadReport,
  getReport,
  type ReportFilters,
  type ReportResponse,
  type ReportType,
} from "../services/reportService";
import "./ReportsPage.css";

const REPORT_LABELS: Record<ReportType, string> = {
  decisions: "Decision Report",
  approvals: "Approval Report",
  teams: "Team Report",
  audit: "Audit Report",
};

const REPORT_TYPES: ReportType[] = [
  "decisions",
  "approvals",
  "teams",
  "audit",
];

function formatValue(value: unknown): string {
  if (value === null || value === undefined || value === "") {
    return "—";
  }

  if (typeof value === "object") {
    return JSON.stringify(value);
  }

  return String(value);
}

function formatColumnLabel(value: string): string {
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

function formatReportCell(value: unknown): string {
  if (value === null || value === undefined || value === "") {
    return "—";
  }

  if (typeof value === "string") {
    const looksLikeDate =
      value.includes("T") &&
      !Number.isNaN(Date.parse(value));

    if (looksLikeDate) {
      return new Date(value).toLocaleString();
    }
  }

  return formatValue(value);
}

function getErrorMessage(error: unknown): string {
  const status = (
    error as {
      response?: {
        status?: number;
      };
    }
  )?.response?.status;

  if (status === 401) {
    return "Your session has expired. Please sign in again.";
  }

  if (status === 403) {
    return "You do not have permission to access this report.";
  }

  if (status === 422) {
    return "One or more report filters are invalid.";
  }

  if (status === 404) {
    return "The requested report was not found.";
  }

  if (status && status >= 500) {
    return "The server is temporarily unavailable. Please try again.";
  }

  return "Unable to load the report. Please try again.";
}

export default function ReportsPage() {
  const { user } = useAuth();

  const normalizedRole = String(user?.role ?? "").toLowerCase();
  const isAdministrator = normalizedRole === "administrator";

  const availableReportTypes = useMemo<ReportType[]>(
    () =>
      REPORT_TYPES.filter(
        (type) => type !== "audit" || isAdministrator,
      ),
    [isAdministrator],
  );

  const [reportType, setReportType] =
    useState<ReportType>("decisions");

  const [report, setReport] =
    useState<ReportResponse | null>(null);

  const [status, setStatus] = useState("");
  const [category, setCategory] = useState("");
  const [approvalStatus, setApprovalStatus] = useState("");
  const [tags, setTags] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");

  const [isLoading, setIsLoading] = useState(true);

  const [isDownloading, setIsDownloading] = useState<
    "pdf" | "excel" | null
  >(null);

  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    if (!availableReportTypes.includes(reportType)) {
      setReportType("decisions");
    }
  }, [availableReportTypes, reportType]);

  const filters = useMemo<ReportFilters>(() => {
    const base: ReportFilters = {
      page: 1,
      page_size: 20,
      date_from: dateFrom
        ? `${dateFrom}T00:00:00`
        : undefined,
      date_to: dateTo
        ? `${dateTo}T23:59:59`
        : undefined,
    };

    if (reportType === "decisions") {
      base.status = status || undefined;
      base.category = category || undefined;
      base.tags = tags || undefined;
      base.sort_by = "created_date";
      base.sort_order = "desc";
    }

    if (reportType === "approvals") {
      base.approval_status =
        approvalStatus || undefined;
      base.sort_by = "approval_date";
      base.sort_order = "desc";
    }

    if (reportType === "teams") {
      base.status = status || undefined;
      base.category = category || undefined;
      base.sort_by = "team_name";
      base.sort_order = "asc";
    }

    if (reportType === "audit") {
      base.sort_by = "created_date";
      base.sort_order = "desc";
    }

    return base;
  }, [
    reportType,
    status,
    category,
    approvalStatus,
    tags,
    dateFrom,
    dateTo,
  ]);

  const loadReport = useCallback(async () => {
    if (reportType === "audit" && !isAdministrator) {
      setReport(null);
      setErrorMessage(
        "You do not have permission to access this report.",
      );
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setErrorMessage("");

    try {
      const data = await getReport(
        reportType,
        filters,
      );

      setReport(data);
    } catch (error: unknown) {
      setReport(null);
      setErrorMessage(getErrorMessage(error));
    } finally {
      setIsLoading(false);
    }
  }, [
    reportType,
    filters,
    isAdministrator,
  ]);

  useEffect(() => {
    void loadReport();
  }, [loadReport]);

  function clearFilters() {
    setStatus("");
    setCategory("");
    setApprovalStatus("");
    setTags("");
    setDateFrom("");
    setDateTo("");
  }

  function handleReportTypeChange(type: ReportType) {
    if (type === "audit" && !isAdministrator) {
      return;
    }

    setReportType(type);
    setReport(null);
    setErrorMessage("");
    clearFilters();
  }

  async function handleDownload(
    format: "pdf" | "excel",
  ) {
    if (reportType === "audit" && !isAdministrator) {
      setErrorMessage(
        "You do not have permission to export this report.",
      );
      return;
    }

    setIsDownloading(format);
    setErrorMessage("");

    try {
      const blob = await downloadReport(
        reportType,
        format,
        filters,
      );

      const url = window.URL.createObjectURL(blob);
      const anchor = document.createElement("a");

      anchor.href = url;
      anchor.download = `${reportType}_report.${
        format === "pdf" ? "pdf" : "xlsx"
      }`;

      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();

      window.URL.revokeObjectURL(url);
    } catch (error: unknown) {
      setErrorMessage(
        `Unable to export the ${format.toUpperCase()} report.`,
      );
    } finally {
      setIsDownloading(null);
    }
  }

  const reportRows = useMemo(() => {
    if (!report) {
      return [];
    }

    const possibleRows = [
      report.data,
      report.rows,
      report.results,
    ];

    for (const value of possibleRows) {
      if (Array.isArray(value)) {
        return value as Record<string, unknown>[];
      }
    }

    return [];
  }, [report]);

  const summary = useMemo(() => {
    if (!report) {
      return [];
    }

    const source =
      report.summary ??
      report.stats ??
      report.statistics;

    if (!source || typeof source !== "object") {
      return [];
    }

    return Object.entries(
      source as Record<string, unknown>,
    );
  }, [report]);

  return (
    <div className="reports-page">
      <header className="reports-header">
        <div>
          <div className="reports-kicker">
            REPORTING & ANALYTICS
          </div>

          <h1>Reports</h1>

          <p>
            Generate, filter, review, and export platform
            reports.
          </p>
        </div>

        <div className="reports-role">
          {user?.role ?? "User"}
        </div>
      </header>

      {errorMessage && (
        <div className="reports-alert">
          <Alert variant="error">
            {errorMessage}
          </Alert>
        </div>
      )}

      <section className="reports-control-card">
        <div className="reports-control-heading">
          <div className="reports-control-icon">
            <BarChart3
              size={18}
              aria-hidden="true"
            />
          </div>

          <div>
            <h2>Report configuration</h2>
            <p>
              Select a report and apply filters before
              exporting.
            </p>
          </div>
        </div>

        <div className="reports-type-grid">
          {availableReportTypes.map((type) => (
            <button
              type="button"
              key={type}
              className={`reports-type-button ${
                reportType === type
                  ? "reports-type-active"
                  : ""
              }`}
              aria-pressed={reportType === type}
              onClick={() =>
                handleReportTypeChange(type)
              }
            >
              {type === "decisions" && (
                <FileText
                  size={17}
                  aria-hidden="true"
                />
              )}

              {type === "approvals" && (
                <FileText
                  size={17}
                  aria-hidden="true"
                />
              )}

              {type === "teams" && (
                <BarChart3
                  size={17}
                  aria-hidden="true"
                />
              )}

              {type === "audit" && (
                <Filter
                  size={17}
                  aria-hidden="true"
                />
              )}

              <span>{REPORT_LABELS[type]}</span>
            </button>
          ))}
        </div>

        <div className="reports-divider" />

        <div className="reports-filters-heading">
          <Filter size={14} aria-hidden="true" />
          Filters
        </div>

        <div className="reports-filters">
          {(reportType === "decisions" ||
            reportType === "teams") && (
            <>
              <label>
                <span>Category</span>
                <input
                  value={category}
                  onChange={(event) =>
                    setCategory(event.target.value)
                  }
                  placeholder="Category"
                />
              </label>

              <label>
                <span>Status</span>
                <select
                  value={status}
                  onChange={(event) =>
                    setStatus(event.target.value)
                  }
                >
                  <option value="">
                    All statuses
                  </option>
                  <option value="Draft">Draft</option>
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
              </label>
            </>
          )}

          {reportType === "decisions" && (
            <label>
              <span>Tags</span>
              <input
                value={tags}
                onChange={(event) =>
                  setTags(event.target.value)
                }
                placeholder="Tags"
              />
            </label>
          )}

          {reportType === "approvals" && (
            <label>
              <span>Approval status</span>
              <select
                value={approvalStatus}
                onChange={(event) =>
                  setApprovalStatus(event.target.value)
                }
              >
                <option value="">
                  All statuses
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
            </label>
          )}

          <label>
            <span>From</span>
            <div className="reports-date-input">
              <CalendarDays
                size={14}
                aria-hidden="true"
              />

              <input
                type="date"
                value={dateFrom}
                onChange={(event) =>
                  setDateFrom(event.target.value)
                }
              />
            </div>
          </label>

          <label>
            <span>To</span>
            <div className="reports-date-input">
              <CalendarDays
                size={14}
                aria-hidden="true"
              />

              <input
                type="date"
                value={dateTo}
                onChange={(event) =>
                  setDateTo(event.target.value)
                }
              />
            </div>
          </label>

          <Button
            variant="secondary"
            onClick={clearFilters}
          >
            Clear
          </Button>
        </div>
      </section>

      <section className="reports-results-card">
        <div className="reports-results-header">
          <div>
            <h2>{REPORT_LABELS[reportType]}</h2>

            <p>
              Data returned from the FastAPI reporting
              service.
            </p>
          </div>

          <button
            type="button"
            className="reports-refresh"
            onClick={() => void loadReport()}
            disabled={isLoading}
          >
            <RefreshCw
              size={14}
              className={
                isLoading
                  ? "reports-spin"
                  : undefined
              }
              aria-hidden="true"
            />

            Refresh
          </button>
        </div>

        <div className="reports-export-bar">
          <span>Export current report</span>

          <div>
            <button
              type="button"
              onClick={() =>
                void handleDownload("pdf")
              }
              disabled={isDownloading !== null}
              aria-label={`Export ${REPORT_LABELS[reportType]} as PDF`}
            >
              <FileText
                size={14}
                aria-hidden="true"
              />

              {isDownloading === "pdf"
                ? "Exporting..."
                : "PDF"}
            </button>

            <button
              type="button"
              onClick={() =>
                void handleDownload("excel")
              }
              disabled={isDownloading !== null}
              aria-label={`Export ${REPORT_LABELS[reportType]} as Excel`}
            >
              <FileSpreadsheet
                size={14}
                aria-hidden="true"
              />

              {isDownloading === "excel"
                ? "Exporting..."
                : "Excel"}
            </button>
          </div>
        </div>

        {isLoading ? (
          <div
            className="reports-loading"
            role="status"
            aria-live="polite"
          >
            <div className="reports-spinner" />
            Loading report...
          </div>
        ) : (
          <>
            {summary.length > 0 && (
              <div className="reports-summary">
                {summary.map(([key, value]) => (
                  <div
                    className="reports-summary-item"
                    key={key}
                  >
                    <span>
                      {formatColumnLabel(key)}
                    </span>

                    <strong>
                      {formatReportCell(value)}
                    </strong>
                  </div>
                ))}
              </div>
            )}

            {reportRows.length === 0 ? (
              <div className="reports-empty">
                <Download
                  size={24}
                  aria-hidden="true"
                />

                <h3>No report rows</h3>

                <p>
                  No records were returned for the
                  selected filters.
                </p>
              </div>
            ) : (
              <div className="reports-table-wrapper">
                <table className="reports-table">
                  <thead>
                    <tr>
                      {Object.keys(
                        reportRows[0],
                      ).map((key) => (
                        <th key={key}>
                          {formatColumnLabel(key)}
                        </th>
                      ))}
                    </tr>
                  </thead>

                  <tbody>
                    {reportRows.map(
                      (row, rowIndex) => (
                        <tr key={rowIndex}>
                          {Object.keys(
                            reportRows[0],
                          ).map((key) => (
                            <td key={key}>
                              {formatReportCell(
                                row[key],
                              )}
                            </td>
                          ))}
                        </tr>
                      ),
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </>
        )}
      </section>
    </div>
  );
}