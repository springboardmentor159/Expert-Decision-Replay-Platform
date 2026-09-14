import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  getAuditLogs,
  getDecisionHistory,
  getDecisionVersions,
  getDecisionVersion,
} from "../../services/auditService";

import { getDecisions } from "../../services/decisionService";

import PageHeader from "../../components/PageHeader";
import Button from "../../components/Button";
import Alert from "../../components/Alert";
import EmptyState from "../../components/EmptyState";

const Audit = () => {
  const navigate = useNavigate();

  // =========================================================
  // AUDIT LOG STATE
  // =========================================================

  const [logs, setLogs] = useState([]);
  const [auditLoading, setAuditLoading] = useState(true);
  const [auditError, setAuditError] = useState("");

  // =========================================================
  // DECISION STATE
  // =========================================================

  const [decisions, setDecisions] = useState([]);
  const [selectedDecisionId, setSelectedDecisionId] = useState("");

  const [decisionLoading, setDecisionLoading] = useState(false);
  const [decisionError, setDecisionError] = useState("");

  // =========================================================
  // HISTORY / VERSION STATE
  // =========================================================

  const [history, setHistory] = useState([]);
  const [versions, setVersions] = useState([]);

  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyError, setHistoryError] = useState("");

  const [selectedVersion, setSelectedVersion] = useState(null);
  const [versionLoading, setVersionLoading] = useState(false);
  const [versionError, setVersionError] = useState("");

  // =========================================================
  // AUDIT FILTER STATE
  // =========================================================

  const [actionFilter, setActionFilter] = useState("");
  const [entityTypeFilter, setEntityTypeFilter] = useState("");

  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [total, setTotal] = useState(0);

  // =========================================================
  // LOAD AUDIT LOGS
  // =========================================================

  const loadAuditLogs = async () => {
    try {
      setAuditLoading(true);
      setAuditError("");

      const params = {
        page,
        page_size: pageSize,
      };

      if (actionFilter.trim()) {
        params.action = actionFilter.trim();
      }

      if (entityTypeFilter.trim()) {
        params.entity_type = entityTypeFilter.trim();
      }

      const data = await getAuditLogs(params);

      // Backend returns:
      // {
      //   items: [...],
      //   page: 1,
      //   page_size: 20,
      //   total: 10
      // }

      setLogs(
        Array.isArray(data)
          ? data
          : data?.items || []
      );

      setTotal(
        Array.isArray(data)
          ? data.length
          : data?.total || 0
      );
    } catch (err) {
      console.error("Audit loading error:", err);

      if (err.response?.status === 401) {
        setAuditError("You are not authenticated.");
      } else if (err.response?.status === 403) {
        setAuditError(
          "Administrator access required to view audit information."
        );
      } else if (err.response?.status === 404) {
        setAuditError(
          "Audit endpoint was not found. Please check the backend route."
        );
      } else if (err.response?.status === 422) {
        setAuditError(
          err.response?.data?.detail ||
            "Invalid audit filter or pagination values."
        );
      } else if (err.response?.status === 500) {
        setAuditError(
          "Server error. Please try again later."
        );
      } else {
        setAuditError(
          "Failed to load audit information."
        );
      }

      setLogs([]);
      setTotal(0);
    } finally {
      setAuditLoading(false);
    }
  };

  // =========================================================
  // LOAD DECISIONS
  // =========================================================

  const loadDecisions = async () => {
    try {
      setDecisionLoading(true);
      setDecisionError("");

      const data = await getDecisions({
        page: 1,
        limit: 100,
        sort_by: "created_at",
        sort_order: "desc",
      });

      if (Array.isArray(data)) {
        setDecisions(data);
      } else if (Array.isArray(data?.items)) {
        setDecisions(data.items);
      } else {
        setDecisions([]);
      }
    } catch (err) {
      console.error("Decision loading error:", err);

      if (err.response?.status === 401) {
        setDecisionError(
          "You are not authenticated."
        );
      } else if (err.response?.status === 403) {
        setDecisionError(
          "You do not have permission to view decisions."
        );
      } else if (err.response?.status === 422) {
        setDecisionError(
          "Invalid decision request."
        );
      } else if (err.response?.status === 500) {
        setDecisionError(
          "Server error while loading decisions."
        );
      } else {
        setDecisionError(
          "Failed to load decisions."
        );
      }

      setDecisions([]);
    } finally {
      setDecisionLoading(false);
    }
  };

  // =========================================================
  // LOAD HISTORY AND VERSIONS
  // =========================================================

  const loadDecisionHistory = async (decisionId) => {
    if (!decisionId) {
      setHistory([]);
      setVersions([]);
      return;
    }

    try {
      setHistoryLoading(true);
      setHistoryError("");
      setSelectedVersion(null);

      const [historyData, versionsData] =
        await Promise.all([
          getDecisionHistory(decisionId),
          getDecisionVersions(decisionId),
        ]);

      // Backend history response:
      // {
      //   decision_id: 1,
      //   history: [...]
      // }

      setHistory(
        Array.isArray(historyData)
          ? historyData
          : historyData?.history || []
      );

      // Backend versions response:
      // {
      //   decision_id: 1,
      //   versions: [...]
      // }

      setVersions(
        Array.isArray(versionsData)
          ? versionsData
          : versionsData?.versions || []
      );
    } catch (err) {
      console.error(
        "Decision history loading error:",
        err
      );

      if (err.response?.status === 401) {
        setHistoryError(
          "You are not authenticated."
        );
      } else if (err.response?.status === 403) {
        setHistoryError(
          "You do not have permission to view decision history."
        );
      } else if (err.response?.status === 404) {
        setHistoryError(
          "Decision history was not found."
        );
      } else if (err.response?.status === 500) {
        setHistoryError(
          "Server error while loading decision history."
        );
      } else {
        setHistoryError(
          "Failed to load decision history."
        );
      }

      setHistory([]);
      setVersions([]);
    } finally {
      setHistoryLoading(false);
    }
  };

  // =========================================================
  // VIEW SPECIFIC VERSION
  // =========================================================

  const viewVersion = async (
    decisionId,
    versionNumber
  ) => {
    try {
      setVersionLoading(true);
      setVersionError("");
      setSelectedVersion(null);

      const data = await getDecisionVersion(
        decisionId,
        versionNumber
      );

      setSelectedVersion(data);
    } catch (err) {
      console.error(
        "Version loading error:",
        err
      );

      if (err.response?.status === 401) {
        setVersionError(
          "You are not authenticated."
        );
      } else if (err.response?.status === 403) {
        setVersionError(
          "You do not have permission to view this version."
        );
      } else if (err.response?.status === 404) {
        setVersionError(
          "The requested decision version was not found."
        );
      } else if (err.response?.status === 500) {
        setVersionError(
          "Server error while loading the version."
        );
      } else {
        setVersionError(
          "Failed to load the selected version."
        );
      }
    } finally {
      setVersionLoading(false);
    }
  };

  // =========================================================
  // INITIAL LOAD
  // =========================================================

  useEffect(() => {
    loadAuditLogs();
  }, [page, actionFilter, entityTypeFilter]);

  useEffect(() => {
    loadDecisions();
  }, []);

  // =========================================================
  // DECISION SELECTION
  // =========================================================

  const handleDecisionChange = async (event) => {
    const decisionId = event.target.value;

    setSelectedDecisionId(decisionId);

    if (decisionId) {
      await loadDecisionHistory(decisionId);
    } else {
      setHistory([]);
      setVersions([]);
      setSelectedVersion(null);
      setHistoryError("");
    }
  };

  // =========================================================
  // FILTER HANDLERS
  // =========================================================

  const handleActionChange = (event) => {
    setActionFilter(event.target.value);
    setPage(1);
  };

  const handleEntityTypeChange = (event) => {
    setEntityTypeFilter(event.target.value);
    setPage(1);
  };

  const clearFilters = () => {
    setActionFilter("");
    setEntityTypeFilter("");
    setPage(1);
  };

  // =========================================================
  // PAGINATION
  // =========================================================

  const totalPages = Math.max(
    1,
    Math.ceil(total / pageSize)
  );

  const handlePreviousPage = () => {
    if (page > 1) {
      setPage((currentPage) => currentPage - 1);
    }
  };

  const handleNextPage = () => {
    if (page < totalPages) {
      setPage((currentPage) => currentPage + 1);
    }
  };

  // =========================================================
  // FORMAT DATE
  // =========================================================

  const formatDate = (value) => {
    if (!value) {
      return "-";
    }

    try {
      return new Date(value).toLocaleString();
    } catch {
      return value;
    }
  };

  // =========================================================
  // RENDER
  // =========================================================

  return (
    <div className="audit-page">

      <PageHeader
        title="Audit & Activity"
        subtitle="View administrator audit records and decision history."
      />

      {/* =====================================================
          AUDIT LOGS
      ====================================================== */}

      <section className="audit-section">

        <div className="audit-section-header">
          <div>
            <h2>Audit Logs</h2>
            <p>
              Administrator-only audit records for system activity.
            </p>
          </div>

          <Button
            onClick={loadAuditLogs}
            disabled={auditLoading}
          >
            {auditLoading ? "Refreshing..." : "Refresh"}
          </Button>
        </div>

        {/* FILTERS */}

        <div className="audit-filters">

          <div className="audit-filter-group">
            <label htmlFor="action-filter">
              Action
            </label>

            <input
              id="action-filter"
              type="text"
              value={actionFilter}
              onChange={handleActionChange}
              placeholder="e.g. LOGIN_SUCCESS"
            />
          </div>

          <div className="audit-filter-group">
            <label htmlFor="entity-filter">
              Entity Type
            </label>

            <input
              id="entity-filter"
              type="text"
              value={entityTypeFilter}
              onChange={handleEntityTypeChange}
              placeholder="e.g. Decision"
            />
          </div>

          <div className="audit-filter-actions">
            <Button
              variant="secondary"
              onClick={clearFilters}
            >
              Clear Filters
            </Button>
          </div>

        </div>

        {auditError && (
          <Alert type="error">
            {auditError}
          </Alert>
        )}

        {auditLoading && (
          <div className="audit-loading">
            Loading audit records...
          </div>
        )}

        {!auditLoading &&
          !auditError &&
          logs.length === 0 && (
            <EmptyState
              title="No Audit Records"
              message="No audit records match the current filters."
            />
          )}

        {!auditLoading &&
          !auditError &&
          logs.length > 0 && (
            <>
              <div className="audit-table-wrapper">
                <table className="audit-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Action</th>
                      <th>User</th>
                      <th>Entity Type</th>
                      <th>Entity ID</th>
                      <th>Description</th>
                      <th>Created At</th>
                    </tr>
                  </thead>

                  <tbody>
                    {logs.map((log) => (
                      <tr key={log.id}>
                        <td>{log.id}</td>

                        <td>
                          {log.action || "-"}
                        </td>

                        <td>
                          {log.user_id || "-"}
                        </td>

                        <td>
                          {log.entity_type || "-"}
                        </td>

                        <td>
                          {log.entity_id || "-"}
                        </td>

                        <td>
                          {log.description ||
                            log.message ||
                            "-"}
                        </td>

                        <td>
                          {formatDate(
                            log.created_at
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* PAGINATION */}

              <div className="audit-pagination">

                <Button
                  variant="secondary"
                  onClick={handlePreviousPage}
                  disabled={page <= 1}
                >
                  Previous
                </Button>

                <span>
                  Page {page} of {totalPages}
                </span>

                <Button
                  variant="secondary"
                  onClick={handleNextPage}
                  disabled={page >= totalPages}
                >
                  Next
                </Button>

              </div>
            </>
          )}

      </section>

      {/* =====================================================
          DECISION HISTORY
      ====================================================== */}

      <section className="audit-section">

        <div className="audit-section-header">
          <div>
            <h2>Decision History & Versions</h2>
            <p>
              Select a decision to view its saved history and versions.
            </p>
          </div>
        </div>

        {decisionError && (
          <Alert type="error">
            {decisionError}
          </Alert>
        )}

        <div className="audit-decision-selector">

          <label htmlFor="decision-select">
            Select Decision
          </label>

          <select
            id="decision-select"
            value={selectedDecisionId}
            onChange={handleDecisionChange}
            disabled={decisionLoading}
          >
            <option value="">
              {decisionLoading
                ? "Loading decisions..."
                : "Select a decision"}
            </option>

            {decisions.map((decision) => (
              <option
                key={decision.id}
                value={decision.id}
              >
                #{decision.id} - {decision.title}
              </option>
            ))}
          </select>

        </div>

        {historyLoading && (
          <div className="audit-loading">
            Loading decision history...
          </div>
        )}

        {historyError && (
          <Alert type="error">
            {historyError}
          </Alert>
        )}

        {/* HISTORY */}

        {!historyLoading &&
          !historyError &&
          selectedDecisionId &&
          history.length === 0 && (
            <EmptyState
              title="No History Available"
              message="No saved history records are available for this decision."
            />
          )}

        {!historyLoading &&
          !historyError &&
          history.length > 0 && (
            <div className="audit-history">

              <h3>History</h3>

              <div className="audit-history-list">

                {history.map((item, index) => (
                  <div
                    className="audit-history-item"
                    key={
                      item.id ||
                      `${item.version_number}-${index}`
                    }
                  >

                    <div className="audit-history-version">
                      Version{" "}
                      {item.version_number ??
                        index + 1}
                    </div>

                    <div className="audit-history-content">

                      <p>
                        <strong>
                          Title:
                        </strong>{" "}
                        {item.title || "-"}
                      </p>

                      <p>
                        <strong>
                          Category:
                        </strong>{" "}
                        {item.category || "-"}
                      </p>

                      <p>
                        <strong>
                          Status:
                        </strong>{" "}
                        {item.status || "-"}
                      </p>

                      <p>
                        <strong>
                          Updated:
                        </strong>{" "}
                        {formatDate(
                          item.created_at ||
                            item.updated_at
                        )}
                      </p>

                    </div>

                  </div>
                ))}

              </div>

            </div>
          )}

        {/* VERSIONS */}

        {!historyLoading &&
          !historyError &&
          selectedDecisionId &&
          versions.length > 0 && (
            <div className="audit-versions">

              <h3>Versions</h3>

              <div className="audit-table-wrapper">

                <table className="audit-table">

                  <thead>
                    <tr>
                      <th>Version</th>
                      <th>Title</th>
                      <th>Status</th>
                      <th>Created At</th>
                      <th>Action</th>
                    </tr>
                  </thead>

                  <tbody>
                    {versions.map(
                      (version, index) => (
                        <tr
                          key={
                            version.id ||
                            `${version.version_number}-${index}`
                          }
                        >

                          <td>
                            {version.version_number ??
                              index + 1}
                          </td>

                          <td>
                            {version.title || "-"}
                          </td>

                          <td>
                            {version.status || "-"}
                          </td>

                          <td>
                            {formatDate(
                              version.created_at ||
                                version.updated_at
                            )}
                          </td>

                          <td>
                            <Button
                              variant="secondary"
                              onClick={() =>
                                viewVersion(
                                  selectedDecisionId,
                                  version.version_number
                                )
                              }
                              disabled={
                                versionLoading
                              }
                            >
                              View Version
                            </Button>
                          </td>

                        </tr>
                      )
                    )}
                  </tbody>

                </table>

              </div>

            </div>
          )}

        {/* SELECTED VERSION */}

        {versionError && (
          <Alert type="error">
            {versionError}
          </Alert>
        )}

        {versionLoading && (
          <div className="audit-loading">
            Loading selected version...
          </div>
        )}

        {selectedVersion && (
          <div className="audit-version-details">

            <div className="audit-version-details-header">

              <div>
                <h3>
                  Version{" "}
                  {selectedVersion.version_number}
                </h3>

                <p>
                  Saved version of the selected decision.
                </p>
              </div>

              <Button
                variant="secondary"
                onClick={() =>
                  setSelectedVersion(null)
                }
              >
                Close
              </Button>

            </div>

            <div className="audit-version-grid">

              <div>
                <strong>ID</strong>
                <span>
                  {selectedVersion.id || "-"}
                </span>
              </div>

              <div>
                <strong>Version</strong>
                <span>
                  {selectedVersion.version_number ||
                    "-"}
                </span>
              </div>

              <div>
                <strong>Title</strong>
                <span>
                  {selectedVersion.title || "-"}
                </span>
              </div>

              <div>
                <strong>Category</strong>
                <span>
                  {selectedVersion.category ||
                    "-"}
                </span>
              </div>

              <div>
                <strong>Status</strong>
                <span>
                  {selectedVersion.status || "-"}
                </span>
              </div>

              <div>
                <strong>Created By</strong>
                <span>
                  {selectedVersion.created_by ||
                    "-"}
                </span>
              </div>

              <div>
                <strong>Created At</strong>
                <span>
                  {formatDate(
                    selectedVersion.created_at
                  )}
                </span>
              </div>

              <div>
                <strong>Updated At</strong>
                <span>
                  {formatDate(
                    selectedVersion.updated_at
                  )}
                </span>
              </div>

            </div>

            <div className="audit-version-text">

              <h4>Problem Statement</h4>

              <p>
                {selectedVersion.problem_statement ||
                  "No problem statement available."}
              </p>

            </div>

            <div className="audit-version-text">

              <h4>Rationale</h4>

              <p>
                {selectedVersion.rationale ||
                  "No rationale available."}
              </p>

            </div>

            <div className="audit-version-actions">

              <Button
                onClick={() =>
                  navigate(
                    `/decisions/${selectedDecisionId}`
                  )
                }
              >
                View Current Decision
              </Button>

            </div>

          </div>
        )}

      </section>

    </div>
  );
};

export default Audit;