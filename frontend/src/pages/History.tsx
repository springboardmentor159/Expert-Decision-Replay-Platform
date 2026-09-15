import { useEffect, useMemo, useState } from "react";
import {
  AlertCircle,
  ArrowLeft,
  CalendarDays,
  CheckCircle2,
  ChevronRight,
  Clock3,
  FileText,
  GitBranch,
  History as HistoryIcon,
  RefreshCw,
  User,
} from "lucide-react";
import { useNavigate, useParams } from "react-router-dom";

import {
  getDecisionHistory,
  getDecisionVersions,
  type DecisionHistoryItem,
  type DecisionVersion,
} from "../services/history";

import { getApiErrorMessage } from "../utils/errors";

function formatDate(value?: string) {
  if (!value) return "—";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString();
}

function formatShortDate(value?: string) {
  if (!value) return "—";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleDateString(undefined, {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function statusClasses(status?: string) {
  const value = status?.toLowerCase();

  if (value === "approved") {
    return "border-emerald-200 bg-emerald-50 text-emerald-700";
  }

  if (value === "rejected") {
    return "border-red-200 bg-red-50 text-red-700";
  }

  if (
    value === "under review" ||
    value === "under_review"
  ) {
    return "border-amber-200 bg-amber-50 text-amber-700";
  }

  if (value === "archived") {
    return "border-slate-300 bg-slate-100 text-slate-700";
  }

  return "border-slate-200 bg-slate-100 text-slate-700";
}

function statusDot(status?: string) {
  const value = status?.toLowerCase();

  if (value === "approved") return "bg-emerald-500";
  if (value === "rejected") return "bg-red-500";
  if (
    value === "under review" ||
    value === "under_review"
  ) {
    return "bg-amber-500";
  }

  if (value === "archived") return "bg-slate-400";

  return "bg-blue-500";
}

function getActionLabel(action?: string) {
  if (!action) return "History Event";

  return action
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function getActionIcon(action?: string) {
  const value = action?.toLowerCase() || "";

  if (
    value.includes("approve") ||
    value.includes("create")
  ) {
    return CheckCircle2;
  }

  if (
    value.includes("update") ||
    value.includes("edit")
  ) {
    return GitBranch;
  }

  if (
    value.includes("submit") ||
    value.includes("review")
  ) {
    return FileText;
  }

  return Clock3;
}

export default function History() {
  const { decisionId } = useParams<{
    decisionId: string;
  }>();

  const navigate = useNavigate();

  const numericDecisionId = Number(decisionId);

  const [versions, setVersions] = useState<
    DecisionVersion[]
  >([]);

  const [history, setHistory] = useState<
    DecisionHistoryItem[]
  >([]);

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const [selectedVersion, setSelectedVersion] =
    useState<DecisionVersion | null>(null);

  async function loadHistory(showFullLoader = true) {
    if (
      !Number.isInteger(numericDecisionId) ||
      numericDecisionId <= 0
    ) {
      setError("Invalid decision ID.");
      setLoading(false);
      return;
    }

    try {
      if (showFullLoader) {
        setLoading(true);
      } else {
        setRefreshing(true);
      }

      setError("");

      const [versionData, historyData] =
        await Promise.all([
          getDecisionVersions(numericDecisionId),
          getDecisionHistory(numericDecisionId),
        ]);

      const sortedVersions = [...versionData].sort(
        (a, b) =>
          b.version_number - a.version_number,
      );

      setVersions(sortedVersions);
      setHistory(historyData);

      if (sortedVersions.length > 0) {
        setSelectedVersion((current) => {
          if (!current) {
            return sortedVersions[0];
          }

          const refreshedVersion =
            sortedVersions.find(
              (version) =>
                version.version_number ===
                current.version_number,
            );

          return (
            refreshedVersion || sortedVersions[0]
          );
        });
      } else {
        setSelectedVersion(null);
      }
    } catch (err: any) {
      console.error(err);

      setError(
        getApiErrorMessage(
          err,
          "Unable to load decision history.",
        ),
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  useEffect(() => {
    loadHistory();
  }, [numericDecisionId]);

  const latestVersion = useMemo(() => {
    if (!versions.length) return null;

    return versions.reduce((latest, current) =>
      current.version_number >
      latest.version_number
        ? current
        : latest,
    );
  }, [versions]);

  const firstVersion = useMemo(() => {
    if (!versions.length) return null;

    return versions.reduce((oldest, current) =>
      current.version_number <
      oldest.version_number
        ? current
        : oldest,
    );
  }, [versions]);

  if (
    !Number.isInteger(numericDecisionId) ||
    numericDecisionId <= 0
  ) {
    return (
      <div className="mx-auto max-w-7xl">
        <button
          type="button"
          onClick={() => navigate("/decisions")}
          className="mb-6 inline-flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100 hover:text-blue-600"
        >
          <ArrowLeft size={17} />
          Back to Decisions
        </button>

        <div className="flex items-center gap-3 rounded-3xl border border-red-200 bg-red-50 p-6 text-sm font-semibold text-red-700">
          <AlertCircle size={20} />
          Invalid decision ID.
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      {/* =====================================================
          PAGE HEADER
      ====================================================== */}

      <section className="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">
        <div className="relative p-6 md:p-8">
          <div className="absolute right-0 top-0 h-40 w-40 rounded-full bg-blue-50 blur-3xl" />

          <div className="relative flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <button
                type="button"
                onClick={() =>
                  navigate(
                    `/decisions/${numericDecisionId}`,
                  )
                }
                className="mb-5 inline-flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100 hover:text-blue-600"
              >
                <ArrowLeft size={17} />
                Back to Decision
              </button>

              <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-blue-100 bg-blue-50 px-3 py-1.5 text-xs font-bold text-blue-700">
                <HistoryIcon size={14} />
                VERSION CONTROL
              </div>

              <h1 className="text-2xl font-bold tracking-tight text-slate-950 md:text-3xl">
                Version & History
              </h1>

              <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
                Review the recorded evolution of Decision #
                {numericDecisionId}, including previous
                versions and important activity events.
              </p>
            </div>

            <button
              type="button"
              onClick={() => loadHistory(false)}
              disabled={refreshing}
              className="inline-flex shrink-0 items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              <RefreshCw
                size={16}
                className={
                  refreshing
                    ? "animate-spin"
                    : ""
                }
              />
              Refresh History
            </button>
          </div>

          {/* =================================================
              SUMMARY
          ================================================== */}

          <div className="relative mt-7 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-bold uppercase tracking-wider text-slate-400">
                    Total Versions
                  </p>

                  <p className="mt-2 text-2xl font-bold text-slate-950">
                    {versions.length}
                  </p>
                </div>

                <div className="rounded-xl bg-blue-100 p-3 text-blue-700">
                  <GitBranch size={20} />
                </div>
              </div>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-bold uppercase tracking-wider text-slate-400">
                    Activity Events
                  </p>

                  <p className="mt-2 text-2xl font-bold text-slate-950">
                    {history.length}
                  </p>
                </div>

                <div className="rounded-xl bg-amber-100 p-3 text-amber-700">
                  <Clock3 size={20} />
                </div>
              </div>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-bold uppercase tracking-wider text-slate-400">
                    Latest Version
                  </p>

                  <p className="mt-2 text-2xl font-bold text-slate-950">
                    {latestVersion
                      ? `v${latestVersion.version_number}`
                      : "—"}
                  </p>
                </div>

                <div className="rounded-xl bg-emerald-100 p-3 text-emerald-700">
                  <CheckCircle2 size={20} />
                </div>
              </div>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-bold uppercase tracking-wider text-slate-400">
                    First Recorded
                  </p>

                  <p className="mt-2 text-sm font-bold text-slate-900">
                    {firstVersion
                      ? formatShortDate(
                          firstVersion.created_at,
                        )
                      : "—"}
                  </p>
                </div>

                <div className="rounded-xl bg-violet-100 p-3 text-violet-700">
                  <CalendarDays size={20} />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* =====================================================
          ERROR
      ====================================================== */}

      {error && (
        <div className="flex flex-col gap-3 rounded-2xl border border-red-200 bg-red-50 px-5 py-4 text-sm font-medium text-red-700 sm:flex-row sm:items-center">
          <AlertCircle
            size={20}
            className="shrink-0"
          />

          <span className="flex-1">{error}</span>

          <button
            type="button"
            onClick={() => loadHistory()}
            className="rounded-lg border border-red-200 bg-white px-3 py-2 text-xs font-bold text-red-700 transition hover:bg-red-100"
          >
            Try Again
          </button>
        </div>
      )}

      {/* =====================================================
          LOADING
      ====================================================== */}

      {loading ? (
        <div className="rounded-3xl border border-slate-200 bg-white p-14 text-center shadow-sm">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-50">
            <RefreshCw
              size={23}
              className="animate-spin text-blue-600"
            />
          </div>

          <h2 className="mt-5 text-base font-bold text-slate-900">
            Loading decision history
          </h2>

          <p className="mt-2 text-sm text-slate-500">
            Retrieving recorded versions and activity...
          </p>
        </div>
      ) : (
        <div className="grid gap-6 lg:grid-cols-[390px_minmax(0,1fr)]">
          {/* =================================================
              VERSION TIMELINE
          ================================================== */}

          <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm md:p-6">
            <div className="mb-6">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2">
                    <GitBranch
                      size={19}
                      className="text-blue-600"
                    />

                    <h2 className="text-lg font-bold text-slate-950">
                      Version Timeline
                    </h2>
                  </div>

                  <p className="mt-1 text-sm leading-6 text-slate-500">
                    Select any recorded version to inspect
                    its state.
                  </p>
                </div>

                <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-bold text-slate-500">
                  {versions.length}
                </span>
              </div>
            </div>

            {versions.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-9 text-center">
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-white shadow-sm">
                  <FileText
                    size={23}
                    className="text-slate-400"
                  />
                </div>

                <p className="mt-4 text-sm font-bold text-slate-700">
                  No versions available
                </p>

                <p className="mt-1 text-xs leading-5 text-slate-500">
                  Version records will appear here as the
                  decision changes.
                </p>
              </div>
            ) : (
              <div className="relative space-y-3">
                {versions.map((version, index) => {
                  const selected =
                    selectedVersion?.version_number ===
                    version.version_number;

                  const isLatest =
                    index === 0;

                  return (
                    <div
                      key={version.id}
                      className="relative"
                    >
                      {index <
                        versions.length - 1 && (
                        <div className="absolute left-5 top-12 bottom-[-12px] w-px bg-slate-200" />
                      )}

                      <button
                        type="button"
                        onClick={() =>
                          setSelectedVersion(version)
                        }
                        className={`group relative z-10 w-full rounded-2xl border p-4 text-left transition ${
                          selected
                            ? "border-blue-300 bg-blue-50 shadow-sm"
                            : "border-slate-200 bg-white hover:border-blue-200 hover:bg-slate-50"
                        }`}
                      >
                        <div className="flex items-start gap-3">
                          <div
                            className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-xs font-extrabold ${
                              selected
                                ? "bg-blue-600 text-white"
                                : "bg-slate-100 text-slate-600 group-hover:bg-blue-100 group-hover:text-blue-700"
                            }`}
                          >
                            v{version.version_number}
                          </div>

                          <div className="min-w-0 flex-1">
                            <div className="flex flex-wrap items-center gap-2">
                              <p className="truncate text-sm font-bold text-slate-900">
                                {version.title ||
                                  "Untitled Decision"}
                              </p>

                              {isLatest && (
                                <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-extrabold uppercase tracking-wide text-emerald-700">
                                  Latest
                                </span>
                              )}
                            </div>

                            <div className="mt-1.5 flex flex-wrap items-center gap-2">
                              <span
                                className={`inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-[10px] font-bold ${statusClasses(
                                  version.status,
                                )}`}
                              >
                                <span
                                  className={`h-1.5 w-1.5 rounded-full ${statusDot(
                                    version.status,
                                  )}`}
                                />

                                {version.status ||
                                  "Unknown"}
                              </span>

                              <span className="text-[11px] text-slate-400">
                                {formatShortDate(
                                  version.created_at,
                                )}
                              </span>
                            </div>

                            <p className="mt-2 line-clamp-2 text-xs leading-5 text-slate-500">
                              {version.problem_statement ||
                                "No problem statement recorded."}
                            </p>
                          </div>

                          <ChevronRight
                            size={17}
                            className={`mt-1 shrink-0 transition ${
                              selected
                                ? "text-blue-600"
                                : "text-slate-300 group-hover:text-blue-500"
                            }`}
                          />
                        </div>
                      </button>
                    </div>
                  );
                })}
              </div>
            )}
          </section>

          {/* =================================================
              DETAILS + ACTIVITY
          ================================================== */}

          <section className="space-y-6">
            {selectedVersion ? (
              <div className="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">
                {/* VERSION HEADER */}

                <div className="border-b border-slate-100 bg-slate-50/70 p-6 md:p-7">
                  <div className="flex flex-col gap-5 md:flex-row md:items-start md:justify-between">
                    <div className="min-w-0">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="rounded-full bg-blue-600 px-3 py-1.5 text-xs font-extrabold text-white">
                          Version{" "}
                          {selectedVersion.version_number}
                        </span>

                        <span
                          className={`rounded-full border px-3 py-1.5 text-xs font-bold ${statusClasses(
                            selectedVersion.status,
                          )}`}
                        >
                          {selectedVersion.status ||
                            "Unknown"}
                        </span>
                      </div>

                      <h2 className="mt-4 text-xl font-bold leading-8 text-slate-950 md:text-2xl">
                        {selectedVersion.title ||
                          "Untitled Decision"}
                      </h2>

                      <div className="mt-3 flex flex-wrap items-center gap-x-5 gap-y-2 text-xs text-slate-500">
                        <span className="inline-flex items-center gap-1.5">
                          <Clock3 size={14} />
                          {formatDate(
                            selectedVersion.created_at,
                          )}
                        </span>

                        <span className="inline-flex items-center gap-1.5">
                          <User size={14} />
                          User{" "}
                          {selectedVersion.created_by ??
                            "—"}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* VERSION CONTENT */}

                <div className="space-y-6 p-6 md:p-7">
                  <div>
                    <div className="mb-2 flex items-center gap-2">
                      <FileText
                        size={15}
                        className="text-blue-600"
                      />

                      <p className="text-xs font-extrabold uppercase tracking-wider text-slate-400">
                        Problem Statement
                      </p>
                    </div>

                    <div className="rounded-2xl border border-slate-200 bg-white p-5 text-sm leading-7 text-slate-700">
                      {selectedVersion.problem_statement ||
                        "No problem statement recorded."}
                    </div>
                  </div>

                  <div>
                    <div className="mb-2 flex items-center gap-2">
                      <FileText
                        size={15}
                        className="text-blue-600"
                      />

                      <p className="text-xs font-extrabold uppercase tracking-wider text-slate-400">
                        Description
                      </p>
                    </div>

                    <div className="rounded-2xl border border-slate-200 bg-white p-5 text-sm leading-7 text-slate-700">
                      {selectedVersion.description ||
                        "No description recorded."}
                    </div>
                  </div>

                  <div className="grid gap-4 sm:grid-cols-2">
                    <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                      <p className="text-xs font-bold uppercase tracking-wide text-slate-400">
                        Category
                      </p>

                      <p className="mt-2 text-sm font-bold text-slate-800">
                        {selectedVersion.category ||
                          "—"}
                      </p>
                    </div>

                    <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                      <p className="text-xs font-bold uppercase tracking-wide text-slate-400">
                        Created By
                      </p>

                      <div className="mt-2 flex items-center gap-2 text-sm font-bold text-slate-800">
                        <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-white text-slate-500">
                          <User size={14} />
                        </span>

                        User{" "}
                        {selectedVersion.created_by ??
                          "—"}
                      </div>
                    </div>

                    <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                      <p className="text-xs font-bold uppercase tracking-wide text-slate-400">
                        Version
                      </p>

                      <p className="mt-2 text-sm font-bold text-slate-800">
                        v
                        {
                          selectedVersion.version_number
                        }
                      </p>
                    </div>

                    <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                      <p className="text-xs font-bold uppercase tracking-wide text-slate-400">
                        Recorded
                      </p>

                      <p className="mt-2 text-sm font-bold text-slate-800">
                        {formatShortDate(
                          selectedVersion.created_at,
                        )}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="rounded-3xl border border-dashed border-slate-300 bg-white p-12 text-center shadow-sm">
                <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-100">
                  <GitBranch
                    size={26}
                    className="text-slate-400"
                  />
                </div>

                <p className="mt-4 text-sm font-bold text-slate-700">
                  Select a version
                </p>

                <p className="mt-1 text-xs text-slate-500">
                  Choose a version from the timeline to
                  inspect its recorded state.
                </p>
              </div>
            )}

            {/* =================================================
                ACTIVITY TIMELINE
            ================================================== */}

            <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm md:p-7">
              <div className="mb-7 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <Clock3
                      size={19}
                      className="text-blue-600"
                    />

                    <h2 className="text-lg font-bold text-slate-950">
                      Activity Timeline
                    </h2>
                  </div>

                  <p className="mt-1 text-sm leading-6 text-slate-500">
                    Recorded events associated with this
                    decision.
                  </p>
                </div>

                <span className="w-fit rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-500">
                  {history.length} events
                </span>
              </div>

              {history.length === 0 ? (
                <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-9 text-center">
                  <Clock3
                    className="mx-auto text-slate-400"
                    size={25}
                  />

                  <p className="mt-3 text-sm font-bold text-slate-700">
                    No history events available
                  </p>

                  <p className="mt-1 text-xs text-slate-500">
                    Decision activity will appear here as
                    events are recorded.
                  </p>
                </div>
              ) : (
                <div className="space-y-0">
                  {history.map((event, index) => {
                    const ActionIcon =
                      getActionIcon(event.action);

                    return (
                      <div
                        key={event.id ?? index}
                        className="relative flex gap-4"
                      >
                        {/* TIMELINE */}

                        <div className="relative flex w-9 shrink-0 justify-center">
                          <div className="relative z-10 flex h-9 w-9 items-center justify-center rounded-full border border-blue-100 bg-blue-50 text-blue-600">
                            <ActionIcon size={16} />
                          </div>

                          {index <
                            history.length - 1 && (
                            <div className="absolute left-1/2 top-9 bottom-0 w-px -translate-x-1/2 bg-slate-200" />
                          )}
                        </div>

                        {/* EVENT */}

                        <div
                          className={`min-w-0 flex-1 ${
                            index <
                            history.length - 1
                              ? "pb-7"
                              : "pb-1"
                          }`}
                        >
                          <div className="rounded-2xl border border-slate-200 bg-white p-4 transition hover:border-blue-100 hover:bg-slate-50">
                            <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                              <div className="min-w-0">
                                <div className="flex flex-wrap items-center gap-2">
                                  <p className="text-sm font-bold text-slate-900">
                                    {getActionLabel(
                                      event.action,
                                    )}
                                  </p>

                                  {event.entity_type && (
                                    <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-bold text-slate-500">
                                      {
                                        event.entity_type
                                      }
                                    </span>
                                  )}
                                </div>

                                <p className="mt-1 text-xs text-slate-400">
                                  {formatDate(
                                    event.created_at,
                                  )}
                                </p>
                              </div>

                              {event.user_id !==
                                undefined &&
                                event.user_id !==
                                  null && (
                                  <span className="inline-flex shrink-0 items-center gap-1.5 text-xs font-medium text-slate-400">
                                    <User size={13} />
                                    User{" "}
                                    {event.user_id}
                                  </span>
                                )}
                            </div>

                            <p className="mt-3 text-sm leading-6 text-slate-600">
                              {event.description ||
                                `${event.entity_type || "Decision"} activity recorded.`}
                            </p>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </section>
        </div>
      )}
    </div>
  );
}