import {
  useCallback,
  useEffect,
  useState,
  type ChangeEvent,
  type FormEvent,
} from "react";

import axios from "axios";

import {
  ArrowLeft,
  MessageSquare,
  Plus,
  RefreshCw,
  Trash2,
  X,
  User,
  CalendarDays,
  CheckCircle2,
  FileText,
  Scale,
  ClipboardCheck,
  History,
} from "lucide-react";

import {
  useNavigate,
  useParams,
} from "react-router-dom";

import api from "../services/api";

interface DiscussionThread {
  id: number;
  title: string;
  description: string;
  status: string;
  created_by: number;
  created_at: string;
}

function getApiErrorMessage(
  error: unknown,
): string {
  if (axios.isAxiosError(error)) {
    const detail =
      error.response?.data?.detail;

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

    if (
      error.response?.status !== undefined &&
      error.response.status >= 500
    ) {
      return "Server error. Please try again.";
    }

    return (
      error.message ||
      "Request failed."
    );
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "Something went wrong. Please try again.";
}

function formatDate(
  value: string,
): string {
  if (!value) {
    return "Unknown date";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function getStatusClass(
  status: string,
): string {
  return status
    .toLowerCase()
    .replace(/\s+/g, "-");
}

export default function Discussion() {
  const { id } =
    useParams<{ id: string }>();

  const navigate = useNavigate();

  const [threads, setThreads] =
    useState<DiscussionThread[]>([]);

  const [selectedThread, setSelectedThread] =
    useState<DiscussionThread | null>(
      null,
    );

  const [title, setTitle] =
    useState("");

  const [description, setDescription] =
    useState("");

  const [isLoading, setIsLoading] =
    useState(true);

  const [isSubmitting, setIsSubmitting] =
    useState(false);

  const [error, setError] =
    useState("");

  const [success, setSuccess] =
    useState("");

  const [showCreateForm, setShowCreateForm] =
    useState(false);

  const loadThreads =
    useCallback(async () => {
      if (!id) {
        return;
      }

      setIsLoading(true);
      setError("");

      try {
        const response =
          await api.get<DiscussionThread[]>(
            `/decisions/${id}/threads`,
          );

        setThreads(response.data);
      } catch (requestError: unknown) {
        console.error(
          "Unable to load discussion threads:",
          requestError,
        );

        setError(
          getApiErrorMessage(
            requestError,
          ),
        );
      } finally {
        setIsLoading(false);
      }
    }, [id]);

  useEffect(() => {
    let cancelled = false;

    const loadInitialThreads =
      async () => {
        if (!id || cancelled) {
          return;
        }

        await loadThreads();
      };

    void loadInitialThreads();

    return () => {
      cancelled = true;
    };
  }, [id, loadThreads]);

  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();

    if (!id) {
      setError(
        "Decision ID is missing.",
      );
      return;
    }

    if (!title.trim()) {
      setError(
        "Discussion title is required.",
      );
      return;
    }

    if (!description.trim()) {
      setError(
        "Discussion description is required.",
      );
      return;
    }

    setIsSubmitting(true);
    setError("");
    setSuccess("");

    try {
      await api.post(
        `/decisions/${id}/threads`,
        {
          title: title.trim(),
          description:
            description.trim(),
        },
      );

      setTitle("");
      setDescription("");
      setShowCreateForm(false);

      setSuccess(
        "Discussion thread created successfully.",
      );

      await loadThreads();
    } catch (requestError: unknown) {
      console.error(
        "Unable to create discussion:",
        requestError,
      );

      setError(
        getApiErrorMessage(
          requestError,
        ),
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (
    threadId: number,
  ) => {
    const confirmed =
      window.confirm(
        "Are you sure you want to delete this discussion?",
      );

    if (!confirmed) {
      return;
    }

    setError("");
    setSuccess("");

    try {
      await api.delete(
        `/threads/${threadId}`,
      );

      if (
        selectedThread?.id ===
        threadId
      ) {
        setSelectedThread(null);
      }

      setSuccess(
        "Discussion deleted successfully.",
      );

      await loadThreads();
    } catch (requestError: unknown) {
      console.error(
        "Unable to delete discussion:",
        requestError,
      );

      setError(
        getApiErrorMessage(
          requestError,
        ),
      );
    }
  };

  const handleThreadClick = (
    thread: DiscussionThread,
  ) => {
    setSelectedThread(thread);

    window.setTimeout(() => {
      document
        .getElementById(
          "discussion-detail",
        )
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
    setDescription(
      event.target.value,
    );
  };

  if (!id) {
    return (
      <main className="discussion-page">
        <div className="discussion-error-state">
          <div className="discussion-error-icon">
            <MessageSquare size={25} />
          </div>

          <h1>Discussion</h1>

          <p>
            Decision ID is missing.
          </p>

          <button
            type="button"
            className="discussion-primary-button"
            onClick={() =>
              navigate("/decisions")
            }
          >
            <ArrowLeft size={17} />
            Back to Decisions
          </button>
        </div>
      </main>
    );
  }

  const decisionTabs = [
    {
      label: "Overview",
      icon: FileText,
      path: `/decisions/${id}`,
    },
    {
      label: "Alternatives",
      icon: Scale,
      path: `/decisions/${id}/alternatives`,
    },
    {
      label: "Discussion",
      icon: MessageSquare,
      path: `/decisions/${id}/discussion`,
    },
    {
      label: "Approval",
      icon: ClipboardCheck,
      path: `/decisions/${id}/approval`,
    },
    {
      label: "History",
      icon: History,
      path: `/decisions/${id}/history`,
    },
  ];

  return (
    <main className="discussion-page">
      {/* HEADER */}

      <header className="discussion-header">
        <div className="discussion-heading">
          <div className="discussion-heading-icon">
            <MessageSquare size={25} />
          </div>

          <div>
            <p className="discussion-eyebrow">
              EXPERT DECISION REPLAY PLATFORM
            </p>

            <h1>
              Discussion
            </h1>

            <p className="discussion-subtitle">
              Collaborate, review perspectives,
              and document discussions for
              Decision #{id}.
            </p>
          </div>
        </div>

        <div className="discussion-header-actions">
          <button
            type="button"
            className="discussion-secondary-button"
            onClick={() =>
              navigate(
                `/decisions/${id}`,
              )
            }
          >
            <ArrowLeft size={17} />
            Back to Decision
          </button>

          <button
            type="button"
            className="discussion-secondary-button"
            onClick={() => {
              void loadThreads();
            }}
            disabled={isLoading}
          >
            <RefreshCw
              size={16}
              className={
                isLoading
                  ? "discussion-spin"
                  : ""
              }
            />

            Refresh
          </button>

          <button
            type="button"
            className="discussion-primary-button"
            onClick={() =>
              setShowCreateForm(
                (current) =>
                  !current,
              )
            }
          >
            {showCreateForm ? (
              <X size={17} />
            ) : (
              <Plus size={17} />
            )}

            {showCreateForm
              ? "Close"
              : "Start Discussion"}
          </button>
        </div>
      </header>

      {/* DECISION NAVIGATION */}

      <nav
        className="decision-context-nav discussion-context-nav"
        aria-label="Decision navigation"
      >
        {decisionTabs.map(
          (tab) => {
            const Icon = tab.icon;

            const isActive =
              tab.label ===
              "Discussion";

            return (
              <button
                key={tab.label}
                type="button"
                className={`decision-context-tab ${
                  isActive
                    ? "active"
                    : ""
                }`}
                onClick={() =>
                  navigate(
                    tab.path,
                  )
                }
              >
                <Icon size={17} />
                <span>
                  {tab.label}
                </span>
              </button>
            );
          },
        )}
      </nav>

      {/* STATUS MESSAGES */}

      {error && (
        <div
          className="discussion-alert discussion-alert-error"
          role="alert"
        >
          <div className="discussion-alert-icon">
            <X size={18} />
          </div>

          <div>
            <strong>
              Something went wrong
            </strong>

            <p>{error}</p>
          </div>
        </div>
      )}

      {success && (
        <div
          className="discussion-alert discussion-alert-success"
          role="status"
        >
          <div className="discussion-alert-icon">
            <CheckCircle2 size={18} />
          </div>

          <div>
            <strong>
              Success
            </strong>

            <p>{success}</p>
          </div>
        </div>
      )}

      {/* CREATE DISCUSSION */}

      {showCreateForm && (
        <section className="discussion-create-card">
          <div className="discussion-section-header">
            <div className="discussion-section-icon">
              <Plus size={20} />
            </div>

            <div>
              <span className="discussion-section-label">
                COLLABORATION
              </span>

              <h2>
                Start a Discussion
              </h2>

              <p>
                Create a discussion thread
                to capture questions,
                opinions, and review
                feedback.
              </p>
            </div>
          </div>

          <form
            onSubmit={handleSubmit}
            className="discussion-form"
          >
            <div className="discussion-field">
              <label htmlFor="discussion-title">
                Discussion Title
              </label>

              <span className="discussion-field-help">
                Give the discussion a
                clear and recognizable
                topic.
              </span>

              <input
                id="discussion-title"
                type="text"
                value={title}
                onChange={
                  handleTitleChange
                }
                placeholder="Enter discussion title"
                disabled={
                  isSubmitting
                }
              />
            </div>

            <div className="discussion-field">
              <label htmlFor="discussion-description">
                Description
              </label>

              <span className="discussion-field-help">
                Explain the question,
                concern, or topic you
                want the team to discuss.
              </span>

              <textarea
                id="discussion-description"
                value={description}
                onChange={
                  handleDescriptionChange
                }
                placeholder="Explain what you want to discuss..."
                rows={6}
                disabled={
                  isSubmitting
                }
              />
            </div>

            <div className="discussion-form-footer">
              <p>
                Provide enough context
                so participants can
                understand the discussion.
              </p>

              <button
                type="submit"
                className="discussion-primary-button"
                disabled={
                  isSubmitting
                }
              >
                {isSubmitting ? (
                  <RefreshCw
                    size={17}
                    className="discussion-spin"
                  />
                ) : (
                  <MessageSquare
                    size={17}
                  />
                )}

                {isSubmitting
                  ? "Creating..."
                  : "Create Discussion"}
              </button>
            </div>
          </form>
        </section>
      )}

      {/* THREADS */}

      <section className="discussion-list-section">
        <div className="discussion-list-header">
          <div>
            <span className="discussion-section-label">
              DECISION COLLABORATION
            </span>

            <h2>
              Discussion Threads
            </h2>

            <p>
              {threads.length}{" "}
              {threads.length === 1
                ? "discussion"
                : "discussions"}{" "}
              available for this
              decision.
            </p>
          </div>

          <div className="discussion-count">
            <MessageSquare size={16} />
            {threads.length}
          </div>
        </div>

        {isLoading ? (
          <div className="discussion-state-card">
            <div className="loading-spinner" />

            <h3>
              Loading discussions...
            </h3>

            <p>
              Retrieving the latest
              discussion threads.
            </p>
          </div>
        ) : threads.length === 0 ? (
          <div className="discussion-state-card">
            <div className="discussion-empty-icon">
              <MessageSquare size={30} />
            </div>

            <h3>
              No discussions yet
            </h3>

            <p>
              Start a discussion to
              collaborate with other
              users.
            </p>

            <button
              type="button"
              className="discussion-primary-button"
              onClick={() =>
                setShowCreateForm(
                  true,
                )
              }
            >
              <Plus size={17} />
              Start Discussion
            </button>
          </div>
        ) : (
          <div className="discussion-thread-grid">
            {threads.map(
              (thread) => (
                <article
                  key={thread.id}
                  className={`discussion-thread-card ${
                    selectedThread?.id ===
                    thread.id
                      ? "discussion-thread-selected"
                      : ""
                  }`}
                  onClick={() =>
                    handleThreadClick(
                      thread,
                    )
                  }
                  role="button"
                  tabIndex={0}
                  onKeyDown={(
                    event,
                  ) => {
                    if (
                      event.key ===
                        "Enter" ||
                      event.key ===
                        " "
                    ) {
                      event.preventDefault();

                      handleThreadClick(
                        thread,
                      );
                    }
                  }}
                >
                  <div className="discussion-thread-top">
                    <div className="discussion-thread-icon">
                      <MessageSquare
                        size={19}
                      />
                    </div>

                    <span
                      className={`discussion-status ${getStatusClass(
                        thread.status,
                      )}`}
                    >
                      {thread.status}
                    </span>
                  </div>

                  <div className="discussion-thread-content">
                    <span className="discussion-thread-number">
                      Discussion #
                      {thread.id}
                    </span>

                    <h3>
                      {thread.title}
                    </h3>

                    <p>
                      {
                        thread.description
                      }
                    </p>
                  </div>

                  <div className="discussion-thread-meta">
                    <div>
                      <User size={14} />

                      <span>
                        User #
                        {
                          thread.created_by
                        }
                      </span>
                    </div>

                    <div>
                      <CalendarDays
                        size={14}
                      />

                      <span>
                        {formatDate(
                          thread.created_at,
                        )}
                      </span>
                    </div>
                  </div>

                  <div className="discussion-thread-footer">
                    <span>
                      View discussion
                      details
                    </span>

                    <button
                      type="button"
                      className="discussion-delete-button"
                      onClick={(
                        event,
                      ) => {
                        event.stopPropagation();

                        void handleDelete(
                          thread.id,
                        );
                      }}
                      aria-label={`Delete discussion ${thread.id}`}
                    >
                      <Trash2
                        size={16}
                      />

                      Delete
                    </button>
                  </div>
                </article>
              ),
            )}
          </div>
        )}
      </section>

      {/* SELECTED DISCUSSION */}

      {selectedThread && (
        <section
          id="discussion-detail"
          className="discussion-detail-card"
        >
          <div className="discussion-detail-header">
            <div className="discussion-detail-heading">
              <div className="discussion-detail-icon">
                <FileText
                  size={21}
                />
              </div>

              <div>
                <span className="discussion-thread-number">
                  Discussion #
                  {
                    selectedThread.id
                  }
                </span>

                <h2>
                  {
                    selectedThread.title
                  }
                </h2>
              </div>
            </div>

            <button
              type="button"
              className="discussion-close-button"
              onClick={() =>
                setSelectedThread(
                  null,
                )
              }
            >
              <X size={17} />
              Close
            </button>
          </div>

          <div className="discussion-detail-description">
            <p>
              {
                selectedThread.description
              }
            </p>
          </div>

          <div className="discussion-detail-divider" />

          <div className="discussion-detail-grid">
            <div className="discussion-detail-item">
              <span>Status</span>

              <strong
                className={`discussion-status ${getStatusClass(
                  selectedThread.status,
                )}`}
              >
                {
                  selectedThread.status
                }
              </strong>
            </div>

            <div className="discussion-detail-item">
              <span>
                Created By
              </span>

              <strong>
                <User size={15} />
                User #
                {
                  selectedThread.created_by
                }
              </strong>
            </div>

            <div className="discussion-detail-item">
              <span>
                Created
              </span>

              <strong>
                <CalendarDays
                  size={15}
                />
                {formatDate(
                  selectedThread.created_at,
                )}
              </strong>
            </div>

            <div className="discussion-detail-item">
              <span>
                Discussion ID
              </span>

              <strong>
                #
                {
                  selectedThread.id
                }
              </strong>
            </div>
          </div>

          <div className="discussion-comments-panel">
            <div className="discussion-comments-icon">
              <MessageSquare
                size={21}
              />
            </div>

            <div>
              <h3>
                Comments & Further
                Discussion
              </h3>

              <p>
                This discussion is
                selected and ready for
                comments and further
                discussion.
              </p>
            </div>
          </div>
        </section>
      )}
    </main>
  );
}