import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Activity as ActivityIcon,
  CalendarDays,
  ChevronLeft,
  Filter,
  RefreshCw,
  UserRound,
} from "lucide-react";

import Alert from "../components/Alert";
import Button from "../components/Button";
import StatusBadge from "../components/StatusBadge";
import { useAuth } from "../auth/AuthContext";
import {
  getActivities,
  type Activity,
} from "../services/activityService";
import "./ActivityPage.css";

function formatDateTime(value: string) {
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

function getActionVariant(
  action: string,
): "success" | "danger" | "warning" | "neutral" {
  const normalized = action.toLowerCase();

  if (
    normalized.includes("create") ||
    normalized.includes("approve") ||
    normalized.includes("complete")
  ) {
    return "success";
  }

  if (
    normalized.includes("delete") ||
    normalized.includes("reject")
  ) {
    return "danger";
  }

  if (
    normalized.includes("update") ||
    normalized.includes("edit")
  ) {
    return "warning";
  }

  return "neutral";
}

function getErrorMessage(error: unknown) {
  const status = (
    error as {
      response?: {
        status?: number;
      };
    }
  )?.response?.status;

  if (status === 401) {
    return "Your session has expired. Please sign in again.";
  }

  if (status === 403) {
    return "You do not have permission to view these activities.";
  }

  if (status === 422) {
    return "One or more filters are invalid.";
  }

  if (status && status >= 500) {
    return "The server is temporarily unavailable. Please try again.";
  }

  return "Unable to load activity records. Please try again.";
}

export default function ActivityPage() {
  const { user } = useAuth();

  const [activities, setActivities] = useState<Activity[]>([]);
  const [action, setAction] = useState("");
  const [entityType, setEntityType] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  const loadActivities = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage("");

    try {
      const data = await getActivities({
        action: action || undefined,
        entity_type: entityType || undefined,
        start_date: startDate
          ? `${startDate}T00:00:00`
          : undefined,
        end_date: endDate
          ? `${endDate}T23:59:59`
          : undefined,
      });

      setActivities(data);
    } catch (error: unknown) {
      setActivities([]);
      setErrorMessage(getErrorMessage(error));
    } finally {
      setIsLoading(false);
    }
  }, [action, entityType, startDate, endDate]);

  useEffect(() => {
    void loadActivities();
  }, [loadActivities]);

  const entityTypes = useMemo(
    () =>
      Array.from(
        new Set(
          activities
            .map((item) => item.entity_type)
            .filter(Boolean),
        ),
      ).sort(),
    [activities],
  );

  const actions = useMemo(
    () =>
      Array.from(
        new Set(
          activities
            .map((item) => item.action)
            .filter(Boolean),
        ),
      ).sort(),
    [activities],
  );

  function clearFilters() {
    setAction("");
    setEntityType("");
    setStartDate("");
    setEndDate("");
  }

  return (
    <div className="activity-page">
      <header className="activity-header">
        <div>
          <div className="activity-kicker">
            PLATFORM ACTIVITY
          </div>

          <h1>Activity</h1>

          <p>
            Review recent activity records available to your
            role.
          </p>
        </div>

        <div className="activity-user-chip">
          <UserRound size={15} aria-hidden="true" />
          {user?.full_name}
        </div>
      </header>

      {errorMessage && (
        <div className="activity-alert">
          <Alert variant="error">
            {errorMessage}
          </Alert>
        </div>
      )}

      <section className="activity-filter-card">
        <div className="activity-filter-title">
          <Filter size={16} aria-hidden="true" />
          <div>
            <h2>Activity filters</h2>
            <p>
              Narrow the activity timeline by action, entity,
              or date.
            </p>
          </div>
        </div>

        <div className="activity-filters">
          <label>
            <span>Action</span>

            <select
              value={action}
              onChange={(event) =>
                setAction(event.target.value)
              }
            >
              <option value="">All actions</option>

              {actions.map((item) => (
                <option value={item} key={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>

          <label>
            <span>Entity</span>

            <select
              value={entityType}
              onChange={(event) =>
                setEntityType(event.target.value)
              }
            >
              <option value="">All entities</option>

              {entityTypes.map((item) => (
                <option value={item} key={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>

          <label>
            <span>From</span>

            <div className="activity-date-input">
              <CalendarDays
                size={14}
                aria-hidden="true"
              />

              <input
                type="date"
                value={startDate}
                onChange={(event) =>
                  setStartDate(event.target.value)
                }
              />
            </div>
          </label>

          <label>
            <span>To</span>

            <div className="activity-date-input">
              <CalendarDays
                size={14}
                aria-hidden="true"
              />

              <input
                type="date"
                value={endDate}
                onChange={(event) =>
                  setEndDate(event.target.value)
                }
              />
            </div>
          </label>

          <Button
            variant="secondary"
            onClick={clearFilters}
          >
            Clear
          </Button>
        </div>
      </section>

      <section className="activity-list-card">
        <div className="activity-list-header">
          <div>
            <h2>Activity timeline</h2>
            <p>
              {activities.length}{" "}
              {activities.length === 1
                ? "activity"
                : "activities"}{" "}
              found
            </p>
          </div>

          <button
            type="button"
            className="activity-refresh-button"
            onClick={() => void loadActivities()}
            disabled={isLoading}
          >
            <RefreshCw
              size={14}
              className={
                isLoading
                  ? "activity-spin"
                  : undefined
              }
              aria-hidden="true"
            />
            Refresh
          </button>
        </div>

        {isLoading ? (
          <div
            className="activity-loading"
            role="status"
            aria-live="polite"
          >
            <div className="activity-spinner" />
            Loading activity...
          </div>
        ) : activities.length === 0 ? (
          <div className="activity-empty">
            <ActivityIcon
              size={25}
              aria-hidden="true"
            />

            <h3>No activity found</h3>

            <p>
              There are no activity records matching the
              selected filters.
            </p>
          </div>
        ) : (
          <div className="activity-timeline">
            {activities.map((item) => (
              <div
                className="activity-item"
                key={item.id}
              >
                <div className="activity-item-marker">
                  <ActivityIcon
                    size={14}
                    aria-hidden="true"
                  />
                </div>

                <div className="activity-item-body">
                  <div className="activity-item-top">
                    <div>
                      <strong>
                        {item.description}
                      </strong>

                      <span>
                        {item.entity_type} #
                        {item.entity_id}
                      </span>
                    </div>

                    <StatusBadge
                      variant={getActionVariant(
                        item.action,
                      )}
                    >
                      {item.action}
                    </StatusBadge>
                  </div>

                  <div className="activity-item-date">
                    <CalendarDays
                      size={12}
                      aria-hidden="true"
                    />
                    {formatDateTime(item.created_at)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      <button
        type="button"
        className="activity-back-button"
        onClick={() => window.history.back()}
      >
        <ChevronLeft size={14} aria-hidden="true" />
        Back
      </button>
    </div>
  );
}