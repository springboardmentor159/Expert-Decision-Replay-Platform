import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertCircle,
  CalendarDays,
  ChevronLeft,
  ChevronRight,
  Filter,
  RefreshCw,
  Search,
  ShieldCheck,
  UserRound,
  X,
} from "lucide-react";

import { getAuditLogs, type AuditLog } from "../services/audit";
import { getApiErrorMessage } from "../utils/errors";

const PAGE_SIZE = 10;

const ACTIONS = [
  "",
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

const ENTITY_TYPES = [
  "",
  "Decision",
  "Alternative",
  "Comment",
  "DiscussionThread",
  "MeetingNote",
  "Approval",
  "User",
];

function formatDate(value?: string) {
  if (!value) return "—";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function actionClass(action: string) {
  switch (action.toUpperCase()) {
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

function actionIconClass(action: string) {
  switch (action.toUpperCase()) {
    case "CREATE":
    case "APPROVE":
      return "bg-emerald-50 text-emerald-600";

    case "DELETE":
    case "REJECT":
      return "bg-red-50 text-red-600";

    case "LOGIN":
      return "bg-purple-50 text-purple-600";

    case "ACCESS":
      return "bg-cyan-50 text-cyan-600";

    case "SUBMIT":
      return "bg-indigo-50 text-indigo-600";

    default:
      return "bg-blue-50 text-blue-600";
  }
}

export default function Audit() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [total, setTotal] = useState(0);

  const [page, setPage] = useState(1);

  const [userId, setUserId] = useState("");
  const [action, setAction] = useState("");
  const [entityType, setEntityType] = useState("");
  const [entityId, setEntityId] = useState("");

  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  const hasFilters = useMemo(() => {
    return Boolean(
      userId ||
        action ||
        entityType ||
        entityId ||
        startDate ||
        endDate,
    );
  }, [
    userId,
    action,
    entityType,
    entityId,
    startDate,
    endDate,
  ]);

  async function loadAuditLogs(
    requestedPage = page,
    showRefresh = false,
  ) {
    try {
      if (showRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }

      setError("");

      const response = await getAuditLogs({
        user_id: userId ? Number(userId) : undefined,
        action: action || undefined,
        entity_type: entityType || undefined,
        entity_id: entityId ? Number(entityId) : undefined,
        start_date: startDate || undefined,
        end_date: endDate || undefined,
        page: requestedPage,
        page_size: PAGE_SIZE,
      });

      setLogs(response.items || []);
      setTotal(response.total || 0);
      setPage(response.page || requestedPage);
    } catch (err: any) {
      console.error("Failed to load audit logs:", err);

      setError(
        getApiErrorMessage(
          err,
          "Unable to load audit logs. Please try again.",
        ),
      );

      setLogs([]);
      setTotal(0);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  useEffect(() => {
    loadAuditLogs(1);
  }, []);

  function applyFilters() {
    setPage(1);
    loadAuditLogs(1);
  }

  function clearFilters() {
    setUserId("");
    setAction("");
    setEntityType("");
    setEntityId("");
    setStartDate("");
    setEndDate("");

    setPage(1);

    setTimeout(() => {
      loadAuditLogs(1);
    }, 0);
  }

  function removeFilter(filter: string) {
    if (filter === "user") setUserId("");
    if (filter === "action") setAction("");
    if (filter === "entityType") setEntityType("");
    if (filter === "entityId") setEntityId("");
    if (filter === "startDate") setStartDate("");
    if (filter === "endDate") setEndDate("");

    setPage(1);

    setTimeout(() => {
      loadAuditLogs(1);
    }, 0);
  }

  function previousPage() {
    if (page <= 1 || loading) return;

    loadAuditLogs(page - 1);
  }

  function nextPage() {
    if (page >= totalPages || loading) return;

    loadAuditLogs(page + 1);
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <section className="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm">
        <div className="relative p-6 sm:p-7">
          <div className="absolute right-0 top-0 h-32 w-32 rounded-full bg-blue-50 blur-3xl" />

          <div className="relative flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
            <div className="flex items-start gap-4">
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-blue-600 text-white shadow-lg shadow-blue-600/20">
                <ShieldCheck size={24} />
              </div>

              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <p className="text-xs font-bold uppercase tracking-widest text-blue-600">
                    Security & Compliance
                  </p>

                  <span className="rounded-full border border-emerald-200 bg-emerald-50 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide text-emerald-700">
                    Protected
                  </span>
                </div>

                <h1 className="mt-1 text-2xl font-bold tracking-tight text-gray-900 sm:text-3xl">
                  Audit Logs
                </h1>

                <p className="mt-2 max-w-2xl text-sm leading-6 text-gray-500">
                  Monitor decision activity, approvals, authentication,
                  system changes, and other auditable events across the
                  platform.
                </p>
              </div>
            </div>

            <button
              type="button"
              onClick={() => loadAuditLogs(page, true)}
              disabled={loading || refreshing}
              className="inline-flex items-center justify-center gap-2 rounded-xl border border-gray-200 bg-white px-4 py-2.5 text-sm font-semibold text-gray-700 shadow-sm transition hover:border-gray-300 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-60"
            >
              <RefreshCw
                size={17}
                className={
                  loading || refreshing ? "animate-spin" : ""
                }
              />
              {refreshing ? "Refreshing..." : "Refresh"}
            </button>
          </div>
        </div>
      </section>

      {/* Summary cards */}
      <section className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">
                Total Events
              </p>

              <p className="mt-2 text-3xl font-bold tracking-tight text-gray-900">
                {total.toLocaleString()}
              </p>

              <p className="mt-1 text-xs text-gray-500">
                Matching current filters
              </p>
            </div>

            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
              <Activity size={20} />
            </div>
          </div>
        </div>

        <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">
                Events Displayed
              </p>

              <p className="mt-2 text-3xl font-bold tracking-tight text-gray-900">
                {logs.length}
              </p>

              <p className="mt-1 text-xs text-gray-500">
                On the current page
              </p>
            </div>

            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600">
              <Filter size={20} />
            </div>
          </div>
        </div>

        <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">
                Audit Monitoring
              </p>

              <p className="mt-2 text-xl font-bold text-gray-900">
                System Active
              </p>

              <p className="mt-1 text-xs text-emerald-600">
                Backend audit recording enabled
              </p>
            </div>

            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600">
              <ShieldCheck size={20} />
            </div>
          </div>
        </div>
      </section>

      {/* Filters */}
      <section className="rounded-2xl border border-gray-200 bg-white shadow-sm">
        <div className="border-b border-gray-100 px-5 py-4 sm:px-6">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gray-100 text-gray-600">
              <Filter size={17} />
            </div>

            <div>
              <h2 className="font-semibold text-gray-900">
                Filter Audit Activity
              </h2>

              <p className="text-xs text-gray-500">
                Narrow down events using audit attributes and dates.
              </p>
            </div>
          </div>
        </div>

        <div className="p-5 sm:p-6">
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            {/* User ID */}
            <div>
              <label className="mb-1.5 block text-sm font-semibold text-gray-700">
                User ID
              </label>

              <div className="relative">
                <UserRound
                  size={16}
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
                />

                <input
                  type="number"
                  min="1"
                  value={userId}
                  onChange={(event) =>
                    setUserId(event.target.value)
                  }
                  placeholder="e.g. 4"
                  className="w-full rounded-xl border border-gray-300 py-2.5 pl-9 pr-3 text-sm outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-50"
                />
              </div>
            </div>

            {/* Action */}
            <div>
              <label className="mb-1.5 block text-sm font-semibold text-gray-700">
                Action
              </label>

              <select
                value={action}
                onChange={(event) =>
                  setAction(event.target.value)
                }
                className="w-full rounded-xl border border-gray-300 bg-white px-3 py-2.5 text-sm outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-50"
              >
                <option value="">All Actions</option>

                {ACTIONS.filter(Boolean).map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </select>
            </div>

            {/* Entity Type */}
            <div>
              <label className="mb-1.5 block text-sm font-semibold text-gray-700">
                Entity Type
              </label>

              <select
                value={entityType}
                onChange={(event) =>
                  setEntityType(event.target.value)
                }
                className="w-full rounded-xl border border-gray-300 bg-white px-3 py-2.5 text-sm outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-50"
              >
                <option value="">All Entity Types</option>

                {ENTITY_TYPES.filter(Boolean).map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </select>
            </div>

            {/* Entity ID */}
            <div>
              <label className="mb-1.5 block text-sm font-semibold text-gray-700">
                Entity ID
              </label>

              <div className="relative">
                <Search
                  size={16}
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
                />

                <input
                  type="number"
                  min="1"
                  value={entityId}
                  onChange={(event) =>
                    setEntityId(event.target.value)
                  }
                  placeholder="e.g. 3"
                  className="w-full rounded-xl border border-gray-300 py-2.5 pl-9 pr-3 text-sm outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-50"
                />
              </div>
            </div>

            {/* Start Date */}
            <div>
              <label className="mb-1.5 block text-sm font-semibold text-gray-700">
                Start Date
              </label>

              <div className="relative">
                <CalendarDays
                  size={16}
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
                />

                <input
                  type="date"
                  value={startDate}
                  onChange={(event) =>
                    setStartDate(event.target.value)
                  }
                  className="w-full rounded-xl border border-gray-300 py-2.5 pl-9 pr-3 text-sm outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-50"
                />
              </div>
            </div>

            {/* End Date */}
            <div>
              <label className="mb-1.5 block text-sm font-semibold text-gray-700">
                End Date
              </label>

              <div className="relative">
                <CalendarDays
                  size={16}
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
                />

                <input
                  type="date"
                  value={endDate}
                  onChange={(event) =>
                    setEndDate(event.target.value)
                  }
                  className="w-full rounded-xl border border-gray-300 py-2.5 pl-9 pr-3 text-sm outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-50"
                />
              </div>
            </div>
          </div>

          {/* Active filters */}
          {hasFilters && (
            <div className="mt-5 flex flex-wrap items-center gap-2 border-t border-gray-100 pt-4">
              <span className="mr-1 text-xs font-semibold uppercase tracking-wide text-gray-400">
                Active:
              </span>

              {userId && (
                <button
                  type="button"
                  onClick={() => removeFilter("user")}
                  className="inline-flex items-center gap-1.5 rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700"
                >
                  User #{userId}
                  <X size={13} />
                </button>
              )}

              {action && (
                <button
                  type="button"
                  onClick={() => removeFilter("action")}
                  className="inline-flex items-center gap-1.5 rounded-full border border-indigo-200 bg-indigo-50 px-3 py-1 text-xs font-semibold text-indigo-700"
                >
                  {action}
                  <X size={13} />
                </button>
              )}

              {entityType && (
                <button
                  type="button"
                  onClick={() => removeFilter("entityType")}
                  className="inline-flex items-center gap-1.5 rounded-full border border-purple-200 bg-purple-50 px-3 py-1 text-xs font-semibold text-purple-700"
                >
                  {entityType}
                  <X size={13} />
                </button>
              )}

              {entityId && (
                <button
                  type="button"
                  onClick={() => removeFilter("entityId")}
                  className="inline-flex items-center gap-1.5 rounded-full border border-cyan-200 bg-cyan-50 px-3 py-1 text-xs font-semibold text-cyan-700"
                >
                  Entity #{entityId}
                  <X size={13} />
                </button>
              )}

              {startDate && (
                <button
                  type="button"
                  onClick={() => removeFilter("startDate")}
                  className="inline-flex items-center gap-1.5 rounded-full border border-gray-200 bg-gray-50 px-3 py-1 text-xs font-semibold text-gray-700"
                >
                  From {startDate}
                  <X size={13} />
                </button>
              )}

              {endDate && (
                <button
                  type="button"
                  onClick={() => removeFilter("endDate")}
                  className="inline-flex items-center gap-1.5 rounded-full border border-gray-200 bg-gray-50 px-3 py-1 text-xs font-semibold text-gray-700"
                >
                  Until {endDate}
                  <X size={13} />
                </button>
              )}
            </div>
          )}

          <div className="mt-5 flex flex-wrap gap-3">
            <button
              type="button"
              onClick={applyFilters}
              disabled={loading}
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 hover:shadow-md disabled:cursor-not-allowed disabled:opacity-60"
            >
              <Search size={16} />
              Apply Filters
            </button>

            <button
              type="button"
              onClick={clearFilters}
              disabled={loading || !hasFilters}
              className="inline-flex items-center justify-center gap-2 rounded-xl border border-gray-300 bg-white px-5 py-2.5 text-sm font-semibold text-gray-700 transition hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-40"
            >
              <X size={16} />
              Clear Filters
            </button>
          </div>
        </div>
      </section>

      {/* Error */}
      {error && (
        <div className="flex items-start gap-3 rounded-2xl border border-red-200 bg-red-50 p-4">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-red-100 text-red-600">
            <AlertCircle size={18} />
          </div>

          <div className="min-w-0">
            <p className="font-semibold text-red-800">
              Unable to load audit logs
            </p>

            <p className="mt-1 text-sm leading-5 text-red-700">
              {error}
            </p>

            <button
              type="button"
              onClick={() => loadAuditLogs(page)}
              className="mt-3 text-sm font-semibold text-red-800 underline underline-offset-2 hover:text-red-900"
            >
              Try again
            </button>
          </div>
        </div>
      )}

      {/* Activity */}
      <section className="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm">
        <div className="flex flex-col gap-3 border-b border-gray-100 px-5 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6">
          <div>
            <h2 className="font-semibold text-gray-900">
              Activity Records
            </h2>

            <p className="mt-1 text-xs text-gray-500">
              Showing {logs.length} of {total.toLocaleString()} events
            </p>
          </div>

          <div className="rounded-full bg-gray-100 px-3 py-1.5 text-xs font-semibold text-gray-600">
            Page {page} of {totalPages}
          </div>
        </div>

        {loading ? (
          <div className="flex min-h-[360px] items-center justify-center px-6">
            <div className="text-center">
              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-blue-50">
                <RefreshCw
                  size={23}
                  className="animate-spin text-blue-600"
                />
              </div>

              <p className="mt-4 text-sm font-semibold text-gray-700">
                Loading audit activity
              </p>

              <p className="mt-1 text-xs text-gray-500">
                Retrieving secure activity records...
              </p>
            </div>
          </div>
        ) : logs.length === 0 ? (
          <div className="flex min-h-[360px] items-center justify-center px-6">
            <div className="max-w-md text-center">
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-gray-100 text-gray-400">
                <Activity size={27} />
              </div>

              <h3 className="mt-5 font-semibold text-gray-900">
                No audit activity found
              </h3>

              <p className="mt-2 text-sm leading-6 text-gray-500">
                There are no audit records matching the selected
                filters. Try changing the filters or viewing all
                activity.
              </p>

              {hasFilters && (
                <button
                  type="button"
                  onClick={clearFilters}
                  className="mt-4 rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700"
                >
                  Clear Filters
                </button>
              )}
            </div>
          </div>
        ) : (
          <>
            {/* Desktop table */}
            <div className="hidden overflow-x-auto lg:block">
              <table className="min-w-full">
                <thead>
                  <tr className="border-b border-gray-100 bg-gray-50/80">
                    <th className="px-6 py-3.5 text-left text-[11px] font-bold uppercase tracking-wider text-gray-500">
                      Event
                    </th>

                    <th className="px-6 py-3.5 text-left text-[11px] font-bold uppercase tracking-wider text-gray-500">
                      Action
                    </th>

                    <th className="px-6 py-3.5 text-left text-[11px] font-bold uppercase tracking-wider text-gray-500">
                      Entity
                    </th>

                    <th className="px-6 py-3.5 text-left text-[11px] font-bold uppercase tracking-wider text-gray-500">
                      User
                    </th>

                    <th className="px-6 py-3.5 text-left text-[11px] font-bold uppercase tracking-wider text-gray-500">
                      Timestamp
                    </th>
                  </tr>
                </thead>

                <tbody className="divide-y divide-gray-100">
                  {logs.map((log) => (
                    <tr
                      key={log.id}
                      className="group transition hover:bg-blue-50/30"
                    >
                      {/* Event */}
                      <td className="max-w-lg px-6 py-4 align-top">
                        <div className="flex gap-3">
                          <div
                            className={`mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-xl ${actionIconClass(
                              log.action,
                            )}`}
                          >
                            <Activity size={16} />
                          </div>

                          <div className="min-w-0">
                            <p className="text-sm font-semibold leading-5 text-gray-900">
                              {log.description || "Audit event"}
                            </p>

                            <p className="mt-1 text-xs text-gray-400">
                              Audit ID #{log.id}
                            </p>
                          </div>
                        </div>
                      </td>

                      {/* Action */}
                      <td className="whitespace-nowrap px-6 py-4 align-top">
                        <span
                          className={`inline-flex rounded-full border px-2.5 py-1 text-[11px] font-bold tracking-wide ${actionClass(
                            log.action,
                          )}`}
                        >
                          {log.action}
                        </span>
                      </td>

                      {/* Entity */}
                      <td className="px-6 py-4 align-top">
                        <p className="text-sm font-semibold text-gray-800">
                          {log.entity_type}
                        </p>

                        <p className="mt-1 text-xs text-gray-500">
                          Entity ID:{" "}
                          <span className="font-medium text-gray-700">
                            {log.entity_id ?? "—"}
                          </span>
                        </p>
                      </td>

                      {/* User */}
                      <td className="whitespace-nowrap px-6 py-4 align-top">
                        <div className="flex items-center gap-2">
                          <div className="flex h-7 w-7 items-center justify-center rounded-full bg-gray-100 text-gray-500">
                            <UserRound size={14} />
                          </div>

                          <div>
                            <p className="text-sm font-medium text-gray-800">
                              {log.user_id
                                ? `User #${log.user_id}`
                                : "System"}
                            </p>

                            {log.ip_address && (
                              <p className="mt-0.5 text-xs text-gray-400">
                                {log.ip_address}
                              </p>
                            )}
                          </div>
                        </div>
                      </td>

                      {/* Timestamp */}
                      <td className="whitespace-nowrap px-6 py-4 align-top">
                        <p className="text-sm font-medium text-gray-700">
                          {formatDate(log.created_at)}
                        </p>

                        {log.request_method && (
                          <span className="mt-1 inline-flex rounded-md bg-gray-100 px-1.5 py-0.5 text-[10px] font-bold text-gray-500">
                            {log.request_method}
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Mobile/tablet cards */}
            <div className="divide-y divide-gray-100 lg:hidden">
              {logs.map((log) => (
                <article
                  key={log.id}
                  className="p-5 transition hover:bg-gray-50"
                >
                  <div className="flex items-start gap-3">
                    <div
                      className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${actionIconClass(
                        log.action,
                      )}`}
                    >
                      <Activity size={17} />
                    </div>

                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-start justify-between gap-2">
                        <p className="text-sm font-semibold leading-5 text-gray-900">
                          {log.description || "Audit event"}
                        </p>

                        <span
                          className={`shrink-0 rounded-full border px-2.5 py-1 text-[10px] font-bold ${actionClass(
                            log.action,
                          )}`}
                        >
                          {log.action}
                        </span>
                      </div>

                      <p className="mt-1 text-xs text-gray-400">
                        Audit ID #{log.id}
                      </p>
                    </div>
                  </div>

                  <div className="mt-4 grid grid-cols-2 gap-3 rounded-xl bg-gray-50 p-3">
                    <div>
                      <p className="text-[10px] font-bold uppercase tracking-wide text-gray-400">
                        Entity
                      </p>

                      <p className="mt-1 text-xs font-semibold text-gray-800">
                        {log.entity_type}
                      </p>

                      <p className="mt-0.5 text-[11px] text-gray-500">
                        ID: {log.entity_id ?? "—"}
                      </p>
                    </div>

                    <div>
                      <p className="text-[10px] font-bold uppercase tracking-wide text-gray-400">
                        User
                      </p>

                      <p className="mt-1 text-xs font-semibold text-gray-800">
                        {log.user_id
                          ? `User #${log.user_id}`
                          : "System"}
                      </p>

                      {log.ip_address && (
                        <p className="mt-0.5 truncate text-[11px] text-gray-500">
                          {log.ip_address}
                        </p>
                      )}
                    </div>

                    <div className="col-span-2 border-t border-gray-200 pt-3">
                      <p className="text-[10px] font-bold uppercase tracking-wide text-gray-400">
                        Timestamp
                      </p>

                      <p className="mt-1 text-xs font-semibold text-gray-700">
                        {formatDate(log.created_at)}
                      </p>

                      {log.request_method && (
                        <span className="mt-1 inline-flex rounded-md bg-white px-1.5 py-0.5 text-[10px] font-bold text-gray-500 shadow-sm">
                          {log.request_method}
                        </span>
                      )}
                    </div>
                  </div>
                </article>
              ))}
            </div>

            {/* Pagination */}
            <div className="flex flex-col gap-3 border-t border-gray-100 px-5 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6">
              <div>
                <p className="text-sm text-gray-500">
                  Page{" "}
                  <span className="font-bold text-gray-800">
                    {page}
                  </span>{" "}
                  of{" "}
                  <span className="font-bold text-gray-800">
                    {totalPages}
                  </span>
                </p>

                <p className="mt-0.5 text-xs text-gray-400">
                  {total.toLocaleString()} total audit events
                </p>
              </div>

              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={previousPage}
                  disabled={page <= 1 || loading}
                  className="inline-flex items-center gap-1.5 rounded-xl border border-gray-300 bg-white px-3.5 py-2 text-sm font-semibold text-gray-700 transition hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  <ChevronLeft size={16} />
                  Previous
                </button>

                <button
                  type="button"
                  onClick={nextPage}
                  disabled={page >= totalPages || loading}
                  className="inline-flex items-center gap-1.5 rounded-xl border border-gray-300 bg-white px-3.5 py-2 text-sm font-semibold text-gray-700 transition hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  Next
                  <ChevronRight size={16} />
                </button>
              </div>
            </div>
          </>
        )}
      </section>
    </div>
  );
}