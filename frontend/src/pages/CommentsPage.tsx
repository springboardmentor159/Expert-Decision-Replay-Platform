import { useCallback, useEffect, useState } from "react";
import {
  ArrowLeft,
  CalendarDays,
  Edit3,
  MessageSquare,
  Send,
  Trash2,
  UserRound,
  X,
} from "lucide-react";
import { useNavigate, useParams } from "react-router-dom";

import Alert from "../components/Alert";
import Button from "../components/Button";
import { useAuth } from "../auth/AuthContext";
import {
  createComment,
  deleteComment,
  getComments,
  updateComment,
  type Comment,
} from "../services/commentService";
import "./CommentsPage.css";

function formatDateTime(value: string): string {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "—";
  }

  return date.toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function getErrorStatus(error: unknown): number | undefined {
  return (
    error as {
      response?: {
        status?: number;
      };
    }
  )?.response?.status;
}

function getErrorMessage(
  error: unknown,
  action: string,
): string {
  const status = getErrorStatus(error);

  if (status === 401) {
    return "Your session has expired. Please sign in again.";
  }

  if (status === 403) {
    return `You do not have permission to ${action}.`;
  }

  if (status === 404) {
    return "The requested comment or decision was not found.";
  }

  if (status === 422) {
    return "Please check the comment and try again.";
  }

  if (status && status >= 500) {
    return "The server is temporarily unavailable. Please try again.";
  }

  return `Unable to ${action}. Please try again.`;
}

