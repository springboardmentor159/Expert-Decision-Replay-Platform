import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  ArrowLeft,
  CalendarDays,
  Clock3,
  History,
  RefreshCw,
  GitBranch,
  User,
  Activity,
  FileText,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Archive,
  CircleDot,
} from "lucide-react";

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

const getStatusInfo = (status) => {
  switch (status) {
    case "Approved":
      return {
        className: "dh-status-approved",
        icon: <CheckCircle2 size={14} />,
      };

    case "Rejected":
      return {
        className: "dh-status-rejected",
        icon: <XCircle size={14} />,
      };

    case "Under Review":
      return {
        className: "dh-status-review",
        icon: <Clock3 size={14} />,
      };

    case "Archived":
      return {
        className: "dh-status-archived",
        icon: <Archive size={14} />,
      };

    case "Draft":
    default:
      return {
        className: "dh-status-draft",
        icon: <CircleDot size={14} />,
      };
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
        getItems(versionsResponse, [
          "versions",
          "results",
          "data",
        ])
      );

      setHistory(
        getItems(historyResponse, [
          "history",
          "results",
          "data",
        ])
      );

      setTimeline(
        getItems(timelineResponse, [
          "timeline",
          "events",
          "results",
          "data",
        ])
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
        <div className="dh-empty">
          <div className="dh-empty-icon">
            <GitBranch size={25} />
          </div>

          <h3>No versions found</h3>

          <p>
            This decision does not have any
            version history available.
          </p>
        </div>
      );
    }

    return (
      <div className="dh-version-list">
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

          const statusInfo =
            getStatusInfo(status);

          return (
            <div
              className="dh-version-card"
              key={
                version?.id ??
                `${versionNumber}-${index}`
              }
            >
              <div className="dh-version-top">

                <div className="dh-version-number">
                  <GitBranch size={17} />

                  <span>
                    Version {versionNumber}
                  </span>
                </div>

                {status && (
                  <span
                    className={`dh-status ${statusInfo.className}`}
                  >
                    {statusInfo.icon}
                    {status}
                  </span>
                )}
              </div>

              <div className="dh-version-title">
                {title}
              </div>

              <div className="dh-version-meta">
                <span>
                  <User size={14} />
                  {getChangedBy(version)}
                </span>

                <span>
                  <CalendarDays size={14} />
                  {formatDate(
                    version?.created_at ??
                      version?.updated_at ??
                      version?.changed_at
                  )}
                </span>
              </div>

              <div className="dh-version-details">

                {category && (
                  <div className="dh-detail-block">
                    <div className="dh-detail-label">
                      Category
                    </div>

                    <div className="dh-detail-value">
                      {category}
                    </div>
                  </div>
                )}

                {problemStatement && (
                  <div className="dh-detail-block">
                    <div className="dh-detail-label">
                      Problem Statement
                    </div>

                    <div className="dh-detail-value dh-long-text">
                      {problemStatement}
                    </div>
                  </div>
                )}

                {rationale && (
                  <div className="dh-detail-block">
                    <div className="dh-detail-label">
                      Rationale
                    </div>

                    <div className="dh-detail-value dh-long-text">
                      {rationale}
                    </div>
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
        <div className="dh-empty">
          <div className="dh-empty-icon">
            <History size={25} />
          </div>

          <h3>No history found</h3>

          <p>
            No recorded decision history is
            available.
          </p>
        </div>
      );
    }

    return (
      <div className="dh-history-list">
        {history.map((item, index) => {
          const action =
            item?.action ??
            item?.event_type ??
            item?.type ??
            "Activity";

          return (
            <div
              className="dh-history-row"
              key={
                item?.id ??
                `${action}-${index}`
              }
            >
              <div className="dh-history-icon">
                <Activity size={17} />
              </div>

              <div className="dh-history-main">
                <div className="dh-history-heading">
                  <h3>{action}</h3>

                  <span>
                    {formatDate(
                      getEventDate(item)
                    )}
                  </span>
                </div>

                <p>
                  {getEventDescription(item) ||
                    "Decision history activity"}
                </p>

                <div className="dh-history-user">
                  <User size={13} />
                  User: {getChangedBy(item)}
                </div>
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
        <div className="dh-empty">
          <div className="dh-empty-icon">
            <Clock3 size={25} />
          </div>

          <h3>No timeline events</h3>

          <p>
            No timeline events are available
            for this decision.
          </p>
        </div>
      );
    }

    return (
      <div className="dh-timeline">
        {timeline.map((event, index) => (
          <div
            className="dh-timeline-item"
            key={
              event?.id ??
              `${getEventTitle(event)}-${index}`
            }
          >
            <div className="dh-timeline-line">
              <div className="dh-timeline-dot">
                <CircleDot size={10} />
              </div>
            </div>

            <div className="dh-timeline-card">
              <div className="dh-timeline-heading">
                <div>
                  <h3>
                    {getEventTitle(event)}
                  </h3>
                </div>

                <span>
                  <CalendarDays size={13} />
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

              <div className="dh-timeline-user">
                <User size={13} />
                User: {getChangedBy(event)}
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="dh-page">

      <style>{`
        .dh-page {
          max-width: 1150px;
          margin: 0 auto;
          padding: 4px 0 40px;
        }

        .dh-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          gap: 20px;
          margin-bottom: 26px;
        }

        .dh-header-left {
          display: flex;
          align-items: flex-start;
          gap: 15px;
        }

        .dh-header-icon {
          width: 50px;
          height: 50px;
          min-width: 50px;
          border-radius: 14px;
          background: #eaf2ff;
          color: #2563eb;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .dh-back {
          display: inline-flex;
          align-items: center;
          gap: 7px;
          text-decoration: none;
          color: #64748b;
          font-size: 13px;
          font-weight: 600;
          margin-bottom: 8px;
        }

        .dh-back:hover {
          color: #2563eb;
        }

        .dh-eyebrow {
          color: #64748b;
          text-transform: uppercase;
          letter-spacing: .08em;
          font-size: 11px;
          font-weight: 800;
          margin-bottom: 5px;
        }

        .dh-header h1 {
          margin: 0;
          color: #0f172a;
          font-size: 29px;
          line-height: 1.2;
        }

        .dh-header p {
          margin: 7px 0 0;
          color: #64748b;
          font-size: 14px;
        }

        .dh-actions {
          display: flex;
          gap: 10px;
          align-items: center;
        }

        .dh-button {
          min-height: 42px;
          padding: 0 15px;
          border: 1px solid #cbd5e1;
          border-radius: 9px;
          background: #fff;
          color: #334155;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          font-family: inherit;
          font-size: 13px;
          font-weight: 700;
          text-decoration: none;
          cursor: pointer;
        }

        .dh-button:hover:not(:disabled) {
          background: #f8fafc;
          border-color: #94a3b8;
        }

        .dh-button:disabled {
          opacity: .6;
          cursor: not-allowed;
        }

        .dh-error {
          display: flex;
          align-items: flex-start;
          gap: 12px;
          padding: 15px 17px;
          margin-bottom: 20px;
          border: 1px solid #fecaca;
          border-radius: 12px;
          background: #fef2f2;
          color: #991b1b;
        }

        .dh-error-icon {
          margin-top: 1px;
        }

        .dh-error strong {
          display: block;
          font-size: 14px;
          margin-bottom: 3px;
        }

        .dh-error p {
          margin: 0 0 10px;
          font-size: 13px;
          line-height: 1.5;
        }

        .dh-main-card {
          background: #fff;
          border: 1px solid #e2e8f0;
          border-radius: 18px;
          box-shadow: 0 8px 30px rgba(15, 23, 42, .06);
          overflow: hidden;
        }

        .dh-tabs {
          display: flex;
          gap: 4px;
          padding: 8px;
          border-bottom: 1px solid #e2e8f0;
          background: #f8fafc;
        }

        .dh-tab {
          flex: 1;
          border: none;
          background: transparent;
          border-radius: 9px;
          min-height: 45px;
          padding: 0 15px;
          color: #64748b;
          font-family: inherit;
          font-size: 13px;
          font-weight: 700;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
        }

        .dh-tab:hover {
          color: #334155;
          background: #fff;
        }

        .dh-tab.active {
          background: #fff;
          color: #2563eb;
          box-shadow: 0 1px 4px rgba(15, 23, 42, .08);
        }

        .dh-tab-count {
          min-width: 22px;
          height: 22px;
          padding: 0 6px;
          border-radius: 20px;
          background: #e2e8f0;
          color: #475569;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          font-size: 11px;
        }

        .dh-tab.active .dh-tab-count {
          background: #dbeafe;
          color: #2563eb;
        }

        .dh-content {
          padding: 26px;
        }

        .dh-loading {
          min-height: 260px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #64748b;
          font-size: 14px;
        }

        .dh-empty {
          min-height: 250px;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          text-align: center;
          padding: 30px;
        }

        .dh-empty-icon {
          width: 54px;
          height: 54px;
          border-radius: 14px;
          background: #f1f5f9;
          color: #64748b;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-bottom: 14px;
        }

        .dh-empty h3 {
          margin: 0 0 6px;
          color: #334155;
          font-size: 16px;
        }

        .dh-empty p {
          max-width: 430px;
          margin: 0;
          color: #94a3b8;
          font-size: 13px;
          line-height: 1.6;
        }

        .dh-version-list {
          display: flex;
          flex-direction: column;
          gap: 17px;
        }

        .dh-version-card {
          border: 1px solid #e2e8f0;
          border-radius: 14px;
          padding: 20px;
          background: #fff;
          transition: box-shadow .2s ease, border-color .2s ease;
        }

        .dh-version-card:hover {
          border-color: #cbd5e1;
          box-shadow: 0 5px 18px rgba(15, 23, 42, .05);
        }

        .dh-version-top {
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 12px;
          margin-bottom: 13px;
        }

        .dh-version-number {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          color: #2563eb;
          font-size: 13px;
          font-weight: 800;
        }

        .dh-version-title {
          color: #0f172a;
          font-size: 18px;
          font-weight: 750;
          margin-bottom: 12px;
        }

        .dh-status {
          display: inline-flex;
          align-items: center;
          gap: 5px;
          padding: 5px 9px;
          border-radius: 20px;
          font-size: 11px;
          font-weight: 750;
          white-space: nowrap;
        }

        .dh-status-approved {
          background: #dcfce7;
          color: #166534;
        }

        .dh-status-rejected {
          background: #fee2e2;
          color: #991b1b;
        }

        .dh-status-review {
          background: #fef3c7;
          color: #92400e;
        }

        .dh-status-archived {
          background: #e2e8f0;
          color: #475569;
        }

        .dh-status-draft {
          background: #dbeafe;
          color: #1d4ed8;
        }

        .dh-version-meta {
          display: flex;
          flex-wrap: wrap;
          gap: 18px;
          padding-bottom: 17px;
          border-bottom: 1px solid #e2e8f0;
          color: #64748b;
          font-size: 12px;
        }

        .dh-version-meta span {
          display: inline-flex;
          align-items: center;
          gap: 6px;
        }

        .dh-version-details {
          display: flex;
          flex-direction: column;
          gap: 17px;
          margin-top: 18px;
        }

        .dh-detail-label {
          color: #64748b;
          font-size: 11px;
          font-weight: 800;
          text-transform: uppercase;
          letter-spacing: .05em;
          margin-bottom: 5px;
        }

        .dh-detail-value {
          color: #334155;
          font-size: 13px;
          line-height: 1.6;
        }

        .dh-long-text {
          white-space: pre-wrap;
        }

        .dh-history-list {
          display: flex;
          flex-direction: column;
        }

        .dh-history-row {
          display: flex;
          gap: 14px;
          padding: 19px 4px;
          border-bottom: 1px solid #e2e8f0;
        }

        .dh-history-row:first-child {
          padding-top: 4px;
        }

        .dh-history-row:last-child {
          border-bottom: none;
          padding-bottom: 4px;
        }

        .dh-history-icon {
          width: 38px;
          height: 38px;
          min-width: 38px;
          border-radius: 10px;
          background: #eff6ff;
          color: #2563eb;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .dh-history-main {
          flex: 1;
          min-width: 0;
        }

        .dh-history-heading {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          gap: 15px;
        }

        .dh-history-heading h3 {
          margin: 0;
          color: #0f172a;
          font-size: 15px;
        }

        .dh-history-heading span {
          color: #94a3b8;
          font-size: 11px;
          white-space: nowrap;
        }

        .dh-history-main p {
          margin: 6px 0 9px;
          color: #64748b;
          font-size: 13px;
          line-height: 1.5;
        }

        .dh-history-user,
        .dh-timeline-user {
          display: inline-flex;
          align-items: center;
          gap: 5px;
          color: #94a3b8;
          font-size: 11px;
        }

        .dh-timeline {
          position: relative;
        }

        .dh-timeline-item {
          display: flex;
          gap: 17px;
          position: relative;
          padding-bottom: 20px;
        }

        .dh-timeline-item:last-child {
          padding-bottom: 0;
        }

        .dh-timeline-line {
          position: relative;
          width: 25px;
          min-width: 25px;
          display: flex;
          justify-content: center;
        }

        .dh-timeline-item:not(:last-child)
          .dh-timeline-line::after {
          content: "";
          position: absolute;
          top: 22px;
          bottom: -20px;
          width: 2px;
          background: #e2e8f0;
        }

        .dh-timeline-dot {
          position: relative;
          z-index: 1;
          width: 25px;
          height: 25px;
          border-radius: 50%;
          background: #dbeafe;
          color: #2563eb;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .dh-timeline-card {
          flex: 1;
          border: 1px solid #e2e8f0;
          border-radius: 13px;
          padding: 17px;
          background: #fff;
        }

        .dh-timeline-heading {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          gap: 15px;
        }

        .dh-timeline-heading h3 {
          margin: 0;
          color: #0f172a;
          font-size: 15px;
        }

        .dh-timeline-heading span {
          display: inline-flex;
          align-items: center;
          gap: 5px;
          color: #94a3b8;
          font-size: 11px;
          white-space: nowrap;
        }

        .dh-timeline-card p {
          margin: 8px 0 10px;
          color: #64748b;
          font-size: 13px;
          line-height: 1.55;
        }

        @media (max-width: 750px) {
          .dh-header {
            flex-direction: column;
          }

          .dh-actions {
            width: 100%;
          }

          .dh-button {
            flex: 1;
          }

          .dh-content {
            padding: 19px;
          }

          .dh-tabs {
            overflow-x: auto;
          }

          .dh-tab {
            min-width: 115px;
          }

          .dh-history-heading,
          .dh-timeline-heading {
            flex-direction: column;
            gap: 5px;
          }
        }

        @media (max-width: 520px) {
          .dh-header h1 {
            font-size: 24px;
          }

          .dh-header-icon {
            width: 44px;
            height: 44px;
            min-width: 44px;
          }

          .dh-actions {
            flex-direction: column;
          }

          .dh-button {
            width: 100%;
          }

          .dh-version-top {
            align-items: flex-start;
            flex-direction: column;
          }

          .dh-content {
            padding: 15px;
          }
        }
      `}</style>

      {/* HEADER */}
      <div className="dh-header">
        <div className="dh-header-left">
          <div className="dh-header-icon">
            <History size={24} />
          </div>

          <div>
            <Link
              to={`/decisions/${decisionId}`}
              className="dh-back"
            >
              <ArrowLeft size={15} />
              Back to Decision
            </Link>

            <div className="dh-eyebrow">
              Decision Tracking
            </div>

            <h1>Decision History</h1>

            <p>
              Review versions, historical changes,
              and the complete decision timeline.
            </p>
          </div>
        </div>

        <div className="dh-actions">
          <Link
            to={`/decisions/${decisionId}`}
            className="dh-button"
          >
            <ArrowLeft size={15} />
            Back to Decision
          </Link>

          <button
            type="button"
            className="dh-button"
            onClick={loadHistory}
            disabled={loading}
          >
            <RefreshCw
              size={15}
              className={
                loading ? "dh-spin" : ""
              }
            />

            {loading
              ? "Refreshing..."
              : "Refresh"}
          </button>
        </div>
      </div>

      {/* ERROR */}
      {error && (
        <div className="dh-error">
          <div className="dh-error-icon">
            <AlertCircle size={20} />
          </div>

          <div>
            <strong>
              Unable to load decision history
            </strong>

            <p>{error}</p>

            <button
              type="button"
              className="dh-button"
              onClick={loadHistory}
            >
              Try Again
            </button>
          </div>
        </div>
      )}

      {/* MAIN */}
      <div className="dh-main-card">

        {/* TABS */}
        <div className="dh-tabs">

          <button
            type="button"
            className={
              activeTab === "versions"
                ? "dh-tab active"
                : "dh-tab"
            }
            onClick={() =>
              setActiveTab("versions")
            }
          >
            <GitBranch size={16} />
            Versions
            <span className="dh-tab-count">
              {versions.length}
            </span>
          </button>

          <button
            type="button"
            className={
              activeTab === "history"
                ? "dh-tab active"
                : "dh-tab"
            }
            onClick={() =>
              setActiveTab("history")
            }
          >
            <History size={16} />
            History
            <span className="dh-tab-count">
              {history.length}
            </span>
          </button>

          <button
            type="button"
            className={
              activeTab === "timeline"
                ? "dh-tab active"
                : "dh-tab"
            }
            onClick={() =>
              setActiveTab("timeline")
            }
          >
            <Clock3 size={16} />
            Timeline
            <span className="dh-tab-count">
              {timeline.length}
            </span>
          </button>

        </div>

        {/* CONTENT */}
        <div className="dh-content">

          {loading ? (
            <div className="dh-loading">
              Loading decision history...
            </div>
          ) : error ? (
            <div className="dh-empty">
              <div className="dh-empty-icon">
                <AlertCircle size={25} />
              </div>

              <h3>
                History could not be displayed
              </h3>

              <p>
                Please try refreshing the page or
                use the Try Again button above.
              </p>
            </div>
          ) : (
            <>
              {activeTab === "versions" &&
                renderVersions()}

              {activeTab === "history" &&
                renderHistory()}

              {activeTab === "timeline" &&
                renderTimeline()}
            </>
          )}

        </div>
      </div>
    </div>
  );
}

export default DecisionHistory;