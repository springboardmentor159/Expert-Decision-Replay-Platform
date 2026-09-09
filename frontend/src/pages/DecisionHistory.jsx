import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import {
  getDecisionVersions,
  getDecisionHistory,
  getDecisionTimeline,
  getVersionHistoryErrorMessage,
} from "../api/versionHistoryApi";


const formatDate = (value) => {
  if (!value) {
    return "—";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString();
};


const getItems = (data, possibleKeys = []) => {
  if (Array.isArray(data)) {
    return data;
  }

  for (const key of possibleKeys) {
    if (Array.isArray(data?.[key])) {
      return data[key];
    }
  }

  return [];
};


const getVersionNumber = (version) => {
  return (
    version?.version_number ??
    version?.version ??
    version?.number ??
    "—"
  );
};


const getChangedBy = (item) => {
  return (
    item?.changed_by_name ??
    item?.updated_by_name ??
    item?.created_by_name ??
    item?.user_name ??
    item?.changed_by ??
    item?.updated_by ??
    item?.created_by ??
    item?.user_id ??
    "—"
  );
};


const getEventDate = (item) => {
  return (
    item?.created_at ??
    item?.updated_at ??
    item?.changed_at ??
    item?.timestamp ??
    item?.event_at ??
    item?.date
  );
};


const getEventTitle = (item) => {
  return (
    item?.title ??
    item?.action ??
    item?.event ??
    item?.event_type ??
    item?.description ??
    "Decision activity"
  );
};


const getEventDescription = (item) => {
  return (
    item?.description ??
    item?.details ??
    item?.message ??
    item?.action_description ??
    ""
  );
};


const getStatusClass = (status) => {
  switch (status) {
    case "Approved":
      return "status-approved";

    case "Rejected":
      return "status-rejected";

    case "Under Review":
      return "status-review";

    case "Archived":
      return "status-archived";

    case "Draft":
    default:
      return "status-draft";
  }
};


function DecisionHistory() {
  const { decisionId } = useParams();

  const [versions, setVersions] = useState([]);
  const [history, setHistory] = useState([]);
  const [timeline, setTimeline] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [activeTab, setActiveTab] = useState("versions");


  const loadHistory = useCallback(async () => {
    if (!decisionId) {
      setError("A decision ID is required.");
      setLoading(false);
      return;
    }

    setLoading(true);
    setError("");

    try {
      const [
        versionsResponse,
        historyResponse,
        timelineResponse,
      ] = await Promise.all([
        getDecisionVersions(decisionId),
        getDecisionHistory(decisionId),
        getDecisionTimeline(decisionId),
      ]);

      setVersions(
        getItems(
          versionsResponse,
          [
            "versions",
            "results",
            "data",
          ]
        )
      );

      setHistory(
        getItems(
          historyResponse,
          [
            "history",
            "results",
            "data",
          ]
        )
      );

      setTimeline(
        getItems(
          timelineResponse,
          [
            "timeline",
            "events",
            "results",
            "data",
          ]
        )
      );
    } catch (requestError) {
      console.error(
        "Unable to load decision history:",
        requestError
      );

      setVersions([]);
      setHistory([]);
      setTimeline([]);

      setError(
        getVersionHistoryErrorMessage(
          requestError
        )
      );
    } finally {
      setLoading(false);
    }
  }, [decisionId]);


  useEffect(() => {
    loadHistory();
  }, [loadHistory]);


  const renderVersions = () => {
    if (versions.length === 0) {
      return (
        <div className="empty-state">
          <h3>No versions found</h3>

          <p>
            This decision does not have any
            version history available.
          </p>
        </div>
      );
    }

    return (
      <div className="history-list">
        {versions.map((version, index) => {
          const versionNumber =
            getVersionNumber(version);

          const status =
            version?.status ??
            version?.decision_status ??
            "";

          const title =
            version?.title ??
            "Decision version";

          const problemStatement =
            version?.problem_statement ??
            version?.problem ??
            "";

          const rationale =
            version?.rationale ??
            "";

          const category =
            version?.category ??
            "";

          return (
            <div
              className="card history-item"
              key={
                version?.id ??
                `${versionNumber}-${index}`
              }
            >
              <div className="history-item-header">

                <div>
                  <h3>
                    Version {versionNumber}
                  </h3>

                  <p>
                    {title}
                  </p>
                </div>

                {status && (
                  <span
                    className={`status-badge ${getStatusClass(
                      status
                    )}`}
                  >
                    {status}
                  </span>
                )}

              </div>


              <div className="history-meta">

                <span>
                  <strong>
                    Changed by:
                  </strong>{" "}
                  {getChangedBy(version)}
                </span>

                <span>
                  <strong>
                    Date:
                  </strong>{" "}
                  {formatDate(
                    version?.created_at ??
                    version?.updated_at ??
                    version?.changed_at
                  )}
                </span>

              </div>


              <div className="history-details">

                {category && (
                  <div>
                    <strong>
                      Category
                    </strong>

                    <p>
                      {category}
                    </p>
                  </div>
                )}


                {problemStatement && (
                  <div>
                    <strong>
                      Problem Statement
                    </strong>

                    <p>
                      {problemStatement}
                    </p>
                  </div>
                )}


                {rationale && (
                  <div>
                    <strong>
                      Rationale
                    </strong>

                    <p>
                      {rationale}
                    </p>
                  </div>
                )}

              </div>

            </div>
          );
        })}
      </div>
    );
  };


  const renderHistory = () => {
    if (history.length === 0) {
      return (
        <div className="empty-state">
          <h3>No history found</h3>

          <p>
            No recorded decision history is
            available.
          </p>
        </div>
      );
    }

    return (
      <div className="history-list">
        {history.map((item, index) => {
          const action =
            item?.action ??
            item?.event_type ??
            item?.type ??
            "Activity";

          return (
            <div
              className="card history-item"
              key={
                item?.id ??
                `${action}-${index}`
              }
            >
              <div className="history-item-header">

                <div>
                  <h3>
                    {action}
                  </h3>

                  <p>
                    {getEventDescription(item) ||
                      "Decision history activity"}
                  </p>
                </div>

              </div>


              <div className="history-meta">

                <span>
                  <strong>
                    User:
                  </strong>{" "}
                  {getChangedBy(item)}
                </span>

                <span>
                  <strong>
                    Date:
                  </strong>{" "}
                  {formatDate(
                    getEventDate(item)
                  )}
                </span>

              </div>

            </div>
          );
        })}
      </div>
    );
  };


  const renderTimeline = () => {
    if (timeline.length === 0) {
      return (
        <div className="empty-state">
          <h3>No timeline events</h3>

          <p>
            No timeline events are available
            for this decision.
          </p>
        </div>
      );
    }

    return (
      <div className="timeline-container">
        {timeline.map((event, index) => (
          <div
            className="timeline-item"
            key={
              event?.id ??
              `${getEventTitle(event)}-${index}`
            }
          >

            <div className="timeline-marker" />

            <div className="timeline-content">

              <div className="timeline-header">

                <h3>
                  {getEventTitle(event)}
                </h3>

                <span>
                  {formatDate(
                    getEventDate(event)
                  )}
                </span>

              </div>


              {getEventDescription(event) && (
                <p>
                  {getEventDescription(event)}
                </p>
              )}


              <div className="timeline-meta">
                <strong>
                  User:
                </strong>{" "}
                {getChangedBy(event)}
              </div>

            </div>

          </div>
        ))}
      </div>
    );
  };


  return (
    <div className="page-container">

      {/* =========================
          HEADER
      ========================== */}

      <div className="page-header">

        <div>
          <h1>
            Decision History
          </h1>

          <p>
            Review versions, historical changes,
            and the decision timeline.
          </p>
        </div>


        <div className="dashboard-header-actions">

          <Link
            to={`/decisions/${decisionId}`}
            className="secondary-button"
          >
            Back to Decision
          </Link>

          <button
            type="button"
            className="secondary-button"
            onClick={loadHistory}
            disabled={loading}
          >
            {loading
              ? "Refreshing..."
              : "Refresh"}
          </button>

        </div>

      </div>


      {/* =========================
          ERROR
      ========================== */}

      {error && (
        <div className="error-message">

          <strong>
            Unable to load decision history
          </strong>

          <p>
            {error}
          </p>

          <button
            type="button"
            className="secondary-button"
            onClick={loadHistory}
          >
            Try Again
          </button>

        </div>
      )}


      {/* =========================
          CONTENT
      ========================== */}

      <div className="card">

        <div className="history-tabs">

          <button
            type="button"
            className={
              activeTab === "versions"
                ? "history-tab active"
                : "history-tab"
            }
            onClick={() =>
              setActiveTab("versions")
            }
          >
            Versions
          </button>


          <button
            type="button"
            className={
              activeTab === "history"
                ? "history-tab active"
                : "history-tab"
            }
            onClick={() =>
              setActiveTab("history")
            }
          >
            History
          </button>


          <button
            type="button"
            className={
              activeTab === "timeline"
                ? "history-tab active"
                : "history-tab"
            }
            onClick={() =>
              setActiveTab("timeline")
            }
          >
            Timeline
          </button>

        </div>


        {loading ? (
          <div className="loading-state">

            <p>
              Loading decision history...
            </p>

          </div>
        ) : error ? (
          <div className="empty-state">

            <p>
              The decision history could not
              be displayed.
            </p>

          </div>
        ) : (
          <div className="history-content">

            {activeTab === "versions" &&
              renderVersions()}

            {activeTab === "history" &&
              renderHistory()}

            {activeTab === "timeline" &&
              renderTimeline()}

          </div>
        )}

      </div>

    </div>
  );
}


export default DecisionHistory;
