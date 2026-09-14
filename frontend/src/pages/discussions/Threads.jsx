import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
  getDecisionThreads,
  createThread,
  updateThread,
  deleteThread,
  createThreadReply,
} from "../../services/discussionService";

import PageHeader from "../../components/PageHeader";
import Button from "../../components/Button";
import Card from "../../components/Card";
import Alert from "../../components/Alert";
import EmptyState from "../../components/EmptyState";

const Threads = () => {
  const { decisionId } = useParams();
  const navigate = useNavigate();

  const [threads, setThreads] = useState([]);

  const [title, setTitle] = useState("");
  const [description, setDescription] =
    useState("");

  const [editingId, setEditingId] =
    useState(null);

  const [replyId, setReplyId] =
    useState(null);

  const [replyContent, setReplyContent] =
    useState("");

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const loadThreads = async () => {
    try {
      setLoading(true);
      setError("");

      const data = await getDecisionThreads(
        decisionId
      );

      const list = Array.isArray(data)
        ? data
        : data?.threads ||
          data?.items ||
          [];

      setThreads(list);
    } catch (err) {
      console.error(
        "Failed to load threads:",
        err
      );

      handleError(err, "load");
    } finally {
      setLoading(false);
    }
  };

  const handleError = (err, action) => {
    const status = err.response?.status;

    if (status === 401) {
      setError(
        "Your session has expired. Please login again."
      );
    } else if (status === 403) {
      setError(
        `You are not authorized to ${action} threads.`
      );
    } else if (status === 404) {
      setError(
        "Decision or thread was not found."
      );
    } else if (status === 422) {
      setError(
        "Please check the entered information."
      );
    } else if (status >= 500) {
      setError(
        "Server error. Please try again later."
      );
    } else if (err.request) {
      setError(
        "Unable to connect to the backend. Please make sure FastAPI is running."
      );
    } else {
      setError(
        `Failed to ${action} thread.`
      );
    }
  };

  useEffect(() => {
    loadThreads();
  }, [decisionId]);

  const resetForm = () => {
    setTitle("");
    setDescription("");
    setEditingId(null);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");

    if (!title.trim()) {
      setError("Thread title is required.");
      return;
    }

    if (!description.trim()) {
      setError(
        "Thread description is required."
      );
      return;
    }

    try {
      setSaving(true);

      if (editingId) {
        await updateThread(editingId, {
          title: title.trim(),
          description: description.trim(),
          status: "Open",
        });
      } else {
        await createThread(decisionId, {
          title: title.trim(),
          description: description.trim(),
        });
      }

      resetForm();
      await loadThreads();
    } catch (err) {
      console.error(
        "Failed to save thread:",
        err
      );

      handleError(err, "save");
    } finally {
      setSaving(false);
    }
  };

  const handleEdit = (thread) => {
    setEditingId(thread.id);
    setTitle(thread.title || "");
    setDescription(
      thread.description || ""
    );

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  const handleDelete = async (threadId) => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this thread?"
    );

    if (!confirmed) {
      return;
    }

    try {
      setError("");

      await deleteThread(threadId);

      await loadThreads();
    } catch (err) {
      console.error(
        "Failed to delete thread:",
        err
      );

      handleError(err, "delete");
    }
  };

  const handleReply = async (threadId) => {
    setError("");

    if (!replyContent.trim()) {
      setError("Reply content is required.");
      return;
    }

    try {
      setSaving(true);

      await createThreadReply(
        threadId,
        replyContent.trim()
      );

      setReplyContent("");
      setReplyId(null);

      // Reload thread list so latest data appears
      await loadThreads();
    } catch (err) {
      console.error(
        "Failed to create thread reply:",
        err
      );

      handleError(err, "create reply");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="threads-page">
        <PageHeader
          title="Discussion Threads"
          subtitle="Discuss topics related to this decision"
        />

        <Card>
          <div className="loading-state">
            Loading threads...
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="threads-page">

      <PageHeader
        title="Discussion Threads"
        subtitle="Discuss topics related to this decision"
      />

      {error && (
        <Alert
          message={error}
          type="error"
          onClose={() => setError("")}
        />
      )}

      <div className="discussion-page-actions">
        <Button
          variant="secondary"
          onClick={() =>
            navigate(
              `/decisions/${decisionId}/discussion`
            )
          }
        >
          Discussion
        </Button>

        <Button
          variant="secondary"
          onClick={() =>
            navigate(`/decisions/${decisionId}`)
          }
        >
          Back to Decision
        </Button>
      </div>

      <Card
        title={
          editingId
            ? "Edit Thread"
            : "Create Thread"
        }
      >
        <form onSubmit={handleSubmit}>

          <div className="form-group">
            <label htmlFor="threadTitle">
              Title *
            </label>

            <input
              id="threadTitle"
              type="text"
              value={title}
              onChange={(event) =>
                setTitle(event.target.value)
              }
              placeholder="Enter thread title"
              maxLength={200}
            />
          </div>

          <div className="form-group">
            <label htmlFor="threadDescription">
              Description *
            </label>

            <textarea
              id="threadDescription"
              value={description}
              onChange={(event) =>
                setDescription(
                  event.target.value
                )
              }
              placeholder="Describe the topic for discussion"
              rows={5}
            />
          </div>

          <div className="create-decision-actions">

            {editingId && (
              <Button
                type="button"
                variant="secondary"
                onClick={resetForm}
                disabled={saving}
              >
                Cancel Edit
              </Button>
            )}

            <Button
              type="submit"
              disabled={saving}
            >
              {saving
                ? "Saving..."
                : editingId
                ? "Update Thread"
                : "Create Thread"}
            </Button>

          </div>
        </form>
      </Card>

      <div className="discussion-section-spacer" />

      {threads.length === 0 ? (
        <Card>
          <EmptyState
            title="No discussion threads"
            message="Create a thread to start a focused discussion about this decision."
          />
        </Card>
      ) : (
        <div className="thread-list">

          {threads.map((thread) => (
            <Card
              key={thread.id}
              className="thread-card"
            >
              <div className="thread-card-header">

                <div>
                  <h2>
                    {thread.title}
                  </h2>

                  <p className="thread-meta">
                    Created by User #
                    {thread.created_by ?? "-"}
                    {" • "}
                    {thread.created_at
                      ? new Date(
                          thread.created_at
                        ).toLocaleString()
                      : "-"}
                  </p>
                </div>

                <span className="thread-status">
                  {thread.status || "Open"}
                </span>

              </div>

              <p className="thread-description">
                {thread.description}
              </p>

              <div className="thread-actions">

                <Button
                  variant="secondary"
                  onClick={() =>
                    handleEdit(thread)
                  }
                >
                  Edit
                </Button>

                <Button
                  variant="danger"
                  onClick={() =>
                    handleDelete(thread.id)
                  }
                >
                  Delete
                </Button>

                <Button
                  onClick={() => {
                    setReplyId(
                      replyId === thread.id
                        ? null
                        : thread.id
                    );
                    setReplyContent("");
                  }}
                >
                  Reply
                </Button>

              </div>

              {replyId === thread.id && (
                <div className="thread-reply-form">

                  <label htmlFor={`reply-${thread.id}`}>
                    Reply
                  </label>

                  <textarea
                    id={`reply-${thread.id}`}
                    value={replyContent}
                    onChange={(event) =>
                      setReplyContent(
                        event.target.value
                      )
                    }
                    placeholder="Write your reply..."
                    rows={4}
                  />

                  <div className="thread-reply-actions">

                    <Button
                      type="button"
                      variant="secondary"
                      onClick={() => {
                        setReplyId(null);
                        setReplyContent("");
                      }}
                      disabled={saving}
                    >
                      Cancel
                    </Button>

                    <Button
                      type="button"
                      onClick={() =>
                        handleReply(thread.id)
                      }
                      disabled={saving}
                    >
                      {saving
                        ? "Sending..."
                        : "Send Reply"}
                    </Button>

                  </div>

                </div>
              )}

            </Card>
          ))}

        </div>
      )}

    </div>
  );
};

export default Threads;