import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  AlertCircle,
  ArrowLeft,
  CheckCircle2,
  Clock,
  Edit3,
  FileText,
  GitBranch,
  Info,
  Loader2,
  MessageSquare,
  Save,
  Send,
  Trash2,
  User,
  X,
} from "lucide-react";

import {
  getDecision,
  updateDecision,
  updateDecisionStatus,
  type Decision,
} from "../services/decisions";

import {
  getDecisionComments,
  createDecisionComment,
  updateComment,
  deleteComment,
  type Comment,
} from "../services/discussions";

import { getApiErrorMessage } from "../utils/errors";
import { useAuth } from "../context/AuthContext";

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

function getStatusClass(status?: string) {
  switch (status) {
    case "Approved":
      return "border-green-200 bg-green-50 text-green-700";

    case "Rejected":
      return "border-red-200 bg-red-50 text-red-700";

    case "Under Review":
      return "border-amber-200 bg-amber-50 text-amber-700";

    case "Draft":
      return "border-slate-200 bg-slate-100 text-slate-700";

    case "Archived":
      return "border-slate-200 bg-slate-100 text-slate-600";

    default:
      return "border-blue-200 bg-blue-50 text-blue-700";
  }
}

function getStatusDot(status?: string) {
  switch (status) {
    case "Approved":
      return "bg-green-500";

    case "Rejected":
      return "bg-red-500";

    case "Under Review":
      return "bg-amber-500";

    case "Archived":
      return "bg-slate-500";

    default:
      return "bg-blue-500";
  }
}

