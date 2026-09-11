import {
  useCallback,
  useEffect,
  useState,
  type ChangeEvent,
  type FormEvent,
} from "react";
import axios from "axios";
import { useNavigate, useParams } from "react-router-dom";
import api from "../services/api";

interface DiscussionThread {
  id: number;
  title: string;
  description: string;
  status: string;
  created_by: number;
  created_at: string;
}

function getApiErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;

    if (typeof detail === "string") {
      return detail;
    }

    if (Array.isArray(detail)) {
      return detail
        .map((item) => {
          if (
            typeof item === "object" &&
            item !== null &&
            "msg" in item
          ) {
            return String(item.msg);
          }

          return String(item);
        })
        .join(", ");
    }

    if (error.response?.status === 401) {
      return "Your session has expired. Please login again.";
    }

    if (error.response?.status === 403) {
      return "You do not have permission to perform this action.";
    }

    if (error.response?.status === 404) {
      return "The discussion could not be found.";
    }

    if (error.response?.status === 422) {
      return "Please check the entered information.";
    }

    if (error.response?.status === 500) {
      return "Server error. Please try again.";
    }

    return error.message || "Request failed.";
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "Something went wrong. Please try again.";
}

function formatDate(value: string): string {
  if (!value) {
    return "Unknown date";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString();
}

export default function Discussion() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [threads, setThreads] = useState<DiscussionThread[]>([]);
  const [selectedThread, setSelectedThread] =
    useState<DiscussionThread | null>(null);

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");

  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [showCreateForm, setShowCreateForm] = useState(false);

  const loadThreads = useCallback(async () => {
    if (!id) {
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      const response = await api.get<DiscussionThread[]>(
        `/decisions/${id}/threads`,
      );

      setThreads(response.data);
    } catch (requestError) {
      console.error(
        "Unable to load discussion threads:",
        requestError,
      );

      setError(getApiErrorMessage(requestError));
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    let cancelled = false;

    const loadInitialThreads = async () => {
      if (!id) {
        return;
      }

      if (cancelled) {
        return;
      }

      await loadThreads();
    };

    loadInitialThreads();

    return () => {
      cancelled = true;
    };
  }, [id, loadThreads]);

  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();

    if (!id) {
      setError("Decision ID is missing.");
      return;
    }

    if (!title.trim()) {
      setError("Discussion title is required.");
      return;
    }

    if (!description.trim()) {
      setError("Discussion description is required.");
      return;
    }

    setIsSubmitting(true);
    setError("");
    setSuccess("");

    try {
      await api.post(`/decisions/${id}/threads`, {
        title: title.trim(),
        description: description.trim(),
      });

      setTitle("");
      setDescription("");
      setShowCreateForm(false);

      setSuccess(
        "Discussion thread created successfully.",
      );

      await loadThreads();
    } catch (requestError) {
      console.error(
        "Unable to create discussion:",
        requestError,
      );

      setError(getApiErrorMessage(requestError));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (threadId: number) => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this discussion?",
    );

    if (!confirmed) {
      return;
    }

    setError("");
    setSuccess("");

    try {
      await api.delete(`/threads/${threadId}`);

      if (selectedThread?.id === threadId) {
        setSelectedThread(null);
      }

      setSuccess(
        "Discussion deleted successfully.",
      );

      await loadThreads();
    } catch (requestError) {
      console.error(
        "Unable to delete discussion:",
        requestError,
      );

      setError(getApiErrorMessage(requestError));
    }
  };

  const handleThreadClick = (
    thread: DiscussionThread,
  ) => {
    setSelectedThread(thread);

    window.setTimeout(() => {
      document
        .getElementById("discussion-detail")
        ?.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
    }, 50);
  };

  const handleTitleChange = (
    event: ChangeEvent<HTMLInputElement>,
  ) => {
    setTitle(event.target.value);
  };

  const handleDescriptionChange = (
    event: ChangeEvent<HTMLTextAreaElement>,
  ) => {
    setDescription(event.target.value);
  };

  if (!id) {
    return (
      <main className="page-container">
        <div className="error-state">
          <h1>Discussion</h1>

          <p>Decision ID is missing.</p>

          <button
            type="button"
            onClick={() => navigate("/decisions")}
          >
            Back to Decisions
          </button>
        </div>
      </main>
    );
  }

  return (
    <main className="page-container">
      <header
        className="page-header"
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          gap: "16px",
          flexWrap: "wrap",
        }}
      >
        <div>
          <button
            type="button"
            onClick={() =>
              navigate(`/decisions/${id}`)
            }
            style={{
              marginBottom: "12px",
            }}
          >
            ← Back to Decision
          </button>

          <h1>Discussion</h1>

          <p>
            Start and manage discussions for this
            decision.
          </p>
        </div>

        <div
          style={{
            display: "flex",
            gap: "10px",
            flexWrap: "wrap",
          }}
        >
          <button
            type="button"
            onClick={() => loadThreads()}
            disabled={isLoading}
          >
            ↻ Refresh
          </button>

          <button
            type="button"
            onClick={() =>
              setShowCreateForm(
                (current) => !current,
              )
            }
          >
            +{" "}
            {showCreateForm
              ? "Close"
              : "Start Discussion"}
          </button>
        </div>
      </header>

      {error && (
        <div
          className="error-state"
          style={{ marginTop: "20px" }}
        >
          <strong>Error:</strong> {error}
        </div>
      )}

      {success && (
        <div
          style={{
            marginTop: "20px",
            padding: "12px 16px",
            borderRadius: "8px",
            border: "1px solid #b7ebc6",
            background: "#f0fff4",
          }}
        >
          {success}
        </div>
      )}

      {showCreateForm && (
        <section
          className="alternative-form-card"
          style={{ marginTop: "24px" }}
        >
          <h2>Start a Discussion</h2>

          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: "16px" }}>
              <label
                htmlFor="discussion-title"
                style={{
                  display: "block",
                  fontWeight: 600,
                  marginBottom: "8px",
                }}
              >
                Discussion Title
              </label>

              <input
                id="discussion-title"
                type="text"
                value={title}
                onChange={handleTitleChange}
                placeholder="Enter discussion title"
                disabled={isSubmitting}
                style={{
                  width: "100%",
                  padding: "10px 12px",
                  borderRadius: "8px",
                  border: "1px solid #ccc",
                }}
              />
            </div>

            <div style={{ marginBottom: "16px" }}>
              <label
                htmlFor="discussion-description"
                style={{
                  display: "block",
                  fontWeight: 600,
                  marginBottom: "8px",
                }}
              >
                Description
              </label>

              <textarea
                id="discussion-description"
                value={description}
                onChange={handleDescriptionChange}
                placeholder="Explain what you want to discuss..."
                rows={5}
                disabled={isSubmitting}
                style={{
                  width: "100%",
                  padding: "10px 12px",
                  borderRadius: "8px",
                  border: "1px solid #ccc",
                  resize: "vertical",
                }}
              />
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
            >
              {isSubmitting
                ? "Creating..."
                : "Create Discussion"}
            </button>
          </form>
        </section>
      )}

      <section style={{ marginTop: "28px" }}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "18px",
          }}
        >
          <div>
            <h2>Discussion Threads</h2>

            <p>
              {threads.length}{" "}
              {threads.length === 1
                ? "discussion"
                : "discussions"}
            </p>
          </div>
        </div>

        {isLoading ? (
          <div className="empty-state">
            <p>Loading discussions...</p>
          </div>
        ) : threads.length === 0 ? (
          <div className="empty-state">
            <h3>No discussions yet</h3>

            <p>
              Start a discussion to collaborate
              with other users.
            </p>
          </div>
        ) : (
          <div
            style={{
              display: "grid",
              gap: "16px",
            }}
          >
            {threads.map((thread) => (
              <article
                key={thread.id}
                className="alternative-card"
                onClick={() =>
                  handleThreadClick(thread)
                }
                role="button"
                tabIndex={0}
                onKeyDown={(event) => {
                  if (
                    event.key === "Enter" ||
                    event.key === " "
                  ) {
                    event.preventDefault();

                    handleThreadClick(thread);
                  }
                }}
                style={{
                  cursor: "pointer",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "flex-start",
                    gap: "16px",
                  }}
                >
                  <div>
                    <h3
                      style={{
                        marginTop: 0,
                        marginBottom: "8px",
                      }}
                    >
                      {thread.title}
                    </h3>

                    <p>
                      {thread.description}
                    </p>
                  </div>

                  <button
                    type="button"
                    onClick={(event) => {
                      event.stopPropagation();

                      handleDelete(thread.id);
                    }}
                  >
                    Delete
                  </button>
                </div>

                <div
                  style={{
                    display: "flex",
                    gap: "12px",
                    flexWrap: "wrap",
                    marginTop: "14px",
                    fontSize: "14px",
                  }}
                >
                  <span>
                    Discussion #{thread.id}
                  </span>

                  <span>
                    Status: {thread.status}
                  </span>

                  <span>
                    Created By User #
                    {thread.created_by}
                  </span>

                  <span>
                    Created:{" "}
                    {formatDate(
                      thread.created_at,
                    )}
                  </span>
                </div>

                <div
                  style={{
                    marginTop: "14px",
                    fontSize: "13px",
                    opacity: 0.7,
                  }}
                >
                  Click this discussion to view
                  details
                </div>
              </article>
            ))}
          </div>
        )}
      </section>

      {selectedThread && (
        <section
          id="discussion-detail"
          className="alternative-form-card"
          style={{ marginTop: "24px" }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "flex-start",
              gap: "16px",
              flexWrap: "wrap",
            }}
          >
            <div>
              <span
                style={{
                  fontSize: "13px",
                  opacity: 0.7,
                }}
              >
                Discussion #{selectedThread.id}
              </span>

              <h2
                style={{
                  marginTop: "6px",
                  marginBottom: "8px",
                }}
              >
                {selectedThread.title}
              </h2>

              <p>
                {selectedThread.description}
              </p>
            </div>

            <button
              type="button"
              onClick={() =>
                setSelectedThread(null)
              }
            >
              Close
            </button>
          </div>

          <hr
            style={{
              margin: "24px 0",
              border: 0,
              borderTop: "1px solid #ddd",
            }}
          />

          <h3>Discussion Details</h3>

          <div
            style={{
              display: "grid",
              gap: "10px",
              marginTop: "12px",
            }}
          >
            <p>
              <strong>Status:</strong>{" "}
              {selectedThread.status}
            </p>

            <p>
              <strong>Created By:</strong> User #
              {selectedThread.created_by}
            </p>

            <p>
              <strong>Created:</strong>{" "}
              {formatDate(
                selectedThread.created_at,
              )}
            </p>
          </div>

          <div
            style={{
              marginTop: "20px",
              padding: "16px",
              borderRadius: "8px",
              border: "1px dashed #bbb",
            }}
          >
            <h3>Comments & Further Discussion</h3>

            <p>
              This discussion is selected and
              ready for comments and further
              discussion.
            </p>
          </div>
        </section>
      )}
    </main>
  );
}