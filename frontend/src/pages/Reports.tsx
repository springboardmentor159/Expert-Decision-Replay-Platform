import {
  Activity,
  BarChart3,
  CheckCircle2,
  ClipboardList,
  Clock3,
  Download,
  FileSpreadsheet,
  FileText,
  Filter,
  RefreshCw,
  ShieldCheck,
  Users,
  XCircle,
} from "lucide-react";
import {
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { useAuth } from "../context/AuthContext";

import {
  exportApprovalExcel,
  exportApprovalPdf,
  exportAuditExcel,
  exportAuditPdf,
  exportDecisionExcel,
  exportDecisionPdf,
  exportTeamExcel,
  exportTeamPdf,
  getApprovalReport,
  getAuditReport,
  getDecisionReport,
  getTeamReport,
  type ApprovalReportResponse,
  type AuditReportResponse,
  type DecisionReportResponse,
  type TeamReportResponse,
} from "../services/reports";

import { getApiErrorMessage } from "../utils/errors";

type ReportType =
  | "decisions"
  | "approvals"
  | "teams"
  | "audit";

const PAGE_SIZE = 10;

const REPORT_TABS: {
  id: ReportType;
  label: string;
  description: string;
  icon: typeof ClipboardList;
}[] = [
  {
    id: "decisions",
    label: "Decisions",
    description: "Decision lifecycle and outcomes",
    icon: ClipboardList,
  },
  {
    id: "approvals",
    label: "Approvals",
    description: "Review and approval performance",
    icon: CheckCircle2,
  },
  {
    id: "teams",
    label: "Teams",
    description: "Team decision performance",
    icon: Users,
  },
  {
    id: "audit",
    label: "Audit",
    description: "System activity and compliance",
    icon: ShieldCheck,
  },
];

const STATUS_OPTIONS = [
  "Draft",
  "Under Review",
  "Approved",
  "Rejected",
  "Archived",
];

const AUDIT_ACTIONS = [
  "CREATE",
  "UPDATE",
  "DELETE",
  "APPROVE",
  "REJECT",
  "SUBMIT",
  "LOGIN",
  "LOGOUT",
  "ACCESS",
  "ARCHIVE",
];

function formatDate(value?: string | null) {
  if (!value) return "—";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function statusClass(status?: string) {
  switch (status) {
    case "Approved":
      return "border-emerald-200 bg-emerald-50 text-emerald-700";

    case "Rejected":
      return "border-red-200 bg-red-50 text-red-700";

    case "Under Review":
      return "border-amber-200 bg-amber-50 text-amber-700";

    case "Pending":
      return "border-amber-200 bg-amber-50 text-amber-700";

    case "Draft":
      return "border-slate-200 bg-slate-100 text-slate-700";

    case "Archived":
      return "border-purple-200 bg-purple-50 text-purple-700";

    default:
      return "border-blue-200 bg-blue-50 text-blue-700";
  }
}

function actionClass(action?: string) {
  switch (action?.toUpperCase()) {
    case "CREATE":
      return "border-emerald-200 bg-emerald-50 text-emerald-700";

    case "UPDATE":
      return "border-blue-200 bg-blue-50 text-blue-700";

    case "DELETE":
      return "border-red-200 bg-red-50 text-red-700";

    case "APPROVE":
      return "border-green-200 bg-green-50 text-green-700";

    case "REJECT":
      return "border-orange-200 bg-orange-50 text-orange-700";

    case "LOGIN":
      return "border-purple-200 bg-purple-50 text-purple-700";

    case "LOGOUT":
      return "border-gray-200 bg-gray-50 text-gray-700";

    case "ACCESS":
      return "border-cyan-200 bg-cyan-50 text-cyan-700";

    case "SUBMIT":
      return "border-indigo-200 bg-indigo-50 text-indigo-700";

    case "ARCHIVE":
      return "border-yellow-200 bg-yellow-50 text-yellow-700";

    default:
      return "border-gray-200 bg-gray-50 text-gray-700";
  }
}

function StatCard({
  label,
  value,
  icon,
  helper,
}: {
  label: string;
  value: number | string;
  icon: ReactNode;
  helper?: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <p className="text-sm font-medium text-slate-500">
            {label}
          </p>

          <p className="mt-2 truncate text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
            {value}
          </p>

          {helper && (
            <p className="mt-1 text-xs text-slate-400">
              {helper}
            </p>
          )}
        </div>

        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
          {icon}
        </div>
      </div>
    </div>
  );
}

export default function Reports() {
  const { user } = useAuth();

  const isAdministrator =
    user?.role === "Administrator";

  const [reportType, setReportType] =
    useState<ReportType>("decisions");

  const [decisionReport, setDecisionReport] =
    useState<DecisionReportResponse | null>(null);

  const [approvalReport, setApprovalReport] =
    useState<ApprovalReportResponse | null>(null);

  const [teamReport, setTeamReport] =
    useState<TeamReportResponse | null>(null);

  const [auditReport, setAuditReport] =
    useState<AuditReportResponse | null>(null);

  const [loading, setLoading] = useState(false);

  const [exporting, setExporting] = useState<
    "pdf" | "excel" | null
  >(null);

  const [error, setError] = useState("");

  const [success, setSuccess] = useState("");

  const [category, setCategory] = useState("");

  const [status, setStatus] = useState("");

  const [startDate, setStartDate] = useState("");

  const [endDate, setEndDate] = useState("");

  const [team, setTeam] = useState("");

  const [action, setAction] = useState("");

  const [entityType, setEntityType] = useState("");

  const [page, setPage] = useState(1);

  function getCommonParams(targetPage: number) {
    return {
      page: targetPage,
      page_size: PAGE_SIZE,
      start_date: startDate || undefined,
      end_date: endDate || undefined,
    };
  }

  async function loadReport(targetPage = page) {
    setLoading(true);
    setError("");
    setSuccess("");

    try {
      if (reportType === "decisions") {
        const data = await getDecisionReport({
          ...getCommonParams(targetPage),
          category: category || undefined,
          status: status || undefined,
          sort_by: "created_date",
          sort_order: "desc",
        });

        setDecisionReport(data);
        setPage(data.page ?? targetPage);
      }

      if (reportType === "approvals") {
        const data = await getApprovalReport({
          ...getCommonParams(targetPage),
          status: status || undefined,
          sort_by: "approval_date",
          sort_order: "desc",
        });

        setApprovalReport(data);
        setPage(data.page ?? targetPage);
      }

      if (reportType === "teams") {
        const data = await getTeamReport({
          ...getCommonParams(targetPage),
          team: team || undefined,
          category: category || undefined,
          status: status || undefined,
          sort_by: "team_name",
          sort_order: "asc",
        });

        setTeamReport(data);
        setPage(data.page ?? targetPage);
      }

      if (reportType === "audit") {
        const data = await getAuditReport({
          ...getCommonParams(targetPage),
          action: action || undefined,
          entity_type: entityType || undefined,
          sort_by: "timestamp",
          sort_order: "desc",
        });

        setAuditReport(data);
        setPage(data.page ?? targetPage);
      }
    } catch (err: any) {
      console.error("Failed to load report:", err);

      setError(
        getApiErrorMessage(
          err,
          "Unable to load the report. Please try again.",
        ),
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!isAdministrator) {
      return;
    }

    loadReport(1);
  }, [reportType]);

  function applyFilters() {
    setPage(1);
    loadReport(1);
  }

  function clearFilters() {
    setCategory("");
    setStatus("");
    setStartDate("");
    setEndDate("");
    setTeam("");
    setAction("");
    setEntityType("");
    setPage(1);

    setTimeout(() => {
      loadReport(1);
    }, 0);
  }

  async function handleExport(
    exportType: "pdf" | "excel",
  ) {
    setError("");
    setSuccess("");
    setExporting(exportType);

    try {
      const params = {
        start_date: startDate || undefined,
        end_date: endDate || undefined,
        category: category || undefined,
        status: status || undefined,
        team: team || undefined,
        action: action || undefined,
        entity_type: entityType || undefined,
        sort_by:
          reportType === "decisions"
            ? "created_date"
            : reportType === "approvals"
              ? "approval_date"
              : reportType === "teams"
                ? "team_name"
                : "timestamp",
        sort_order:
          reportType === "teams"
            ? "asc"
            : "desc",
      };

      if (reportType === "decisions") {
        if (exportType === "pdf") {
          await exportDecisionPdf(params);
        } else {
          await exportDecisionExcel(params);
        }
      }

      if (reportType === "approvals") {
        if (exportType === "pdf") {
          await exportApprovalPdf(params);
        } else {
          await exportApprovalExcel(params);
        }
      }

      if (reportType === "teams") {
        if (exportType === "pdf") {
          await exportTeamPdf(params);
        } else {
          await exportTeamExcel(params);
        }
      }

      if (reportType === "audit") {
        if (exportType === "pdf") {
          await exportAuditPdf(params);
        } else {
          await exportAuditExcel(params);
        }
      }

      setSuccess(
        `${reportType.charAt(0).toUpperCase() + reportType.slice(1)} report exported successfully as ${
          exportType === "pdf" ? "PDF" : "Excel"
        }.`,
      );
    } catch (err: any) {
      console.error("Failed to export report:", err);

      setError(
        getApiErrorMessage(
          err,
          "Unable to export the report. Please try again.",
        ),
      );
    } finally {
      setExporting(null);
    }
  }

  if (!isAdministrator) {
    return (
      <div className="flex min-h-[420px] items-center justify-center rounded-2xl border border-red-200 bg-red-50 p-8">
        <div className="max-w-md text-center">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-red-100 text-red-600">
            <ShieldCheck size={28} />
          </div>

          <h2 className="mt-5 text-xl font-bold text-red-900">
            Access restricted
          </h2>

          <p className="mt-2 text-sm leading-6 text-red-700">
            Reports and analytics are currently available
            to Administrators only.
          </p>
        </div>
      </div>
    );
  }

  const currentTotal =
    reportType === "decisions"
      ? decisionReport?.total ?? 0
      : reportType === "approvals"
        ? approvalReport?.total ?? 0
        : reportType === "teams"
          ? teamReport?.total ?? 0
          : auditReport?.total ?? 0;

  const currentPage =
    reportType === "decisions"
      ? decisionReport?.page ?? page
      : reportType === "approvals"
        ? approvalReport?.page ?? page
        : reportType === "teams"
          ? teamReport?.page ?? page
          : auditReport?.page ?? page;

  const totalPages = Math.max(
    1,
    Math.ceil(currentTotal / PAGE_SIZE),
  );

  const currentTab = REPORT_TABS.find(
    (tab) => tab.id === reportType,
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
        <div className="relative p-6 sm:p-7">
          <div className="absolute right-0 top-0 h-40 w-40 rounded-full bg-blue-50 blur-3xl" />

          <div className="relative flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
            <div className="flex items-start gap-4">
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-blue-600 text-white shadow-lg shadow-blue-600/20">
                <BarChart3 size={24} />
              </div>

              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <p className="text-xs font-bold uppercase tracking-widest text-blue-600">
                    Administrator Console
                  </p>

                  <span className="rounded-full border border-blue-200 bg-blue-50 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide text-blue-700">
                    Analytics
                  </span>
                </div>

                <h1 className="mt-1 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
                  Reports & Analytics
                </h1>

                <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
                  Generate operational reports, monitor decision
                  performance, analyze approvals and export
                  compliance-ready records.
                </p>
              </div>
            </div>

            <button
              type="button"
              onClick={() => loadReport(currentPage)}
              disabled={loading}
              className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-slate-300 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
            >
              <RefreshCw
                size={17}
                className={
                  loading ? "animate-spin" : ""
                }
              />
              {loading ? "Refreshing..." : "Refresh"}
            </button>
          </div>
        </div>
      </section>

      {/* Report selector */}
      <section className="rounded-2xl border border-slate-200 bg-white p-2 shadow-sm">
        <div className="grid grid-cols-2 gap-2 lg:grid-cols-4">
          {REPORT_TABS.map((tab) => {
            const Icon = tab.icon;
            const active = reportType === tab.id;

            return (
              <button
                key={tab.id}
                type="button"
                onClick={() => setReportType(tab.id)}
                className={`rounded-xl p-4 text-left transition ${
                  active
                    ? "bg-blue-600 text-white shadow-md shadow-blue-600/20"
                    : "text-slate-600 hover:bg-slate-50"
                }`}
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`flex h-9 w-9 items-center justify-center rounded-lg ${
                      active
                        ? "bg-white/15"
                        : "bg-slate-100"
                    }`}
                  >
                    <Icon size={18} />
                  </div>

                  <div className="min-w-0">
                    <p className="text-sm font-bold">
                      {tab.label}
                    </p>

                    <p
                      className={`mt-0.5 truncate text-[11px] ${
                        active
                          ? "text-blue-100"
                          : "text-slate-400"
                      }`}
                    >
                      {tab.description}
                    </p>
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </section>

      {/* Filters */}
      <section className="rounded-2xl border border-slate-200 bg-white shadow-sm">
        <div className="flex flex-col gap-3 border-b border-slate-100 px-5 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-50 text-blue-600">
              <Filter size={17} />
            </div>

            <div>
              <h2 className="font-semibold text-slate-900">
                Report Filters
              </h2>

              <p className="text-xs text-slate-500">
                Configure the dataset before generating or
                exporting.
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={clearFilters}
            className="text-left text-sm font-semibold text-blue-600 transition hover:text-blue-700 sm:text-right"
          >
            Clear all filters
          </button>
        </div>

        <div className="p-5 sm:p-6">
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
            {(reportType === "decisions" ||
              reportType === "teams") && (
              <div>
                <label className="mb-1.5 block text-sm font-semibold text-slate-700">
                  Category
                </label>

                <input
                  value={category}
                  onChange={(event) =>
                    setCategory(event.target.value)
                  }
                  placeholder="e.g. Technology"
                  className="w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-4 focus:ring-blue-50"
                />
              </div>
            )}

            {(reportType === "decisions" ||
              reportType === "approvals" ||
              reportType === "teams") && (
              <div>
                <label className="mb-1.5 block text-sm font-semibold text-slate-700">
                  Status
                </label>

                <select
                  value={status}
                  onChange={(event) =>
                    setStatus(event.target.value)
                  }
                  className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-50"
                >
                  <option value="">
                    All statuses
                  </option>

                  {STATUS_OPTIONS.map((item) => (
                    <option
                      key={item}
                      value={item}
                    >
                      {item}
                    </option>
                  ))}

                  {reportType === "approvals" && (
                    <option value="Pending">
                      Pending
                    </option>
                  )}
                </select>
              </div>
            )}

            {reportType === "teams" && (
              <div>
                <label className="mb-1.5 block text-sm font-semibold text-slate-700">
                  Team
                </label>

                <input
                  value={team}
                  onChange={(event) =>
                    setTeam(event.target.value)
                  }
                  placeholder="Department / team"
                  className="w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-4 focus:ring-blue-50"
                />
              </div>
            )}

            {reportType === "audit" && (
              <>
                <div>
                  <label className="mb-1.5 block text-sm font-semibold text-slate-700">
                    Action
                  </label>

                  <select
                    value={action}
                    onChange={(event) =>
                      setAction(event.target.value)
                    }
                    className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-50"
                  >
                    <option value="">
                      All actions
                    </option>

                    {AUDIT_ACTIONS.map((item) => (
                      <option
                        key={item}
                        value={item}
                      >
                        {item}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="mb-1.5 block text-sm font-semibold text-slate-700">
                    Entity Type
                  </label>

                  <input
                    value={entityType}
                    onChange={(event) =>
                      setEntityType(
                        event.target.value,
                      )
                    }
                    placeholder="e.g. Decision"
                    className="w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-4 focus:ring-blue-50"
                  />
                </div>
              </>
            )}

            <div>
              <label className="mb-1.5 block text-sm font-semibold text-slate-700">
                Start date
              </label>

              <input
                type="date"
                value={startDate}
                onChange={(event) =>
                  setStartDate(event.target.value)
                }
                className="w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-50"
              />
            </div>

            <div>
              <label className="mb-1.5 block text-sm font-semibold text-slate-700">
                End date
              </label>

              <input
                type="date"
                value={endDate}
                onChange={(event) =>
                  setEndDate(event.target.value)
                }
                className="w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-50"
              />
            </div>
          </div>

          <div className="mt-5 flex flex-col gap-3 border-t border-slate-100 pt-5 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                Selected report
              </p>

              <p className="mt-1 text-sm font-bold text-slate-800">
                {currentTab?.label}
              </p>
            </div>

            <button
              type="button"
              onClick={applyFilters}
              disabled={loading}
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 hover:shadow-md disabled:cursor-not-allowed disabled:opacity-60"
            >
              <Filter size={16} />
              {loading ? "Generating..." : "Apply Filters"}
            </button>
          </div>
        </div>
      </section>

      {/* Messages */}
      {success && (
        <div className="rounded-2xl border border-emerald-200 bg-emerald-50 px-5 py-4">
          <div className="flex items-start gap-3">
            <CheckCircle2
              size={19}
              className="mt-0.5 shrink-0 text-emerald-600"
            />

            <div>
              <p className="text-sm font-semibold text-emerald-800">
                Export completed
              </p>

              <p className="mt-1 text-sm text-emerald-700">
                {success}
              </p>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="rounded-2xl border border-red-200 bg-red-50 px-5 py-4">
          <div className="flex items-start gap-3">
            <XCircle
              size={19}
              className="mt-0.5 shrink-0 text-red-600"
            />

            <div>
              <p className="text-sm font-semibold text-red-800">
                Report operation failed
              </p>

              <p className="mt-1 text-sm text-red-700">
                {error}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Export */}
      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex items-start gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-600">
              <Download size={19} />
            </div>

            <div>
              <h2 className="font-semibold text-slate-900">
                Export Report
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Download the current{" "}
                <span className="font-semibold text-slate-700">
                  {currentTab?.label}
                </span>{" "}
                report using the filters above.
              </p>
            </div>
          </div>

          <div className="flex flex-col gap-2 sm:flex-row">
            <button
              type="button"
              onClick={() => handleExport("pdf")}
              disabled={Boolean(exporting)}
              className="inline-flex items-center justify-center gap-2 rounded-xl border border-red-200 bg-white px-4 py-2.5 text-sm font-semibold text-red-600 shadow-sm transition hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {exporting === "pdf" ? (
                <RefreshCw
                  size={16}
                  className="animate-spin"
                />
              ) : (
                <FileText size={16} />
              )}

              {exporting === "pdf"
                ? "Generating PDF..."
                : "Export PDF"}
            </button>

            <button
              type="button"
              onClick={() => handleExport("excel")}
              disabled={Boolean(exporting)}
              className="inline-flex items-center justify-center gap-2 rounded-xl border border-emerald-200 bg-white px-4 py-2.5 text-sm font-semibold text-emerald-700 shadow-sm transition hover:bg-emerald-50 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {exporting === "excel" ? (
                <RefreshCw
                  size={16}
                  className="animate-spin"
                />
              ) : (
                <FileSpreadsheet size={16} />
              )}

              {exporting === "excel"
                ? "Generating Excel..."
                : "Export Excel"}
            </button>
          </div>
        </div>
      </section>

      {/* Loading */}
      {loading && (
        <section className="flex min-h-[300px] items-center justify-center rounded-2xl border border-slate-200 bg-white shadow-sm">
          <div className="text-center">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-blue-50">
              <RefreshCw
                size={23}
                className="animate-spin text-blue-600"
              />
            </div>

            <p className="mt-4 text-sm font-semibold text-slate-700">
              Generating {currentTab?.label} report
            </p>

            <p className="mt-1 text-xs text-slate-500">
              Preparing the latest report data...
            </p>
          </div>
        </section>
      )}

      {/* Decision report */}
      {!loading &&
        reportType === "decisions" &&
        decisionReport && (
          <>
            <div className="grid grid-cols-2 gap-4 lg:grid-cols-3 xl:grid-cols-6">
              <StatCard
                label="Total"
                value={
                  decisionReport.summary
                    .total_decisions
                }
                helper="All decisions"
                icon={
                  <ClipboardList size={19} />
                }
              />

              <StatCard
                label="Draft"
                value={
                  decisionReport.summary
                    .draft_decisions
                }
                helper="Not submitted"
                icon={<Activity size={19} />}
              />

              <StatCard
                label="Under Review"
                value={
                  decisionReport.summary
                    .under_review_decisions
                }
                helper="Awaiting review"
                icon={<Clock3 size={19} />}
              />

              <StatCard
                label="Approved"
                value={
                  decisionReport.summary
                    .approved_decisions
                }
                helper="Accepted"
                icon={
                  <CheckCircle2 size={19} />
                }
              />

              <StatCard
                label="Rejected"
                value={
                  decisionReport.summary
                    .rejected_decisions
                }
                helper="Not accepted"
                icon={<XCircle size={19} />}
              />

              <StatCard
                label="Archived"
                value={
                  decisionReport.summary
                    .archived_decisions
                }
                helper="Historical"
                icon={<ShieldCheck size={19} />}
              />
            </div>

            <ReportSection title="Decision Records">
              <div className="overflow-x-auto">
                <table className="min-w-[1000px] w-full text-sm">
                  <thead className="bg-slate-50">
                    <tr>
                      {[
                        "ID",
                        "Title",
                        "Category",
                        "Status",
                        "Created By",
                        "Created",
                        "Alternatives",
                        "Approvals",
                        "Tags",
                      ].map((heading) => (
                        <th
                          key={heading}
                          className="whitespace-nowrap px-4 py-3 text-left text-[11px] font-bold uppercase tracking-wide text-slate-500"
                        >
                          {heading}
                        </th>
                      ))}
                    </tr>
                  </thead>

                  <tbody className="divide-y divide-slate-100">
                    {decisionReport.items.map(
                      (item) => (
                        <tr
                          key={item.decision_id}
                          className="transition hover:bg-blue-50/30"
                        >
                          <td className="px-4 py-4 font-bold text-slate-700">
                            #{item.decision_id}
                          </td>

                          <td className="max-w-xs px-4 py-4">
                            <p className="truncate font-semibold text-slate-900">
                              {item.title}
                            </p>
                          </td>

                          <td className="px-4 py-4 text-slate-600">
                            {item.category || "—"}
                          </td>

                          <td className="px-4 py-4">
                            <span
                              className={`inline-flex rounded-full border px-2.5 py-1 text-[11px] font-bold ${statusClass(
                                item.status,
                              )}`}
                            >
                              {item.status || "—"}
                            </span>
                          </td>

                          <td className="px-4 py-4 text-slate-600">
                            {item.created_by ?? "—"}
                          </td>

                          <td className="whitespace-nowrap px-4 py-4 text-slate-600">
                            {formatDate(
                              item.created_date,
                            )}
                          </td>

                          <td className="px-4 py-4 font-medium text-slate-700">
                            {item.alternatives_count ?? 0}
                          </td>

                          <td className="px-4 py-4 font-medium text-slate-700">
                            {item.approvals_count ?? 0}
                          </td>

                          <td className="max-w-xs px-4 py-4 text-slate-500">
                            <p className="truncate">
                              {item.tags?.length
                                ? item.tags.join(", ")
                                : "—"}
                            </p>
                          </td>
                        </tr>
                      ),
                    )}
                  </tbody>
                </table>
              </div>
            </ReportSection>
          </>
        )}

      {/* Approval report */}
      {!loading &&
        reportType === "approvals" &&
        approvalReport && (
          <>
            <div className="grid grid-cols-2 gap-4 lg:grid-cols-3 xl:grid-cols-6">
              <StatCard
                label="Total"
                value={
                  approvalReport.summary
                    .total_approvals
                }
                helper="All approvals"
                icon={<ClipboardList size={19} />}
              />

              <StatCard
                label="Pending"
                value={
                  approvalReport.summary
                    .pending_approvals
                }
                helper="Awaiting action"
                icon={<Clock3 size={19} />}
              />

              <StatCard
                label="Approved"
                value={
                  approvalReport.summary
                    .approved_approvals
                }
                helper="Accepted"
                icon={
                  <CheckCircle2 size={19} />
                }
              />

              <StatCard
                label="Rejected"
                value={
                  approvalReport.summary
                    .rejected_approvals
                }
                helper="Declined"
                icon={<XCircle size={19} />}
              />

              <StatCard
                label="Avg. Days"
                value={
                  approvalReport.summary
                    .average_turnaround_days ?? 0
                }
                helper="Average turnaround"
                icon={<Activity size={19} />}
              />

              <StatCard
                label="Completion"
                value={`${approvalReport.summary.completion_rate}%`}
                helper="Workflow completion"
                icon={<BarChart3 size={19} />}
              />
            </div>

            <ReportSection title="Approval Records">
              <div className="overflow-x-auto">
                <table className="min-w-[1000px] w-full text-sm">
                  <thead className="bg-slate-50">
                    <tr>
                      {[
                        "Approval",
                        "Decision",
                        "Title",
                        "Reviewer",
                        "Level",
                        "Status",
                        "Assigned",
                        "Completed",
                        "Turnaround",
                      ].map((heading) => (
                        <th
                          key={heading}
                          className="whitespace-nowrap px-4 py-3 text-left text-[11px] font-bold uppercase tracking-wide text-slate-500"
                        >
                          {heading}
                        </th>
                      ))}
                    </tr>
                  </thead>

                  <tbody className="divide-y divide-slate-100">
                    {approvalReport.items.map(
                      (item) => (
                        <tr
                          key={item.approval_id}
                          className="transition hover:bg-blue-50/30"
                        >
                          <td className="px-4 py-4 font-bold text-slate-700">
                            #{item.approval_id}
                          </td>

                          <td className="px-4 py-4 text-slate-600">
                            #{item.decision_id}
                          </td>

                          <td className="max-w-xs px-4 py-4 font-semibold text-slate-900">
                            <p className="truncate">
                              {item.decision_title}
                            </p>
                          </td>

                          <td className="px-4 py-4 text-slate-600">
                            {item.reviewer_id}
                          </td>

                          <td className="px-4 py-4 text-slate-600">
                            Level {item.approval_level}
                          </td>

                          <td className="px-4 py-4">
                            <span
                              className={`inline-flex rounded-full border px-2.5 py-1 text-[11px] font-bold ${statusClass(
                                item.status,
                              )}`}
                            >
                              {item.status}
                            </span>
                          </td>

                          <td className="whitespace-nowrap px-4 py-4 text-slate-600">
                            {formatDate(
                              item.assigned_date,
                            )}
                          </td>

                          <td className="whitespace-nowrap px-4 py-4 text-slate-600">
                            {formatDate(
                              item.completed_date,
                            )}
                          </td>

                          <td className="px-4 py-4 font-semibold text-slate-700">
                            {item.turnaround_days ?? "—"}
                          </td>
                        </tr>
                      ),
                    )}
                  </tbody>
                </table>
              </div>
            </ReportSection>
          </>
        )}

      {/* Team report */}
      {!loading &&
        reportType === "teams" &&
        teamReport && (
          <>
            <div className="grid grid-cols-2 gap-4 lg:grid-cols-3 xl:grid-cols-6">
              <StatCard
                label="Teams"
                value={
                  teamReport.summary.total_teams
                }
                helper="Active teams"
                icon={<Users size={19} />}
              />

              <StatCard
                label="Members"
                value={
                  teamReport.summary.total_members
                }
                helper="Team members"
                icon={<Users size={19} />}
              />

              <StatCard
                label="Decisions"
                value={
                  teamReport.summary.total_decisions
                }
                helper="Team decisions"
                icon={<ClipboardList size={19} />}
              />

              <StatCard
                label="Approved"
                value={
                  teamReport.summary.total_approved
                }
                helper="Accepted decisions"
                icon={
                  <CheckCircle2 size={19} />
                }
              />

              <StatCard
                label="Rejected"
                value={
                  teamReport.summary.total_rejected
                }
                helper="Rejected decisions"
                icon={<XCircle size={19} />}
              />

              <StatCard
                label="Pending"
                value={
                  teamReport.summary.total_pending
                }
                helper="Pending decisions"
                icon={<Clock3 size={19} />}
              />
            </div>

            <ReportSection title="Team Performance">
              <div className="overflow-x-auto">
                <table className="min-w-[850px] w-full text-sm">
                  <thead className="bg-slate-50">
                    <tr>
                      {[
                        "Team",
                        "Members",
                        "Decisions",
                        "Approved",
                        "Rejected",
                        "Pending",
                        "Approval Rate",
                      ].map((heading) => (
                        <th
                          key={heading}
                          className="whitespace-nowrap px-4 py-3 text-left text-[11px] font-bold uppercase tracking-wide text-slate-500"
                        >
                          {heading}
                        </th>
                      ))}
                    </tr>
                  </thead>

                  <tbody className="divide-y divide-slate-100">
                    {teamReport.items.map(
                      (item) => (
                        <tr
                          key={item.team_name}
                          className="transition hover:bg-blue-50/30"
                        >
                          <td className="px-4 py-4 font-bold text-slate-900">
                            {item.team_name}
                          </td>

                          <td className="px-4 py-4 text-slate-600">
                            {item.members}
                          </td>

                          <td className="px-4 py-4 text-slate-600">
                            {item.total_decisions}
                          </td>

                          <td className="px-4 py-4 font-semibold text-emerald-700">
                            {item.approved_decisions}
                          </td>

                          <td className="px-4 py-4 font-semibold text-red-700">
                            {item.rejected_decisions}
                          </td>

                          <td className="px-4 py-4 font-semibold text-amber-700">
                            {item.pending_decisions}
                          </td>

                          <td className="px-4 py-4">
                            <span className="rounded-full border border-blue-200 bg-blue-50 px-2.5 py-1 text-xs font-bold text-blue-700">
                              {item.approval_rate}%
                            </span>
                          </td>
                        </tr>
                      ),
                    )}
                  </tbody>
                </table>
              </div>
            </ReportSection>
          </>
        )}

      {/* Audit report */}
      {!loading &&
        reportType === "audit" &&
        auditReport && (
          <>
            <div className="grid grid-cols-2 gap-4 lg:grid-cols-3 xl:grid-cols-5">
              <StatCard
                label="Total Logs"
                value={
                  auditReport.summary
                    .total_audit_logs
                }
                helper="Audit events"
                icon={<ShieldCheck size={19} />}
              />

              <StatCard
                label="Create"
                value={
                  auditReport.summary
                    .create_actions
                }
                helper="Creation events"
                icon={<Activity size={19} />}
              />

              <StatCard
                label="Update"
                value={
                  auditReport.summary
                    .update_actions
                }
                helper="Modification events"
                icon={<Activity size={19} />}
              />

              <StatCard
                label="Approvals"
                value={
                  auditReport.summary
                    .approve_actions
                }
                helper="Approval events"
                icon={
                  <CheckCircle2 size={19} />
                }
              />

              <StatCard
                label="Logins"
                value={
                  auditReport.summary
                    .login_actions
                }
                helper="Authentication events"
                icon={<Users size={19} />}
              />
            </div>

            <ReportSection title="Audit Records">
              <div className="overflow-x-auto">
                <table className="min-w-[1050px] w-full text-sm">
                  <thead className="bg-slate-50">
                    <tr>
                      {[
                        "Audit ID",
                        "User",
                        "Action",
                        "Entity",
                        "Entity ID",
                        "Description",
                        "Timestamp",
                        "IP Address",
                      ].map((heading) => (
                        <th
                          key={heading}
                          className="whitespace-nowrap px-4 py-3 text-left text-[11px] font-bold uppercase tracking-wide text-slate-500"
                        >
                          {heading}
                        </th>
                      ))}
                    </tr>
                  </thead>

                  <tbody className="divide-y divide-slate-100">
                    {auditReport.items.map(
                      (item) => (
                        <tr
                          key={item.audit_id}
                          className="transition hover:bg-blue-50/30"
                        >
                          <td className="px-4 py-4 font-bold text-slate-700">
                            #{item.audit_id}
                          </td>

                          <td className="px-4 py-4 text-slate-600">
                            User #{item.user_id}
                          </td>

                          <td className="px-4 py-4">
                            <span
                              className={`inline-flex rounded-full border px-2.5 py-1 text-[11px] font-bold ${actionClass(
                                item.action,
                              )}`}
                            >
                              {item.action}
                            </span>
                          </td>

                          <td className="px-4 py-4 font-medium text-slate-700">
                            {item.entity_type}
                          </td>

                          <td className="px-4 py-4 text-slate-600">
                            {item.entity_id ?? "—"}
                          </td>

                          <td className="max-w-sm px-4 py-4 text-slate-600">
                            <p className="line-clamp-2">
                              {item.description || "—"}
                            </p>
                          </td>

                          <td className="whitespace-nowrap px-4 py-4 text-slate-600">
                            {formatDate(
                              item.timestamp,
                            )}
                          </td>

                          <td className="px-4 py-4 text-slate-500">
                            {item.ip_address || "—"}
                          </td>
                        </tr>
                      ),
                    )}
                  </tbody>
                </table>
              </div>
            </ReportSection>
          </>
        )}

      {/* Empty state */}
      {!loading && currentTotal === 0 && (
        <div className="rounded-2xl border border-slate-200 bg-white p-12 text-center shadow-sm">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-100 text-slate-400">
            <BarChart3 size={27} />
          </div>

          <h3 className="mt-5 text-lg font-bold text-slate-800">
            No report data found
          </h3>

          <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-500">
            There are no records matching the selected
            filters. Try changing the filters or clear them
            to view the complete report.
          </p>

          <button
            type="button"
            onClick={clearFilters}
            className="mt-5 rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700"
          >
            Clear Filters
          </button>
        </div>
      )}

      {/* Pagination */}
      {!loading && currentTotal > 0 && (
        <div className="flex flex-col gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm text-slate-500">
              Page{" "}
              <span className="font-bold text-slate-800">
                {currentPage}
              </span>{" "}
              of{" "}
              <span className="font-bold text-slate-800">
                {totalPages}
              </span>
            </p>

            <p className="mt-0.5 text-xs text-slate-400">
              {currentTotal.toLocaleString()} total records
            </p>
          </div>

          <div className="flex gap-2">
            <button
              type="button"
              disabled={currentPage <= 1}
              onClick={() =>
                loadReport(currentPage - 1)
              }
              className="rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
            >
              Previous
            </button>

            <button
              type="button"
              disabled={currentPage >= totalPages}
              onClick={() =>
                loadReport(currentPage + 1)
              }
              className="rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-40"
            >
              Next
            </button>
          </div>
        </div>
      )}

      {/* Export information */}
      <div className="rounded-2xl border border-blue-100 bg-blue-50 p-5">
        <div className="flex items-start gap-3">
          <Download
            size={19}
            className="mt-0.5 shrink-0 text-blue-600"
          />

          <div>
            <p className="text-sm font-bold text-blue-900">
              Export follows your selected filters
            </p>

            <p className="mt-1 text-sm leading-6 text-blue-700">
              PDF and Excel files are generated by the
              backend using the current report type and
              filter configuration. Exported records are
              independent of the current page.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function ReportSection({
  title,
  children,
}: {
  title: string;
  children: ReactNode;
}) {
  return (
    <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-100 px-5 py-4 sm:px-6">
        <h2 className="font-semibold text-slate-900">
          {title}
        </h2>

        <p className="mt-1 text-xs text-slate-500">
          Detailed records for the selected report.
        </p>
      </div>

      {children}
    </section>
  );
}