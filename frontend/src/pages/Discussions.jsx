import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  ArrowLeft,
  MessageSquare,
  MessageCircle,
  Plus,
  Pencil,
  Trash2,
  Send,
  User,
  CalendarDays,
  Reply,
  X,
  Save,
  Loader2,
  AlertCircle,
} from "lucide-react";

import { getDecision } from "../api/decisionApi";

import {
  getThreads,
  createThread,
  updateThread,
  deleteThread,
  getDecisionComments,
  createDecisionComment,
  updateComment,
  deleteComment,
  getThreadReplies,
  createThreadReply,
} from "../api/discussionApi";

function formatDate(dateValue) {
  if (!dateValue) return "—";

  const date = new Date(dateValue);

  if (Number.isNaN(date.getTime())) {
    return "—";
  }

  return date.toLocaleString();
}

function Discussions() {
  const { decisionId } = useParams();

  const [decision, setDecision] = useState(null);
  const [threads, setThreads] = useState([]);
  const [comments, setComments] = useState([]);
  const [threadReplies, setThreadReplies] = useState({});

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [threadTitle, setThreadTitle] = useState("");
  const [threadDescription, setThreadDescription] = useState("");

  const [commentContent, setCommentContent] = useState("");

  const [replyContent, setReplyContent] = useState({});

  const [creatingThread, setCreatingThread] = useState(false);
  const [creatingComment, setCreatingComment] = useState(false);
  const [creatingReply, setCreatingReply] = useState({});

  const [editingThreadId, setEditingThreadId] = useState(null);
  const [editingThreadTitle, setEditingThreadTitle] = useState("");
  const [editingThreadDescription, setEditingThreadDescription] =
    useState("");

  const [editingCommentId, setEditingCommentId] = useState(null);
  const [editingCommentContent, setEditingCommentContent] = useState("");

  const [deletingThreadId, setDeletingThreadId] = useState(null);
  const [deletingCommentId, setDeletingCommentId] = useState(null);

  useEffect(() => {
    loadDiscussionPage();
  }, [decisionId]);

  async function loadDiscussionPage() {
    try {
      setLoading(true);
      setError("");

      const [
        decisionData,
        threadData,
        commentData,
      ] = await Promise.all([
        getDecision(decisionId),
        getThreads(decisionId),
        getDecisionComments(decisionId),
      ]);

      setDecision(decisionData);
      setThreads(threadData || []);
      setComments(commentData || []);

      const replies = {};

      await Promise.all(
        (threadData || []).map(async (thread) => {
          try {
            const data = await getThreadReplies(thread.id);
            replies[thread.id] = data || [];
          } catch (err) {
            console.error(
              `Failed to load replies for thread ${thread.id}`,
              err
            );

            replies[thread.id] = [];
          }
        })
      );

      setThreadReplies(replies);
    } catch (err) {
      console.error("Failed to load discussions:", err);

      if (err.response?.status === 401) {
        setError(
          "Your session has expired. Please log in again."
        );
      } else if (err.response?.status === 403) {
        setError(
          "You do not have permission to view discussions."
        );
      } else if (err.response?.status === 404) {
        setError("The decision could not be found.");
      } else if (err.response?.status >= 500) {
        setError(
          "The server encountered an error. Please try again."
        );
      } else {
        setError("Unable to load discussions.");
      }
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateThread(event) {
    event.preventDefault();

    if (!threadTitle.trim()) {
      return;
    }

    try {
      setCreatingThread(true);
      setError("");

      const newThread = await createThread(decisionId, {
        title: threadTitle.trim(),
        description: threadDescription.trim(),
      });

      setThreads((current) => [...current, newThread]);

      setThreadReplies((current) => ({
        ...current,
        [newThread.id]: [],
      }));

      setThreadTitle("");
      setThreadDescription("");
    } catch (err) {
      console.error("Failed to create thread:", err);

      setError(
        getErrorMessage(
          err,
          "Unable to create discussion thread."
        )
      );
    } finally {
      setCreatingThread(false);
    }
  }

  async function handleCreateComment(event) {
    event.preventDefault();

    if (!commentContent.trim()) {
      return;
    }

    try {
      setCreatingComment(true);
      setError("");

      const newComment = await createDecisionComment(
        decisionId,
        {
          content: commentContent.trim(),
        }
      );

      setComments((current) => [
        ...current,
        newComment,
      ]);

      setCommentContent("");
    } catch (err) {
      console.error("Failed to create comment:", err);

      setError(
        getErrorMessage(
          err,
          "Unable to add comment."
        )
      );
    } finally {
      setCreatingComment(false);
    }
  }

  async function handleCreateReply(threadId) {
    const content = replyContent[threadId] || "";

    if (!content.trim()) {
      return;
    }

    try {
      setCreatingReply((current) => ({
        ...current,
        [threadId]: true,
      }));

      setError("");

      const newReply = await createThreadReply(
        threadId,
        {
          content: content.trim(),
        }
      );

      setThreadReplies((current) => ({
        ...current,
        [threadId]: [
          ...(current[threadId] || []),
          newReply,
        ],
      }));

      setReplyContent((current) => ({
        ...current,
        [threadId]: "",
      }));
    } catch (err) {
      console.error("Failed to create reply:", err);

      setError(
        getErrorMessage(
          err,
          "Unable to add reply."
        )
      );
    } finally {
      setCreatingReply((current) => ({
        ...current,
        [threadId]: false,
      }));
    }
  }

  function startThreadEdit(thread) {
    setEditingThreadId(thread.id);
    setEditingThreadTitle(thread.title || "");
    setEditingThreadDescription(
      thread.description || ""
    );
  }

  async function handleSaveThreadEdit(threadId) {
    if (!editingThreadTitle.trim()) {
      return;
    }

    try {
      const updatedThread = await updateThread(
        threadId,
        {
          title: editingThreadTitle.trim(),
          description:
            editingThreadDescription.trim(),
        }
      );

      setThreads((current) =>
        current.map((thread) =>
          thread.id === threadId
            ? updatedThread
            : thread
        )
      );

      setEditingThreadId(null);
      setEditingThreadTitle("");
      setEditingThreadDescription("");
    } catch (err) {
      console.error("Failed to update thread:", err);

      setError(
        getErrorMessage(
          err,
          "Unable to update discussion thread."
        )
      );
    }
  }

  async function handleDeleteThread(threadId) {
    const confirmed = window.confirm(
      "Are you sure you want to delete this discussion thread?"
    );

    if (!confirmed) {
      return;
    }

    try {
      setDeletingThreadId(threadId);
      setError("");

      await deleteThread(threadId);

      setThreads((current) =>
        current.filter(
          (thread) => thread.id !== threadId
        )
      );

      setThreadReplies((current) => {
        const next = {
          ...current,
        };

        delete next[threadId];

        return next;
      });
    } catch (err) {
      console.error("Failed to delete thread:", err);

      setError(
        getErrorMessage(
          err,
          "Unable to delete discussion thread."
        )
      );
    } finally {
      setDeletingThreadId(null);
    }
  }

  function startCommentEdit(comment) {
    setEditingCommentId(comment.id);
    setEditingCommentContent(
      comment.content || ""
    );
  }

  async function handleSaveCommentEdit(commentId) {
    if (!editingCommentContent.trim()) {
      return;
    }

    try {
      const updatedComment = await updateComment(
        commentId,
        {
          content:
            editingCommentContent.trim(),
        }
      );

      setComments((current) =>
        current.map((comment) =>
          comment.id === commentId
            ? updatedComment
            : comment
        )
      );

      setThreadReplies((current) => {
        const next = {
          ...current,
        };

        Object.keys(next).forEach((threadId) => {
          next[threadId] =
            next[threadId].map((reply) =>
              reply.id === commentId
                ? updatedComment
                : reply
            );
        });

        return next;
      });

      setEditingCommentId(null);
      setEditingCommentContent("");
    } catch (err) {
      console.error("Failed to update comment:", err);

      setError(
        getErrorMessage(
          err,
          "Unable to update comment."
        )
      );
    }
  }

  async function handleDeleteComment(commentId) {
    const confirmed = window.confirm(
      "Are you sure you want to delete this comment?"
    );

    if (!confirmed) {
      return;
    }

    try {
      setDeletingCommentId(commentId);
      setError("");

      await deleteComment(commentId);

      setComments((current) =>
        current.filter(
          (comment) => comment.id !== commentId
        )
      );

      setThreadReplies((current) => {
        const next = {
          ...current,
        };

        Object.keys(next).forEach((threadId) => {
          next[threadId] =
            next[threadId].filter(
              (reply) =>
                reply.id !== commentId
            );
        });

        return next;
      });
    } catch (err) {
      console.error("Failed to delete comment:", err);

      setError(
        getErrorMessage(
          err,
          "Unable to delete comment."
        )
      );
    } finally {
      setDeletingCommentId(null);
    }
  }

  function getErrorMessage(err, fallback) {
    if (err.response?.status === 401) {
      return "Your session has expired. Please log in again.";
    }

    if (err.response?.status === 403) {
      return (
        err.response?.data?.detail ||
        "You do not have permission to perform this action."
      );
    }

    if (err.response?.status === 404) {
      return (
        err.response?.data?.detail ||
        "The requested resource was not found."
      );
    }

    if (err.response?.status === 422) {
      const detail = err.response?.data?.detail;

      if (Array.isArray(detail)) {
        return detail
          .map((item) => item.msg)
          .join(" ");
      }

      return (
        detail ||
        "Please check the information entered."
      );
    }

    if (err.response?.status >= 500) {
      return "The server encountered an error. Please try again.";
    }

    return fallback;
  }

  if (loading) {
    return (
      <div className="discussion-page-loading">
        <Loader2
          size={24}
          className="discussion-spin"
        />
        <span>Loading discussions...</span>
      </div>
    );
  }

  if (error && !decision) {
    return (
      <div className="discussion-page">
        <div className="discussion-error-page">
          <AlertCircle size={28} />

          <h2>Unable to Load Discussions</h2>

          <p>{error}</p>

          <button
            type="button"
            className="discussion-primary"
            onClick={loadDiscussionPage}
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="discussion-page">

      <style>{`
        .discussion-page {
          max-width: 1120px;
          margin: 0 auto;
          padding: 4px 0 40px;
        }

        .discussion-page-loading {
          min-height: 400px;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 10px;
          color: #64748b;
          font-size: 14px;
        }

        .discussion-spin {
          animation: discussionSpin 1s linear infinite;
        }

        @keyframes discussionSpin {
          from {
            transform: rotate(0deg);
          }

          to {
            transform: rotate(360deg);
          }
        }

        .discussion-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          gap: 20px;
          margin-bottom: 25px;
        }

        .discussion-header-left {
          display: flex;
          gap: 15px;
          align-items: flex-start;
        }

        .discussion-header-icon {
          width: 50px;
          height: 50px;
          min-width: 50px;
          border-radius: 14px;
          background: #eaf2ff;
          color: #2563eb;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .discussion-back {
          display: inline-flex;
          align-items: center;
          gap: 7px;
          color: #64748b;
          text-decoration: none;
          font-size: 13px;
          font-weight: 650;
          margin-bottom: 8px;
        }

        .discussion-back:hover {
          color: #2563eb;
        }

        .discussion-eyebrow {
          color: #64748b;
          font-size: 11px;
          font-weight: 800;
          letter-spacing: .08em;
          text-transform: uppercase;
          margin-bottom: 5px;
        }

        .discussion-header h1 {
          margin: 0;
          color: #0f172a;
          font-size: 29px;
        }

        .discussion-header p {
          margin: 7px 0 0;
          color: #64748b;
          font-size: 14px;
        }

        .discussion-header strong {
          color: #334155;
        }

        .discussion-card {
          background: #fff;
          border: 1px solid #e2e8f0;
          border-radius: 17px;
          box-shadow: 0 7px 25px rgba(15, 23, 42, .05);
          margin-bottom: 20px;
          overflow: hidden;
        }

        .discussion-card-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          gap: 15px;
          padding: 20px 23px;
          border-bottom: 1px solid #e2e8f0;
          background: #f8fafc;
        }

        .discussion-card-title {
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .discussion-card-title-icon {
          width: 36px;
          height: 36px;
          border-radius: 10px;
          background: #dbeafe;
          color: #2563eb;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .discussion-card-header h2 {
          margin: 0;
          color: #0f172a;
          font-size: 17px;
        }

        .discussion-card-header p {
          margin: 4px 0 0;
          color: #64748b;
          font-size: 12px;
        }

        .discussion-count {
          padding: 5px 10px;
          border-radius: 20px;
          background: #e2e8f0;
          color: #475569;
          font-size: 11px;
          font-weight: 750;
        }

        .discussion-card-body {
          padding: 23px;
        }

        .discussion-form-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 18px;
        }

        .discussion-full {
          grid-column: 1 / -1;
        }

        .discussion-field {
          display: flex;
          flex-direction: column;
          gap: 7px;
        }

        .discussion-field label {
          display: flex;
          align-items: center;
          gap: 6px;
          color: #334155;
          font-size: 13px;
          font-weight: 750;
        }

        .discussion-required {
          color: #dc2626;
        }

        .discussion-field input,
        .discussion-field textarea,
        .discussion-reply-form textarea,
        .discussion-edit textarea {
          width: 100%;
          box-sizing: border-box;
          border: 1px solid #cbd5e1;
          border-radius: 10px;
          padding: 11px 13px;
          background: #fff;
          color: #0f172a;
          font-family: inherit;
          font-size: 13px;
          outline: none;
          resize: vertical;
          transition: border-color .2s, box-shadow .2s;
        }

        .discussion-field input {
          min-height: 44px;
        }

        .discussion-field textarea {
          min-height: 110px;
        }

        .discussion-field input:focus,
        .discussion-field textarea:focus,
        .discussion-reply-form textarea:focus,
        .discussion-edit textarea:focus {
          border-color: #2563eb;
          box-shadow: 0 0 0 3px rgba(37, 99, 235, .1);
        }

        .discussion-field input::placeholder,
        .discussion-field textarea::placeholder,
        .discussion-reply-form textarea::placeholder {
          color: #94a3b8;
        }

        .discussion-primary,
        .discussion-secondary,
        .discussion-danger {
          min-height: 40px;
          padding: 0 14px;
          border-radius: 8px;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: 7px;
          font-family: inherit;
          font-size: 12px;
          font-weight: 750;
          cursor: pointer;
          border: 1px solid transparent;
          transition: .15s ease;
        }

        .discussion-primary {
          background: #2563eb;
          color: #fff;
        }

        .discussion-primary:hover:not(:disabled) {
          background: #1d4ed8;
          box-shadow: 0 4px 12px rgba(37, 99, 235, .18);
        }

        .discussion-secondary {
          background: #fff;
          border-color: #cbd5e1;
          color: #475569;
        }

        .discussion-secondary:hover:not(:disabled) {
          background: #f8fafc;
        }

        .discussion-danger {
          background: #fff;
          border-color: #fecaca;
          color: #dc2626;
        }

        .discussion-danger:hover:not(:disabled) {
          background: #fef2f2;
        }

        .discussion-primary:disabled,
        .discussion-secondary:disabled,
        .discussion-danger:disabled {
          opacity: .55;
          cursor: not-allowed;
        }

        .discussion-form-action {
          margin-top: 18px;
          display: flex;
          justify-content: flex-end;
        }

        .discussion-error {
          display: flex;
          align-items: flex-start;
          gap: 10px;
          margin-bottom: 20px;
          padding: 14px 16px;
          border: 1px solid #fecaca;
          border-radius: 11px;
          background: #fef2f2;
          color: #991b1b;
          font-size: 13px;
        }

        .discussion-error p {
          margin: 0;
          line-height: 1.5;
        }

        .discussion-error-page {
          min-height: 400px;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          text-align: center;
          color: #64748b;
        }

        .discussion-error-page h2 {
          margin: 12px 0 5px;
          color: #334155;
        }

        .discussion-error-page p {
          margin: 0 0 18px;
        }

        .discussion-list {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .discussion-thread {
          border: 1px solid #e2e8f0;
          border-radius: 13px;
          overflow: hidden;
          background: #fff;
        }

        .discussion-thread-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          gap: 15px;
          padding: 18px 20px;
          background: #f8fafc;
          border-bottom: 1px solid #e2e8f0;
        }

        .discussion-thread-header h3 {
          margin: 0 0 5px;
          color: #0f172a;
          font-size: 16px;
        }

        .discussion-thread-meta {
          display: flex;
          align-items: center;
          flex-wrap: wrap;
          gap: 8px;
          color: #94a3b8;
          font-size: 11px;
        }

        .discussion-thread-meta span {
          display: inline-flex;
          align-items: center;
          gap: 4px;
        }

        .discussion-thread-actions {
          display: flex;
          gap: 7px;
        }

        .discussion-thread-description {
          padding: 17px 20px;
          color: #64748b;
          font-size: 13px;
          line-height: 1.6;
        }

        .discussion-edit {
          padding: 20px;
        }

        .discussion-edit-actions {
          display: flex;
          justify-content: flex-end;
          gap: 8px;
          margin-top: 14px;
        }

        .discussion-replies {
          border-top: 1px solid #e2e8f0;
          padding: 18px 20px;
          background: #fcfdff;
        }

        .discussion-replies-title {
          display: flex;
          align-items: center;
          gap: 7px;
          margin-bottom: 13px;
          color: #475569;
          font-size: 12px;
          font-weight: 800;
          text-transform: uppercase;
          letter-spacing: .04em;
        }

        .discussion-reply {
          padding: 14px;
          margin-bottom: 10px;
          border: 1px solid #e2e8f0;
          border-radius: 10px;
          background: #fff;
        }

        .discussion-comment-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 10px;
        }

        .discussion-comment-user {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          color: #334155;
          font-size: 12px;
          font-weight: 750;
        }

        .discussion-comment-date {
          color: #94a3b8;
          font-size: 10px;
        }

        .discussion-comment-content {
          margin: 8px 0 10px;
          color: #475569;
          font-size: 13px;
          line-height: 1.6;
          white-space: pre-wrap;
        }

        .discussion-comment-actions {
          display: flex;
          gap: 7px;
        }

        .discussion-reply-form {
          display: flex;
          gap: 9px;
          align-items: flex-end;
          margin-top: 13px;
        }

        .discussion-reply-form textarea {
          min-height: 42px;
          max-height: 130px;
        }

        .discussion-reply-form button {
          flex-shrink: 0;
        }

        .discussion-no-replies {
          color: #94a3b8;
          font-size: 12px;
          margin-bottom: 12px;
        }

        .discussion-comments-list {
          margin-top: 22px;
          display: flex;
          flex-direction: column;
          gap: 10px;
        }

        .discussion-comment {
          padding: 16px;
          border: 1px solid #e2e8f0;
          border-radius: 11px;
          background: #fff;
        }

        .discussion-empty {
          padding: 45px 20px;
          text-align: center;
          color: #94a3b8;
        }

        .discussion-empty-icon {
          width: 50px;
          height: 50px;
          margin: 0 auto 12px;
          border-radius: 13px;
          background: #f1f5f9;
          color: #64748b;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .discussion-empty h3 {
          margin: 0 0 5px;
          color: #475569;
          font-size: 15px;
        }

        .discussion-empty p {
          margin: 0;
          font-size: 12px;
        }

        .discussion-footer {
          display: flex;
          justify-content: flex-start;
          margin-top: 5px;
        }

        @media (max-width: 760px) {
          .discussion-header {
            flex-direction: column;
          }

          .discussion-form-grid {
            grid-template-columns: 1fr;
          }

          .discussion-full {
            grid-column: auto;
          }

          .discussion-thread-header {
            flex-direction: column;
          }

          .discussion-thread-actions {
            width: 100%;
          }

          .discussion-thread-actions button {
            flex: 1;
          }
        }

        @media (max-width: 550px) {
          .discussion-page {
            padding-bottom: 25px;
          }

          .discussion-header h1 {
            font-size: 24px;
          }

          .discussion-card-body,
          .discussion-thread-header,
          .discussion-thread-description,
          .discussion-replies {
            padding: 16px;
          }

          .discussion-reply-form {
            flex-direction: column;
            align-items: stretch;
          }

          .discussion-reply-form button {
            width: 100%;
          }

          .discussion-form-action {
            justify-content: stretch;
          }

          .discussion-form-action button {
            width: 100%;
          }
        }
      `}</style>

      {/* HEADER */}
      <div className="discussion-header">
        <div className="discussion-header-left">

          <div className="discussion-header-icon">
            <MessageSquare size={24} />
          </div>

          <div>
            <Link
              to={`/decisions/${decisionId}`}
              className="discussion-back"
            >
              <ArrowLeft size={15} />
              Back to Decision
            </Link>

            <div className="discussion-eyebrow">
              Decision Collaboration
            </div>

            <h1>Discussions</h1>

            <p>
              Decision #{decisionId}:{" "}
              <strong>
                {decision?.title || "Untitled Decision"}
              </strong>
            </p>
          </div>

        </div>
      </div>

      {/* ERROR */}
      {error && (
        <div className="discussion-error">
          <AlertCircle size={19} />

          <p>{error}</p>
        </div>
      )}

      {/* CREATE THREAD */}
      <div className="discussion-card">

        <div className="discussion-card-header">
          <div className="discussion-card-title">
            <div className="discussion-card-title-icon">
              <Plus size={18} />
            </div>

            <div>
              <h2>Start a Discussion</h2>

              <p>
                Create a focused discussion thread
                for this decision.
              </p>
            </div>
          </div>
        </div>

        <div className="discussion-card-body">

          <form onSubmit={handleCreateThread}>

            <div className="discussion-form-grid">

              <div className="discussion-field">
                <label htmlFor="thread-title">
                  <MessageSquare size={14} />
                  Discussion Title
                  <span className="discussion-required">
                    *
                  </span>
                </label>

                <input
                  id="thread-title"
                  type="text"
                  placeholder="e.g. Should we choose AWS?"
                  value={threadTitle}
                  onChange={(event) =>
                    setThreadTitle(
                      event.target.value
                    )
                  }
                  disabled={creatingThread}
                />
              </div>

              <div className="discussion-field">
                <label>
                  <User size={14} />
                  Discussion Purpose
                </label>

                <div
                  style={{
                    minHeight: "44px",
                    display: "flex",
                    alignItems: "center",
                    color: "#64748b",
                    fontSize: "12px",
                  }}
                >
                  Discuss options, concerns and
                  supporting information.
                </div>
              </div>

              <div className="discussion-field discussion-full">
                <label htmlFor="thread-description">
                  Description
                </label>

                <textarea
                  id="thread-description"
                  rows="5"
                  placeholder="Describe the topic you want the team to discuss..."
                  value={threadDescription}
                  onChange={(event) =>
                    setThreadDescription(
                      event.target.value
                    )
                  }
                  disabled={creatingThread}
                />
              </div>

            </div>

            <div className="discussion-form-action">
              <button
                type="submit"
                className="discussion-primary"
                disabled={
                  creatingThread ||
                  !threadTitle.trim()
                }
              >
                {creatingThread ? (
                  <>
                    <Loader2
                      size={15}
                      className="discussion-spin"
                    />
                    Creating...
                  </>
                ) : (
                  <>
                    <Plus size={15} />
                    Create Discussion
                  </>
                )}
              </button>
            </div>

          </form>

        </div>
      </div>

      {/* THREADS */}
      <div className="discussion-card">

        <div className="discussion-card-header">

          <div className="discussion-card-title">

            <div className="discussion-card-title-icon">
              <MessageCircle size={18} />
            </div>

            <div>
              <h2>Discussion Threads</h2>

              <p>
                Topics and conversations related
                to this decision.
              </p>
            </div>

          </div>

          <span className="discussion-count">
            {threads.length}{" "}
            {threads.length === 1
              ? "thread"
              : "threads"}
          </span>

        </div>

        <div className="discussion-card-body">

          {threads.length === 0 ? (
            <div className="discussion-empty">

              <div className="discussion-empty-icon">
                <MessageSquare size={23} />
              </div>

              <h3>
                No Discussion Threads
              </h3>

              <p>
                Start the first discussion for
                this decision.
              </p>

            </div>
          ) : (
            <div className="discussion-list">

              {threads.map((thread) => {

                const replies =
                  threadReplies[thread.id] || [];

                return (
                  <div
                    key={thread.id}
                    className="discussion-thread"
                  >

                    {editingThreadId ===
                    thread.id ? (
                      <div className="discussion-edit">

                        <div className="discussion-field">
                          <label>
                            Discussion Title
                          </label>

                          <input
                            type="text"
                            value={
                              editingThreadTitle
                            }
                            onChange={(event) =>
                              setEditingThreadTitle(
                                event.target.value
                              )
                            }
                          />
                        </div>

                        <div
                          className="discussion-field"
                          style={{
                            marginTop: "16px",
                          }}
                        >
                          <label>
                            Description
                          </label>

                          <textarea
                            rows="4"
                            value={
                              editingThreadDescription
                            }
                            onChange={(event) =>
                              setEditingThreadDescription(
                                event.target.value
                              )
                            }
                          />
                        </div>

                        <div className="discussion-edit-actions">

                          <button
                            type="button"
                            className="discussion-secondary"
                            onClick={() =>
                              setEditingThreadId(
                                null
                              )
                            }
                          >
                            <X size={14} />
                            Cancel
                          </button>

                          <button
                            type="button"
                            className="discussion-primary"
                            onClick={() =>
                              handleSaveThreadEdit(
                                thread.id
                              )
                            }
                          >
                            <Save size={14} />
                            Save Changes
                          </button>

                        </div>

                      </div>
                    ) : (
                      <>
                        <div className="discussion-thread-header">

                          <div>

                            <h3>
                              {thread.title}
                            </h3>

                            <div className="discussion-thread-meta">

                              <span>
                                <MessageSquare
                                  size={12}
                                />
                                Thread #{thread.id}
                              </span>

                              <span>•</span>

                              <span>
                                <User size={12} />
                                User{" "}
                                {thread.created_by}
                              </span>

                              <span>•</span>

                              <span>
                                <CalendarDays
                                  size={12}
                                />
                                {formatDate(
                                  thread.created_at
                                )}
                              </span>

                            </div>

                          </div>

                          <div className="discussion-thread-actions">

                            <button
                              type="button"
                              className="discussion-secondary"
                              onClick={() =>
                                startThreadEdit(
                                  thread
                                )
                              }
                            >
                              <Pencil size={13} />
                              Edit
                            </button>

                            <button
                              type="button"
                              className="discussion-danger"
                              onClick={() =>
                                handleDeleteThread(
                                  thread.id
                                )
                              }
                              disabled={
                                deletingThreadId ===
                                thread.id
                              }
                            >
                              {deletingThreadId ===
                              thread.id ? (
                                <Loader2
                                  size={13}
                                  className="discussion-spin"
                                />
                              ) : (
                                <Trash2 size={13} />
                              )}

                              {deletingThreadId ===
                              thread.id
                                ? "Deleting..."
                                : "Delete"}
                            </button>

                          </div>

                        </div>

                        <div className="discussion-thread-description">
                          {thread.description ||
                            "No description provided."}
                        </div>
                      </>
                    )}

                    {/* REPLIES */}
                    <div className="discussion-replies">

                      <div className="discussion-replies-title">
                        <Reply size={14} />
                        Replies
                        <span>
                          ({replies.length})
                        </span>
                      </div>

                      {replies.length === 0 ? (
                        <div className="discussion-no-replies">
                          No replies yet. Start the
                          conversation below.
                        </div>
                      ) : (
                        replies.map((reply) => (
                          <div
                            key={reply.id}
                            className="discussion-reply"
                          >

                            {editingCommentId ===
                            reply.id ? (
                              <div className="discussion-edit">

                                <textarea
                                  rows="4"
                                  value={
                                    editingCommentContent
                                  }
                                  onChange={(event) =>
                                    setEditingCommentContent(
                                      event.target.value
                                    )
                                  }
                                />

                                <div className="discussion-edit-actions">

                                  <button
                                    type="button"
                                    className="discussion-secondary"
                                    onClick={() =>
                                      setEditingCommentId(
                                        null
                                      )
                                    }
                                  >
                                    <X size={14} />
                                    Cancel
                                  </button>

                                  <button
                                    type="button"
                                    className="discussion-primary"
                                    onClick={() =>
                                      handleSaveCommentEdit(
                                        reply.id
                                      )
                                    }
                                  >
                                    <Save size={14} />
                                    Save
                                  </button>

                                </div>

                              </div>
                            ) : (
                              <>
                                <div className="discussion-comment-header">

                                  <div className="discussion-comment-user">
                                    <User size={13} />
                                    User{" "}
                                    {reply.user_id}
                                  </div>

                                  <span className="discussion-comment-date">
                                    {formatDate(
                                      reply.created_at
                                    )}
                                  </span>

                                </div>

                                <div className="discussion-comment-content">
                                  {reply.content}
                                </div>

                                <div className="discussion-comment-actions">

                                  <button
                                    type="button"
                                    className="discussion-secondary"
                                    onClick={() =>
                                      startCommentEdit(
                                        reply
                                      )
                                    }
                                  >
                                    <Pencil size={12} />
                                    Edit
                                  </button>

                                  <button
                                    type="button"
                                    className="discussion-danger"
                                    onClick={() =>
                                      handleDeleteComment(
                                        reply.id
                                      )
                                    }
                                    disabled={
                                      deletingCommentId ===
                                      reply.id
                                    }
                                  >
                                    <Trash2 size={12} />
                                    Delete
                                  </button>

                                </div>
                              </>
                            )}

                          </div>
                        ))
                      )}

                      {/* REPLY FORM */}
                      <div className="discussion-reply-form">

                        <textarea
                          rows="2"
                          placeholder="Write a reply..."
                          value={
                            replyContent[
                              thread.id
                            ] || ""
                          }
                          onChange={(event) =>
                            setReplyContent(
                              (current) => ({
                                ...current,
                                [thread.id]:
                                  event.target.value,
                              })
                            )
                          }
                        />

                        <button
                          type="button"
                          className="discussion-primary"
                          onClick={() =>
                            handleCreateReply(
                              thread.id
                            )
                          }
                          disabled={
                            creatingReply[
                              thread.id
                            ] ||
                            !(
                              replyContent[
                                thread.id
                              ] || ""
                            ).trim()
                          }
                        >
                          {creatingReply[
                            thread.id
                          ] ? (
                            <>
                              <Loader2
                                size={14}
                                className="discussion-spin"
                              />
                              Replying...
                            </>
                          ) : (
                            <>
                              <Send size={14} />
                              Reply
                            </>
                          )}
                        </button>

                      </div>

                    </div>

                  </div>
                );
              })}

            </div>
          )}

        </div>
      </div>

      {/* COMMENTS */}
      <div className="discussion-card">

        <div className="discussion-card-header">

          <div className="discussion-card-title">

            <div className="discussion-card-title-icon">
              <MessageCircle size={18} />
            </div>

            <div>
              <h2>Decision Comments</h2>

              <p>
                General comments directly associated
                with this decision.
              </p>
            </div>

          </div>

          <span className="discussion-count">
            {comments.length}{" "}
            {comments.length === 1
              ? "comment"
              : "comments"}
          </span>

        </div>

        <div className="discussion-card-body">

          <form onSubmit={handleCreateComment}>

            <div className="discussion-field">

              <label htmlFor="decision-comment">
                <MessageCircle size={14} />
                Add Comment
              </label>

              <textarea
                id="decision-comment"
                rows="4"
                placeholder="Write a comment about this decision..."
                value={commentContent}
                onChange={(event) =>
                  setCommentContent(
                    event.target.value
                  )
                }
                disabled={creatingComment}
              />

            </div>

            <div className="discussion-form-action">

              <button
                type="submit"
                className="discussion-primary"
                disabled={
                  creatingComment ||
                  !commentContent.trim()
                }
              >
                {creatingComment ? (
                  <>
                    <Loader2
                      size={15}
                      className="discussion-spin"
                    />
                    Adding...
                  </>
                ) : (
                  <>
                    <Send size={15} />
                    Add Comment
                  </>
                )}
              </button>

            </div>

          </form>

          <div className="discussion-comments-list">

            {comments.length === 0 ? (
              <div className="discussion-empty">

                <div className="discussion-empty-icon">
                  <MessageCircle size={22} />
                </div>

                <h3>No Comments Yet</h3>

                <p>
                  Be the first to add a comment
                  to this decision.
                </p>

              </div>
            ) : (
              comments.map((comment) => (
                <div
                  key={comment.id}
                  className="discussion-comment"
                >

                  {editingCommentId ===
                  comment.id ? (
                    <div className="discussion-edit">

                      <textarea
                        rows="4"
                        value={
                          editingCommentContent
                        }
                        onChange={(event) =>
                          setEditingCommentContent(
                            event.target.value
                          )
                        }
                      />

                      <div className="discussion-edit-actions">

                        <button
                          type="button"
                          className="discussion-secondary"
                          onClick={() =>
                            setEditingCommentId(
                              null
                            )
                          }
                        >
                          <X size={14} />
                          Cancel
                        </button>

                        <button
                          type="button"
                          className="discussion-primary"
                          onClick={() =>
                            handleSaveCommentEdit(
                              comment.id
                            )
                          }
                        >
                          <Save size={14} />
                          Save
                        </button>

                      </div>

                    </div>
                  ) : (
                    <>
                      <div className="discussion-comment-header">

                        <div className="discussion-comment-user">
                          <User size={13} />
                          User{" "}
                          {comment.user_id}
                        </div>

                        <span className="discussion-comment-date">
                          {formatDate(
                            comment.created_at
                          )}
                        </span>

                      </div>

                      <div className="discussion-comment-content">
                        {comment.content}
                      </div>

                      <div className="discussion-comment-actions">

                        <button
                          type="button"
                          className="discussion-secondary"
                          onClick={() =>
                            startCommentEdit(
                              comment
                            )
                          }
                        >
                          <Pencil size={12} />
                          Edit
                        </button>

                        <button
                          type="button"
                          className="discussion-danger"
                          onClick={() =>
                            handleDeleteComment(
                              comment.id
                            )
                          }
                          disabled={
                            deletingCommentId ===
                            comment.id
                          }
                        >
                          {deletingCommentId ===
                          comment.id ? (
                            <Loader2
                              size={12}
                              className="discussion-spin"
                            />
                          ) : (
                            <Trash2 size={12} />
                          )}

                          {deletingCommentId ===
                          comment.id
                            ? "Deleting..."
                            : "Delete"}
                        </button>

                      </div>
                    </>
                  )}

                </div>
              ))
            )}

          </div>
        </div>
      </div>

      {/* FOOTER */}
      <div className="discussion-footer">

        <Link
          to={`/decisions/${decisionId}`}
          className="discussion-secondary"
        >
          <ArrowLeft size={15} />
          Back to Decision
        </Link>

      </div>

    </div>
  );
}

export default Discussions;