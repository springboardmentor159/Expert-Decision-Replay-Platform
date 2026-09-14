import { useEffect, useState } from "react";
import api from "../services/api";

function Reports() {
  const [activeReport, setActiveReport] = useState("decisions");

  const [reportData, setReportData] = useState(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fetchReport = async (reportType) => {
    try {
      setLoading(true);
      setError("");
      setReportData(null);

      const endpoint =
        reportType === "decisions"
          ? "/reports/decisions"
          : "/reports/approvals";

      const response = await api.get(endpoint);

      setReportData(response.data);
    } catch (error) {
      console.error("Failed to load report:", error);

      setError(
        error.response?.data?.detail ||
          "Unable to load report."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReport(activeReport);
  }, [activeReport]);

  const formatLabel = (key) => {
    return key
      .replace(/_/g, " ")
      .replace(/\b\w/g, (char) => char.toUpperCase());
  };

  const formatDate = (date) => {
    if (!date) {
      return "N/A";
    }

    return new Date(date).toLocaleString();
  };

  return (
    <div className="page-container">

      <div className="page-header">
        <div>
          <h1>Reports</h1>
          <p>
            View decision and approval reports
          </p>
        </div>
      </div>

      {/* Report Selector */}
      <div className="details-card">

        <div className="decision-actions">

          <button
            type="button"
            className={
              activeReport === "decisions"
                ? "action-button edit-button"
                : "action-button"
            }
            onClick={() =>
              setActiveReport("decisions")
            }
          >
            Decision Report
          </button>

          <button
            type="button"
            className={
              activeReport === "approvals"
                ? "action-button edit-button"
                : "action-button"
            }
            onClick={() =>
              setActiveReport("approvals")
            }
          >
            Approval Report
          </button>

        </div>

      </div>

      {/* Error */}
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="details-card">
          <p>Loading report...</p>
        </div>
      )}

      {/* Report */}
      {!loading && reportData && (
        <>
          {/* Summary */}
          <div className="details-card">

            <h2>
              {activeReport === "decisions"
                ? "Decision Statistics"
                : "Approval Statistics"}
            </h2>

            <div className="details-grid">

              {reportData.summary &&
                Object.entries(
                  reportData.summary
                ).map(([key, value]) => (
                  <div key={key}>

                    <strong>
                      {formatLabel(key)}
                    </strong>

                    <p>{value}</p>

                  </div>
                ))}

            </div>

          </div>

          {/* Report Table */}
          <div className="details-card">

            <h2>
              {activeReport === "decisions"
                ? "Decisions"
                : "Approvals"}
            </h2>

            {reportData.data?.length > 0 ? (

              <div className="decision-table-container">

                <table className="decision-table">

                  {activeReport === "decisions" ? (

                    <>
                      <thead>
                        <tr>
                          <th>ID</th>
                          <th>Title</th>
                          <th>Category</th>
                          <th>Status</th>
                          <th>Created By</th>
                          <th>Alternatives</th>
                          <th>Approvals</th>
                          <th>Created</th>
                        </tr>
                      </thead>

                      <tbody>

                        {reportData.data.map(
                          (decision) => (
                            <tr
                              key={
                                decision.decision_id
                              }
                            >

                              <td>
                                {decision.decision_id}
                              </td>

                              <td className="decision-title">
                                {decision.title}
                              </td>

                              <td>
                                {decision.category ||
                                  "N/A"}
                              </td>

                              <td>
                                {decision.status ||
                                  "N/A"}
                              </td>

                              <td>
                                {decision.created_by ||
                                  "N/A"}
                              </td>

                              <td>
                                {
                                  decision.number_of_alternatives
                                }
                              </td>

                              <td>
                                {
                                  decision.number_of_approvals
                                }
                              </td>

                              <td>
                                {formatDate(
                                  decision.created_date
                                )}
                              </td>

                            </tr>
                          )
                        )}

                      </tbody>
                    </>

                  ) : (

                    <>
                      <thead>
                        <tr>
                          <th>Approval ID</th>
                          <th>Decision ID</th>
                          <th>Decision</th>
                          <th>Reviewer</th>
                          <th>Status</th>
                          <th>Assigned</th>
                          <th>Completed</th>
                          <th>Turnaround</th>
                        </tr>
                      </thead>

                      <tbody>

                        {reportData.data.map(
                          (approval) => (
                            <tr
                              key={
                                approval.approval_id
                              }
                            >

                              <td>
                                {approval.approval_id}
                              </td>

                              <td>
                                {approval.decision_id}
                              </td>

                              <td className="decision-title">
                                {approval.title ||
                                  "N/A"}
                              </td>

                              <td>
                                {approval.reviewer ||
                                  "N/A"}
                              </td>

                              <td>
                                {approval.status ||
                                  "N/A"}
                              </td>

                              <td>
                                {formatDate(
                                  approval.assigned_at
                                )}
                              </td>

                              <td>
                                {formatDate(
                                  approval.completed_at
                                )}
                              </td>

                              <td>
                                {approval.turnaround ||
                                  "N/A"}
                              </td>

                            </tr>
                          )
                        )}

                      </tbody>
                    </>

                  )}

                </table>

              </div>

            ) : (

              <p>
                No report data available.
              </p>

            )}

          </div>

          {/* Pagination Information */}
          <div className="details-card">

            <p>
              Showing{" "}
              <strong>
                {reportData.data?.length || 0}
              </strong>{" "}
              of{" "}
              <strong>
                {reportData.total_records || 0}
              </strong>{" "}
              records
            </p>

            <p>
              Page {reportData.page || 1} of{" "}
              {reportData.total_pages || 1}
            </p>

          </div>
        </>
      )}

    </div>
  );
}

export default Reports;