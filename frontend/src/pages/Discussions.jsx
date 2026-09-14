import { useEffect, useState } from "react";
import api from "../services/api";

function Discussions() {
  const [decisions, setDecisions] = useState([]);
  const [selectedDecisionId, setSelectedDecisionId] = useState("");

  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState("");
  const [editingCommentId, setEditingCommentId] = useState(null);
  const [editingContent, setEditingContent] = useState("");

  const [threads, setThreads] = useState([]);
  const [newThreadTitle, setNewThreadTitle] = useState("");
  const [newThreadDescription, setNewThreadDescription] = useState("");
  const [editingThreadId, setEditingThreadId] = useState(null);
  const [editingThreadTitle, setEditingThreadTitle] = useState("");
  const [editingThreadDescription, setEditingThreadDescription] = useState("");
  const [editingThreadStatus, setEditingThreadStatus] = useState("Open");

  const [threadReplies, setThreadReplies] = useState({});
  const [newReply, setNewReply] = useState({});
  const [loadingReplies, setLoadingReplies] = useState({});
  const [editingReplyId, setEditingReplyId] = useState(null);
  const [editingReplyContent, setEditingReplyContent] = useState("");

  const [loadingDecisions, setLoadingDecisions] = useState(true);
  const [loadingComments, setLoadingComments] = useState(false);
  const [loadingThreads, setLoadingThreads] = useState(false);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    fetchDecisions();
  }, []);

  useEffect(() => {
    if (selectedDecisionId) {
      fetchComments(selectedDecisionId);
      fetchThreads(selectedDecisionId);
    }
  }, [selectedDecisionId]);

  const fetchDecisions = async () => {
    try {
      setLoadingDecisions(true);
      setError("");

      const response = await api.get("/decisions");

      setDecisions(response.data);

      if (response.data.length > 0) {
        setSelectedDecisionId(String(response.data[0].id));
      }
    } catch (error) {
      console.error("Failed to load decisions:", error);

      if (error.response?.status === 401) {
        setError("Your session has expired. Please login again.");
      } else if (error.response?.status === 403) {
        setError("You are not authorized to view decisions.");
      } else {
        setError(
          error.response?.data?.detail ||
            "Unable to load decisions."
        );
      }
    } finally {
      setLoadingDecisions(false);
    }
  };

  const fetchComments = async (decisionId) => {
    try {
      setLoadingComments(true);
      setError("");

      const response = await api.get(
        `/decisions/${decisionId}/comments`
      );

      setComments(response.data);
    } catch (error) {
      console.error("Failed to load comments:", error);

      if (error.response?.status === 401) {
        setError("Your session has expired. Please login again.");
      } else if (error.response?.status === 403) {
        setError("You are not authorized to view comments.");
      } else if (error.response?.status === 404) {
        setError("Decision not found.");
      } else {
        setError(
          error.response?.data?.detail ||
            "Unable to load comments."
        );
      }
    } finally {
      setLoadingComments(false);
    }
  };

  const handleAddComment = async (event) => {
    event.preventDefault();

    if (!selectedDecisionId) {
      setError("Please select a decision.");
      return;
    }

    if (!newComment.trim()) {
      setError("Comment cannot be empty.");
      return;
    }

    try {
      setError("");
      setSuccess("");

      const response = await api.post(
        `/decisions/${selectedDecisionId}/comments`,
        {
          content: newComment.trim(),
        }
      );

      setComments((previous) => [
        ...previous,
        response.data,
      ]);

      setNewComment("");
      setSuccess("Comment added successfully.");
    } catch (error) {
      console.error("Failed to add comment:", error);

      if (error.response?.status === 401) {
        setError("Your session has expired. Please login again.");
      } else if (error.response?.status === 403) {
        setError("You are not authorized to add a comment.");
      } else if (error.response?.status === 404) {
        setError("Decision not found.");
      } else if (error.response?.status === 422) {
        setError("Please enter a valid comment.");
      } else {
        setError(
          error.response?.data?.detail ||
            "Unable to add comment."
        );
      }
    }
  };

  const handleEdit = (comment) => {
    setEditingCommentId(comment.id);
    setEditingContent(comment.content);
    setError("");
    setSuccess("");
  };

  const handleCancelEdit = () => {
    setEditingCommentId(null);
    setEditingContent("");
  };

  const handleUpdateComment = async (commentId) => {
    if (!editingContent.trim()) {
      setError("Comment cannot be empty.");
      return;
    }

    try {
      setError("");
      setSuccess("");

      const response = await api.put(
        `/comments/${commentId}`,
        {
          content: editingContent.trim(),
        }
      );

      setComments((previous) =>
        previous.map((comment) =>
          comment.id === commentId
            ? response.data
            : comment
        )
      );

      setEditingCommentId(null);
      setEditingContent("");
      setSuccess("Comment updated successfully.");
    } catch (error) {
      console.error("Failed to update comment:", error);

      if (error.response?.status === 401) {
        setError("Your session has expired. Please login again.");
      } else if (error.response?.status === 403) {
        setError("You can only edit your own comments.");
      } else if (error.response?.status === 404) {
        setError("Comment not found.");
      } else {
        setError(
          error.response?.data?.detail ||
            "Unable to update comment."
        );
      }
    }
  };

  const handleDeleteComment = async (comment) => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this comment?"
    );

    if (!confirmed) return;

    try {
      setError("");
      setSuccess("");

      await api.delete(`/comments/${comment.id}`);

      setComments((previous) =>
        previous.filter(
          (item) => item.id !== comment.id
        )
      );

      setSuccess("Comment deleted successfully.");
    } catch (error) {
      console.error("Failed to delete comment:", error);

      if (error.response?.status === 401) {
        setError("Your session has expired. Please login again.");
      } else if (error.response?.status === 403) {
        setError("You can only delete your own comments.");
      } else if (error.response?.status === 404) {
        setError("Comment not found.");
      } else {
        setError(
          error.response?.data?.detail ||
            "Unable to delete comment."
        );
      }
    }
  };

  const fetchThreads = async (decisionId) => {
    try {
      setLoadingThreads(true);
      setError("");

      const response = await api.get(
        `/decisions/${decisionId}/threads`
      );

      setThreads(response.data);
    } catch (error) {
      console.error(
        "Failed to load discussion threads:",
        error
      );

      if (error.response?.status === 401) {
        setError("Your session has expired. Please login again.");
      } else if (error.response?.status === 403) {
        setError(
          "You are not authorized to view discussion threads."
        );
      } else if (error.response?.status === 404) {
        setError("Decision not found.");
      } else {
        setError(
          error.response?.data?.detail ||
            "Unable to load discussion threads."
        );
      }
    } finally {
      setLoadingThreads(false);
    }
  };

  const handleCreateThread = async (event) => {
    event.preventDefault();

    if (!selectedDecisionId) {
      setError("Please select a decision.");
      return;
    }

    if (!newThreadTitle.trim()) {
      setError("Thread title cannot be empty.");
      return;
    }

    if (!newThreadDescription.trim()) {
      setError("Thread description cannot be empty.");
      return;
    }

    try {
      setError("");
      setSuccess("");

      const response = await api.post(
        `/decisions/${selectedDecisionId}/threads`,
        {
          title: newThreadTitle.trim(),
          description: newThreadDescription.trim(),
        }
      );

      setThreads((previous) => [
        ...previous,
        response.data,
      ]);

      setNewThreadTitle("");
      setNewThreadDescription("");

      setSuccess("Discussion thread created successfully.");
    } catch (error) {
      console.error(
        "Failed to create discussion thread:",
        error
      );

      if (error.response?.status === 401) {
        setError("Your session has expired. Please login again.");
      } else if (error.response?.status === 403) {
        setError(
          "You are not authorized to create a discussion thread."
        );
      } else if (error.response?.status === 404) {
        setError("Decision not found.");
      } else {
        setError(
          error.response?.data?.detail ||
            "Unable to create discussion thread."
        );
      }
    }
  };

  const handleEditThread = (thread) => {
    setEditingThreadId(thread.id);
    setEditingThreadTitle(thread.title);
    setEditingThreadDescription(thread.description || "");
    setEditingThreadStatus(thread.status || "Open");

    setError("");
    setSuccess("");
  };

  const handleCancelThreadEdit = () => {
    setEditingThreadId(null);
    setEditingThreadTitle("");
    setEditingThreadDescription("");
    setEditingThreadStatus("Open");
  };

  const handleUpdateThread = async (threadId) => {
    if (!editingThreadTitle.trim()) {
      setError("Thread title cannot be empty.");
      return;
    }

    if (!editingThreadDescription.trim()) {
      setError("Thread description cannot be empty.");
      return;
    }

    try {
      setError("");
      setSuccess("");

      const response = await api.put(
        `/threads/${threadId}`,
        {
          title: editingThreadTitle.trim(),
          description: editingThreadDescription.trim(),
          status: editingThreadStatus,
        }
      );

      setThreads((previous) =>
        previous.map((thread) =>
          thread.id === threadId
            ? response.data
            : thread
        )
      );

      handleCancelThreadEdit();

      setSuccess("Discussion thread updated successfully.");
    } catch (error) {
      console.error(
        "Failed to update discussion thread:",
        error
      );

      if (error.response?.status === 401) {
        setError("Your session has expired. Please login again.");
      } else if (error.response?.status === 403) {
        setError(
          "You can only update your own discussion threads."
        );
      } else if (error.response?.status === 404) {
        setError("Discussion thread not found.");
      } else {
        setError(
          error.response?.data?.detail ||
            "Unable to update discussion thread."
        );
      }
    }
  };

  const handleDeleteThread = async (thread) => {
    const confirmed = window.confirm(
      `Are you sure you want to delete "${thread.title}"?`
    );

    if (!confirmed) return;

    try {
      setError("");
      setSuccess("");

      await api.delete(`/threads/${thread.id}`);

      setThreads((previous) =>
        previous.filter(
          (item) => item.id !== thread.id
        )
      );

      setThreadReplies((previous) => {
        const updated = { ...previous };
        delete updated[thread.id];
        return updated;
      });

      if (editingThreadId === thread.id) {
        handleCancelThreadEdit();
      }

      setSuccess("Discussion thread deleted successfully.");
    } catch (error) {
      console.error(
        "Failed to delete discussion thread:",
        error
      );

      if (error.response?.status === 401) {
        setError("Your session has expired. Please login again.");
      } else if (error.response?.status === 403) {
        setError(
          "You can only delete your own discussion threads."
        );
      } else if (error.response?.status === 404) {
        setError("Discussion thread not found.");
      } else {
        setError(
          error.response?.data?.detail ||
            "Unable to delete discussion thread."
        );
      }
    }
  };

  const fetchThreadReplies = async (threadId) => {
    try {
      setLoadingReplies((previous) => ({
        ...previous,
        [threadId]: true,
      }));

      setError("");

      const response = await api.get(
        `/threads/${threadId}/comments`
      );

      setThreadReplies((previous) => ({
        ...previous,
        [threadId]: response.data,
      }));
    } catch (error) {
      console.error(
        "Failed to load thread replies:",
        error
      );

      if (error.response?.status === 401) {
        setError("Your session has expired. Please login again.");
      } else if (error.response?.status === 404) {
        setError("Discussion thread not found.");
      } else {
        setError(
          error.response?.data?.detail ||
            "Unable to load thread replies."
        );
      }
    } finally {
      setLoadingReplies((previous) => ({
        ...previous,
        [threadId]: false,
      }));
    }
  };

  const handleAddReply = async (threadId) => {
    const content = newReply[threadId]?.trim();

    if (!content) {
      setError("Reply cannot be empty.");
      return;
    }

    try {
      setError("");
      setSuccess("");

      const response = await api.post(
        `/threads/${threadId}/comments`,
        {
          content,
        }
      );

      setThreadReplies((previous) => ({
        ...previous,
        [threadId]: [
          ...(previous[threadId] || []),
          response.data,
        ],
      }));

      setNewReply((previous) => ({
        ...previous,
        [threadId]: "",
      }));

      setSuccess("Reply added successfully.");
    } catch (error) {
      console.error("Failed to add reply:", error);

      if (error.response?.status === 401) {
        setError("Your session has expired. Please login again.");
      } else if (error.response?.status === 403) {
        setError("You are not authorized to add a reply.");
      } else if (error.response?.status === 404) {
        setError("Discussion thread not found.");
      } else {
        setError(
          error.response?.data?.detail ||
            "Unable to add reply."
        );
      }
    }
  };

  const handleEditReply = (reply) => {
    setEditingReplyId(reply.id);
    setEditingReplyContent(reply.content);
    setError("");
    setSuccess("");
  };

  const handleCancelReplyEdit = () => {
    setEditingReplyId(null);
    setEditingReplyContent("");
  };

  const handleUpdateReply = async (replyId, threadId) => {
    if (!editingReplyContent.trim()) {
      setError("Reply cannot be empty.");
      return;
    }

    try {
      setError("");
      setSuccess("");

      const response = await api.put(
        `/comments/${replyId}`,
        {
          content: editingReplyContent.trim(),
        }
      );

      setThreadReplies((previous) => ({
        ...previous,
        [threadId]: (previous[threadId] || []).map(
          (reply) =>
            reply.id === replyId
              ? response.data
              : reply
        ),
      }));

      setEditingReplyId(null);
      setEditingReplyContent("");

      setSuccess("Reply updated successfully.");
    } catch (error) {
      console.error("Failed to update reply:", error);

      if (error.response?.status === 401) {
        setError("Your session has expired. Please login again.");
      } else if (error.response?.status === 403) {
        setError("You can only edit your own replies.");
      } else if (error.response?.status === 404) {
        setError("Reply not found.");
      } else {
        setError(
          error.response?.data?.detail ||
            "Unable to update reply."
        );
      }
    }
  };

  const handleDeleteReply = async (replyId, threadId) => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this reply?"
    );

    if (!confirmed) return;

    try {
      setError("");
      setSuccess("");

      await api.delete(`/comments/${replyId}`);

      setThreadReplies((previous) => ({
        ...previous,
        [threadId]: (previous[threadId] || []).filter(
          (reply) => reply.id !== replyId
        ),
      }));

      setSuccess("Reply deleted successfully.");
    } catch (error) {
      console.error("Failed to delete reply:", error);

      if (error.response?.status === 401) {
        setError("Your session has expired. Please login again.");
      } else if (error.response?.status === 403) {
        setError("You can only delete your own replies.");
      } else if (error.response?.status === 404) {
        setError("Reply not found.");
      } else {
        setError(
          error.response?.data?.detail ||
            "Unable to delete reply."
        );
      }
    }
  };

  const selectedDecision = decisions.find(
    (decision) =>
      String(decision.id) === String(selectedDecisionId)
  );

  if (loadingDecisions) {
    return (
      <div className="page-container">
        <h1>Discussions</h1>
        <p>Loading decisions...</p>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1>Discussions</h1>
          <p>
            Discuss decisions, share opinions, and collaborate
            with your team.
          </p>
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {success && (
        <div className="success-message">
          {success}
        </div>
      )}

      <div className="details-card">
        <h2>Select Decision</h2>

        {decisions.length === 0 ? (
          <p>No decisions available.</p>
        ) : (
          <select
            value={selectedDecisionId}
            onChange={(event) =>
              setSelectedDecisionId(event.target.value)
            }
          >
            {decisions.map((decision) => (
              <option
                key={decision.id}
                value={decision.id}
              >
                #{decision.id} - {decision.title}
              </option>
            ))}
          </select>
        )}
      </div>

      {selectedDecision && (
        <div className="details-card">
          <h2>{selectedDecision.title}</h2>

          <p>
            <strong>Category:</strong>{" "}
            {selectedDecision.category || "N/A"}
          </p>

          <p>
            <strong>Status:</strong>{" "}
            {selectedDecision.status || "N/A"}
          </p>
        </div>
      )}

      {selectedDecisionId && (
        <>
          <div className="details-card">
            <h2>Start Discussion Thread</h2>

            <form onSubmit={handleCreateThread}>
              <input
                type="text"
                placeholder="Thread title..."
                value={newThreadTitle}
                onChange={(event) =>
                  setNewThreadTitle(event.target.value)
                }
              />

              <textarea
                rows="4"
                placeholder="Describe the discussion topic..."
                value={newThreadDescription}
                onChange={(event) =>
                  setNewThreadDescription(event.target.value)
                }
              />

              <button type="submit">
                Create Thread
              </button>
            </form>
          </div>

          <div className="details-card">
            <h2>
              Discussion Threads ({threads.length})
            </h2>

            {loadingThreads ? (
              <p>Loading discussion threads...</p>
            ) : threads.length === 0 ? (
              <div className="empty-state">
                <h3>No discussion threads yet</h3>
                <p>
                  Start a thread to discuss this decision.
                </p>
              </div>
            ) : (
              <div className="comments-list">
                {threads.map((thread) => (
                  <div
                    key={thread.id}
                    className="comment-card"
                  >
                    {editingThreadId === thread.id ? (
                      <>
                        <h3>Edit Discussion Thread</h3>

                        <input
                          type="text"
                          value={editingThreadTitle}
                          onChange={(event) =>
                            setEditingThreadTitle(
                              event.target.value
                            )
                          }
                        />

                        <textarea
                          rows="4"
                          value={editingThreadDescription}
                          onChange={(event) =>
                            setEditingThreadDescription(
                              event.target.value
                            )
                          }
                        />

                        <select
                          value={editingThreadStatus}
                          onChange={(event) =>
                            setEditingThreadStatus(
                              event.target.value
                            )
                          }
                        >
                          <option value="Open">Open</option>
                          <option value="Closed">Closed</option>
                        </select>

                        <div className="decision-actions">
                          <button
                            type="button"
                            className="action-button edit-button"
                            onClick={() =>
                              handleUpdateThread(thread.id)
                            }
                          >
                            Save
                          </button>

                          <button
                            type="button"
                            className="action-button"
                            onClick={handleCancelThreadEdit}
                          >
                            Cancel
                          </button>
                        </div>
                      </>
                    ) : (
                      <>
                        <h3>{thread.title}</h3>

                        <p>
                          {thread.description ||
                            "No description provided."}
                        </p>

                        <small>
                          Status: {thread.status || "N/A"}
                          {" • "}
                          User #{thread.created_by}
                          {" • "}
                          {thread.created_at
                            ? new Date(
                                thread.created_at
                              ).toLocaleString()
                            : "N/A"}
                        </small>

                        <div className="decision-actions">
                          <button
                            type="button"
                            className="action-button edit-button"
                            onClick={() =>
                              handleEditThread(thread)
                            }
                          >
                            Edit
                          </button>

                          <button
                            type="button"
                            className="action-button delete-button"
                            onClick={() =>
                              handleDeleteThread(thread)
                            }
                          >
                            Delete
                          </button>
                        </div>

                        <button
                          type="button"
                          onClick={() =>
                            fetchThreadReplies(thread.id)
                          }
                        >
                          View Replies
                        </button>

                        <div className="thread-replies">
                          <h4>
                            Replies (
                            {threadReplies[thread.id]?.length || 0}
                            )
                          </h4>

                          {loadingReplies[thread.id] ? (
                            <p>Loading replies...</p>
                          ) : (
                            <>
                              {(threadReplies[thread.id] || []).length ===
                              0 ? (
                                <p>No replies yet.</p>
                              ) : (
                                <div className="replies-list">
                                  {(threadReplies[thread.id] || []).map(
                                    (reply) => (
                                      <div
                                        key={reply.id}
                                        className="comment-card"
                                      >
                                        {editingReplyId === reply.id ? (
                                          <>
                                            <textarea
                                              rows="3"
                                              value={editingReplyContent}
                                              onChange={(event) =>
                                                setEditingReplyContent(
                                                  event.target.value
                                                )
                                              }
                                            />

                                            <div className="decision-actions">
                                              <button
                                                type="button"
                                                className="action-button edit-button"
                                                onClick={() =>
                                                  handleUpdateReply(
                                                    reply.id,
                                                    thread.id
                                                  )
                                                }
                                              >
                                                Save
                                              </button>

                                              <button
                                                type="button"
                                                className="action-button"
                                                onClick={
                                                  handleCancelReplyEdit
                                                }
                                              >
                                                Cancel
                                              </button>
                                            </div>
                                          </>
                                        ) : (
                                          <>
                                            <p>
                                              {reply.content}
                                            </p>

                                            <small>
                                              User #{reply.user_id}
                                              {" • "}
                                              {reply.created_at
                                                ? new Date(
                                                    reply.created_at
                                                  ).toLocaleString()
                                                : "N/A"}
                                            </small>

                                            <div className="decision-actions">
                                              <button
                                                type="button"
                                                className="action-button edit-button"
                                                onClick={() =>
                                                  handleEditReply(reply)
                                                }
                                              >
                                                Edit
                                              </button>

                                              <button
                                                type="button"
                                                className="action-button delete-button"
                                                onClick={() =>
                                                  handleDeleteReply(
                                                    reply.id,
                                                    thread.id
                                                  )
                                                }
                                              >
                                                Delete
                                              </button>
                                            </div>
                                          </>
                                        )}
                                      </div>
                                    )
                                  )}
                                </div>
                              )}

                              <div className="reply-form">
                                <textarea
                                  rows="3"
                                  placeholder="Write a reply..."
                                  value={
                                    newReply[thread.id] || ""
                                  }
                                  onChange={(event) =>
                                    setNewReply((previous) => ({
                                      ...previous,
                                      [thread.id]:
                                        event.target.value,
                                    }))
                                  }
                                />

                                <button
                                  type="button"
                                  onClick={() =>
                                    handleAddReply(thread.id)
                                  }
                                >
                                  Add Reply
                                </button>
                              </div>
                            </>
                          )}
                        </div>
                      </>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}

      {selectedDecisionId && (
        <div className="details-card">
          <h2>Add Comment</h2>

          <form onSubmit={handleAddComment}>
            <textarea
              rows="4"
              placeholder="Write your comment..."
              value={newComment}
              onChange={(event) =>
                setNewComment(event.target.value)
              }
            />

            <button type="submit">
              Add Comment
            </button>
          </form>
        </div>
      )}

      <div className="details-card">
        <h2>
          Comments ({comments.length})
        </h2>

        {loadingComments ? (
          <p>Loading comments...</p>
        ) : comments.length === 0 ? (
          <div className="empty-state">
            <h3>No comments yet</h3>
            <p>
              Be the first person to start the discussion.
            </p>
          </div>
        ) : (
          <div className="comments-list">
            {comments.map((comment) => (
              <div
                key={comment.id}
                className="comment-card"
              >
                {editingCommentId === comment.id ? (
                  <>
                    <textarea
                      rows="4"
                      value={editingContent}
                      onChange={(event) =>
                        setEditingContent(event.target.value)
                      }
                    />

                    <div className="decision-actions">
                      <button
                        type="button"
                        className="action-button edit-button"
                        onClick={() =>
                          handleUpdateComment(comment.id)
                        }
                      >
                        Save
                      </button>

                      <button
                        type="button"
                        className="action-button"
                        onClick={handleCancelEdit}
                      >
                        Cancel
                      </button>
                    </div>
                  </>
                ) : (
                  <>
                    <p>{comment.content}</p>

                    <small>
                      User #{comment.user_id} •{" "}
                      {comment.created_at
                        ? new Date(
                            comment.created_at
                          ).toLocaleString()
                        : "N/A"}
                    </small>

                    <div className="decision-actions">
                      <button
                        type="button"
                        className="action-button edit-button"
                        onClick={() =>
                          handleEdit(comment)
                        }
                      >
                        Edit
                      </button>

                      <button
                        type="button"
                        className="action-button delete-button"
                        onClick={() =>
                          handleDeleteComment(comment)
                        }
                      >
                        Delete
                      </button>
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default Discussions;