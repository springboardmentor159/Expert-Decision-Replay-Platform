import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../services/api";

function Comments() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [comments, setComments] = useState([]);
  const [content, setContent] = useState("");
  const [editingId, setEditingId] = useState(null);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const fetchComments = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await api.get(`/decisions/${id}/comments`);
      setComments(response.data);
    } catch (err) {
      console.error("Comments error:", err);
      setError("Unable to load comments.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchComments();
  }, [id]);

  const clearForm = () => {
    setContent("");
    setEditingId(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError("");
    setMessage("");

    if (!content.trim()) {
      setError("Comment cannot be empty.");
      return;
    }

    setSaving(true);

    try {
      if (editingId) {
        const response = await api.put(`/comments/${editingId}`, {
          content: content,
        });

        setComments((current) =>
          current.map((comment) =>
            comment.id === editingId ? response.data : comment
          )
        );

        setMessage("Comment updated successfully.");
      } else {
        const response = await api.post(`/decisions/${id}/comments`, {
          content: content,
        });

        setComments((current) => [...current, response.data]);

        setMessage("Comment added successfully.");
      }

      clearForm();
    } catch (err) {
      console.error("Comment save error:", err);

      if (err.response?.data?.detail) {
        setError(
          typeof err.response.data.detail === "string"
            ? err.response.data.detail
            : "Unable to save comment."
        );
      } else {
        setError("Unable to save comment.");
      }
    } finally {
      setSaving(false);
    }
  };

  const handleEdit = (comment) => {
    setEditingId(comment.id);
    setContent(comment.content || "");

    setMessage("");
    setError("");

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  const handleDelete = async (commentId) => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this comment?"
    );

    if (!confirmed) {
      return;
    }

    setError("");
    setMessage("");

    try {
      await api.delete(`/comments/${commentId}`);

      setComments((current) =>
        current.filter((comment) => comment.id !== commentId)
      );

      setMessage("Comment deleted successfully.");

      if (editingId === commentId) {
        clearForm();
      }
    } catch (err) {
      console.error("Comment delete error:", err);

      if (err.response?.data?.detail) {
        setError(
          typeof err.response.data.detail === "string"
            ? err.response.data.detail
            : "Unable to delete comment."
        );
      } else {
        setError("Unable to delete comment.");
      }
    }
  };

  return (
    <div className="comments-page">

      {/* Header */}
      <div className="comments-page-header">
        <div>
          <div className="page-breadcrumb">
            Decisions / Discussion
          </div>

          <h1>Discussion & Comments</h1>

          <p>
            Share feedback, questions, and insights related to this decision.
          </p>
        </div>

        <div className="comments-header-actions">
          <div className="decision-id-badge">
            Decision #{id}
          </div>

          <button
            className="secondary-page-button"
            onClick={() => navigate(`/decisions/${id}`)}
          >
            ← Decision Details
          </button>
        </div>
      </div>

      {/* Summary */}
      <div className="comments-summary">

        <div className="comment-summary-card">
          <div className="comment-summary-icon">💬</div>

          <div>
            <span>Total Comments</span>
            <strong>{comments.length}</strong>
          </div>
        </div>

        <div className="comment-summary-card">
          <div className="comment-summary-icon">▣</div>

          <div>
            <span>Discussion</span>
            <strong>Decision #{id}</strong>
          </div>
        </div>

        <div className="comment-summary-card">
          <div className="comment-summary-icon">✓</div>

          <div>
            <span>Status</span>
            <strong>Active</strong>
          </div>
        </div>

      </div>

      {/* Add / Edit Comment */}
      <div className="comment-composer-card">

        <div className="comment-card-title">
          <div className="composer-icon">
            {editingId ? "✎" : "＋"}
          </div>

          <div>
            <h2>
              {editingId ? "Edit Comment" : "Start a Discussion"}
            </h2>

            <p>
              {editingId
                ? "Update your comment below."
                : "Add your thoughts or feedback about this decision."}
            </p>
          </div>
        </div>

        <form onSubmit={handleSubmit}>

          <textarea
            className="comment-textarea"
            rows="5"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Write your comment or discussion here..."
          />

          <div className="comment-form-footer">

            <span className="character-hint">
              Please keep your discussion clear and relevant.
            </span>

            <div className="comment-form-actions">

              {editingId && (
                <button
                  type="button"
                  className="cancel-comment-button"
                  onClick={clearForm}
                >
                  Cancel
                </button>
              )}

              <button
                type="submit"
                className="primary-submit-button"
                disabled={saving}
              >
                {saving
                  ? "Saving..."
                  : editingId
                  ? "Update Comment"
                  : "Post Comment"}
              </button>

            </div>
          </div>

        </form>

      </div>

      {/* Messages */}
      {message && (
        <div className="success-message">
          <span>✓</span>
          {message}
        </div>
      )}

      {error && (
        <div className="error-message">
          <span>!</span>
          {error}
        </div>
      )}

      {/* Existing Comments */}
      <div className="comments-list-card">

        <div className="comments-list-header">
          <div>
            <h2>Discussion Thread</h2>
            <p>
              Conversations and feedback from decision participants.
            </p>
          </div>

          <span className="comment-count-badge">
            {comments.length} {comments.length === 1 ? "Comment" : "Comments"}
          </span>
        </div>

        {loading ? (
          <div className="page-loading">
            <div className="loading-spinner"></div>
            <p>Loading discussion...</p>
          </div>
        ) : comments.length === 0 ? (
          <div className="comments-empty">

            <div className="comments-empty-icon">
              💬
            </div>

            <h3>No Comments Yet</h3>

            <p>
              Start the discussion by adding the first comment
              about this decision.
            </p>

          </div>
        ) : (
          <div className="comments-thread">

            {comments.map((comment, index) => (
              <div className="comment-item" key={comment.id}>

                <div className="comment-avatar">
                  {String(comment.user_id || "U").charAt(0).toUpperCase()}
                </div>

                <div className="comment-content">

                  <div className="comment-top-row">

                    <div>
                      <strong>
                        User #{comment.user_id}
                      </strong>

                      <span className="comment-number">
                        Comment {index + 1}
                      </span>
                    </div>

                    <div className="comment-actions">

                      <button
                        className="edit-comment-button"
                        onClick={() => handleEdit(comment)}
                      >
                        Edit
                      </button>

                      <button
                        className="delete-comment-button"
                        onClick={() =>
                          handleDelete(comment.id)
                        }
                      >
                        Delete
                      </button>

                    </div>

                  </div>

                  <div className="comment-text">
                    {comment.content}
                  </div>

                  <div className="comment-meta">

                    <span>
                      Created:{" "}
                      {comment.created_at
                        ? new Date(
                            comment.created_at
                          ).toLocaleString()
                        : "-"}
                    </span>

                    {comment.updated_at && (
                      <span>
                        Updated:{" "}
                        {new Date(
                          comment.updated_at
                        ).toLocaleString()}
                      </span>
                    )}

                  </div>

                </div>

              </div>
            ))}

          </div>
        )}

      </div>

      {/* Bottom Navigation */}
      <div className="comments-bottom-actions">

        <button
          className="secondary-page-button"
          onClick={() =>
            navigate(`/decisions/${id}/alternatives`)
          }
        >
          ← Alternatives
        </button>

        <button
          className="primary-submit-button"
          onClick={() => navigate(`/decisions/${id}`)}
        >
          Decision Details
        </button>

      </div>

    </div>
  );
}

export default Comments;