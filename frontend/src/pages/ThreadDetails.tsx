import { useEffect, useState } from "react";
import {
  ArrowLeft,
  Edit3,
  MessageCircle,
  Send,
  Trash2,
  X,
} from "lucide-react";
import { useNavigate, useParams } from "react-router-dom";

import {
  createThreadComment,
  deleteComment,
  getThread,
  getThreadComments,
  updateComment,
  updateThread,
  type Comment,
  type DiscussionThread,
} from "../services/discussions";

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

export default function ThreadDetails() {
  const {
    decisionId,
    threadId,
  } = useParams<{
    decisionId: string;
    threadId: string;
  }>();

  const navigate = useNavigate();

  const numericDecisionId = Number(decisionId);
  const numericThreadId = Number(threadId);

  const [thread, setThread] =
    useState<DiscussionThread | null>(null);

  const [comments, setComments] =
    useState<Comment[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [commentText, setCommentText] =
    useState("");

  const [sending, setSending] =
    useState(false);

  const [editingThread, setEditingThread] =
    useState(false);

  const [threadTitle, setThreadTitle] =
    useState("");

  const [threadDescription, setThreadDescription] =
    useState("");

  const [threadStatus, setThreadStatus] =
    useState("Open");

  const [savingThread, setSavingThread] =
    useState(false);

  const [editingCommentId, setEditingCommentId] =
    useState<number | null>(null);

  const [editingCommentText, setEditingCommentText] =
    useState("");

  const [savingComment, setSavingComment] =
    useState(false);

  async function loadThread() {
    if (
      !Number.isInteger(numericThreadId) ||
      numericThreadId <= 0
    ) {
      setError("Invalid thread ID.");
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError("");

      const [threadData, commentData] =
        await Promise.all([
          getThread(numericThreadId),
          getThreadComments(numericThreadId),
        ]);

      setThread(threadData);
      setComments(commentData);
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ||
          err?.message ||
          "Unable to load discussion.",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadThread();
  }, [numericThreadId]);

  async function handleAddComment(
    event: React.FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    if (!commentText.trim()) {
      setError("Comment cannot be empty.");
      return;
    }

    try {
      setSending(true);
      setError("");

      await createThreadComment(
        numericThreadId,
        commentText.trim(),
      );

      setCommentText("");

      const updatedComments =
        await getThreadComments(
          numericThreadId,
        );

      setComments(updatedComments);
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ||
          err?.message ||
          "Unable to add comment.",
      );
    } finally {
      setSending(false);
    }
  }

  function startThreadEdit() {
    if (!thread) {
      return;
    }

    setThreadTitle(thread.title || "");
    setThreadDescription(
      thread.description || "",
    );
    setThreadStatus(
      thread.status || "Open",
    );
    setEditingThread(true);
  }

  function cancelThreadEdit() {
    setEditingThread(false);
    setThreadTitle("");
    setThreadDescription("");
    setThreadStatus("Open");
  }

  async function handleThreadUpdate(
    event: React.FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    if (!threadTitle.trim()) {
      setError("Thread title is required.");
      return;
    }

    if (!threadDescription.trim()) {
      setError(
        "Thread description is required.",
      );
      return;
    }

    try {
      setSavingThread(true);
      setError("");

      const updated = await updateThread(
        numericThreadId,
        {
          title: threadTitle.trim(),
          description:
            threadDescription.trim(),
          status: threadStatus,
        },
      );

      setThread(updated);
      cancelThreadEdit();
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ||
          err?.message ||
          "Unable to update discussion.",
      );
    } finally {
      setSavingThread(false);
    }
  }

  function startCommentEdit(
    comment: Comment,
  ) {
    setEditingCommentId(comment.id);
    setEditingCommentText(
      comment.content || "",
    );
  }

  function cancelCommentEdit() {
    setEditingCommentId(null);
    setEditingCommentText("");
  }

  async function handleCommentUpdate(
    commentId: number,
  ) {
    if (!editingCommentText.trim()) {
      setError("Comment cannot be empty.");
      return;
    }

    try {
      setSavingComment(true);
      setError("");

      const updated =
        await updateComment(
          commentId,
          editingCommentText.trim(),
        );

      setComments((current) =>
        current.map((comment) =>
          comment.id === commentId
            ? updated
            : comment,
        ),
      );

      cancelCommentEdit();
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ||
          err?.message ||
          "Unable to update comment.",
      );
    } finally {
      setSavingComment(false);
    }
  }

  async function handleCommentDelete(
    commentId: number,
  ) {
    const confirmed = window.confirm(
      "Are you sure you want to delete this comment?",
    );

    if (!confirmed) {
      return;
    }

    try {
      setError("");

      await deleteComment(commentId);

      setComments((current) =>
        current.filter(
          (comment) =>
            comment.id !== commentId,
        ),
      );
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ||
          err?.message ||
          "Unable to delete comment.",
      );
    }
  }

  if (
    !Number.isInteger(numericDecisionId) ||
    numericDecisionId <= 0 ||
    !Number.isInteger(numericThreadId) ||
    numericThreadId <= 0
  ) {
    return (
      <div className="p-6">
        <div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-red-700">
          Invalid discussion information.
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 p-6">
        <div className="mx-auto max-w-5xl">
          <div className="rounded-3xl border border-slate-200 bg-white p-12 text-center shadow-sm">
            <div className="mx-auto h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-blue-600" />

            <p className="mt-4 text-sm text-slate-500">
              Loading discussion...
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (!thread) {
    return (
      <div className="min-h-screen bg-slate-50 p-6">
        <div className="mx-auto max-w-5xl">
          <button
            type="button"
            onClick={() =>
              navigate(
                `/decisions/${numericDecisionId}/discussions`,
              )
            }
            className="mb-5 inline-flex items-center gap-2 text-sm font-medium text-slate-600 hover:text-slate-900"
          >
            <ArrowLeft size={17} />
            Back to Discussions
          </button>

          <div className="rounded-3xl border border-red-200 bg-red-50 p-6 text-red-700">
            {error ||
              "Discussion thread not found."}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 p-4 md:p-6">
      <div className="mx-auto max-w-5xl space-y-6">

        {/* HEADER */}

        <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <button
            type="button"
            onClick={() =>
              navigate(
                `/decisions/${numericDecisionId}/discussions`,
              )
            }
            className="mb-5 inline-flex items-center gap-2 text-sm font-medium text-slate-600 hover:text-slate-900"
          >
            <ArrowLeft size={17} />
            Back to Discussions
          </button>

          <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
            <div className="flex gap-4">
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-blue-50 text-blue-600">
                <MessageCircle size={22} />
              </div>

              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
                    Thread #{thread.id}
                  </span>

                  <span
                    className={`rounded-full border px-3 py-1 text-xs font-semibold ${getStatusClasses(
                      thread.status,
                    )}`}
                  >
                    {thread.status || "Open"}
                  </span>
                </div>

                {!editingThread && (
                  <>
                    <h1 className="mt-3 text-2xl font-bold text-slate-900 md:text-3xl">
                      {thread.title}
                    </h1>

                    <p className="mt-2 text-sm leading-6 text-slate-500">
                      {thread.description ||
                        "No description provided."}
                    </p>
                  </>
                )}
              </div>
            </div>

            {!editingThread && (
              <button
                type="button"
                onClick={startThreadEdit}
                className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50"
              >
                <Edit3 size={16} />
                Edit
              </button>
            )}
          </div>

          {/* EDIT THREAD */}

          {editingThread && (
            <form
              onSubmit={handleThreadUpdate}
              className="mt-6 space-y-5 border-t border-slate-100 pt-6"
            >
              <div>
                <label className="mb-2 block text-sm font-semibold text-slate-700">
                  Title
                </label>

                <input
                  type="text"
                  value={threadTitle}
                  onChange={(event) =>
                    setThreadTitle(
                      event.target.value,
                    )
                  }
                  className="w-full rounded-xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-semibold text-slate-700">
                  Description
                </label>

                <textarea
                  rows={4}
                  value={threadDescription}
                  onChange={(event) =>
                    setThreadDescription(
                      event.target.value,
                    )
                  }
                  className="w-full resize-none rounded-xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-semibold text-slate-700">
                  Status
                </label>

                <select
                  value={threadStatus}
                  onChange={(event) =>
                    setThreadStatus(
                      event.target.value,
                    )
                  }
                  className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                >
                  <option value="Open">
                    Open
                  </option>

                  <option value="Closed">
                    Closed
                  </option>
                </select>
              </div>

              <div className="flex flex-col gap-3 sm:flex-row sm:justify-end">
                <button
                  type="button"
                  onClick={cancelThreadEdit}
                  className="rounded-xl border border-slate-200 px-5 py-3 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  disabled={savingThread}
                  className="rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-60"
                >
                  {savingThread
                    ? "Saving..."
                    : "Save Changes"}
                </button>
              </div>
            </form>
          )}

          <div className="mt-5 flex flex-wrap gap-4 border-t border-slate-100 pt-4 text-xs text-slate-400">
            <span>
              Created{" "}
              {formatDate(thread.created_at)}
            </span>

            {thread.created_by !==
              undefined && (
              <span>
                User {thread.created_by}
              </span>
            )}
          </div>
        </div>

        {/* ERROR */}

        {error && (
          <div className="flex items-center justify-between rounded-2xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">
            <span>{error}</span>

            <button
              type="button"
              onClick={() => setError("")}
            >
              <X size={17} />
            </button>
          </div>
        )}

        {/* COMMENTS */}

        <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <h2 className="flex items-center gap-2 text-xl font-bold text-slate-900">
                <MessageCircle
                  size={20}
                  className="text-blue-600"
                />
                Comments
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Collaborate and share feedback on this
                discussion.
              </p>
            </div>

            <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
              {comments.length}{" "}
              {comments.length === 1
                ? "Comment"
                : "Comments"}
            </span>
          </div>

          {/* COMMENT LIST */}

          {comments.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-8 text-center">
              <MessageCircle
                size={25}
                className="mx-auto text-slate-400"
              />

              <p className="mt-3 text-sm font-medium text-slate-600">
                No comments yet.
              </p>

              <p className="mt-1 text-xs text-slate-400">
                Be the first to add feedback.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {comments.map((comment) => (
                <div
                  key={comment.id}
                  className="rounded-2xl border border-slate-200 bg-slate-50 p-5"
                >
                  {editingCommentId ===
                  comment.id ? (
                    <div className="space-y-4">
                      <textarea
                        rows={4}
                        value={
                          editingCommentText
                        }
                        onChange={(event) =>
                          setEditingCommentText(
                            event.target.value,
                          )
                        }
                        className="w-full resize-none rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                      />

                      <div className="flex justify-end gap-2">
                        <button
                          type="button"
                          onClick={
                            cancelCommentEdit
                          }
                          className="rounded-xl border border-slate-200 bg-white px-4 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50"
                        >
                          Cancel
                        </button>

                        <button
                          type="button"
                          disabled={
                            savingComment
                          }
                          onClick={() =>
                            handleCommentUpdate(
                              comment.id,
                            )
                          }
                          className="rounded-xl bg-blue-600 px-4 py-2 text-xs font-semibold text-white hover:bg-blue-700 disabled:opacity-60"
                        >
                          {savingComment
                            ? "Saving..."
                            : "Save"}
                        </button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                        <div>
                          <p className="text-sm font-semibold text-slate-800">
                            User{" "}
                            {comment.user_id ??
                              "—"}
                          </p>

                          <p className="mt-1 text-xs text-slate-400">
                            {formatDate(
                              comment.created_at,
                            )}
                          </p>
                        </div>

                        <div className="flex gap-2">
                          <button
                            type="button"
                            onClick={() =>
                              startCommentEdit(
                                comment,
                              )
                            }
                            className="rounded-lg border border-slate-200 bg-white p-2 text-slate-500 hover:text-blue-600"
                            title="Edit comment"
                          >
                            <Edit3
                              size={14}
                            />
                          </button>

                          <button
                            type="button"
                            onClick={() =>
                              handleCommentDelete(
                                comment.id,
                              )
                            }
                            className="rounded-lg border border-red-100 bg-white p-2 text-red-500 hover:bg-red-50"
                            title="Delete comment"
                          >
                            <Trash2
                              size={14}
                            />
                          </button>
                        </div>
                      </div>

                      <p className="mt-4 text-sm leading-6 text-slate-700">
                        {comment.content}
                      </p>
                    </>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* ADD COMMENT */}

          <form
            onSubmit={handleAddComment}
            className="mt-6 border-t border-slate-100 pt-6"
          >
            <label className="mb-2 block text-sm font-semibold text-slate-700">
              Add a comment
            </label>

            <textarea
              rows={4}
              value={commentText}
              onChange={(event) =>
                setCommentText(
                  event.target.value,
                )
              }
              placeholder="Write your feedback or comment..."
              className="w-full resize-none rounded-xl border border-slate-200 px-4 py-3 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            />

            <div className="mt-3 flex justify-end">
              <button
                type="submit"
                disabled={sending}
                className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
              >
                <Send size={16} />

                {sending
                  ? "Posting..."
                  : "Post Comment"}
              </button>
            </div>
          </form>
        </section>
      </div>
    </div>
  );
}