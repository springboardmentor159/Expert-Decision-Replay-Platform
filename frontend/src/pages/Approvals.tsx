import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  AlertCircle,
  ArrowLeft,
  CheckCircle2,
  ChevronRight,
  Clock3,
  ExternalLink,
  FileCheck2,
  Loader2,
  RefreshCw,
  ShieldCheck,
  XCircle,
} from "lucide-react";

import {
  getPendingApprovals,
  updateApproval,
  type Approval,
} from "../services/approvals";

import { getApiErrorMessage } from "../utils/errors";

function formatDate(value?: string) {
  if (!value) return "—";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString();
}

export default function Approvals() {
  const navigate = useNavigate();

  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [updatingId, setUpdatingId] = useState<number | null>(null);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function loadApprovals(
    showFullLoader = true,
  ) {
    try {
      if (showFullLoader) {
        setLoading(true);
      } else {
        setRefreshing(true);
      }

      setError("");

      const response = await getPendingApprovals();

      setApprovals(response);
    } catch (err: any) {
      console.error(err);

      setError(
        getApiErrorMessage(
          err,
          "Unable to load pending approvals.",
        ),
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  useEffect(() => {
    loadApprovals();
  }, []);

  async function handleApproval(
    approvalId: number,
    status: "Approved" | "Rejected",
  ) {
    const action =
      status === "Approved"
        ? "approve"
        : "reject";

    const confirmed = window.confirm(
      `Are you sure you want to ${action} this approval?`,
    );

    if (!confirmed) {
      return;
    }

    try {
      setUpdatingId(approvalId);
      setError("");
      setSuccess("");

      await updateApproval(
        approvalId,
        status,
      );

      setSuccess(
        `Approval ${status.toLowerCase()} successfully.`,
      );

      await loadApprovals(false);

      setTimeout(() => {
        setSuccess("");
      }, 3000);
    } catch (err: any) {
      console.error(err);

      setError(
        getApiErrorMessage(
          err,
          `Unable to ${action} approval.`,
        ),
      );
    } finally {
      setUpdatingId(null);
    }
  }

  const totalPending = approvals.length;

  const approvalLevels = useMemo(() => {
    return new Set(
      approvals.map(
        (approval) => approval.approval_level,
      ),
    ).size;
  }, [approvals]);

  const latestApproval = useMemo(() => {
    if (!approvals.length) {
      return null;
    }

    return approvals[0];
  }, [approvals]);

  if (loading) {
    return (
      <div className="mx-auto flex min-h-[500px] max-w-7xl items-center justify-center">
        <div className="text-center">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-50">
            <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
          </div>

          <h2 className="mt-4 text-base font-bold text-slate-900">
            Loading approvals
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Retrieving decisions waiting for review...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      {/* =====================================================
          HEADER
      ====================================================== */}

      <section className="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">
        <div className="relative p-6 md:p-8">
          <div className="absolute right-0 top-0 h-48 w-48 rounded-full bg-blue-50 blur-3xl" />

          <div className="relative flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <button
                type="button"
                onClick={() =>
                  navigate("/dashboard")
                }
                className="mb-5 inline-flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100 hover:text-blue-600"
              >
                <ArrowLeft size={17} />
                Back to Dashboard
              </button>

              <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-blue-100 bg-blue-50 px-3 py-1.5 text-xs font-bold text-blue-700">
                <ShieldCheck size={14} />
                APPROVAL WORKFLOW
              </div>

              <h1 className="text-2xl font-bold tracking-tight text-slate-950 md:text-3xl">
                Approvals
              </h1>

              <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
                Review decisions assigned to you and
                approve or reject them as part of the
                decision workflow.
              </p>
            </div>

            <button
              type="button"
              onClick={() => loadApprovals(false)}
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
              Refresh
            </button>
          </div>

          {/* =================================================
              SUMMARY
          ================================================== */}

          <div className="relative mt-7 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-2xl border border-amber-200 bg-amber-50/60 p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-bold uppercase tracking-wider text-amber-600">
                    Pending
                  </p>

                  <p className="mt-2 text-3xl font-bold text-slate-950">
                    {totalPending}
                  </p>

                  <p className="mt-1 text-xs text-amber-700">
                    Awaiting your review
                  </p>
                </div>

                <div className="rounded-xl bg-white p-3 shadow-sm">
                  <Clock3
                    size={21}
                    className="text-amber-600"
                  />
                </div>
              </div>
            </div>

            <div className="rounded-2xl border border-blue-200 bg-blue-50/60 p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-bold uppercase tracking-wider text-blue-600">
                    Approval Levels
                  </p>

                  <p className="mt-2 text-3xl font-bold text-slate-950">
                    {approvalLevels}
                  </p>

                  <p className="mt-1 text-xs text-blue-700">
                    Active levels
                  </p>
                </div>

                <div className="rounded-xl bg-white p-3 shadow-sm">
                  <ShieldCheck
                    size={21}
                    className="text-blue-600"
                  />
                </div>
              </div>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-bold uppercase tracking-wider text-slate-400">
                    Workflow
                  </p>

                  <p className="mt-2 text-lg font-bold text-slate-950">
                    Review
                  </p>

                  <p className="mt-1 text-xs text-slate-500">
                    Decisions awaiting action
                  </p>
                </div>

                <div className="rounded-xl bg-white p-3 shadow-sm">
                  <FileCheck2
                    size={21}
                    className="text-slate-600"
                  />
                </div>
              </div>
            </div>

            <div className="rounded-2xl border border-emerald-200 bg-emerald-50/60 p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-bold uppercase tracking-wider text-emerald-600">
                    Current State
                  </p>

                  <p className="mt-2 text-lg font-bold text-slate-950">
                    {totalPending > 0
                      ? "Awaiting Review"
                      : "All Clear"}
                  </p>

                  <p className="mt-1 text-xs text-emerald-700">
                    {latestApproval
                      ? `Latest: #${latestApproval.id}`
                      : "No pending items"}
                  </p>
                </div>

                <div className="rounded-xl bg-white p-3 shadow-sm">
                  <CheckCircle2
                    size={21}
                    className="text-emerald-600"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* =====================================================
          ALERTS
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
            onClick={() => loadApprovals()}
            className="rounded-lg border border-red-200 bg-white px-3 py-2 text-xs font-bold text-red-700 transition hover:bg-red-100"
          >
            Try Again
          </button>
        </div>
      )}

      {success && (
        <div className="flex items-center gap-3 rounded-2xl border border-emerald-200 bg-emerald-50 px-5 py-4 text-sm font-medium text-emerald-700">
          <CheckCircle2
            size={20}
            className="shrink-0"
          />

          <span>{success}</span>
        </div>
      )}

      {/* =====================================================
          SECTION HEADER
      ====================================================== */}

      {approvals.length > 0 && (
        <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h2 className="text-lg font-bold text-slate-950">
              Pending Review
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              These decisions require an approval action.
            </p>
          </div>

          <span className="w-fit rounded-full bg-slate-100 px-3 py-1.5 text-xs font-bold text-slate-500">
            {approvals.length}{" "}
            {approvals.length === 1
              ? "approval"
              : "approvals"}
          </span>
        </div>
      )}

      {/* =====================================================
          EMPTY STATE
      ====================================================== */}

      {approvals.length === 0 && (
        <section className="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">
          <div className="px-6 py-16 text-center md:px-10">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-emerald-50">
              <CheckCircle2
                size={31}
                className="text-emerald-600"
              />
            </div>

            <div className="mx-auto mt-5 max-w-md">
              <h2 className="text-xl font-bold text-slate-950">
                No pending approvals
              </h2>

              <p className="mt-2 text-sm leading-6 text-slate-500">
                There are currently no decisions waiting
                for your approval. New assignments will
                appear here when they enter your review
                queue.
              </p>
            </div>

            <div className="mt-7 flex flex-col justify-center gap-3 sm:flex-row">
              <button
                type="button"
                onClick={() =>
                  navigate("/decisions")
                }
                className="inline-flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-bold text-white transition hover:bg-blue-700"
              >
                View Decisions
                <ExternalLink size={16} />
              </button>

              <button
                type="button"
                onClick={() =>
                  loadApprovals(false)
                }
                disabled={refreshing}
                className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-5 py-2.5 text-sm font-bold text-slate-700 transition hover:bg-slate-50 disabled:opacity-60"
              >
                <RefreshCw
                  size={16}
                  className={
                    refreshing
                      ? "animate-spin"
                      : ""
                  }
                />
                Check Again
              </button>
            </div>
          </div>
        </section>
      )}

      {/* =====================================================
          APPROVAL CARDS
      ====================================================== */}

      {approvals.length > 0 && (
        <div className="space-y-5">
          {approvals.map((approval) => {
            const isUpdating =
              updatingId === approval.id;

            return (
              <article
                key={approval.id}
                className="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm transition hover:border-blue-200 hover:shadow-md"
              >
                {/* TOP ACCENT */}

                <div className="h-1 bg-blue-600" />

                <div className="p-5 md:p-6">
                  {/* =================================================
                      CARD HEADER
                  ================================================== */}

                  <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
                    <div className="min-w-0">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="inline-flex items-center gap-1.5 rounded-full border border-amber-200 bg-amber-50 px-3 py-1 text-xs font-bold text-amber-700">
                          <span className="h-1.5 w-1.5 rounded-full bg-amber-500" />
                          {approval.status}
                        </span>

                        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-500">
                          Approval #{approval.id}
                        </span>
                      </div>

                      <h3 className="mt-3 text-xl font-bold text-slate-950">
                        Decision #
                        {approval.decision_id}
                      </h3>

                      <p className="mt-1 text-sm leading-6 text-slate-500">
                        This decision is awaiting your
                        approval action.
                      </p>
                    </div>

                    <div className="flex w-fit items-center gap-2 rounded-2xl border border-blue-100 bg-blue-50 px-4 py-3">
                      <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-white text-blue-600 shadow-sm">
                        <ShieldCheck size={18} />
                      </div>

                      <div>
                        <p className="text-[10px] font-bold uppercase tracking-wider text-blue-500">
                          Approval Level
                        </p>

                        <p className="text-sm font-extrabold text-blue-800">
                          Level{" "}
                          {approval.approval_level}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* =================================================
                      DETAILS
                  ================================================== */}

                  <div className="mt-6 grid gap-3 border-y border-slate-100 py-5 sm:grid-cols-2 lg:grid-cols-4">
                    <div className="rounded-2xl bg-slate-50 p-4">
                      <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                        Decision
                      </p>

                      <p className="mt-2 text-sm font-bold text-slate-800">
                        #{approval.decision_id}
                      </p>
                    </div>

                    <div className="rounded-2xl bg-slate-50 p-4">
                      <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                        Reviewer
                      </p>

                      <p className="mt-2 text-sm font-bold text-slate-800">
                        User #{approval.reviewer_id}
                      </p>
                    </div>

                    <div className="rounded-2xl bg-slate-50 p-4">
                      <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                        Approval Level
                      </p>

                      <p className="mt-2 text-sm font-bold text-slate-800">
                        Level{" "}
                        {approval.approval_level}
                      </p>
                    </div>

                    <div className="rounded-2xl bg-slate-50 p-4">
                      <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                        Last Updated
                      </p>

                      <p className="mt-2 text-xs font-bold text-slate-700">
                        {formatDate(
                          approval.updated_at,
                        )}
                      </p>
                    </div>
                  </div>

                  {/* =================================================
                      ACTION ROW
                  ================================================== */}

                  <div className="mt-5 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                    <button
                      type="button"
                      onClick={() =>
                        navigate(
                          `/decisions/${approval.decision_id}`,
                        )
                      }
                      className="group inline-flex w-fit items-center gap-2 text-sm font-bold text-blue-600 transition hover:text-blue-700"
                    >
                      <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-50 transition group-hover:bg-blue-100">
                        <ExternalLink size={15} />
                      </span>

                      Review Decision

                      <ChevronRight
                        size={15}
                        className="transition group-hover:translate-x-0.5"
                      />
                    </button>

                    <div className="flex flex-col gap-3 sm:flex-row">
                      <button
                        type="button"
                        disabled={isUpdating}
                        onClick={() =>
                          handleApproval(
                            approval.id,
                            "Rejected",
                          )
                        }
                        className="inline-flex items-center justify-center gap-2 rounded-xl border border-red-200 bg-white px-5 py-3 text-sm font-bold text-red-600 transition hover:bg-red-50 hover:border-red-300 disabled:cursor-not-allowed disabled:opacity-60"
                      >
                        {isUpdating ? (
                          <Loader2
                            size={16}
                            className="animate-spin"
                          />
                        ) : (
                          <XCircle size={17} />
                        )}

                        Reject
                      </button>

                      <button
                        type="button"
                        disabled={isUpdating}
                        onClick={() =>
                          handleApproval(
                            approval.id,
                            "Approved",
                          )
                        }
                        className="inline-flex items-center justify-center gap-2 rounded-xl bg-emerald-600 px-6 py-3 text-sm font-bold text-white shadow-sm transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-60"
                      >
                        {isUpdating ? (
                          <Loader2
                            size={16}
                            className="animate-spin"
                          />
                        ) : (
                          <CheckCircle2 size={17} />
                        )}

                        Approve Decision
                      </button>
                    </div>
                  </div>
                </div>
              </article>
            );
          })}
        </div>
      )}
    </div>
  );
}