export default function CommentsPage() {
  const { decisionId } = useParams<{ decisionId: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [comments, setComments] = useState<Comment[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [pageError, setPageError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const [content, setContent] = useState("");
  const [editingComment, setEditingComment] =
    useState<Comment | null>(null);
  const [editingContent, setEditingContent] = useState("");
  const [deletingCommentId, setDeletingCommentId] =
    useState<number | null>(null);

  const numericDecisionId = Number(decisionId);

  const loadComments = useCallback(async () => {
    if (
      !decisionId ||
      !Number.isInteger(numericDecisionId) ||
      numericDecisionId <= 0
    ) {
      setPageError("Invalid decision identifier.");
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setPageError("");

    try {
      const data = await getComments(numericDecisionId);
      setComments(data);
    } catch (error: unknown) {
      setPageError(getErrorMessage(error, "load comments"));
    } finally {
      setIsLoading(false);
    }
  }, [decisionId, numericDecisionId]);

  useEffect(() => {
    void loadComments();
  }, [loadComments]);

  function validateContent(value: string): string {
    const trimmed = value.trim();

    if (!trimmed) {
      return "Comment cannot be empty.";
    }

    if (trimmed.length > 2000) {
      return "Comment must be 2000 characters or fewer.";
    }

    return "";
  }

  async function handleCreateComment() {
    const validationError = validateContent(content);

    if (validationError) {
      setPageError(validationError);
      return;
    }

    setIsSubmitting(true);
    setPageError("");
    setSuccessMessage("");

    try {
      const newComment = await createComment(
        numericDecisionId,
        {
          content: content.trim(),
        },
      );

      setComments((current) => [...current, newComment]);
      setContent("");
      setSuccessMessage("Comment added successfully.");
    } catch (error: unknown) {
      setPageError(
        getErrorMessage(error, "add the comment"),
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  function startEditing(comment: Comment) {
    setEditingComment(comment);
    setEditingContent(comment.content);
    setPageError("");
    setSuccessMessage("");
  }

  function cancelEditing() {
    setEditingComment(null);
    setEditingContent("");
  }

  async function handleUpdateComment() {
    if (!editingComment) {
      return;
    }

    const validationError = validateContent(editingContent);

    if (validationError) {
      setPageError(validationError);
      return;
    }

    setIsSubmitting(true);
    setPageError("");
    setSuccessMessage("");

    try {
      const updatedComment = await updateComment(
        editingComment.id,
        {
          content: editingContent.trim(),
        },
      );

      setComments((current) =>
        current.map((comment) =>
          comment.id === updatedComment.id
            ? updatedComment
            : comment,
        ),
      );

      cancelEditing();
      setSuccessMessage("Comment updated successfully.");
    } catch (error: unknown) {
      setPageError(
        getErrorMessage(error, "update the comment"),
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleDeleteComment(commentId: number) {
    setDeletingCommentId(commentId);
    setPageError("");
    setSuccessMessage("");

    try {
      await deleteComment(commentId);

      setComments((current) =>
        current.filter((comment) => comment.id !== commentId),
      );

      if (editingComment?.id === commentId) {
        cancelEditing();
      }

      setSuccessMessage("Comment deleted successfully.");
    } catch (error: unknown) {
      setPageError(
        getErrorMessage(error, "delete the comment"),
      );
    } finally {
      setDeletingCommentId(null);
    }
  }

  if (
    !decisionId ||
    !Number.isInteger(numericDecisionId) ||
    numericDecisionId <= 0
  ) {
    return (
      <div className="comments-page">
        <div className="comments-error-state">
          <Alert variant="error">
            Invalid decision identifier.
          </Alert>

          <Button
            variant="secondary"
            onClick={() => navigate("/decisions")}
          >
            <ArrowLeft size={16} aria-hidden="true" />
            Back to Decisions
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="comments-page">
      <header className="comments-header">
        <div>
          <button
            type="button"
            className="comments-back-button"
            onClick={() =>
              navigate(`/decisions/${numericDecisionId}`)
            }
          >
            <ArrowLeft size={15} aria-hidden="true" />
            Back to Decision
          </button>

          <div className="comments-kicker">
            DECISION DISCUSSION
          </div>

          <div className="comments-title-row">
            <div className="comments-title-icon">
              <MessageSquare
                size={23}
                aria-hidden="true"
              />
            </div>

            <div>
              <h1>Discussion &amp; Comments</h1>
              <p>
                Share observations, questions, and context
                related to this decision.
              </p>
            </div>
          </div>
        </div>

        <div className="comments-decision-chip">
          Decision #{numericDecisionId}
        </div>
      </header>

      {pageError && (
        <div className="comments-alert">
          <Alert variant="error">{pageError}</Alert>
        </div>
      )}

      {successMessage && (
        <div className="comments-alert">
          <Alert variant="success">
            {successMessage}
          </Alert>
        </div>
      )}

      <div className="comments-layout">
        <main className="comments-main">
          <section className="comments-card">
            <div className="comments-card-header">
              <div>
                <h2>Conversation</h2>
                <p>
                  {comments.length === 0
                    ? "No comments yet. Start the discussion."
                    : `${comments.length} ${
                        comments.length === 1
                          ? "comment"
                          : "comments"
                      }`}
                </p>
              </div>

              <div className="comments-count">
                {comments.length}
              </div>
            </div>

            {isLoading ? (
              <div
                className="comments-loading"
                role="status"
                aria-live="polite"
              >
                <div className="comments-spinner" />
                <span>Loading discussion...</span>
              </div>
            ) : comments.length === 0 ? (
              <div className="comments-empty">
                <div className="comments-empty-icon">
                  <MessageSquare
                    size={24}
                    aria-hidden="true"
                  />
                </div>

                <h3>No comments yet</h3>
                <p>
                  Be the first to add context or ask a question
                  about this decision.
                </p>
              </div>
            ) : (
              <div className="comments-list">
                {comments.map((comment) => {
                  const isOwner =
                    user?.id === comment.user_id;

                  return (
                    <article
                      className="comment-item"
                      key={comment.id}
                    >
                      <div className="comment-avatar">
                        <UserRound
                          size={17}
                          aria-hidden="true"
                        />
                      </div>

                      <div className="comment-body">
                        <div className="comment-top">
                          <div>
                            <strong>
                              User #{comment.user_id}
                            </strong>

                            {isOwner && (
                              <span className="comment-owner">
                                You
                              </span>
                            )}
                          </div>

                          <span className="comment-date">
                            <CalendarDays
                              size={13}
                              aria-hidden="true"
                            />
                            {formatDateTime(
                              comment.created_at,
                            )}
                          </span>
                        </div>

                        {editingComment?.id ===
                        comment.id ? (
                          <div className="comment-edit-form">
                            <textarea
                              value={editingContent}
                              onChange={(event) =>
                                setEditingContent(
                                  event.target.value,
                                )
                              }
                              maxLength={2000}
                              rows={5}
                              aria-label="Edit comment"
                              autoFocus
                            />

                            <div className="comment-edit-footer">
                              <span>
                                {editingContent.length}/2000
                              </span>

                              <div className="comment-edit-actions">
                                <Button
                                  variant="secondary"
                                  onClick={cancelEditing}
                                  disabled={isSubmitting}
                                >
                                  <X
                                    size={15}
                                    aria-hidden="true"
                                  />
                                  Cancel
                                </Button>

                                <Button
                                  onClick={
                                    handleUpdateComment
                                  }
                                  disabled={isSubmitting}
                                >
                                  <Send
                                    size={15}
                                    aria-hidden="true"
                                  />
                                  {isSubmitting
                                    ? "Saving..."
                                    : "Save Changes"}
                                </Button>
                              </div>
                            </div>
                          </div>
                        ) : (
                          <>
                            <p className="comment-content">
                              {comment.content}
                            </p>

                            {comment.updated_at !==
                              comment.created_at && (
                              <span className="comment-edited">
                                Edited{" "}
                                {formatDateTime(
                                  comment.updated_at,
                                )}
                              </span>
                            )}

                            {isOwner && (
                              <div className="comment-actions">
                                <button
                                  type="button"
                                  onClick={() =>
                                    startEditing(comment)
                                  }
                                  disabled={
                                    deletingCommentId ===
                                    comment.id
                                  }
                                >
                                  <Edit3
                                    size={14}
                                    aria-hidden="true"
                                  />
                                  Edit
                                </button>

                                <button
                                  type="button"
                                  className="comment-delete-action"
                                  onClick={() =>
                                    void handleDeleteComment(
                                      comment.id,
                                    )
                                  }
                                  disabled={
                                    deletingCommentId ===
                                    comment.id
                                  }
                                >
                                  <Trash2
                                    size={14}
                                    aria-hidden="true"
                                  />
                                  {deletingCommentId ===
                                  comment.id
                                    ? "Deleting..."
                                    : "Delete"}
                                </button>
                              </div>
                            )}
                          </>
                        )}
                      </div>
                    </article>
                  );
                })}
              </div>
            )}
          </section>
        </main>

        <aside className="comments-sidebar">
          <section className="comments-compose-card">
            <div className="comments-compose-heading">
              <div className="comments-compose-icon">
                <MessageSquare
                  size={18}
                  aria-hidden="true"
                />
              </div>

              <div>
                <h2>Add a comment</h2>
                <p>
                  Your comment will be recorded with your
                  authenticated account.
                </p>
              </div>
            </div>

            <div className="comments-field">
              <label htmlFor="comment-content">
                Comment
              </label>

              <textarea
                id="comment-content"
                value={content}
                onChange={(event) =>
                  setContent(event.target.value)
                }
                placeholder="Share your thoughts about this decision..."
                rows={7}
                maxLength={2000}
              />
            </div>

            <div className="comments-compose-footer">
              <span>{content.length}/2000</span>

              <Button
                onClick={() => void handleCreateComment()}
                disabled={isSubmitting || !content.trim()}
              >
                <Send size={16} aria-hidden="true" />
                {isSubmitting
                  ? "Posting..."
                  : "Post Comment"}
              </Button>
            </div>
          </section>

          <section className="comments-info-card">
            <span className="comments-info-label">
              DISCUSSION GUIDELINE
            </span>

            <h3>Keep the conversation useful.</h3>

            <p>
              Add decision-specific context, questions,
              observations, or information that can help
              reviewers understand the decision.
            </p>
          </section>
        </aside>
      </div>
    </div>
  );
}