import React, { useEffect, useState } from "react";
import reportService from "../services/reportService";
import "./Reports.css";

const Reports = () => {
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadReports = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await reportService.getDecisionReport();

      console.log("Reports response:", response);

      setReportData(response || {});
    } catch (err) {
      console.error("Error loading reports:", err);

      const detail = err.response?.data?.detail;

      if (Array.isArray(detail)) {
        setError(
          detail
            .map((item) => item.msg || "Validation error")
            .join(", ")
        );
      } else if (typeof detail === "string") {
        setError(detail);
      } else {
        setError("Unable to load reports.");
      }

      setReportData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReports();
  }, []);

  const summary = reportData?.summary || {};

  const totalDecisions = summary.total || 0;
  const approvedDecisions = summary.approved || 0;
  const pendingDecisions = summary.under_review || 0;
  const rejectedDecisions = summary.rejected || 0;

  const decisionData = Array.isArray(reportData?.data)
    ? reportData.data
    : [];

  const getPercentage = (value) => {
    if (!totalDecisions) return 0;

    return Math.min((value / totalDecisions) * 100, 100);
  };

  const StatCard = ({ title, value, className }) => (
    <div className="report-stat-card">
      <span className="report-stat-title">{title}</span>
      <strong className={className}>{value}</strong>
    </div>
  );

  return (
    <div className="reports-page">

      {/* Header */}
      <div className="reports-header">
        <div>
          <div className="reports-breadcrumb">
            Workspace / Reports
          </div>

          <h1>Reports</h1>

          <p>
            View decision statistics and system reports.
          </p>
        </div>

        <button
          type="button"
          onClick={loadReports}
          className="reports-refresh-btn"
        >
          ↻ Refresh
        </button>
      </div>

      {/* Loading */}
      {loading && (
        <div className="reports-state-card">
          <div className="reports-spinner"></div>

          <h3>Loading reports...</h3>

          <p>
            Please wait while the report data is loaded.
          </p>
        </div>
      )}

      {/* Error */}
      {!loading && error && (
        <div className="reports-error">

          <div className="reports-error-icon">
            !
          </div>

          <div>
            <strong>
              Unable to load reports
            </strong>

            <p>{error}</p>
          </div>

          <button
            type="button"
            onClick={loadReports}
            className="reports-retry-btn"
          >
            Try Again
          </button>

        </div>
      )}

      {/* Report Content */}
      {!loading && !error && reportData && (
        <>
          {/* Section heading */}
          <div className="reports-section-heading">
            <div>
              <h2>Decision Overview</h2>

              <p>
                Summary of decisions recorded in the system.
              </p>
            </div>
          </div>

          {/* Statistics */}
          <div className="reports-stats-grid">

            <StatCard
              title="Total Decisions"
              value={totalDecisions}
              className="stat-blue"
            />

            <StatCard
              title="Approved Decisions"
              value={approvedDecisions}
              className="stat-green"
            />

            <StatCard
              title="Under Review"
              value={pendingDecisions}
              className="stat-yellow"
            />

            <StatCard
              title="Rejected Decisions"
              value={rejectedDecisions}
              className="stat-red"
            />

          </div>

          {/* Main panels */}
          <div className="reports-content-grid">

            {/* Decision Summary */}
            <div className="report-panel">

              <div className="report-panel-header">
                <div>
                  <h2>Decision Summary</h2>

                  <p>
                    Current decision status distribution.
                  </p>
                </div>
              </div>

              <div className="report-progress-list">

                {/* Approved */}
                <div className="report-progress-item">

                  <div className="report-progress-label">
                    <span>Approved</span>

                    <strong>
                      {approvedDecisions}
                    </strong>
                  </div>

                  <div className="report-progress-track">

                    <div
                      className="report-progress approved-progress"
                      style={{
                        width: `${getPercentage(
                          approvedDecisions
                        )}%`,
                      }}
                    ></div>

                  </div>

                </div>

                {/* Under Review */}
                <div className="report-progress-item">

                  <div className="report-progress-label">
                    <span>Under Review</span>

                    <strong>
                      {pendingDecisions}
                    </strong>
                  </div>

                  <div className="report-progress-track">

                    <div
                      className="report-progress pending-progress"
                      style={{
                        width: `${getPercentage(
                          pendingDecisions
                        )}%`,
                      }}
                    ></div>

                  </div>

                </div>

                {/* Rejected */}
                <div className="report-progress-item">

                  <div className="report-progress-label">
                    <span>Rejected</span>

                    <strong>
                      {rejectedDecisions}
                    </strong>
                  </div>

                  <div className="report-progress-track">

                    <div
                      className="report-progress rejected-progress"
                      style={{
                        width: `${getPercentage(
                          rejectedDecisions
                        )}%`,
                      }}
                    ></div>

                  </div>

                </div>

              </div>
            </div>

            {/* Report Information */}
            <div className="report-panel">

              <div className="report-panel-header">
                <div>
                  <h2>Report Information</h2>

                  <p>
                    Details returned by the decision report.
                  </p>
                </div>
              </div>

              <div className="report-info-list">

                <div className="report-info-row">
                  <span>Report Type</span>

                  <strong>
                    {reportData.report || "Decision Report"}
                  </strong>
                </div>

                <div className="report-info-row">
                  <span>Total Decisions</span>

                  <strong>
                    {totalDecisions}
                  </strong>
                </div>

                <div className="report-info-row">
                  <span>Approved</span>

                  <strong>
                    {approvedDecisions}
                  </strong>
                </div>

                <div className="report-info-row">
                  <span>Under Review</span>

                  <strong>
                    {pendingDecisions}
                  </strong>
                </div>

                <div className="report-info-row">
                  <span>Rejected</span>

                  <strong>
                    {rejectedDecisions}
                  </strong>
                </div>

                <div className="report-info-row">
                  <span>Records Returned</span>

                  <strong>
                    {decisionData.length}
                  </strong>
                </div>

              </div>
            </div>

          </div>

          {/* Decision Records */}
          {decisionData.length > 0 && (
            <div className="report-panel report-records-panel">

              <div className="report-panel-header">

                <div>
                  <h2>Decision Records</h2>

                  <p>
                    Decisions included in the report.
                  </p>
                </div>

                <span className="records-count">
                  {decisionData.length} Records
                </span>

              </div>

              <div className="report-table-wrapper">

                <table className="report-table">

                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Title</th>
                      <th>Category</th>
                      <th>Status</th>
                      <th>Created At</th>
                    </tr>
                  </thead>

                  <tbody>

                    {decisionData.map((decision, index) => (

                      <tr key={decision.id || index}>

                        <td>
                          {decision.id || "-"}
                        </td>

                        <td>
                          {decision.title ||
                            decision.name ||
                            "Untitled Decision"}
                        </td>

                        <td>
                          {decision.category || "-"}
                        </td>

                        <td>

                          <span
                            className={`report-status ${
                              decision.status
                                ?.toLowerCase()
                                .replace(/\s+/g, "-") ||
                              "unknown"
                            }`}
                          >
                            {decision.status || "Unknown"}
                          </span>

                        </td>

                        <td>
                          {decision.created_at
                            ? new Date(
                                decision.created_at
                              ).toLocaleDateString()
                            : "-"}
                        </td>

                      </tr>

                    ))}

                  </tbody>

                </table>

              </div>
            </div>
          )}

          {/* No records */}
          {decisionData.length === 0 && (
            <div className="report-panel">

              <div className="report-panel-header">
                <div>
                  <h2>Decision Records</h2>

                  <p>
                    No decision records were returned for this report.
                  </p>
                </div>
              </div>

            </div>
          )}

        </>
      )}

    </div>
  );
};

export default Reports;