import { useEffect, useMemo, useState } from "react";
import {
  ArrowLeft,
  Edit3,
  MessageCircle,
  Plus,
  Send,
  Trash2,
  X,
  Loader2,
  RefreshCw,
  AlertCircle,
  ExternalLink,
  Users,
  MessageSquareText,
  CircleDot,
  Clock3,
  Sparkles,
} from "lucide-react";
import { useNavigate, useParams } from "react-router-dom";

import {
  createThread,
  deleteThread,
  getThreads,
  updateThread,
  type DiscussionThread,
} from "../services/discussions";

import { getApiErrorMessage } from "../utils/errors";

function formatDate(value?: string) {
  if (!value) {
    return "—";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString();
}

function getStatusClasses(status?: string) {
  const normalized = status?.toLowerCase();

  if (normalized === "open") {
    return "border-emerald-200 bg-emerald-50 text-emerald-700";
  }

  if (normalized === "closed") {
    return "border-slate-200 bg-slate-100 text-slate-600";
  }

  return "border-blue-200 bg-blue-50 text-blue-700";
}

function getStatusDot(status?: string) {
  const normalized = status?.toLowerCase();

  if (normalized === "open") {
    return "bg-emerald-500";
  }

  if (normalized === "closed") {
    return "bg-slate-400";
  }

  return "bg-blue-500";
}

export default function Discussions() {
  const { decisionId } = useParams<{
    decisionId: string;
  }>();

  const navigate = useNavigate();

  const numericDecisionId = Number(decisionId);

  const [threads, setThreads] = useState<
    DiscussionThread[]
  >([]);

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] =
    useState(false);
  const [submitting, setSubmitting] =
    useState(false);
  const [deletingId, setDeletingId] =
    useState<number | null>(null);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [showCreate, setShowCreate] =
    useState(false);

  const [editingThread, setEditingThread] =
    useState<DiscussionThread | null>(null);

  const [title, setTitle] = useState("");
  const [description, setDescription] =
    useState("");
  const [status, setStatus] = useState("Open");

  /* =========================
     LOAD THREADS
  ========================= */

  async function loadThreads(
    showFullLoader = true,
  ) {
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

      const data =
        await getThreads(numericDecisionId);

      setThreads(data);
    } catch (err: any) {
      console.error(err);

      setError(
        getApiErrorMessage(
          err,
          "Unable to load discussion threads.",
        ),
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  useEffect(() => {
    loadThreads();
  }, [numericDecisionId]);

  /* =========================
     SUMMARY
  ========================= */

  const openThreads = useMemo(
    () =>
      threads.filter(
        (thread) =>
          (thread.status || "Open").toLowerCase() ===
          "open",
      ).length,
    [threads],
  );

  const closedThreads = useMemo(
    () =>
      threads.filter(
        (thread) =>
          (thread.status || "").toLowerCase() ===
          "closed",
      ).length,
    [threads],
  );

  /* =========================
     FORM
  ========================= */

  function resetForm() {
    setTitle("");
    setDescription("");
    setStatus("Open");
    setEditingThread(null);
    setShowCreate(false);
  }

  function startCreate() {
    setEditingThread(null);
    setTitle("");
    setDescription("");
    setStatus("Open");
    setError("");
    setSuccess("");
    setShowCreate(true);

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  }

  function startEdit(
    thread: DiscussionThread,
  ) {
    setEditingThread(thread);
    setTitle(thread.title || "");
    setDescription(thread.description || "");
    setStatus(thread.status || "Open");
    setError("");
    setSuccess("");
    setShowCreate(true);

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  }

  /* =========================
     CREATE / UPDATE
  ========================= */

  async function handleSubmit(
    event: React.FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    if (
      !Number.isInteger(numericDecisionId) ||
      numericDecisionId <= 0
    ) {
      setError("Invalid decision ID.");
      return;
    }

    if (!title.trim()) {
      setError("Thread title is required.");
      return;
    }

    if (!description.trim()) {
      setError(
        "Thread description is required.",
      );
      return;
    }

    try {
      setSubmitting(true);
      setError("");
      setSuccess("");

      if (editingThread) {
        await updateThread(
          editingThread.id,
          {
            title: title.trim(),
            description: description.trim(),
            status,
          },
        );

        setSuccess(
          "Discussion thread updated successfully.",
        );
      } else {
        await createThread(
          numericDecisionId,
          {
            title: title.trim(),
            description: description.trim(),
          },
        );

        setSuccess(
          "Discussion thread created successfully.",
        );
      }

      resetForm();

      await loadThreads(false);

      setTimeout(() => {
        setSuccess("");
      }, 3000);
    } catch (err: any) {
      console.error(err);

      setError(
        getApiErrorMessage(
          err,
          "Unable to save discussion thread.",
        ),
      );
    } finally {
      setSubmitting(false);
    }
  }

  /* =========================
     DELETE
  ========================= */

  async function handleDelete(
    thread: DiscussionThread,
  ) {
    const confirmed = window.confirm(
      `Are you sure you want to delete "${thread.title}"? This action cannot be undone.`,
    );

    if (!confirmed) {
      return;
    }

    try {
      setDeletingId(thread.id);
      setError("");
      setSuccess("");

      await deleteThread(thread.id);

      setThreads((current) =>
        current.filter(
          (item) => item.id !== thread.id,
        ),
      );

      setSuccess(
        "Discussion thread deleted successfully.",
      );

      setTimeout(() => {
        setSuccess("");
      }, 3000);
    } catch (err: any) {
      console.error(err);

      setError(
        getApiErrorMessage(
          err,
          "Unable to delete discussion thread.",
        ),
      );
    } finally {
      setDeletingId(null);
    }
  }

  /* =========================
     INVALID ID
  ========================= */

  if (
    !Number.isInteger(numericDecisionId) ||
    numericDecisionId <= 0
  ) {
    return (
      <div className="mx-auto max-w-6xl">
        <button
          type="button"
          onClick={() =>
            navigate("/decisions")
          }
          className="mb-6 inline-flex items-center gap-2 text-sm font-medium text-slate-600 transition hover:text-blue-600"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Decisions
        </button>

        <div className="flex items-center gap-3 rounded-2xl border border-red-200 bg-red-50 p-6 text-sm font-medium text-red-700">
          <AlertCircle className="h-5 w-5" />
          Invalid decision ID.
        </div>
      </div>
    );
  }

  /* =========================
     LOADING
  ========================= */

  if (loading) {
    return (
      <div className="flex min-h-[500px] items-center justify-center">
        <div className="text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-50">
            <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
          </div>

          <p className="mt-4 text-sm font-semibold text-slate-600">
            Loading discussions...
          </p>

          <p className="mt-1 text-xs text-slate-400">
            Preparing the collaboration workspace
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl space-y-6">

      {/* =========================
          BACK
      ========================= */}

      <button
        type="button"
        onClick={() =>
          navigate(
            `/decisions/${numericDecisionId}`,
          )
        }
        className="inline-flex items-center gap-2 text-sm font-medium text-slate-600 transition hover:text-blue-600"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Decision
      </button>

      {/* =========================
          HERO
      ========================= */}

      <section className="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">

        <div className="relative overflow-hidden bg-gradient-to-br from-blue-50 via-white to-indigo-50 px-6 py-8 sm:px-8">

          <div className="absolute -right-16 -top-16 h-48 w-48 rounded-full bg-blue-100/60 blur-3xl" />

          <div className="relative flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">

            <div className="flex items-start gap-4">

              <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-blue-600 text-white shadow-lg shadow-blue-600/20">
                <MessageCircle className="h-7 w-7" />
              </div>

              <div>

                <div className="mb-2 inline-flex items-center gap-2 rounded-full border border-blue-100 bg-white/80 px-3 py-1 text-xs font-bold text-blue-700">
                  <Sparkles className="h-3.5 w-3.5" />
                  Collaboration Workspace
                </div>

                <h1 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
                  Discussions
                </h1>

                <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
                  Collaborate around Decision #
                  {numericDecisionId} through focused
                  discussion threads and documented
                  viewpoints.
                </p>

              </div>

            </div>

            <div className="flex flex-wrap gap-3">

              <button
                type="button"
                onClick={() =>
                  loadThreads(false)
                }
                disabled={refreshing}
                className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
              >
                <RefreshCw
                  className={`h-4 w-4 ${
                    refreshing
                      ? "animate-spin"
                      : ""
                  }`}
                />
                Refresh
              </button>

              <button
                type="button"
                onClick={startCreate}
                className="inline-flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white shadow-sm shadow-blue-600/20 transition hover:bg-blue-700"
              >
                <Plus className="h-5 w-5" />
                New Discussion
              </button>

            </div>

          </div>
        </div>

        {/* =========================
            SUMMARY
        ========================= */}

        <div className="grid border-t border-slate-100 sm:grid-cols-3">

          <div className="border-b border-slate-100 p-5 sm:border-r sm:border-b-0">

            <div className="flex items-center justify-between">

              <div>
                <p className="text-xs font-bold uppercase tracking-wide text-slate-400">
                  Total Threads
                </p>

                <p className="mt-2 text-2xl font-bold text-slate-900">
                  {threads.length}
                </p>

                <p className="mt-1 text-xs text-slate-500">
                  Documented conversations
                </p>
              </div>

              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
                <MessageSquareText className="h-5 w-5" />
              </div>

            </div>
          </div>

          <div className="border-b border-slate-100 p-5 sm:border-r sm:border-b-0">

            <div className="flex items-center justify-between">

              <div>
                <p className="text-xs font-bold uppercase tracking-wide text-slate-400">
                  Open
                </p>

                <p className="mt-2 text-2xl font-bold text-emerald-600">
                  {openThreads}
                </p>

                <p className="mt-1 text-xs text-slate-500">
                  Active conversations
                </p>
              </div>

              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600">
                <CircleDot className="h-5 w-5" />
              </div>

            </div>
          </div>

          <div className="p-5">

            <div className="flex items-center justify-between">

              <div>
                <p className="text-xs font-bold uppercase tracking-wide text-slate-400">
                  Closed
                </p>

                <p className="mt-2 text-2xl font-bold text-slate-700">
                  {closedThreads}
                </p>

                <p className="mt-1 text-xs text-slate-500">
                  Completed conversations
                </p>
              </div>

              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-100 text-slate-500">
                <Clock3 className="h-5 w-5" />
              </div>

            </div>
          </div>

        </div>
      </section>

      {/* =========================
          ALERTS
      ========================= */}

      {error && (
        <div className="flex items-start gap-3 rounded-2xl border border-red-200 bg-red-50 px-5 py-4 text-sm font-medium text-red-700">

          <AlertCircle className="mt-0.5 h-5 w-5 shrink-0" />

          <span className="flex-1">
            {error}
          </span>

          <button
            type="button"
            onClick={() => setError("")}
            className="rounded-lg p-1 text-red-500 transition hover:bg-red-100 hover:text-red-700"
            aria-label="Close error"
          >
            <X className="h-4 w-4" />
          </button>

        </div>
      )}

      {success && (
        <div className="flex items-center gap-3 rounded-2xl border border-emerald-200 bg-emerald-50 px-5 py-4 text-sm font-medium text-emerald-700">

          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white text-emerald-600">
            <MessageCircle className="h-4 w-4" />
          </div>

          <span>{success}</span>

        </div>
      )}

      {/* =========================
          CREATE / EDIT FORM
      ========================= */}

      {showCreate && (
        <section className="overflow-hidden rounded-3xl border border-blue-100 bg-white shadow-sm">

          <div className="border-b border-slate-100 bg-gradient-to-r from-blue-50 to-white px-6 py-6 sm:px-8">

            <div className="flex items-start justify-between gap-4">

              <div className="flex items-start gap-3">

                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-600 text-white">
                  {editingThread ? (
                    <Edit3 className="h-5 w-5" />
                  ) : (
                    <Plus className="h-5 w-5" />
                  )}
                </div>

                <div>

                  <h2 className="text-lg font-bold text-slate-900">
                    {editingThread
                      ? "Edit Discussion"
                      : "Start a Discussion"}
                  </h2>

                  <p className="mt-1 text-sm text-slate-500">
                    {editingThread
                      ? "Update the discussion details and status."
                      : "Create a focused conversation around this decision."}
                  </p>

                </div>

              </div>

              <button
                type="button"
                onClick={() => {
                  resetForm();
                  setError("");
                }}
                disabled={submitting}
                className="rounded-xl p-2 text-slate-400 transition hover:bg-white hover:text-slate-700 disabled:cursor-not-allowed disabled:opacity-50"
                aria-label="Close discussion form"
              >
                <X className="h-5 w-5" />
              </button>

            </div>
          </div>

          <form
            onSubmit={handleSubmit}
            className="space-y-6 p-6 sm:p-8"
          >

            {/* TITLE */}

            <div>
              <div className="mb-2 flex items-center justify-between gap-3">

                <label
                  htmlFor="discussion-title"
                  className="text-sm font-semibold text-slate-700"
                >
                  Discussion Title *
                </label>

                <span className="text-xs text-slate-400">
                  {title.length}/150
                </span>

              </div>

              <input
                id="discussion-title"
                type="text"
                maxLength={150}
                value={title}
                onChange={(event) =>
                  setTitle(event.target.value)
                }
                placeholder="e.g. Should we choose the cloud deployment option?"
                className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-500/10"
              />
            </div>

            {/* DESCRIPTION */}

            <div>
              <div className="mb-2 flex items-center justify-between gap-3">

                <label
                  htmlFor="discussion-description"
                  className="text-sm font-semibold text-slate-700"
                >
                  Discussion Description *
                </label>

                <span className="text-xs text-slate-400">
                  {description.length}/1000
                </span>

              </div>

              <textarea
                id="discussion-description"
                maxLength={1000}
                value={description}
                onChange={(event) =>
                  setDescription(
                    event.target.value,
                  )
                }
                placeholder="Explain the topic, question, concern, or decision point that should be discussed..."
                rows={6}
                className="w-full resize-y rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm leading-7 text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-500/10"
              />
            </div>

            {/* STATUS */}

            {editingThread && (
              <div className="max-w-md">

                <label
                  htmlFor="discussion-status"
                  className="mb-2 block text-sm font-semibold text-slate-700"
                >
                  Discussion Status
                </label>

                <select
                  id="discussion-status"
                  value={status}
                  onChange={(event) =>
                    setStatus(
                      event.target.value,
                    )
                  }
                  className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-500/10"
                >
                  <option value="Open">
                    Open
                  </option>

                  <option value="Closed">
                    Closed
                  </option>
                </select>

                <p className="mt-2 text-xs text-slate-400">
                  Close the discussion when the
                  conversation is complete.
                </p>

              </div>
            )}

            {/* FORM FOOTER */}

            <div className="flex flex-col-reverse gap-3 border-t border-slate-100 pt-6 sm:flex-row sm:justify-end">

              <button
                type="button"
                onClick={() => {
                  resetForm();
                  setError("");
                }}
                disabled={submitting}
                className="rounded-xl border border-slate-200 px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
              >
                Cancel
              </button>

              <button
                type="submit"
                disabled={submitting}
                className="inline-flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-6 py-3 text-sm font-semibold text-white shadow-sm shadow-blue-600/20 transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {submitting ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : editingThread ? (
                  <SaveIcon />
                ) : (
                  <Send className="h-4 w-4" />
                )}

                {submitting
                  ? "Saving..."
                  : editingThread
                    ? "Update Discussion"
                    : "Create Discussion"}
              </button>

            </div>
          </form>
        </section>
      )}

      {/* =========================
          EMPTY STATE
      ========================= */}

      {threads.length === 0 && (
        <section className="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">

          <div className="px-6 py-16 text-center sm:px-8">

            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-50 text-blue-600">
              <MessageCircle className="h-8 w-8" />
            </div>

            <h2 className="mt-6 text-xl font-bold text-slate-900">
              No discussions yet
            </h2>

            <p className="mx-auto mt-2 max-w-lg text-sm leading-7 text-slate-500">
              Start the first discussion to
              collaborate, share viewpoints, raise
              concerns, and document important
              decision conversations.
            </p>

            <button
              type="button"
              onClick={startCreate}
              className="mt-7 inline-flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700"
            >
              <Plus className="h-4 w-4" />
              Start First Discussion
            </button>

          </div>

          <div className="grid border-t border-slate-100 sm:grid-cols-3">

            <div className="p-5 text-center sm:border-r sm:border-slate-100">
              <Users className="mx-auto h-5 w-5 text-slate-400" />

              <p className="mt-2 text-xs font-semibold text-slate-500">
                Collaborate
              </p>
            </div>

            <div className="border-t border-slate-100 p-5 text-center sm:border-r sm:border-t-0 sm:border-slate-100">
              <MessageSquareText className="mx-auto h-5 w-5 text-slate-400" />

              <p className="mt-2 text-xs font-semibold text-slate-500">
                Discuss
              </p>
            </div>

            <div className="border-t border-slate-100 p-5 text-center sm:border-t-0">
              <Clock3 className="mx-auto h-5 w-5 text-slate-400" />

              <p className="mt-2 text-xs font-semibold text-slate-500">
                Document
              </p>
            </div>

          </div>
        </section>
      )}

      {/* =========================
          THREAD LIST
      ========================= */}

      {threads.length > 0 && (
        <section>

          <div className="mb-5 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">

            <div>

              <div className="flex items-center gap-2">

                <h2 className="text-xl font-bold text-slate-900">
                  Discussion Threads
                </h2>

                <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-bold text-slate-600">
                  {threads.length}
                </span>

              </div>

              <p className="mt-1 text-sm text-slate-500">
                Review and continue conversations
                connected to this decision.
              </p>

            </div>

            <button
              type="button"
              onClick={startCreate}
              className="inline-flex w-fit items-center gap-2 rounded-xl border border-blue-200 bg-blue-50 px-4 py-2.5 text-sm font-semibold text-blue-700 transition hover:bg-blue-100"
            >
              <Plus className="h-4 w-4" />
              New Thread
            </button>

          </div>

          <div className="space-y-4">

            {threads.map((thread) => {
              const isDeleting =
                deletingId === thread.id;

              const threadStatus =
                thread.status || "Open";

              return (
                <article
                  key={thread.id}
                  className="group overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm transition duration-200 hover:-translate-y-0.5 hover:border-blue-200 hover:shadow-lg"
                >

                  {/* THREAD HEADER */}

                  <div className="p-6 sm:p-7">

                    <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">

                      <div className="flex min-w-0 gap-4">

                        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
                          <MessageCircle className="h-5 w-5" />
                        </div>

                        <div className="min-w-0">

                          <div className="flex flex-wrap items-center gap-2">

                            <h2 className="text-lg font-bold text-slate-900">
                              {thread.title}
                            </h2>

                            <span
                              className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-bold ${getStatusClasses(
                                threadStatus,
                              )}`}
                            >
                              <span
                                className={`h-1.5 w-1.5 rounded-full ${getStatusDot(
                                  threadStatus,
                                )}`}
                              />

                              {threadStatus}
                            </span>

                          </div>

                          <p className="mt-2 text-sm leading-7 text-slate-600">
                            {thread.description ||
                              "No description provided."}
                          </p>

                        </div>
                      </div>

                      {/* ACTIONS */}

                      <div className="flex shrink-0 flex-wrap gap-2">

                        <button
                          type="button"
                          onClick={() =>
                            navigate(
                              `/decisions/${numericDecisionId}/discussions/${thread.id}`,
                            )
                          }
                          className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-xs font-bold text-white shadow-sm transition hover:bg-blue-700"
                        >
                          Open Thread
                          <ExternalLink className="h-3.5 w-3.5" />
                        </button>

                        <button
                          type="button"
                          onClick={() =>
                            startEdit(thread)
                          }
                          disabled={isDeleting}
                          className="inline-flex items-center gap-2 rounded-xl border border-slate-200 px-3 py-2.5 text-xs font-bold text-slate-600 transition hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                          <Edit3 className="h-4 w-4" />
                          Edit
                        </button>

                        <button
                          type="button"
                          onClick={() =>
                            handleDelete(thread)
                          }
                          disabled={isDeleting}
                          className="inline-flex items-center gap-2 rounded-xl border border-red-100 px-3 py-2.5 text-xs font-bold text-red-600 transition hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                          {isDeleting ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                          ) : (
                            <Trash2 className="h-4 w-4" />
                          )}

                          {isDeleting
                            ? "Deleting..."
                            : "Delete"}
                        </button>

                      </div>

                    </div>

                  </div>

                  {/* THREAD METADATA */}

                  <div className="flex flex-col gap-3 border-t border-slate-100 bg-slate-50/60 px-6 py-4 text-xs text-slate-400 sm:flex-row sm:items-center sm:justify-between sm:px-7">

                    <div className="flex flex-wrap gap-x-5 gap-y-2">

                      <span className="inline-flex items-center gap-1.5">
                        <MessageCircle className="h-3.5 w-3.5" />
                        Thread #{thread.id}
                      </span>

                      <span className="inline-flex items-center gap-1.5">
                        <Clock3 className="h-3.5 w-3.5" />
                        Created{" "}
                        {formatDate(
                          thread.created_at,
                        )}
                      </span>

                      {thread.created_by !==
                        undefined && (
                        <span className="inline-flex items-center gap-1.5">
                          <Users className="h-3.5 w-3.5" />
                          User{" "}
                          {thread.created_by}
                        </span>
                      )}

                    </div>

                    <button
                      type="button"
                      onClick={() =>
                        navigate(
                          `/decisions/${numericDecisionId}/discussions/${thread.id}`,
                        )
                      }
                      className="inline-flex w-fit items-center gap-1.5 font-semibold text-blue-600 transition hover:text-blue-700"
                    >
                      Continue discussion
                      <ExternalLink className="h-3.5 w-3.5" />
                    </button>

                  </div>

                </article>
              );
            })}

          </div>
        </section>
      )}

    </div>
  );
}

/* =========================
   SMALL SAVE ICON
========================= */

function SaveIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-4 w-4"
      aria-hidden="true"
    >
      <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2Z" />
      <polyline points="17 21 17 13 7 13 7 21" />
      <polyline points="7 3 7 8 15 8" />
    </svg>
  );
}