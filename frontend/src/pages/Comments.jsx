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

      const response = await api.get(
        `/decisions/${id}/comments`
      );

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
        const response = await api.put(
          `/comments/${editingId}`,
          {
            content: content,
          }
        );

        setComments((current) =>
          current.map((comment) =>
            comment.id === editingId
              ? response.data
              : comment
          )
        );

        setMessage("Comment updated successfully.");
      } else {
        const response = await api.post(
          `/decisions/${id}/comments`,
          {
            content: content,
          }
        );

        setComments((current) => [
          ...current,
          response.data,
        ]);

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
        current.filter(
          (comment) => comment.id !== commentId
        )
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
    <div>
      <h1>Discussion & Comments</h1>

      <p>
        <strong>Decision ID:</strong> {id}
      </p>

      <hr />

      <h2>
        {editingId ? "Edit Comment" : "Add Comment"}
      </h2>

      <form onSubmit={handleSubmit}>
        <div>
          <label>
            <strong>Comment:</strong>
          </label>
          <br />

          <textarea
            rows="5"
            cols="60"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Enter your comment or discussion..."
          />
        </div>

        <br />

        <button type="submit" disabled={saving}>
          {saving
            ? "Saving..."
            : editingId
            ? "Update Comment"
            : "Add Comment"}
        </button>

        {editingId && (
          <button
            type="button"
            onClick={clearForm}
            style={{ marginLeft: "10px" }}
          >
            Cancel Edit
          </button>
        )}
      </form>

      <br />

      {message && (
        <p>
          <strong>{message}</strong>
        </p>
      )}

      {error && <p>{error}</p>}

      <hr />

      <h2>Existing Comments</h2>

      {loading ? (
        <p>Loading comments...</p>
      ) : comments.length === 0 ? (
        <p>No comments found for this decision.</p>
      ) : (
        <table border="1" cellPadding="10">
          <thead>
            <tr>
              <th>ID</th>
              <th>User ID</th>
              <th>Comment</th>
              <th>Created At</th>
              <th>Updated At</th>
              <th>Actions</th>
            </tr>
          </thead>

          <tbody>
            {comments.map((comment) => (
              <tr key={comment.id}>
                <td>{comment.id}</td>

                <td>{comment.user_id}</td>

                <td>{comment.content}</td>

                <td>
                  {comment.created_at
                    ? new Date(
                        comment.created_at
                      ).toLocaleString()
                    : "-"}
                </td>

                <td>
                  {comment.updated_at
                    ? new Date(
                        comment.updated_at
                      ).toLocaleString()
                    : "-"}
                </td>

                <td>
                  <button
                    onClick={() =>
                      handleEdit(comment)
                    }
                  >
                    Edit
                  </button>

                  <button
                    onClick={() =>
                      handleDelete(comment.id)
                    }
                    style={{ marginLeft: "10px" }}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <br />

      <button
        onClick={() =>
          navigate(`/decisions/${id}`)
        }
      >
        Back to Decision
      </button>
    </div>
  );
}

export default Comments;