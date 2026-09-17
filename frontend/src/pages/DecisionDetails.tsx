import {
  useEffect,
  useState,
  type KeyboardEvent,
} from "react";
import {
  ArrowLeft as ArrowLeftIcon,
  ArrowRight as ArrowRightIcon,
  Calendar as CalendarIcon,
  CheckCircle2 as CheckCircle2Icon,
  Edit as EditIcon,
  FileText as FileTextIcon,
  GitBranch as GitBranchIcon,
  History as HistoryIcon,
  MessageSquare as MessageSquareIcon,
  Scale as ScaleIcon,
  ClipboardCheck as ClipboardCheckIcon,
} from "lucide-react";
import { useNavigate, useParams } from "react-router-dom";
import { isAxiosError } from "axios";

import api from "../services/api";

interface Decision {
  id: number;
  title: string;
  problem_statement: string;
  category: string;
  status: string;
  created_by: number;
  created_at: string;
  updated_at: string;
}

function formatDate(dateString: string) {
  return new Date(dateString).toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function getStatusClass(status: string) {
  return status.toLowerCase().replace(/\s+/g, "-");
}

export default function DecisionDetails() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [decision, setDecision] = useState<Decision | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let isMounted = true;

    const loadDecision = async () => {
      if (!id) {
        if (isMounted) {
          setError("Invalid decision ID.");
          setIsLoading(false);
        }
        return;
      }

      try {
        if (isMounted) {
          setError("");
          setIsLoading(true);
        }

        const response = await api.get<Decision>(
          `/decisions/${id}`
        );

        if (isMounted) {
          setDecision(response.data);
        }
      } catch (err: unknown) {
        if (!isMounted) {
          return;
        }

        if (isAxiosError(err)) {
          const status = err.response?.status;

          if (status === 401) {
            setError(
              "Your session has expired. Please sign in again."
            );
          } else if (status === 403) {
            setError(
              "You do not have permission to view this decision."
            );
          } else if (status === 404) {
            setError("Decision not found.");
          } else if (status && status >= 500) {
            setError(
              "Server error. Please try again later."
            );
          } else if (err.request) {
            setError(
              "Unable to connect to the server. Make sure FastAPI is running."
            );
          } else {
            setError("Unable to load the decision.");
          }
        } else {
          setError("Unable to load the decision.");
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    void loadDecision();

    return () => {
      isMounted = false;
    };
  }, [id]);

  const retryLoad = async () => {
    if (!id) {
      setError("Invalid decision ID.");
      return;
    }

    try {
      setError("");
      setIsLoading(true);

      const response = await api.get<Decision>(
        `/decisions/${id}`
      );

      setDecision(response.data);
    } catch (err: unknown) {
      if (isAxiosError(err)) {
        const status = err.response?.status;

        if (status === 401) {
          setError(
            "Your session has expired. Please sign in again."
          );
        } else if (status === 403) {
          setError(
            "You do not have permission to view this decision."
          );
        } else if (status === 404) {
          setError("Decision not found.");
        } else if (status && status >= 500) {
          setError(
            "Server error. Please try again later."
          );
        } else if (err.request) {
          setError(
            "Unable to connect to the server. Make sure FastAPI is running."
          );
        } else {
          setError("Unable to load the decision.");
        }
      } else {
        setError("Unable to load the decision.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleWorkspaceKeyDown = (
    event: KeyboardEvent<HTMLDivElement>,
    path: string
  ) => {
    if (
      event.key === "Enter" ||
      event.key === " "
    ) {
      event.preventDefault();
      navigate(path);
    }
  };

  const decisionTabs = [
    {
      label: "Overview",
      icon: FileTextIcon,
      path: `/decisions/${id}`,
    },
    {
      label: "Alternatives",
      icon: ScaleIcon,
      path: `/decisions/${id}/alternatives`,
    },
    {
      label: "Discussion",
      icon: MessageSquareIcon,
      path: `/decisions/${id}/discussion`,
    },
    {
      label: "Approval",
      icon: ClipboardCheckIcon,
      path: `/decisions/${id}/approval`,
    },
    {
      label: "History",
      icon: HistoryIcon,
      path: `/decisions/${id}/history`,
    },
  ];

  if (isLoading) {
    return (
      <main className="decision-details-loading-page">
        <div className="decision-details-loading-card">
          <div className="loading-spinner" />
          <p>Loading decision...</p>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="decision-details-page">
        <section
          className="decision-details-error-card"
          role="alert"
        >
          <div className="decision-details-error-icon">
            <FileTextIcon size={24} />
          </div>

          <div className="decision-details-error-content">
            <p className="decision-details-eyebrow">
              Decision Details
            </p>

            <h1>Unable to load decision</h1>

            <p>{error}</p>

            <div className="decision-details-error-actions">
              <button
                type="button"
                className="decision-details-secondary-button"
                onClick={() =>
                  navigate("/decisions")
                }
              >
                <ArrowLeftIcon size={18} />
                Back to Decisions
              </button>

              <button
                type="button"
                className="decision-details-primary-button"
                onClick={() => {
                  void retryLoad();
                }}
              >
                Try Again
              </button>
            </div>
          </div>
        </section>
      </main>
    );
  }

  if (!decision) {
    return null;
  }

  const statusClass = getStatusClass(
    decision.status
  );

  const workspaceItems = [
    {
      title: "Alternatives",
      description:
        "Compare possible solutions for this decision.",
      action: "Open Alternative Analysis",
      icon: ScaleIcon,
      path: `/decisions/${decision.id}/alternatives`,
      className: "alternatives",
    },
    {
      title: "Discussion",
      description:
        "Review comments and decision discussions.",
      action: "Open Discussion",
      icon: MessageSquareIcon,
      path: `/decisions/${decision.id}/discussion`,
      className: "discussion",
    },
    {
      title: "Approval",
      description:
        "Track the decision approval workflow.",
      action: "Open Approval Workflow",
      icon: ClipboardCheckIcon,
      path: `/decisions/${decision.id}/approval`,
      className: "approval",
    },
    {
      title: "History",
      description:
        "Review versions and the decision timeline.",
      action: "Open Version History",
      icon: HistoryIcon,
      path: `/decisions/${decision.id}/history`,
      className: "history",
    },
  ];

  return (
    <main className="decision-details-page">
      <div className="decision-details-container">

        {/* Header */}
        <header className="decision-details-header">
          <div className="decision-details-heading">
            <div className="decision-details-title-icon">
              <FileTextIcon size={24} />
            </div>

            <div className="decision-details-title-content">
              <p className="decision-details-eyebrow">
                Expert Decision Replay Platform
              </p>

              <div className="decision-details-title-row">
                <h1>{decision.title}</h1>

                <span
                  className={`decision-details-status ${statusClass}`}
                >
                  <CheckCircle2Icon size={15} />
                  {decision.status}
                </span>
              </div>

              <p className="decision-details-reference">
                Decision #{decision.id}
              </p>
            </div>
          </div>

          <div className="decision-details-header-actions">
            <button
              type="button"
              className="decision-details-secondary-button"
              onClick={() =>
                navigate("/decisions")
              }
            >
              <ArrowLeftIcon size={18} />
              Back to Decisions
            </button>

            <button
              type="button"
              className="decision-details-primary-button"
              onClick={() =>
                navigate(
                  `/decisions/${decision.id}/edit`
                )
              }
            >
              <EditIcon size={18} />
              Edit Decision
            </button>
          </div>
        </header>

        {/* Decision Navigation */}
        <nav
          className="decision-context-nav"
          aria-label="Decision navigation"
        >
          {decisionTabs.map((tab) => {
            const Icon = tab.icon;

            const isActive =
              tab.label === "Overview";

            return (
              <button
                key={tab.label}
                type="button"
                className={`decision-context-tab ${
                  isActive ? "active" : ""
                }`}
                onClick={() => navigate(tab.path)}
              >
                <Icon size={17} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Decision Information */}
        <section className="decision-details-card">
          <div className="decision-details-card-header">
            <div className="decision-details-card-icon">
              <FileTextIcon size={21} />
            </div>

            <div>
              <h2>Decision Information</h2>

              <p>
                Review the information and current
                status of this decision.
              </p>
            </div>
          </div>

          <div className="decision-details-info-grid">
            <div className="decision-details-info-item">
              <span className="decision-details-info-label">
                Decision ID
              </span>

              <strong className="decision-details-id-value">
                #{decision.id}
              </strong>
            </div>

            <div className="decision-details-info-item">
              <span className="decision-details-info-label">
                Category
              </span>

              <strong className="decision-details-category-value">
                {decision.category}
              </strong>
            </div>

            <div className="decision-details-info-item">
              <span className="decision-details-info-label">
                Status
              </span>

              <span
                className={`decision-details-status ${statusClass}`}
              >
                <CheckCircle2Icon size={15} />
                {decision.status}
              </span>
            </div>

            <div className="decision-details-info-item">
              <span className="decision-details-info-label">
                Created By
              </span>

              <strong>
                User #{decision.created_by}
              </strong>
            </div>

            <div className="decision-details-info-item">
              <span className="decision-details-info-label">
                Created
              </span>

              <strong className="decision-details-date-value">
                <CalendarIcon size={16} />
                {formatDate(decision.created_at)}
              </strong>
            </div>

            <div className="decision-details-info-item">
              <span className="decision-details-info-label">
                Last Updated
              </span>

              <strong className="decision-details-date-value">
                <CalendarIcon size={16} />
                {formatDate(decision.updated_at)}
              </strong>
            </div>
          </div>

          {/* Problem Statement */}
          <div className="decision-details-problem-section">
            <div className="decision-details-section-heading">
              <div className="decision-details-section-icon">
                <FileTextIcon size={17} />
              </div>

              <h3>Problem Statement</h3>
            </div>

            <div className="decision-details-problem">
              <p>{decision.problem_statement}</p>
            </div>
          </div>
        </section>

        {/* Decision Workspace */}
        <section className="decision-details-card">
          <div className="decision-details-card-header">
            <div className="decision-details-card-icon workspace">
              <GitBranchIcon size={21} />
            </div>

            <div>
              <h2>Decision Workspace</h2>

              <p>
                Explore the complete decision
                lifecycle.
              </p>
            </div>
          </div>

          <div className="decision-details-workspace-grid">
            {workspaceItems.map((item) => {
              const Icon = item.icon;

              return (
                <div
                  key={item.title}
                  className={`decision-details-workspace-card ${item.className}`}
                  onClick={() =>
                    navigate(item.path)
                  }
                  role="button"
                  tabIndex={0}
                  onKeyDown={(event) =>
                    handleWorkspaceKeyDown(
                      event,
                      item.path
                    )
                  }
                >
                  <div className="decision-details-workspace-top">
                    <div className="decision-details-workspace-icon">
                      <Icon size={21} />
                    </div>

                    <ArrowRightIcon
                      className="decision-details-workspace-arrow"
                      size={19}
                    />
                  </div>

                  <div className="decision-details-workspace-content">
                    <h3>{item.title}</h3>

                    <p>{item.description}</p>

                    <span>
                      {item.action}
                      <ArrowRightIcon size={15} />
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      </div>
    </main>
  );
}