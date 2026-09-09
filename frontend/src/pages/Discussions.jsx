import { useEffect, useState } from "react";
import {
  Link,
  useParams,
} from "react-router-dom";

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

  const [decision, setDecision] =
    useState(null);

  const [threads, setThreads] =
    useState([]);

  const [comments, setComments] =
    useState([]);

  const [threadReplies, setThreadReplies] =
    useState({});

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [threadTitle, setThreadTitle] =
    useState("");

  const [threadDescription, setThreadDescription] =
    useState("");

  const [commentContent, setCommentContent] =
    useState("");

  const [replyContent, setReplyContent] =
    useState({});

  const [creatingThread, setCreatingThread] =
    useState(false);

  const [creatingComment, setCreatingComment] =
    useState(false);

  const [creatingReply, setCreatingReply] =
    useState({});

  const [editingThreadId, setEditingThreadId] =
    useState(null);

  const [editingThreadTitle, setEditingThreadTitle] =
    useState("");

  const [editingThreadDescription, setEditingThreadDescription] =
    useState("");

  const [editingCommentId, setEditingCommentId] =
    useState(null);

  const [editingCommentContent, setEditingCommentContent] =
    useState("");

  const [deletingThreadId, setDeletingThreadId] =
    useState(null);

  const [deletingCommentId, setDeletingCommentId] =
    useState(null);

  // =====================================================
  // LOAD DATA
  // =====================================================

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

      // Load replies for all threads
      const replies = {};

      await Promise.all(
        (threadData || []).map(
          async (thread) => {
            try {
              const data =
                await getThreadReplies(
                  thread.id
                );

              replies[thread.id] =
                data || [];
            } catch (err) {
              console.error(
                `Failed to load replies for thread ${thread.id}`,
                err
              );

              replies[thread.id] = [];
            }
          }
        )
      );

      setThreadReplies(replies);
    } catch (err) {
      console.error(
        "Failed to load discussions:",
        err
      );

      if (err.response?.status === 401) {
        setError(
          "Your session has expired. Please log in again."
        );
      } else if (err.response?.status === 403) {
        setError(
          "You do not have permission to view discussions."
        );
      } else if (err.response?.status === 404) {
        setError(
          "The decision could not be found."
        );
      } else if (err.response?.status >= 500) {
        setError(
          "The server encountered an error. Please try again."
        );
      } else {
        setError(
          "Unable to load discussions."
        );
      }
    } finally {
      setLoading(false);
    }
  }

  // =====================================================
  // CREATE THREAD
  // =====================================================

  async function handleCreateThread(event) {
    event.preventDefault();

    if (!threadTitle.trim()) {
      return;
    }

    try {
      setCreatingThread(true);
      setError("");

      const newThread =
        await createThread(
          decisionId,
          {
            title:
              threadTitle.trim(),
            description:
              threadDescription.trim(),
          }
        );

      setThreads((current) => [
        ...current,
        newThread,
      ]);

      setThreadReplies((current) => ({
        ...current,
        [newThread.id]: [],
      }));

      setThreadTitle("");
      setThreadDescription("");
    } catch (err) {
      console.error(
        "Failed to create thread:",
        err
      );

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

  // =====================================================
  // CREATE DECISION COMMENT
  // =====================================================

  async function handleCreateComment(event) {
    event.preventDefault();

    if (!commentContent.trim()) {
      return;
    }

    try {
      setCreatingComment(true);
      setError("");

      const newComment =
        await createDecisionComment(
          decisionId,
          {
            content:
              commentContent.trim(),
          }
        );

      setComments((current) => [
        ...current,
        newComment,
      ]);

      setCommentContent("");
    } catch (err) {
      console.error(
        "Failed to create comment:",
        err
      );

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

  // =====================================================
  // CREATE THREAD REPLY
  // =====================================================

  async function handleCreateReply(
    threadId
  ) {
    const content =
      replyContent[threadId] || "";

    if (!content.trim()) {
      return;
    }

    try {
      setCreatingReply(
        (current) => ({
          ...current,
          [threadId]: true,
        })
      );

      setError("");

      const newReply =
        await createThreadReply(
          threadId,
          {
            content:
              content.trim(),
          }
        );

      setThreadReplies(
        (current) => ({
          ...current,
          [threadId]: [
            ...(current[threadId] ||
              []),
            newReply,
          ],
        })
      );

      setReplyContent(
        (current) => ({
          ...current,
          [threadId]: "",
        })
      );
    } catch (err) {
      console.error(
        "Failed to create reply:",
        err
      );

      setError(
        getErrorMessage(
          err,
          "Unable to add reply."
        )
      );
    } finally {
      setCreatingReply(
        (current) => ({
          ...current,
          [threadId]: false,
        })
      );
    }
  }

  // =====================================================
  // START THREAD EDIT
  // =====================================================

  function startThreadEdit(thread) {
    setEditingThreadId(thread.id);

    setEditingThreadTitle(
      thread.title || ""
    );

    setEditingThreadDescription(
      thread.description || ""
    );
  }

  // =====================================================
  // SAVE THREAD EDIT
  // =====================================================

  async function handleSaveThreadEdit(
    threadId
  ) {
    if (!editingThreadTitle.trim()) {
      return;
    }

    try {
      const updatedThread =
        await updateThread(
          threadId,
          {
            title:
              editingThreadTitle.trim(),
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
      console.error(
        "Failed to update thread:",
        err
      );

      setError(
        getErrorMessage(
          err,
          "Unable to update discussion thread."
        )
      );
    }
  }

  // =====================================================
  // DELETE THREAD
  // =====================================================

  async function handleDeleteThread(
    threadId
  ) {
    try {
      setDeletingThreadId(threadId);
      setError("");

      await deleteThread(threadId);

      setThreads((current) =>
        current.filter(
          (thread) =>
            thread.id !== threadId
        )
      );

      setThreadReplies(
        (current) => {
          const next = {
            ...current,
          };

          delete next[threadId];

          return next;
        }
      );
    } catch (err) {
      console.error(
        "Failed to delete thread:",
        err
      );

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

  // =====================================================
  // START COMMENT EDIT
  // =====================================================

  function startCommentEdit(comment) {
    setEditingCommentId(
      comment.id
    );

    setEditingCommentContent(
      comment.content || ""
    );
  }

  // =====================================================
  // SAVE COMMENT EDIT
  // =====================================================

  async function handleSaveCommentEdit(
    commentId
  ) {
    if (!editingCommentContent.trim()) {
      return;
    }

    try {
      const updatedComment =
        await updateComment(
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

      setThreadReplies(
        (current) => {
          const next = {
            ...current,
          };

          Object.keys(next).forEach(
            (threadId) => {
              next[threadId] =
                next[threadId].map(
                  (reply) =>
                    reply.id === commentId
                      ? updatedComment
                      : reply
                );
            }
          );

          return next;
        }
      );

      setEditingCommentId(null);
      setEditingCommentContent("");
    } catch (err) {
      console.error(
        "Failed to update comment:",
        err
      );

      setError(
        getErrorMessage(
          err,
          "Unable to update comment."
        )
      );
    }
  }

  // =====================================================
  // DELETE COMMENT
  // =====================================================

  async function handleDeleteComment(
    commentId
  ) {
    try {
      setDeletingCommentId(commentId);
      setError("");

      await deleteComment(
        commentId
      );

      setComments((current) =>
        current.filter(
          (comment) =>
            comment.id !== commentId
        )
      );

      setThreadReplies(
        (current) => {
          const next = {
            ...current,
          };

          Object.keys(next).forEach(
            (threadId) => {
              next[threadId] =
                next[threadId].filter(
                  (reply) =>
                    reply.id !== commentId
                );
            }
          );

          return next;
        }
      );
    } catch (err) {
      console.error(
        "Failed to delete comment:",
        err
      );

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

  // =====================================================
  // ERROR HELPER
  // =====================================================

  function getErrorMessage(
    err,
    fallback
  ) {
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
      const detail =
        err.response?.data?.detail;

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

  // =====================================================
  // LOADING
  // =====================================================

  if (loading) {
    return (
      <div className="loading-state">
        Loading discussions...
      </div>
    );
  }

  // =====================================================
  // PAGE ERROR
  // =====================================================

  if (error && !decision) {
    return (
      <div className="error-state">

        <h2>
          Unable to Load Discussions
        </h2>

        <p>{error}</p>

        <button
          type="button"
          className="primary-button"
          onClick={loadDiscussionPage}
        >
          Try Again
        </button>

      </div>
    );
  }

  return (
    <div className="page-container">

      {/* =================================================
          HEADER
      ================================================= */}

      <div className="page-header">

        <div>

          <Link
            to={`/decisions/${decisionId}`}
            className="back-link"
          >
            ← Back to Decision
          </Link>

          <h1>
            Discussions
          </h1>

          <p>
            Decision #{decisionId}:{" "}
            <strong>
              {decision?.title}
            </strong>
          </p>

        </div>

      </div>


      {/* =================================================
          ERROR
      ================================================= */}

      {error && (
        <div className="error-state">
          <p>{error}</p>
        </div>
      )}


      {/* =================================================
          CREATE THREAD
      ================================================= */}

      <div className="card">

        <h2>
          Start a Discussion
        </h2>

        <p>
          Create a focused discussion thread
          for this decision.
        </p>

        <form
          onSubmit={handleCreateThread}
        >

          <div className="form-group">

            <label htmlFor="thread-title">
              Discussion Title *
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
              disabled={
                creatingThread
              }
            />

          </div>


          <div className="form-group">

            <label htmlFor="thread-description">
              Description
            </label>

            <textarea
              id="thread-description"
              rows="5"
              placeholder="Describe the topic you want the team to discuss..."
              value={
                threadDescription
              }
              onChange={(event) =>
                setThreadDescription(
                  event.target.value
                )
              }
              disabled={
                creatingThread
              }
            />

          </div>


          <button
            type="submit"
            className="primary-button"
            disabled={
              creatingThread ||
              !threadTitle.trim()
            }
          >
            {creatingThread
              ? "Creating..."
              : "Create Discussion"}
          </button>

        </form>

      </div>


      {/* =================================================
          DISCUSSION THREADS
      ================================================= */}

      <div className="card">

        <div className="section-header">

          <div>

            <h2>
              Discussion Threads
            </h2>

            <p>
              {threads.length} thread
              {threads.length !== 1
                ? "s"
                : ""}
            </p>

          </div>

        </div>


        {threads.length === 0 ? (
          <div className="empty-state">

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

            {threads.map(
              (thread) => (
                <div
                  key={thread.id}
                  className="discussion-thread"
                >

                  {/* THREAD HEADER */}

                  {editingThreadId ===
                  thread.id ? (
                    <div>

                      <div className="form-group">

                        <label>
                          Title
                        </label>

                        <input
                          type="text"
                          value={
                            editingThreadTitle
                          }
                          onChange={(
                            event
                          ) =>
                            setEditingThreadTitle(
                              event.target
                                .value
                            )
                          }
                        />

                      </div>

                      <div className="form-group">

                        <label>
                          Description
                        </label>

                        <textarea
                          rows="4"
                          value={
                            editingThreadDescription
                          }
                          onChange={(
                            event
                          ) =>
                            setEditingThreadDescription(
                              event.target
                                .value
                            )
                          }
                        />

                      </div>

                      <div className="form-actions">

                        <button
                          type="button"
                          className="secondary-button"
                          onClick={() =>
                            setEditingThreadId(
                              null
                            )
                          }
                        >
                          Cancel
                        </button>

                        <button
                          type="button"
                          className="primary-button"
                          onClick={() =>
                            handleSaveThreadEdit(
                              thread.id
                            )
                          }
                        >
                          Save
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

                          <small>
                            Thread #
                            {thread.id}
                            {" • "}
                            Created by User{" "}
                            {thread.created_by}
                            {" • "}
                            {formatDate(
                              thread.created_at
                            )}
                          </small>

                        </div>

                        <div>

                          <button
                            type="button"
                            className="secondary-button small-button"
                            onClick={() =>
                              startThreadEdit(
                                thread
                              )
                            }
                          >
                            Edit
                          </button>

                          <button
                            type="button"
                            className="danger-button small-button"
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
                            thread.id
                              ? "Deleting..."
                              : "Delete"}
                          </button>

                        </div>

                      </div>

                      <p>
                        {thread.description ||
                          "No description provided."}
                      </p>
                    </>
                  )}


                  {/* THREAD REPLIES */}

                  <div className="thread-replies">

                    <h4>
                      Replies
                    </h4>

                    {(threadReplies[
                      thread.id
                    ] || []).length ===
                    0 ? (
                      <p className="muted-text">
                        No replies yet.
                      </p>
                    ) : (
                      (
                        threadReplies[
                          thread.id
                        ] || []
                      ).map(
                        (reply) => (
                          <div
                            key={reply.id}
                            className="comment-item"
                          >

                            {editingCommentId ===
                            reply.id ? (
                              <div>

                                <textarea
                                  rows="4"
                                  value={
                                    editingCommentContent
                                  }
                                  onChange={(
                                    event
                                  ) =>
                                    setEditingCommentContent(
                                      event.target
                                        .value
                                    )
                                  }
                                />

                                <div className="form-actions">

                                  <button
                                    type="button"
                                    className="secondary-button"
                                    onClick={() =>
                                      setEditingCommentId(
                                        null
                                      )
                                    }
                                  >
                                    Cancel
                                  </button>

                                  <button
                                    type="button"
                                    className="primary-button"
                                    onClick={() =>
                                      handleSaveCommentEdit(
                                        reply.id
                                      )
                                    }
                                  >
                                    Save
                                  </button>

                                </div>

                              </div>
                            ) : (
                              <>
                                <div className="comment-header">

                                  <strong>
                                    User{" "}
                                    {reply.user_id}
                                  </strong>

                                  <small>
                                    {formatDate(
                                      reply.created_at
                                    )}
                                  </small>

                                </div>

                                <p>
                                  {reply.content}
                                </p>

                                <div className="comment-actions">

                                  <button
                                    type="button"
                                    className="secondary-button small-button"
                                    onClick={() =>
                                      startCommentEdit(
                                        reply
                                      )
                                    }
                                  >
                                    Edit
                                  </button>

                                  <button
                                    type="button"
                                    className="danger-button small-button"
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
                                    Delete
                                  </button>

                                </div>

                              </>
                            )}

                          </div>
                        )
                      )
                    )}


                    {/* REPLY FORM */}

                    <div className="reply-form">

                      <textarea
                        rows="3"
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
                                event.target
                                  .value,
                            })
                          )
                        }
                      />

                      <button
                        type="button"
                        className="primary-button"
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
                        ]
                          ? "Replying..."
                          : "Reply"}
                      </button>

                    </div>

                  </div>

                </div>
              )
            )}

          </div>
        )}

      </div>


      {/* =================================================
          GENERAL COMMENTS
      ================================================= */}

      <div className="card">

        <h2>
          Decision Comments
        </h2>

        <p>
          General comments directly associated
          with this decision.
        </p>


        <form
          onSubmit={handleCreateComment}
        >

          <div className="form-group">

            <label htmlFor="decision-comment">
              Add Comment
            </label>

            <textarea
              id="decision-comment"
              rows="5"
              placeholder="Write a comment..."
              value={commentContent}
              onChange={(event) =>
                setCommentContent(
                  event.target.value
                )
              }
              disabled={
                creatingComment
              }
            />

          </div>

          <button
            type="submit"
            className="primary-button"
            disabled={
              creatingComment ||
              !commentContent.trim()
            }
          >
            {creatingComment
              ? "Adding..."
              : "Add Comment"}
          </button>

        </form>


        {/* COMMENTS LIST */}

        <div className="comments-list">

          {comments.length === 0 ? (
            <div className="empty-state">

              <p>
                No comments yet.
              </p>

            </div>
          ) : (
            comments.map(
              (comment) => (
                <div
                  key={comment.id}
                  className="comment-item"
                >

                  {editingCommentId ===
                  comment.id ? (
                    <div>

                      <textarea
                        rows="4"
                        value={
                          editingCommentContent
                        }
                        onChange={(
                          event
                        ) =>
                          setEditingCommentContent(
                            event.target
                              .value
                          )
                        }
                      />

                      <div className="form-actions">

                        <button
                          type="button"
                          className="secondary-button"
                          onClick={() =>
                            setEditingCommentId(
                              null
                            )
                          }
                        >
                          Cancel
                        </button>

                        <button
                          type="button"
                          className="primary-button"
                          onClick={() =>
                            handleSaveCommentEdit(
                              comment.id
                            )
                          }
                        >
                          Save
                        </button>

                      </div>

                    </div>
                  ) : (
                    <>
                      <div className="comment-header">

                        <strong>
                          User{" "}
                          {comment.user_id}
                        </strong>

                        <small>
                          {formatDate(
                            comment.created_at
                          )}
                        </small>

                      </div>

                      <p>
                        {comment.content}
                      </p>

                      <div className="comment-actions">

                        <button
                          type="button"
                          className="secondary-button small-button"
                          onClick={() =>
                            startCommentEdit(
                              comment
                            )
                          }
                        >
                          Edit
                        </button>

                        <button
                          type="button"
                          className="danger-button small-button"
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
                          comment.id
                            ? "Deleting..."
                            : "Delete"}
                        </button>

                      </div>

                    </>
                  )}

                </div>
              )
            )
          )}

        </div>

      </div>


      {/* =================================================
          FOOTER
      ================================================= */}

      <div className="page-footer-actions">

        <Link
          to={`/decisions/${decisionId}`}
          className="secondary-button"
        >
          ← Back to Decision
        </Link>

      </div>

    </div>
  );
}

export default Discussions;