export default function DecisionDetails() {
  const { decisionId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const numericDecisionId = Number(decisionId);

  const [decision, setDecision] =
    useState<Decision | null>(null);

  const [comments, setComments] =
    useState<Comment[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [commentsLoading, setCommentsLoading] =
    useState(true);

  const [saving, setSaving] =
    useState(false);

  const [submitting, setSubmitting] =
    useState(false);

  const [commentSubmitting, setCommentSubmitting] =
    useState(false);

  const [error, setError] =
    useState("");

  const [success, setSuccess] =
    useState("");

  const [commentError, setCommentError] =
    useState("");

  const [commentText, setCommentText] =
    useState("");

  const [editingCommentId, setEditingCommentId] =
    useState<number | null>(null);

  const [editingCommentText, setEditingCommentText] =
    useState("");

  const [isEditing, setIsEditing] =
    useState(false);

  const [title, setTitle] =
    useState("");

  const [problemStatement, setProblemStatement] =
    useState("");

  const [category, setCategory] =
    useState("");

  const [rationale, setRationale] =
    useState("");

  const isDecisionCreator =
    Boolean(
      user?.id &&
        decision?.created_by &&
        user.id === decision.created_by,
    );

  async function loadDecision() {
    if (
      !decisionId ||
      !Number.isInteger(numericDecisionId) ||
      numericDecisionId <= 0
    ) {
      setError("Invalid decision ID.");
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError("");

      const data =
        await getDecision(numericDecisionId);

      setDecision(data);

      setTitle(data.title || "");
      setProblemStatement(
        data.problem_statement || "",
      );
      setCategory(data.category || "");
      setRationale(data.rationale || "");
    } catch (err: any) {
      console.error(err);

      setError(
        getApiErrorMessage(
          err,
          "Failed to load decision.",
        ),
      );
    } finally {
      setLoading(false);
    }
  }

  async function loadComments() {
    if (
      !Number.isInteger(numericDecisionId) ||
      numericDecisionId <= 0
    ) {
      setCommentsLoading(false);
      return;
    }

    try {
      setCommentsLoading(true);
      setCommentError("");

      const data =
        await getDecisionComments(
          numericDecisionId,
        );

      setComments(data);
    } catch (err: any) {
      console.error(err);

      setCommentError(
        getApiErrorMessage(
          err,
          "Unable to load comments.",
        ),
      );
    } finally {
      setCommentsLoading(false);
    }
  }

  useEffect(() => {
    loadDecision();
    loadComments();
  }, [decisionId]);

  function showSuccess(message: string) {
    setSuccess(message);

    window.setTimeout(() => {
      setSuccess("");
    }, 3000);
  }

  function startEditing() {
    if (!decision || !isDecisionCreator) {
      return;
    }

    setTitle(decision.title || "");
    setProblemStatement(
      decision.problem_statement || "",
    );
    setCategory(decision.category || "");
    setRationale(decision.rationale || "");

    setError("");
    setSuccess("");
    setIsEditing(true);
  }

  function cancelEditing() {
    if (decision) {
      setTitle(decision.title || "");
      setProblemStatement(
        decision.problem_statement || "",
      );
      setCategory(decision.category || "");
      setRationale(decision.rationale || "");
    }

    setError("");
    setIsEditing(false);
  }

  async function handleSave() {
    if (!decision || !isDecisionCreator) {
      return;
    }

    if (!title.trim()) {
      setError("Decision title is required.");
      return;
    }

    if (!problemStatement.trim()) {
      setError(
        "Problem statement is required.",
      );
      return;
    }

    if (!category.trim()) {
      setError("Category is required.");
      return;
    }

    try {
      setSaving(true);
      setError("");
      setSuccess("");

      const updatedDecision =
        await updateDecision(
          decision.id,
          {
            title: title.trim(),
            problem_statement:
              problemStatement.trim(),
            category: category.trim(),
            rationale: rationale.trim(),
          },
        );

      setDecision(updatedDecision);

      setTitle(
        updatedDecision.title || "",
      );

      setProblemStatement(
        updatedDecision.problem_statement ||
          "",
      );

      setCategory(
        updatedDecision.category || "",
      );

      setRationale(
        updatedDecision.rationale || "",
      );

      setIsEditing(false);

      showSuccess(
        "Decision updated successfully.",
      );
    } catch (err: any) {
      console.error(err);

      setError(
        getApiErrorMessage(
          err,
          "Failed to update decision.",
        ),
      );
    } finally {
      setSaving(false);
    }
  }

  async function handleSubmitForReview() {
    if (
      !decision ||
      !isDecisionCreator ||
      decision.status !== "Draft"
    ) {
      return;
    }

    const confirmed = window.confirm(
      "Are you sure you want to submit this decision for review?",
    );

    if (!confirmed) {
      return;
    }

    try {
      setSubmitting(true);
      setError("");
      setSuccess("");

      const updatedDecision =
        await updateDecisionStatus(
          decision.id,
          "Under Review",
        );

      setDecision(updatedDecision);

      showSuccess(
        "Decision submitted for review successfully.",
      );
    } catch (err: any) {
      console.error(err);

      setError(
        getApiErrorMessage(
          err,
          "Failed to submit decision for review.",
        ),
      );
    } finally {
      setSubmitting(false);
    }
  }

  async function handleAddComment() {
    if (!decision) {
      return;
    }

    if (!commentText.trim()) {
      setCommentError(
        "Comment cannot be empty.",
      );
      return;
    }

    try {
      setCommentSubmitting(true);
      setCommentError("");

      const newComment =
        await createDecisionComment(
          decision.id,
          commentText.trim(),
        );

      setComments((current) => [
        ...current,
        newComment,
      ]);

      setCommentText("");
    } catch (err: any) {
      console.error(err);

      setCommentError(
        getApiErrorMessage(
          err,
          "Unable to add comment.",
        ),
      );
    } finally {
      setCommentSubmitting(false);
    }
  }

  function startCommentEditing(
    comment: Comment,
  ) {
    setEditingCommentId(comment.id);
    setEditingCommentText(
      comment.content,
    );
    setCommentError("");
  }

  function cancelCommentEditing() {
    setEditingCommentId(null);
    setEditingCommentText("");
  }

  async function handleUpdateComment(
    commentId: number,
  ) {
    if (!editingCommentText.trim()) {
      setCommentError(
        "Comment cannot be empty.",
      );
      return;
    }

    try {
      setCommentError("");

      const updatedComment =
        await updateComment(
          commentId,
          editingCommentText.trim(),
        );

      setComments((current) =>
        current.map((comment) =>
          comment.id === commentId
            ? updatedComment
            : comment,
        ),
      );

      cancelCommentEditing();
    } catch (err: any) {
      console.error(err);

      setCommentError(
        getApiErrorMessage(
          err,
          "Unable to update comment.",
        ),
      );
    }
  }

  async function handleDeleteComment(
    commentId: number,
  ) {
    const confirmed = window.confirm(
      "Are you sure you want to delete this comment?",
    );

    if (!confirmed) {
      return;
    }

    try {
      setCommentError("");

      await deleteComment(commentId);

      setComments((current) =>
        current.filter(
          (comment) =>
            comment.id !== commentId,
        ),
      );
    } catch (err: any) {
      console.error(err);

      setCommentError(
        getApiErrorMessage(
          err,
          "Unable to delete comment.",
        ),
      );
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-50">
            <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
          </div>

          <p className="mt-4 text-sm font-medium text-slate-600">
            Loading decision...
          </p>

          <p className="mt-1 text-xs text-slate-400">
            Preparing the decision workspace
          </p>
        </div>
      </div>
    );
  }

  if (error && !decision) {
    return (
      <div className="mx-auto max-w-5xl">

        <button
          type="button"
          onClick={() =>
            navigate("/decisions")
          }
          className="mb-6 inline-flex items-center gap-2 text-sm font-semibold text-slate-600 transition hover:text-blue-600"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Decisions
        </button>

        <div className="rounded-2xl border border-red-200 bg-red-50 p-6">
          <div className="flex items-start gap-3">
            <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-red-600" />

            <div>
              <p className="font-semibold text-red-800">
                Unable to load decision
              </p>

              <p className="mt-1 text-sm text-red-700">
                {error}
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={loadDecision}
            className="mt-4 rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-red-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!decision) {
    return null;
  }

  return (
    <div className="mx-auto max-w-7xl space-y-6">

      {/* =====================================================
          TOP NAVIGATION
      ===================================================== */}

      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">

        <button
          type="button"
          onClick={() =>
            navigate("/decisions")
          }
          className="inline-flex w-fit items-center gap-2 text-sm font-semibold text-slate-600 transition hover:text-blue-600"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Decisions
        </button>

        {!isEditing &&
          isDecisionCreator && (
            <div className="flex flex-col gap-2 sm:flex-row">

              {decision.status === "Draft" && (
                <button
                  type="button"
                  onClick={
                    handleSubmitForReview
                  }
                  disabled={submitting}
                  className="inline-flex items-center justify-center gap-2 rounded-xl bg-green-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {submitting ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <CheckCircle2 className="h-4 w-4" />
                  )}

                  {submitting
                    ? "Submitting..."
                    : "Submit for Review"}
                </button>
              )}

              <button
                type="button"
                onClick={startEditing}
                className="inline-flex items-center justify-center gap-2 rounded-xl border border-blue-200 bg-white px-5 py-2.5 text-sm font-semibold text-blue-700 shadow-sm transition hover:bg-blue-50"
              >
                <Edit3 className="h-4 w-4" />
                Edit Decision
              </button>

            </div>
          )}

      </div>

      {/* =====================================================
          SUCCESS / ERROR
      ===================================================== */}

      {success && (
        <div className="flex items-center gap-3 rounded-xl border border-green-200 bg-green-50 px-4 py-3 text-sm font-semibold text-green-700">
          <CheckCircle2 className="h-5 w-5" />
          {success}
        </div>
      )}

      {error && (
        <div className="flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700">
          <AlertCircle className="mt-0.5 h-5 w-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* =====================================================
          DECISION HEADER
      ===================================================== */}

      <section className="relative overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">

        <div className="absolute -right-20 -top-24 h-64 w-64 rounded-full bg-blue-50 blur-3xl" />

        <div className="relative p-6 sm:p-8">

          <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">

            <div className="min-w-0">

              <div className="mb-4 flex flex-wrap items-center gap-2">

                <span
                  className={`inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-semibold ${getStatusClass(
                    decision.status,
                  )}`}
                >
                  <span
                    className={`h-2 w-2 rounded-full ${getStatusDot(
                      decision.status,
                    )}`}
                  />

                  {decision.status ||
                    "Unknown"}
                </span>

                {decision.category && (
                  <span className="rounded-full border border-blue-100 bg-blue-50 px-3 py-1.5 text-xs font-semibold text-blue-700">
                    {decision.category}
                  </span>
                )}

              </div>

              {isEditing ? (
                <div className="space-y-5">

                  <div>
                    <label
                      htmlFor="decision-title"
                      className="mb-2 block text-sm font-semibold text-slate-700"
                    >
                      Decision Title
                    </label>

                    <input
                      id="decision-title"
                      type="text"
                      value={title}
                      onChange={(event) =>
                        setTitle(
                          event.target.value,
                        )
                      }
                      className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-xl font-bold text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
                    />
                  </div>

                  <div>
                    <label
                      htmlFor="decision-category"
                      className="mb-2 block text-sm font-semibold text-slate-700"
                    >
                      Category
                    </label>

                    <input
                      id="decision-category"
                      type="text"
                      value={category}
                      onChange={(event) =>
                        setCategory(
                          event.target.value,
                        )
                      }
                      className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
                    />
                  </div>

                </div>
              ) : (
                <>
                  <h1 className="max-w-4xl text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl lg:text-4xl">
                    {decision.title}
                  </h1>

                  <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-500">
                    Decision #{decision.id} · Created{" "}
                    {formatDate(
                      decision.created_at,
                    )}
                  </p>
                </>
              )}

            </div>

            {!isEditing && (
              <div className="shrink-0 rounded-2xl border border-slate-200 bg-slate-50 px-5 py-4">

                <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                  Decision ID
                </p>

                <p className="mt-1 text-xl font-bold text-slate-900">
                  #{decision.id}
                </p>

              </div>
            )}

          </div>

        </div>
      </section>

      {/* =====================================================
          MAIN CONTENT
      ===================================================== */}

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_300px]">

        {/* PRIMARY CONTENT */}

        <div className="space-y-6">

          {/* Problem */}

          <section className="rounded-2xl border border-slate-200 bg-white shadow-sm">

            <div className="border-b border-slate-100 px-6 py-5">

              <div className="flex items-center gap-3">

                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
                  <FileText className="h-5 w-5" />
                </div>

                <div>
                  <h2 className="text-lg font-bold text-slate-900">
                    Problem Statement
                  </h2>

                  <p className="text-xs text-slate-500">
                    What requires a decision?
                  </p>
                </div>

              </div>

            </div>

            <div className="p-6">

              {isEditing ? (
                <textarea
                  value={problemStatement}
                  onChange={(event) =>
                    setProblemStatement(
                      event.target.value,
                    )
                  }
                  rows={8}
                  className="w-full resize-y rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm leading-7 text-slate-900 outline-none transition focus:border-blue-500 focus:bg-white focus:ring-2 focus:ring-blue-500/20"
                />
              ) : (
                <p className="whitespace-pre-wrap text-sm leading-7 text-slate-700">
                  {decision.problem_statement ||
                    "No problem statement provided."}
                </p>
              )}

            </div>

          </section>

          {/* Rationale */}

          <section className="rounded-2xl border border-slate-200 bg-white shadow-sm">

            <div className="border-b border-slate-100 px-6 py-5">

              <div className="flex items-center gap-3">

                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-50 text-purple-600">
                  <Info className="h-5 w-5" />
                </div>

                <div>
                  <h2 className="text-lg font-bold text-slate-900">
                    Rationale
                  </h2>

                  <p className="text-xs text-slate-500">
                    Reasoning and context behind the decision.
                  </p>
                </div>

              </div>

            </div>

            <div className="p-6">

              {isEditing ? (
                <textarea
                  value={rationale}
                  onChange={(event) =>
                    setRationale(
                      event.target.value,
                    )
                  }
                  rows={7}
                  className="w-full resize-y rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm leading-7 text-slate-900 outline-none transition focus:border-blue-500 focus:bg-white focus:ring-2 focus:ring-blue-500/20"
                />
              ) : (
                <p className="whitespace-pre-wrap text-sm leading-7 text-slate-700">
                  {decision.rationale ||
                    "No rationale provided."}
                </p>
              )}

            </div>

          </section>

          {/* Edit actions */}

          {isEditing && (
            <section className="rounded-2xl border border-blue-100 bg-blue-50/50 p-5">

              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">

                <div>
                  <p className="text-sm font-semibold text-slate-800">
                    Unsaved changes
                  </p>

                  <p className="mt-1 text-xs text-slate-500">
                    Save your changes or cancel to restore
                    the original decision.
                  </p>
                </div>

                <div className="flex flex-col gap-2 sm:flex-row">

                  <button
                    type="button"
                    onClick={cancelEditing}
                    disabled={saving}
                    className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:opacity-50"
                  >
                    <X className="h-4 w-4" />
                    Cancel
                  </button>

                  <button
                    type="button"
                    onClick={handleSave}
                    disabled={saving}
                    className="inline-flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {saving ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Save className="h-4 w-4" />
                    )}

                    {saving
                      ? "Saving..."
                      : "Save Changes"}
                  </button>

                </div>

              </div>

            </section>
          )}

          {/* =================================================
              COMMENTS
          ================================================= */}

          {!isEditing && (
            <section className="rounded-2xl border border-slate-200 bg-white shadow-sm">

              <div className="border-b border-slate-100 px-6 py-5">

                <div className="flex items-center gap-3">

                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-50 text-purple-600">
                    <MessageSquare className="h-5 w-5" />
                  </div>

                  <div>
                    <h2 className="text-lg font-bold text-slate-900">
                      Decision Comments
                    </h2>

                    <p className="text-xs text-slate-500">
                      Feedback and observations from the team.
                    </p>
                  </div>

                </div>

              </div>

              <div className="p-6">

                {/* Add comment */}

                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">

                  <textarea
                    value={commentText}
                    onChange={(event) =>
                      setCommentText(
                        event.target.value,
                      )
                    }
                    rows={3}
                    placeholder="Write a comment or question..."
                    className="w-full resize-y rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm leading-6 text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
                  />

                  <div className="mt-3 flex justify-end">

                    <button
                      type="button"
                      onClick={
                        handleAddComment
                      }
                      disabled={
                        commentSubmitting ||
                        !commentText.trim()
                      }
                      className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      {commentSubmitting ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Send className="h-4 w-4" />
                      )}

                      {commentSubmitting
                        ? "Posting..."
                        : "Add Comment"}
                    </button>

                  </div>

                </div>

                {commentError && (
                  <div className="mt-4 flex items-start gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700">
                    <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
                    {commentError}
                  </div>
                )}

                {/* Comments list */}

                <div className="mt-6">

                  {commentsLoading ? (
                    <div className="py-8 text-center">
                      <Loader2 className="mx-auto h-6 w-6 animate-spin text-blue-600" />

                      <p className="mt-3 text-sm text-slate-500">
                        Loading comments...
                      </p>
                    </div>
                  ) : comments.length === 0 ? (
                    <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-6 py-10 text-center">

                      <MessageSquare className="mx-auto h-7 w-7 text-slate-400" />

                      <p className="mt-3 text-sm font-semibold text-slate-600">
                        No comments yet
                      </p>

                      <p className="mt-1 text-xs text-slate-400">
                        Start the conversation around this
                        decision.
                      </p>

                    </div>
                  ) : (
                    <div className="space-y-4">

                      {comments.map((comment) => {
                        const isCommentOwner =
                          comment.user_id ===
                          user?.id;

                        const isEditingComment =
                          editingCommentId ===
                          comment.id;

                        return (
                          <article
                            key={comment.id}
                            className="rounded-2xl border border-slate-200 bg-white p-4 transition hover:border-slate-300"
                          >

                            <div className="flex items-start justify-between gap-4">

                              <div className="flex min-w-0 items-center gap-3">

                                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-blue-50 text-blue-600">
                                  <User className="h-4 w-4" />
                                </div>

                                <div className="min-w-0">

                                  <p className="text-sm font-semibold text-slate-800">
                                    User #
                                    {comment.user_id ??
                                      "—"}
                                  </p>

                                  <p className="mt-0.5 flex items-center gap-1.5 text-xs text-slate-400">
                                    <Clock className="h-3 w-3" />
                                    {formatDate(
                                      comment.created_at,
                                    )}
                                  </p>

                                </div>

                              </div>

                              {isCommentOwner &&
                                !isEditingComment && (
                                  <div className="flex shrink-0 gap-1">

                                    <button
                                      type="button"
                                      onClick={() =>
                                        startCommentEditing(
                                          comment,
                                        )
                                      }
                                      className="rounded-lg p-2 text-slate-400 transition hover:bg-blue-50 hover:text-blue-600"
                                      title="Edit comment"
                                    >
                                      <Edit3 className="h-4 w-4" />
                                    </button>

                                    <button
                                      type="button"
                                      onClick={() =>
                                        handleDeleteComment(
                                          comment.id,
                                        )
                                      }
                                      className="rounded-lg p-2 text-slate-400 transition hover:bg-red-50 hover:text-red-600"
                                      title="Delete comment"
                                    >
                                      <Trash2 className="h-4 w-4" />
                                    </button>

                                  </div>
                                )}

                            </div>

                            <div className="mt-4">

                              {isEditingComment ? (
                                <div>

                                  <textarea
                                    value={
                                      editingCommentText
                                    }
                                    onChange={(
                                      event,
                                    ) =>
                                      setEditingCommentText(
                                        event.target
                                          .value,
                                      )
                                    }
                                    rows={3}
                                    className="w-full resize-y rounded-xl border border-slate-200 px-4 py-3 text-sm leading-6 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
                                  />

                                  <div className="mt-3 flex justify-end gap-2">

                                    <button
                                      type="button"
                                      onClick={
                                        cancelCommentEditing
                                      }
                                      className="rounded-lg border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-600 transition hover:bg-slate-50"
                                    >
                                      Cancel
                                    </button>

                                    <button
                                      type="button"
                                      onClick={() =>
                                        handleUpdateComment(
                                          comment.id,
                                        )
                                      }
                                      disabled={
                                        !editingCommentText.trim()
                                      }
                                      className="inline-flex items-center gap-1.5 rounded-lg bg-blue-600 px-3 py-2 text-xs font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
                                    >
                                      <Save className="h-3.5 w-3.5" />
                                      Save
                                    </button>

                                  </div>

                                </div>
                              ) : (
                                <p className="whitespace-pre-wrap text-sm leading-7 text-slate-700">
                                  {comment.content}
                                </p>
                              )}

                            </div>

                          </article>
                        );
                      })}

                    </div>
                  )}

                </div>

              </div>
            </section>
          )}

        </div>

        {/* =====================================================
            SIDEBAR
        ===================================================== */}

        <aside className="space-y-6">

          {/* Decision metadata */}

          {!isEditing && (
            <section className="rounded-2xl border border-slate-200 bg-white shadow-sm">

              <div className="border-b border-slate-100 px-5 py-4">
                <h2 className="text-sm font-bold text-slate-900">
                  Decision Information
                </h2>
              </div>

              <div className="divide-y divide-slate-100">

                <div className="p-4">
                  <p className="text-xs font-medium text-slate-400">
                    Created By
                  </p>

                  <div className="mt-2 flex items-center gap-2">
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-100">
                      <User className="h-4 w-4 text-slate-500" />
                    </div>

                    <p className="text-sm font-semibold text-slate-800">
                      User #
                      {decision.created_by ??
                        "—"}
                    </p>
                  </div>
                </div>

                <div className="p-4">
                  <p className="text-xs font-medium text-slate-400">
                    Created
                  </p>

                  <p className="mt-1 text-sm font-semibold text-slate-800">
                    {formatDate(
                      decision.created_at,
                    )}
                  </p>
                </div>

                <div className="p-4">
                  <p className="text-xs font-medium text-slate-400">
                    Last Updated
                  </p>

                  <p className="mt-1 text-sm font-semibold text-slate-800">
                    {formatDate(
                      decision.updated_at,
                    )}
                  </p>
                </div>

              </div>

            </section>
          )}

          {/* Workflow */}

          <section className="rounded-2xl border border-slate-200 bg-white shadow-sm">

            <div className="border-b border-slate-100 px-5 py-4">
              <h2 className="text-sm font-bold text-slate-900">
                Decision Workflow
              </h2>

              <p className="mt-1 text-xs text-slate-500">
                Continue working with this decision.
              </p>
            </div>

            <div className="space-y-2 p-3">

              <button
                type="button"
                onClick={() =>
                  navigate(
                    `/decisions/${decision.id}/alternatives`,
                  )
                }
                className="group flex w-full items-center gap-3 rounded-xl p-3 text-left transition hover:bg-blue-50"
              >
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-blue-50 text-blue-600 group-hover:bg-blue-100">
                  <GitBranch className="h-4 w-4" />
                </div>

                <div className="min-w-0">
                  <p className="text-sm font-semibold text-slate-800">
                    Alternatives
                  </p>

                  <p className="text-xs text-slate-500">
                    Compare possible options
                  </p>
                </div>
              </button>

              <button
                type="button"
                onClick={() =>
                  navigate(
                    `/decisions/${decision.id}/discussions`,
                  )
                }
                className="group flex w-full items-center gap-3 rounded-xl p-3 text-left transition hover:bg-purple-50"
              >
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-purple-50 text-purple-600 group-hover:bg-purple-100">
                  <MessageSquare className="h-4 w-4" />
                </div>

                <div className="min-w-0">
                  <p className="text-sm font-semibold text-slate-800">
                    Discussions
                  </p>

                  <p className="text-xs text-slate-500">
                    Team discussion threads
                  </p>
                </div>
              </button>

              <button
                type="button"
                onClick={() =>
                  navigate(
                    `/decisions/${decision.id}/history`,
                  )
                }
                className="group flex w-full items-center gap-3 rounded-xl p-3 text-left transition hover:bg-orange-50"
              >
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-orange-50 text-orange-600 group-hover:bg-orange-100">
                  <Clock className="h-4 w-4" />
                </div>

                <div className="min-w-0">
                  <p className="text-sm font-semibold text-slate-800">
                    Version History
                  </p>

                  <p className="text-xs text-slate-500">
                    Review decision changes
                  </p>
                </div>
              </button>

              <button
                type="button"
                onClick={() =>
                  navigate("/approvals")
                }
                className="group flex w-full items-center gap-3 rounded-xl p-3 text-left transition hover:bg-green-50"
              >
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-green-50 text-green-600 group-hover:bg-green-100">
                  <CheckCircle2 className="h-4 w-4" />
                </div>

                <div className="min-w-0">
                  <p className="text-sm font-semibold text-slate-800">
                    Approvals
                  </p>

                  <p className="text-xs text-slate-500">
                    Review approval workflow
                  </p>
                </div>
              </button>

            </div>
          </section>

          {/* Status information */}

          <section className="rounded-2xl border border-blue-100 bg-blue-50 p-5">

            <div className="flex items-start gap-3">

              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-white text-blue-600 shadow-sm">
                <Info className="h-4 w-4" />
              </div>

              <div>
                <p className="text-sm font-semibold text-blue-900">
                  Current Status
                </p>

                <p className="mt-1 text-xs leading-5 text-blue-700">
                  This decision is currently{" "}
                  <span className="font-semibold">
                    {decision.status ||
                      "Unknown"}
                  </span>
                  .
                </p>

                {decision.status ===
                  "Draft" && (
                  <p className="mt-2 text-xs leading-5 text-blue-700">
                    Complete the decision details and
                    submit it when ready for review.
                  </p>
                )}

              </div>

            </div>

          </section>

        </aside>

      </div>

    </div>
  );
}